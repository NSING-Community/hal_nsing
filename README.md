# hal_nsing

Standard driver libraries for all series of Nsing MCUs, packaged as a Zephyr
module.

## Contents

| Directory   | Description                                                                                          |
| ----------- | ---------------------------------------------------------------------------------------------------- |
| `n32g45x/`  | N32G45x series: CMSIS device headers, `system_n32g45x.c` and the N32G45x Standard Peripheral Library |

Every series directory uses the same layout:

```
n32g45x/
├── include/              CMSIS device headers (n32g45x.h, system_n32g45x.h, ...)
├── source/               CMSIS device sources (system_n32g45x.c)
└── standard_peripheral/
    ├── include/          peripheral driver headers
    └── source/           peripheral driver sources
```

so that further Nsing series can be added alongside `n32g45x/`.

## Build integration

`zephyr/module.yml` declares `cmake-ext` and `kconfig-ext`, so the CMake and
Kconfig files that wire this module into the build are provided from the Zephyr
tree under `modules/hal_nsing/`, following the same layout as `hal_wch` and
`hal_gigadevice`.

## Binary blobs

No precompiled libraries are shipped in this repository. Binary artifacts
(for example the TSC touch-sensing algorithm) have to be fetched with
`west blobs fetch` and declared in the `blobs` section of `zephyr/module.yml`.
The `zephyr/blobs/` directory is git-ignored.

## License

Distributed under the BSD 3-Clause license. See [LICENSE](LICENSE).
