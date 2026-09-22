#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2026 Nsing Technologies Inc.
# SPDX-License-Identifier: BSD-3-Clause
#
"""Mirror one Nsing MCU series from an upstream SDK checkout into this module.

Every Nsing SDK is laid out the same way::

    firmware/
    |-- CMSIS/
    |   |-- core/                  not mirrored (Zephyr's cmsis module provides it)
    |   `-- device/
    |       |-- <dev>.h            -> <series>/CMSIS/device/
    |       |-- <dev>_conf.h       -> <series>/CMSIS/device/
    |       |-- <dev>_flash.ld     not mirrored (lives in the Zephyr tree, soc/)
    |       |-- startup/           not mirrored (Zephyr builds its own vector table)
    |       |-- system_<dev>.c     -> <series>/CMSIS/device/
    |       `-- system_<dev>.h     -> <series>/CMSIS/device/
    `-- <dev>_std_periph_driver/
        |-- inc/*.h                -> <series>/<dev>_std_periph_driver/inc/
        `-- src/*.c                -> <series>/<dev>_std_periph_driver/src/

Destinations keep upstream's own directory names, so a refresh is a directory
copy rather than a remapping.

``<dev>`` is the device prefix and normally equals ``<series>``. Pass
``--device-prefix`` for the exceptions, e.g. N32M016FocRL ships
``n32g033_std_periph_driver`` and is a variant of N32G033 rather than a series
of its own.

Files are written with LF line endings whatever the SDK ships.

Binary blobs are never copied. Upstream keeps ``n32xx_tsc_alg_api.lib`` inside
the header directory it belongs to, so this script drops every ``*.lib`` along
with the header of the same stem -- a directory glob cannot smuggle a
precompiled library in.

Usage::

    sync_series.py         n32g45x /path/to/N32G45x-SDK/firmware
    sync_series.py --check n32g45x /path/to/N32G45x-SDK/firmware
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

FLASH_LD_SUFFIX = "_flash.ld"


def to_lf(data: bytes) -> bytes:
    """Normalise CRLF (and stray CR) to LF."""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def blob_stems(directory: Path) -> set[str]:
    """Stems of the ``*.lib`` files in *directory*, i.e. their companion headers."""
    return {p.stem for p in directory.iterdir() if p.is_file() and p.suffix == ".lib"}


def build_plan(series: str, dev: str, firmware: Path):
    """Return ``(entries, notes)``.

    *entries* is a list of ``(source_path, repo-relative destination)``;
    *notes* explains everything that was deliberately left behind.
    """
    cmsis = firmware / "CMSIS" / "device"
    std = firmware / f"{dev}_std_periph_driver"

    for required in (cmsis, std):
        if not required.is_dir():
            sys.exit(f"error: {required} is not a directory")

    cmsis_dest = f"{series}/CMSIS/device"
    std_dest = f"{series}/{dev}_std_periph_driver"

    entries: list[tuple[Path, str]] = []
    notes: list[str] = []

    wanted = {
        f"{dev}.h": cmsis_dest,
        f"{dev}_conf.h": cmsis_dest,
        f"system_{dev}.h": cmsis_dest,
        f"system_{dev}.c": cmsis_dest,
    }
    for name, dest in sorted(wanted.items()):
        path = cmsis / name
        if path.is_file():
            entries.append((path, f"{dest}/{name}"))
        else:
            notes.append(f"missing upstream, skipped: CMSIS/device/{name}")

    # Surface anything else sitting at CMSIS/device level, so a new upstream
    # file cannot go unnoticed just because it is not in the allow-list above.
    for path in sorted(cmsis.iterdir()):
        if path.is_dir():
            notes.append(f"not mirrored: CMSIS/device/{path.name}/")
        elif path.name not in wanted:
            notes.append(f"not mirrored: CMSIS/device/{path.name}")

    for sub in ("inc", "src"):
        directory = std / sub
        if not directory.is_dir():
            notes.append(f"missing upstream, skipped: {std.name}/{sub}/")
            continue
        blobs = blob_stems(directory)
        for path in sorted(directory.iterdir()):
            if not path.is_file():
                continue
            if path.suffix == ".lib":
                notes.append(f"binary blob dropped: {std.name}/{sub}/{path.name}")
            elif path.stem in blobs:
                notes.append(f"blob companion dropped: {std.name}/{sub}/{path.name}")
            elif path.suffix in (".h", ".c"):
                entries.append((path, f"{std_dest}/{sub}/{path.name}"))
            else:
                notes.append(f"not mirrored: {std.name}/{sub}/{path.name}")

    return entries, notes


def report_notes(notes: list[str]) -> None:
    if notes:
        print("\nnot copied:")
        for note in notes:
            print(f"  - {note}")


def do_sync(entries) -> None:
    written, current = 0, 0
    for src, rel in entries:
        dst = REPO_ROOT / rel
        data = to_lf(src.read_bytes())
        if dst.is_file() and dst.read_bytes() == data:
            current += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        print(f"  updated {rel}")
        written += 1
    print(f"\n{len(entries)} files: {written} written, {current} already current")


def do_check(entries) -> int:
    drift: list[tuple[str, str]] = []
    expected = set()

    for src, rel in entries:
        expected.add(rel)
        dst = REPO_ROOT / rel
        if not dst.is_file():
            drift.append((rel, "missing from the repo"))
        elif dst.read_bytes() != to_lf(src.read_bytes()):
            drift.append((rel, "differs from upstream"))

    # Anything sitting in a mirrored directory that upstream no longer has.
    for dest_dir in sorted({str(Path(rel).parent.as_posix()) for _, rel in entries}):
        for path in sorted((REPO_ROOT / dest_dir).iterdir()):
            if not path.is_file():
                continue
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel not in expected:
                drift.append((rel, "in the repo but not upstream"))

    if drift:
        print(f"{len(drift)} file(s) out of sync:")
        for rel, why in drift:
            print(f"  {rel}: {why}")
        return 1

    print(f"{len(entries)} files match upstream")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mirror one Nsing MCU series from an upstream SDK checkout.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("series", help="series directory name, e.g. n32g45x")
    parser.add_argument(
        "firmware",
        type=Path,
        help="path to the SDK's firmware/ directory, e.g. N32G45x-SDK/firmware",
    )
    parser.add_argument(
        "--device-prefix",
        help="override the device prefix when it differs from SERIES "
        "(e.g. N32M016FocRL ships n32g033_std_periph_driver)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift without writing anything; exits non-zero if out of sync",
    )
    args = parser.parse_args()

    entries, notes = build_plan(args.series, args.device_prefix or args.series, args.firmware)

    print(f"{args.series}: {len(entries)} files from {args.firmware}")
    status = do_check(entries) if args.check else (do_sync(entries) or 0)
    report_notes(notes)
    return status


if __name__ == "__main__":
    sys.exit(main())
