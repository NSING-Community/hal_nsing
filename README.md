# Introduction

The **hal_nsing** is a set of standard firmware libraries and ARM CMSIS configurations for
NSING N32 MCUs. The HAL is organized following the directory structure detailed below.

## Directory Structure

The directory is composed of three parts:

 - SoC specific libraries.
 - ZephyrRTOS module directory (`zephyr`).
 - This README file.

On top of those sit the files that describe the repository itself: `LICENSE`, `LICENSES/`,
`REUSE.toml`, `.gitattributes` and `scripts/sync_series.py`.

```
.
├── n32g45x/                     one directory per series, named after the lowercase SoC series
│   ├── README.md                upstream origin, SDK version, what was and was not mirrored
│   ├── CMSIS/device/            <series>.h, <series>_conf.h, system_<series>.{c,h}
│   └── <series>_std_periph_driver/{inc,src}/
├── LICENSES/BSD-3-Clause.txt    license text, in the REUSE layout
├── REUSE.toml                   per-path licensing; vendored sources are declared, never edited
├── scripts/sync_series.py       mirror or verify one series against its upstream SDK
├── zephyr/module.yml            Zephyr module definition
├── .gitattributes               pins LF endings for every tracked file
├── .gitignore
└── LICENSE
```

### Per-series layout

Each N32 firmware library is organized in the following structure:

```
<series>/
├── README.md
├── CMSIS/device/            <series>.h, <series>_conf.h, system_<series>.{c,h}
└── <series>_std_periph_driver/
    ├── inc/                 headers
    └── src/                 sources
```

Upstream's own directory names are kept, so a refresh is a directory copy rather than a
remapping. The only thing missing from upstream's `CMSIS/device/` is `startup/` and
`<series>_flash.ld`: CMSIS core headers come from Zephyr's own `cmsis` module, the vector table
is built from devicetree, and linker scripts live in the Zephyr tree under `soc/`.

## Build integration

`zephyr/module.yml` declares `cmake-ext` and `kconfig-ext`, so the CMake and Kconfig glue that
wires this module into the build lives in the Zephyr tree at `modules/hal_nsing/`, the same
arrangement as `hal_gigadevice` and `hal_wch`.

That glue derives every path from `CONFIG_SOC_SERIES`:

```cmake
set(nsing_soc_dir ${ZEPHYR_HAL_NSING_MODULE_DIR}/${CONFIG_SOC_SERIES})
```

which is why a series directory **must** be named exactly after the lowercase SoC series.

## Supported series

