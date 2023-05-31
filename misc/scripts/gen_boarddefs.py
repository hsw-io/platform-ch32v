#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import json

@dataclass
class ChipInfo:
    name: str
    flash_kb: int
    sram_kb: int
    freq_mhz: int
    package: str

    def get_classification_macro(self) -> Optional[str]:
        # the V003 series intentionally has no classification macro
        return None

    def get_riscv_arch_and_abi(self) -> Tuple[str, str]:
        # ch32v00x only rv32ecxw (RISC-V2A)
        name_lower = self.name.lower() 
        if name_lower.startswith("ch32v0"):
            return ("rv32ecxw", "ilp32e")
        else:
            print("ERROR: UNKNOWN CHIP ABI/ARCH FOR " + self.name)
            exit(-1)
            return ("unknown", "unknown")

    def chip_without_package(self) -> str:
        return self.name[:-2]

    def exact_series(self) -> str:
        return self.name[0:len("ch32vxxx")]

chip_db: List[ChipInfo] = [
    # CH32V003
    ChipInfo("CH32V003F4P6", 16, 2, 48, "TSSOP20"),
    ChipInfo("CH32V003F4U6", 16, 2, 48, "QFN20"),
    ChipInfo("CH32V003A4M6", 16, 2, 48, "SOP16"),
    ChipInfo("CH32V003J4M6", 16, 2, 48, "SOP8"),
]

def get_chip(name: str) -> Optional[ChipInfo]:
    for c in chip_db:
        if c.name.lower() == name.lower():
            return c
    return None

@dataclass
class KnownBoard:
    file_name: str
    board_name: str
    chip: ChipInfo
    url: str
    vendor: str
    add_info: Optional[Dict[str, Any]] = None

known_boards: List[KnownBoard] = [
    KnownBoard("ch32v003f4p6_evt_r0", "CH32V003F4P6-EVT-R0", get_chip("CH32V003F4P6"),
               "https://www.aliexpress.com/item/1005004895791296.html", "W.CH"),
]

def create_board_json(info: ChipInfo, board_name:str, output_path: str, patch_info: Optional[Dict[str, Any]] = None, addtl_extra_flags:List[str] = None):
    arch, abi = info.get_riscv_arch_and_abi()
    base_json = {
        "build": {
            "f_cpu": str(info.freq_mhz * 1000_000) + "L",
            "extra_flags": "",
            "hwids": [
                [
                    "0x1A86",
                    "0x8010"
                ]
            ],
            "mabi": abi,
            "march": arch,
            "mcu": info.name.lower(),
            "series": info.exact_series().lower()
        },
        "debug": {
            "onboard_tools": [
                "wch-link"
            ],
            "openocd_config": "wch-riscv.cfg",
            "svd_path": info.exact_series().upper() + "xx.svd"
        },
        "frameworks": [
            "noneos-sdk"
        ],
        "name": board_name,
        "upload": {
            "maximum_ram_size": info.sram_kb * 1024,
            "maximum_size": info.flash_kb * 1024,
            "protocols": [
                "wch-link",
                "isp"
            ],
            "protocol": "wch-link"
        },
        "url": f"http://www.wch-ic.com/products/{info.exact_series().upper()}.html",
        "vendor": "W.CH"
    }
    chip_l = info.name.lower()
    if chip_l.startswith("ch32v003"):
        base_json["build"]["core"] = "ch32v003"
        base_json["build"]["variant"] = "WCH32V003"
    extra_flags = [
        f"-D{info.chip_without_package()}",
        f"-D{info.name[0:len('ch32vxx')]}X",
        f"-D{info.name[0:len('ch32vxxx')]}",
    ]
    classification_macro = info.get_classification_macro()
    if classification_macro is not None:
        extra_flags += ["-D" + classification_macro]
    if addtl_extra_flags is not None:
        extra_flags.extend(addtl_extra_flags)
    base_json["build"]["extra_flags"] = " ".join(extra_flags)
    if patch_info is not None:
        for k, v in patch_info.items():
            # upmost level
            if k.count(".") == 0:
                base_json[k] = v
            # one deeper (e.g. build.extra_flags)
            if k.count(".") == 1:
                k1, k2 = k.split(".")
                base_json[k1][k2] = v
    as_str = json.dumps(base_json, indent=2)
    print("DEFINITION FOR %s:\n%s" % (board_name, as_str))
    try:
        Path(output_path).write_text(as_str, encoding='utf-8')
    except Exception as exc:
        print("Error writing board definition: %s" % repr(exc))


def main():
    # generate board JSON for all known chips directly into boards folder
    base_path = Path(__file__).parents[2].resolve() / "boards"
    # all generic chips first
    for info in chip_db:
        output_path = base_path / f"generic{info.name.upper()}.json"
        name = f"Generic {info.name.upper()}"
        create_board_json(info, name, output_path)
        #return
    # all known boards now
    for known_board in known_boards:
        output_path = base_path / f"{known_board.file_name}.json"
        create_board_json(known_board.chip, known_board.board_name, output_path, {
                          "url": known_board.url, "vendor": known_board.vendor})
    pass


if __name__ == '__main__':
    main()
