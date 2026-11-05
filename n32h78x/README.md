# N32H78x

Nations N32H7xx series (Arm Cortex-M7 and Cortex-M4 dual core) driver library for Zephyr.

## Origin

|              |                                                                       |
| ------------ | --------------------------------------------------------------------- |
| Package      | `Nations.N32H7xx_Library.1.3.0`                                       |
| Git copy     | [`NSING-Community/N32H7xx-SDK`][sdk]                                  |
| Core         | Arm Cortex-M7 and Cortex-M4                                           |
| Imported via | `scripts/sync_series.py n32h78x <git copy>/firmware --device-prefix n32h7xx` |

[sdk]: https://github.com/NSING-Community/N32H7xx-SDK

The SDK is distributed as a zip download from nationstech.com (nsing.com.sg). The git copy above
is maintained by NSING; a git revision can be pinned and re-checked.

The device prefix of the SDK is `n32h7xx`, while the Zephyr SoC series is `n32h78x`.
`sync_series.py` therefore needs `--device-prefix n32h7xx` to find
`firmware/n32h7xx_std_periph_driver/`.

## Layout

Upstream paths are preserved so that a refresh is a file-for-file copy:

| This directory                        | Upstream source                                                                |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| `CMSIS/device/`                       | `firmware/CMSIS/device/` — `n32h7xx.h`, `system_n32h7xx.{c,h}`                |
| `n32h7xx_std_periph_driver/inc/`      | `firmware/n32h7xx_std_periph_driver/inc/` — 44 files                          |
| `n32h7xx_std_periph_driver/src/`      | `firmware/n32h7xx_std_periph_driver/src/` — 44 files                          |

Upstream's own directory names are kept, so a refresh is a directory copy rather than a
remapping. The same library serves the Cortex-M7 and the Cortex-M4 image; the core is selected
by the SoC build (`CORE_CM7` / `CORE_CM4`).

All files are stored with LF endings, whatever the SDK ships.

## Deliberately not mirrored

| Upstream path                                       | Why                                                                                                                   |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `firmware/CMSIS/core/`                              | Zephyr's own `cmsis` module supplies the CMSIS core headers. A second copy causes conflicting definitions.             |
| `firmware/CMSIS/device/startup/`                    | Zephyr builds its own vector table from devicetree. The vendor's GCC / EWARM startup files are unused.                 |
| `firmware/CMSIS/device/*_flash.ld`                  | Linker scripts live in the Zephyr tree under `soc/`.                                                                   |
| `firmware/n32h7xx_std_periph_driver/inc/n32h7xx_conf.h` | Not present in the SDK; `sync_series.py` reports it as "missing upstream, skipped".                                |

## Refreshing from upstream

```sh
python scripts/sync_series.py --check n32h78x <path-to>/N32H7xx-SDK/firmware --device-prefix n32h7xx
python scripts/sync_series.py         n32h78x <path-to>/N32H7xx-SDK/firmware --device-prefix n32h7xx
```

`--check` only reports drift and exits non-zero; it never writes.

## License

The vendored driver sources keep their upstream headers, Copyright (c) 2025 Nations Technologies
Inc., and are declared as BSD-3-Clause in the root `REUSE.toml`. They are not edited here — see
the root README for why.
