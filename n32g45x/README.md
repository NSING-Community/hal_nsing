# N32G45x

Nations N32G45x series (Arm Cortex-M4) driver library for Zephyr.

## Origin

|              |                                                              |
| ------------ | ------------------------------------------------------------ |
| Package      | `Nations.N32G45x_Library.2.6.0`                               |
| Git copy     | [`Nsing-Community/N32G45x-SDK`][sdk]                          |
| Core         | Arm Cortex-M4                                                 |
| Imported via | `scripts/sync_series.py n32g45x <git copy>/firmware`          |

[sdk]: https://github.com/Nsing-Community/N32G45x-SDK

Nations publishes no git repository. The SDK is distributed as a zip download from
nationstech.com (nsing.com.sg); the device support files also ship separately as the
`Nationstech.N32G45x_DFP` CMSIS pack. The git copy above is community-maintained, is not
affiliated with the vendor, and carries no license file of its own; it is used here only
because a git revision can be pinned and re-checked.

That copy was verified against the vendor package before import, and the two agree: of the 102
files under the package's `firmware/`, 89 are byte-identical and the remaining 13 differ only
in line endings, with no file differing in content. Everything in this directory comes from
that set.

## Layout

Upstream paths are preserved so that a refresh is a file-for-file copy:

| This directory                        | Upstream source                                                                   |
| ------------------------------------- | --------------------------------------------------------------------------------- |
| `CMSIS/device/`                       | `firmware/CMSIS/device/` — `n32g45x.h`, `n32g45x_conf.h`, `system_n32g45x.{c,h}`  |
| `n32g45x_std_periph_driver/inc/`      | `firmware/n32g45x_std_periph_driver/inc/` — 28 of 30 files                        |
| `n32g45x_std_periph_driver/src/`      | `firmware/n32g45x_std_periph_driver/src/` — 28 files                              |

Upstream's own directory names are kept, so a refresh is a directory copy rather than a
remapping. The only thing missing from `CMSIS/device/` is `startup/` and `n32g45x_flash.ld`,
which belong in the Zephyr tree — see the table below.

All files are stored with LF endings, whatever the SDK ships.

## Deliberately not mirrored

| Upstream path                                       | Why                                                                                                                   |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `firmware/CMSIS/core/`                              | Zephyr's own `cmsis` module supplies the CMSIS core headers. `n32g45x.h` includes `core_cm4.h` and gets it from there. A second copy causes conflicting definitions. |
| `firmware/CMSIS/device/startup/`                    | Zephyr builds its own vector table from devicetree. The vendor's GCC / EWARM / armcc startup files are unused.         |
| `firmware/CMSIS/device/n32g45x_flash.ld`            | Linker scripts live in the Zephyr tree under `soc/`.                                                                   |
| `.../inc/n32xx_tsc_alg_api.{h,lib}`                 | Precompiled touch-sensing algorithm. Zephyr modules do not accept binary blobs that are not declared and fetched — see the root README. |

`n32xx_tsc_alg_api.lib` sits *inside* `inc/`, next to the other headers, so any script that
globbed that directory would quietly commit 3.2 MB of precompiled code. `sync_series.py` drops
every `*.lib` together with the header of the same name, which is what removes both files.

## Refreshing from upstream

```sh
python scripts/sync_series.py --check n32g45x <path-to>/N32G45x-SDK/firmware
python scripts/sync_series.py         n32g45x <path-to>/N32G45x-SDK/firmware
```

`--check` only reports drift and exits non-zero; it never writes.

## License

The vendored driver sources keep their upstream headers, Copyright (c) 2019, 2025 Nations
Technologies Inc., and are declared as BSD-3-Clause in the root `REUSE.toml`. They are not edited
here — see the root README for why.

`n32g457_eth.{c,h}` are the two files dated 2025, and the only two that do not follow the
`n32g45x_<peripheral>.{c,h}` naming; they belong to the N32G457 variant. The rest are dated 2019.