| Directory  | Core       | Upstream SDK                                                          |
| ---------- | ---------- | --------------------------------------------------------------------- |
| `n32g45x/` | Cortex-M4  | [`NSING-Community/N32G45x-SDK`](https://github.com/NSING-Community/N32G45x-SDK) |

Further series are added as sibling directories, named after the lowercase `CONFIG_SOC_SERIES` —
see [Adding a series](#adding-a-series).

# How to submit code

 - **Land the newest firmware library version.** The vendor's SDK package is the source of
   truth here, not the git copy it is fetched from: Nations publishes no git repository, so the
   SDK copies on GitHub are community mirrors. The package a series was taken from is recorded
   in the series' README — check a mirror against it before trusting it.

 - **The vendored sources are never edited.** They are a byte-for-byte mirror of the upstream
   SDK, and editing them would break the invariant `scripts/sync_series.py --check` relies on.
   Their licensing is declared in `REUSE.toml` instead of written into the files. See
   [License](#license).

 - **Changes are submitted with Linux LF endings.** `.gitattributes` pins `* text=auto eol=lf`
   so the working tree is byte-identical to the committed blobs on every platform, and
   `sync_series.py` normalises on write whatever the SDK ships. There is no need to run
   `dos2unix` by hand.

 - **Directory names keep upstream's spelling.** That includes the capital `CMSIS`. This
   deliberately departs from the lowercase convention `hal_gigadevice` follows: keeping
   upstream's own names is what makes refreshing a series a directory copy rather than a
   remapping. Exceptions should be discussed at review phase.

 - **A series directory is named after the lowercase `CONFIG_SOC_SERIES`.** This one *is* a
   hard rule — the build glue derives every path from
   `${ZEPHYR_HAL_NSING_MODULE_DIR}/${CONFIG_SOC_SERIES}`.

 - **`python scripts/sync_series.py --check` reports no drift** for every series.

 - **`reuse lint` reports no missing licenses.** A new series needs its own entry in
   `REUSE.toml`; the globs there are written per series and are not covered automatically.

## Adding a series

1. Clone its SDK and mirror it:

   ```sh
   git clone https://github.com/NSING-Community/N32G43x-SDK
   python scripts/sync_series.py n32g43x N32G43x-SDK/firmware
   ```

   The script copies only the files a HAL needs, writes them with LF endings, and reports
   everything it deliberately left behind. Re-run it with `--check` at any time to see whether
   the tree has drifted from upstream. Pass `--device-prefix` when the SDK's device prefix
   differs from the series name.

2. Add `n32g43x/README.md`, using `n32g45x/README.md` as the template, recording the upstream
   repository, the SDK package version and any exclusions specific to that series.

3. Add the series to [Supported series](#supported-series) above.

4. Add the series to `REUSE.toml`, under the vendored-sources annotation.

5. Extend `modules/hal_nsing/CMakeLists.txt` and `Kconfig` in the Zephyr tree with the new
   series' peripheral sources, then commit with `git commit -s`.

6. Run `reuse lint` and make sure it still reports 0 missing licenses.

## Exceptions

 - **A precompiled blob sits inside a header directory.** Upstream ships
   `n32xx_tsc_alg_api.lib` next to the other headers in `.../std_periph_driver/inc/` for
   N32G45x, N32G4FR and N32WB452. Any glob or whole-directory copy of that directory would
   quietly commit 3.2 MB of precompiled code. `sync_series.py` drops every `*.lib` along with
   the header of the same stem, which is what removes both files.

 - **Extra libraries are optional.** `<series>_algo_lib`, `<series>_usbfs_driver` /
   `_usbfsd_driver` / `_usbhs_driver`, `<series>_periph_lib` and `<series>_ble_driver` exist
   for some series only. Add them as separate directories when they are actually wired into a
   build, not speculatively. Note that `<series>_algo_lib/lib/` holds five prebuilt libraries
   of its own (`aes`, `algo_common`, `des`, `hash`, `rng` for N32G45x), which are out of
   scope until a `blobs:` entry exists for them.

# Binary blobs

No precompiled libraries are committed to this repository. Zephyr's
[binary blobs policy](https://docs.zephyrproject.org/latest/contribute/bin_blobs.html) requires
blobs to be declared in the `blobs:` section of `zephyr/module.yml` and fetched with
`west blobs fetch` into `zephyr/blobs/`, which is git-ignored; `hal_stm32` is a working example
of that layout. Nothing in the module currently references a blob, so no blob is declared. A
series that needs the TSC touch-sensing algorithm will have to add a `blobs:` entry with its
URL, SHA256 and license path.

# License

BSD 3-Clause; see [LICENSE](LICENSE). The repository is compliant with
[REUSE](https://reuse.software/) 3.3 — `REUSE.toml` and `LICENSES/` carry the machine-readable
form, and `reuse lint` is expected to stay clean.

The driver sources under each series directory are vendored verbatim from the upstream SDK and
keep their own headers, Copyright (c) 2019, 2025 Nations Technologies Inc. They are **declared**
as BSD-3-Clause in `REUSE.toml` rather than edited, because editing them would break the
byte-for-byte mirror that `scripts/sync_series.py` maintains.

Note that upstream describes its own terms as "BSD-style" rather than naming a SPDX identifier,
and the header text differs in drafting from the standard BSD-3-Clause — the binary-redistribution
clause is not enumerated, and the disclaimer carries an extra "AND NON-INFRINGEMENT". The exact
text is the header of each file. Worth putting to Nations if this module is ever challenged on it.
