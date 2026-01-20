# Copyright (C) 2026 Noa-Emil Nissinen

# This is program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.    If not, see <https://www.gnu.org/licenses/>.

import math
from dataclasses import dataclass
from enum import Enum


class Typename(Enum):
    BYTE = "byte"
    SHORT = "short"
    INT = "int"
    BOOLEAN = "boolean"
    BYTEARRAY = "[]"

    @property
    def is_array(self) -> bool:
        return self == Typename.BYTEARRAY

@dataclass
class Def:
    name: str
    len: int
    type: Typename


def get_type_capacity(typename: Typename) -> int:
    match (typename):
        case Typename.BYTE:
            return 8
        case Typename.SHORT:
            return 16
        case Typename.INT:
            return 32
        case Typename.BOOLEAN:
            return 1
        case Typename.BYTEARRAY:
            return 999999
        case _:
            return 32


def generate_plan(definitions: list[Def]) -> None:
    current_bit_cursor = 0

    print(f"{'FIELD':<10} {'TYPE':<7} | {'IDX':<3} | {'BUF_IDX':<7} | {'MASK (Hex)':<10} | {'UNPACK (Read Logic)':<50} | {'PACK (Write Logic)'}")
    print("-" * 155)

    for definition in definitions:
        # Validation
        cap = get_type_capacity(definition.type)
        if definition.len > cap:
            print(f"ERROR: {definition.name} too big for {definition.type.value}")
            return

        is_array = definition.type.is_array

        if is_array:
            num_chunks = math.ceil(definition.len / 8)
            chunk_size = 8
        else:
            num_chunks = 1
            chunk_size = definition.len

        remaining_total = definition.len

        for i in range(num_chunks):
            bits_in_chunk = min(remaining_total, chunk_size)

            dest_var = f"val[{i}]" if is_array else "val"
            dest_type = "byte" if is_array else definition.type.value

            remaining_chunk_bits = bits_in_chunk

            while remaining_chunk_bits > 0:
                byte_index = current_bit_cursor // 8
                bit_offset = current_bit_cursor % 8

                bits_available_in_byte = 8 - bit_offset
                bits_to_process = min(remaining_chunk_bits, bits_available_in_byte)

                mask = ((1 << bits_to_process) - 1) << (8 - bit_offset - bits_to_process)
                mask_str = f"0x{mask:02x}"

                buf_r_shift = (8 - bit_offset - bits_to_process)

                var_l_shift = remaining_chunk_bits - bits_to_process

                if definition.type == Typename.BOOLEAN:
                    unpack_final = f"{dest_var} = ((buf[{byte_index}] & {mask_str}) != 0);"
                    pack_final = f"buf[{byte_index}] |= ({dest_var} ? (byte) {mask_str} : 0);"
                else:
                    # UNPACK
                    unpack_str = f"(buf[{byte_index}] & {mask_str})"
                    if buf_r_shift > 0:
                        unpack_str = f"({unpack_str} >>> {buf_r_shift})"
                    if var_l_shift > 0:
                        unpack_str = f"({unpack_str} << {var_l_shift})"

                    operator = "=" if remaining_chunk_bits == bits_in_chunk else "|="
                    unpack_final = f"{dest_var} {operator} ({dest_type}) {unpack_str};"

                    # PACK
                    pack_str = dest_var
                    if var_l_shift > 0:
                        pack_str = f"({pack_str} >>> {var_l_shift})"
                    if buf_r_shift > 0:
                        pack_str = f"({pack_str} << {buf_r_shift})"

                    pack_final = f"buf[{byte_index}] |= (byte) ({pack_str} & {mask_str});"

                print(f"{definition.name:<10} {definition.type.value:<7} | {i:<3} | {byte_index:<7} | {mask_str:<10} | {unpack_final:<50} | {pack_final}")

                remaining_chunk_bits -= bits_to_process
                current_bit_cursor += bits_to_process

            remaining_total -= bits_in_chunk

            # Formatting separator between array indices for clarity
            if is_array and remaining_total > 0:
                print(f"{'':<10} {'':<7} | {'-':<3} | {'-':<7} | {'-':<10} | {'-'*50} | {'-'*20}")

    print("-" * 155)
