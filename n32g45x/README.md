# N32G45x

Nations N32G45x series (Arm Cortex-M4) driver library for Zephyr.

## Origin

|              |                                                              |
| ------------ | ------------------------------------------------------------ |
| Upstream     | [`Nsing-Community/N32G45x-SDK`][sdk]                          |
| Package      | `Nations.N32G45x_Library.2.6.0`                               |
| Core         | Arm Cortex-M4                                                 |
| Imported via | `scripts/sync_series.py n32g45x <sdk>/firmware`               |

[sdk]: https://github.com/Nsing-Community/N32G45x-SDK

## Layout

Upstream paths are preserved so that a refresh is a file-for-file copy:

| This directory                          | Upstream source                                                    |
| --------------------------------------- | ------------------------------------------------------------------ |
| `cmsis/device/n32g45x/include/`         | `firmware/CMSIS/device/` — `n32g45x.h`, `n32g45x_conf.h`, `system_n32g45x.h` |
| `cmsis/device/n32g45x/source/`          | `firmware/CMSIS/device/system_n32g45x.c`                           |
| `std_periph/include/`                   | `firmware/n32g45x_std_periph_driver/inc/` — 28 of 30 files         |
| `std_periph/source/`                    | `firmware/n32g45x_std_periph_driver/src/` — 28 files               |

`cmsis/device/n32g45x/` is split into `include/` and `source/` where upstream keeps both flat.
Only the file *set* mirrors upstream; the split is for build ergonomics.

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

The vendored driver sources are BSD 3-Clause, Copyright (c) 2019, 2025 Nations Technologies Inc.
See the license header in each file.
