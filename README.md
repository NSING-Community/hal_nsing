# hal_nsing

Standard driver libraries for Nations Nsing MCUs, packaged as a Zephyr module.

## Supported series

| Directory  | Core       | Upstream SDK                                                          |
| ---------- | ---------- | --------------------------------------------------------------------- |
| `n32g45x/` | Cortex-M4  | [`Nsing-Community/N32G45x-SDK`](https://github.com/Nsing-Community/N32G45x-SDK) |

Further series are added as sibling directories — see [Adding a series](#adding-a-series).

## Repository structure

```
.
├── n32g45x/                 one directory per series, named after the lowercase SoC series
│   ├── README.md            upstream origin, SDK version, what was and was not mirrored
│   ├── cmsis/device/n32g45x/
│   └── std_periph/
├── scripts/sync_series.py   mirror or verify one series against its upstream SDK
├── zephyr/module.yml        Zephyr module definition
└── LICENSE
```

## Per-series layout

Every series directory has the same shape, and mirrors the upstream SDK paths so that a
refresh is a file-for-file copy:

```
<series>/
├── README.md
├── cmsis/device/<series>/
│   ├── include/             <series>.h, <series>_conf.h, system_<series>.h
│   └── source/              system_<series>.c
└── std_periph/
    ├── include/             <series>_std_periph_driver/inc/
    └── source/              <series>_std_periph_driver/src/
```

CMSIS core headers, startup files and linker scripts are **not** part of this module. Zephyr's
`cmsis` module provides the core headers, the vector table is built from devicetree, and linker
scripts live in the Zephyr tree under `soc/`.

## Build integration

`zephyr/module.yml` declares `cmake-ext` and `kconfig-ext`, so the CMake and Kconfig glue that
wires this module into the build lives in the Zephyr tree at `modules/hal_nsing/`, the same
arrangement as `hal_gigadevice` and `hal_wch`.

That glue derives every path from `CONFIG_SOC_SERIES`:

```cmake
set(nsing_soc_dir ${ZEPHYR_HAL_NSING_MODULE_DIR}/${CONFIG_SOC_SERIES})
```

which is why a series directory **must** be named exactly after the lowercase SoC series.

## Adding a series

1. Check the series against the [known-series table](#known-series) below — a few entries there
   are variants rather than series of their own.

2. Clone its SDK and mirror it:

   ```sh
   git clone https://github.com/Nsing-Community/N32G43x-SDK
   python scripts/sync_series.py n32g43x N32G43x-SDK/firmware
   ```

   The script copies only the files a HAL needs, writes them with LF endings, and reports
   everything it deliberately left behind. Re-run it with `--check` at any time to see whether
   the tree has drifted from upstream.

3. Add `n32g43x/README.md`, using `n32g45x/README.md` as the template, recording the upstream
   repository, the SDK package version and any exclusions specific to that series.

4. Add the series to [Supported series](#supported-series) above.

5. Extend `modules/hal_nsing/CMakeLists.txt` and `Kconfig` in the Zephyr tree with the new
   series' peripheral sources, then commit with `git commit -s`.

### Things that vary between series

* **The peripheral library directory name is uniform.** All 21 Nsing SDKs use
  `<lowercase series>_std_periph_driver`, so `sync_series.py` can find it without a mapping
  table.
* **Extra libraries are optional.** `<series>_algo_lib` (present for 11 of the 21 series),
  `<series>_usbfs_driver` / `_usbfsd_driver` / `_usbhs_driver`, `<series>_periph_lib` and
  `<series>_ble_driver` exist for some series only. Add them as separate directories when they
  are actually wired into a build, not speculatively.
* **Some series keep a blob inside a header directory.** Upstream ships
  `n32xx_tsc_alg_api.lib` next to the other headers in `.../std_periph_driver/inc/` for N32G45x,
  N32G4FR and N32WB452. `sync_series.py` drops every `*.lib` along with the header of the same
  stem, so such a file can never be committed by accident.

### Known series

Not all of these are supported yet; the table exists so that a new series can be sized up
before any work starts.

| Series        | Core               | SDK repository                                                              |
| ------------- | ------------------ | --------------------------------------------------------------------------- |
| `n32g45x`     | Cortex-M4          | [N32G45x-SDK](https://github.com/Nsing-Community/N32G45x-SDK) *(supported)* |
| `n32g43x`     | Cortex-M4          | [N32G43x-SDK](https://github.com/Nsing-Community/N32G43x-SDK)               |
| `n32g41x`     | Cortex-M4          | [N32G41x-SDK](https://github.com/Nsing-Community/N32G41x-SDK)               |
| `n32g4fr`     | Cortex-M4          | [N32G4FR-SDK](https://github.com/Nsing-Community/N32G4FR-SDK)               |
| `n32g430`     | Cortex-M4          | [N32G430-SDK](https://github.com/Nsing-Community/N32G430-SDK)               |
| `n32g401`     | Cortex-M4          | [N32G401-SDK](https://github.com/Nsing-Community/N32G401-SDK)               |
| `n32g05x`     | Cortex-M0          | [N32G05x-SDK](https://github.com/Nsing-Community/N32G05x-SDK)               |
| `n32g033`     | Cortex-M0          | [N32G033-SDK](https://github.com/Nsing-Community/N32G033-SDK)               |
| `n32g032`     | Cortex-M0          | [N32G032-SDK](https://github.com/Nsing-Community/N32G032-SDK)               |
| `n32g031`     | Cortex-M0          | [N32G031-SDK](https://github.com/Nsing-Community/N32G031-SDK)               |
| `n32g030`     | Cortex-M0          | [N32G030-SDK](https://github.com/Nsing-Community/N32G030-SDK)               |
| `n32g003`     | Cortex-M0          | [N32G003-SDK](https://github.com/Nsing-Community/N32G003-SDK)               |
| `n32l43x`     | Cortex-M4          | [N32L43x-SDK](https://github.com/Nsing-Community/N32L43x-SDK)               |
| `n32l40x`     | Cortex-M4          | [N32L40x-SDK](https://github.com/Nsing-Community/N32L40x-SDK)               |
| `n32h49x`     | Cortex-M4          | [N32H49x-SDK](https://github.com/Nsing-Community/N32H49x-SDK)               |
| `n32h7xx`     | Cortex-M4 + M7     | [N32H7xx-SDK](https://github.com/Nsing-Community/N32H7xx-SDK)               |
| `n32a455`     | Cortex-M4          | [N32A455-SDK](https://github.com/Nsing-Community/N32A455-SDK)               |
| `n32a052`     | Cortex-M0          | [N32A052-SDK](https://github.com/Nsing-Community/N32A052-SDK)               |
| `n32a003`     | Cortex-M0          | [N32A003-SDK](https://github.com/Nsing-Community/N32A003-SDK)               |
| `n32wb452`    | Cortex-M4          | [N32WB452-SDK](https://github.com/Nsing-Community/N32WB452-SDK)             |
| `n32wb03x`    | Cortex-M0          | [N32WB03x-SDK](https://github.com/Nsing-Community/N32WB03x-SDK)             |

Two entries need care:

* **`n32h7xx` is dual-core** (Cortex-M4 plus Cortex-M7) with per-core startup files, linker
  scripts and algorithm libraries. The single flat series directory used everywhere else cannot
  express that; it needs a per-core split.
* **[`N32M016FocRL`](https://github.com/Nsing-Community/N32M016FocRL) is not a series.** Its
  `firmware/` contains `n32g033_std_periph_driver` and the N32G033 device headers — it is
  N32G033 silicon aimed at FOC motor control. Mirror it as a variant of `n32g033`, using
  `--device-prefix n32g033`, rather than as a series of its own.

## Binary blobs

No precompiled libraries are committed to this repository. Zephyr's
[binary blobs policy](https://docs.zephyrproject.org/latest/contribute/bin_blobs.html) requires
blobs to be declared in the `blobs:` section of `zephyr/module.yml` and fetched with
`west blobs fetch` into `zephyr/blobs/`, which is git-ignored.

Nothing in the module currently references a blob, so no blob is declared. A series that needs
the TSC touch-sensing algorithm will have to add a `blobs:` entry with its URL, SHA256 and
license path.

## License

This repository is distributed under the BSD 3-Clause license; see [LICENSE](LICENSE).

The vendored driver sources under each series directory carry their own BSD 3-Clause headers,
Copyright (c) 2019, 2025 Nations Technologies Inc.
