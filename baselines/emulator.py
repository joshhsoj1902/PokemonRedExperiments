class Emulator:
    def __init__(self, pyboy):

        self.pyboy = pyboy

    def read_m(self, addr):
        try:
            return self.pyboy.get_memory_value(addr)
        except Exception as e:
            print(f"Error reading memory address ({addr}): {e}")

    def read_bit(self, addr, bit: int) -> bool:
        # add padding so zero will read '0b100000000' instead of '0b0'
        return bin(256 + self.read_m(addr))[-bit-1] == '1'

    def read_triple(self, start_add):
        return 256*256*self.read_m(start_add) + 256*self.read_m(start_add+1) + self.read_m(start_add+2)

    def bit_count(self, bits):
        return bin(bits).count('1')