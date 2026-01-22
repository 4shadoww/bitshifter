from bitshifter import Def, Typename, generate_plan, print_plan

PACKET_DEF = [
    Def("flags", 2, Typename.BYTE),
    Def("value1",    10,  Typename.BYTEARRAY),
    Def("value2", 20, Typename.BYTEARRAY),
    Def("checksum", 8,  Typename.BYTE),
    Def("is_enabled", 1,  Typename.BOOLEAN),
]

def main() -> None:
    print_plan(generate_plan(PACKET_DEF))

if __name__ == "__main__":
    main()
