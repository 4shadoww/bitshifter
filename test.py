from bitshifter import Def, Typename, generate_plan

PACKET_DEF = [
    Def("deviceId", 12, Typename.SHORT),
    Def("flags",    4,  Typename.BYTE),
    Def("signature", 24, Typename.BYTEARRAY),
    Def("checksum", 8,  Typename.BYTE),
    Def("true", 1,  Typename.BOOLEAN),
]

def main() -> None:
    generate_plan(PACKET_DEF)

if __name__ == "__main__":
    main()
