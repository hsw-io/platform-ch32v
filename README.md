# CH32V003: development platform for [PlatformIO](https://platformio.org)

The CH32V series offers industrial-grade, general-purpose microcontrollers based on a range of QingKe 32-bit RISC-V cores. All devices feature a DMA and a hardware stack area, which greatly improves interrupt latency. This repository is a PlatformIO platform only for ultra-cheap, low-end CH32V003 with 2kB RAM / 16kB flash

Head over to `examples` folder to see example projects and detailed starting instructions.


# Support
- chips
    - [x] CH32V003 (QingKe V2A)
- development boards
    - [x] CH32V003F4P6-EVT-R0 (official by W.CH)
- frameworks
    - [x] None OS ("Simple Peripheral Library" / native SDK)
- debuggers (also implicitly uploaders)
    - [x] WCH-Link(E)
- uploaders (no debugging)
  - [x] USB ISP bootloader (supported via [wchisp](https://github.com/ch32-rs/wchisp))


# Installation

1. [Install PlatformIO](https://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](https://docs.platformio.org/page/projectconf.html) file:
3. For Linux, add PlatformIO per [documentation](https://docs.platformio.org/en/latest/core/installation/udev-rules.html#platformio-udev-rules). Then, add WCH udev rules by appending the following content to `etc/udev/rules.d/99-platformio-udev.rules`.

```
SUBSYSTEM=="usb", ATTR{idVendor}="1a86", ATTR{idProduct}=="8010", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}="4348", ATTR{idProduct}=="55e0", GROUP="plugdev"
SUBSYSTEM=="usb", ATTR{idVendor}="1a86", ATTR{idProduct}=="8012", GROUP="plugdev"
```

**Without these udev rules or the missing group membership of the user in the plugdev group, accessing the WCH-Link(E) via OpenOCD or wchisp will not work!!**

## Development version

```ini
[env:development]
platform = https://github.com/hsw-io/platform-ch32v003.git
board = ...
...
```

# Configuration

The configuration in regards to the builder scripts etc. are still in progress. See the above mentioned projects repository for now.

