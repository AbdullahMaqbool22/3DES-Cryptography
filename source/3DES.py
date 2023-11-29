def getCorrectKeyInput(index):
    key = input(f'Enter key {index}: ')
    while len(key) != 8:
        print('Incorrect key format (8 words)')
        key = input(f'Enter key {index}: ')
    # end while

    return textToBinStr(key)
# end getCorrectKeyInput()

def textToBinStr(text):
    return ''.join(f'{ord(x):b}'.zfill(8) for x in text)
# end textToBinStr()

def binStrToText(bin_str):
    return ''.join([chr(int(bin_str[i:i+8], 2)) for i in range(0, len(bin_str), 8)])
# end binStrToText()

def binStrToHexStr(bin_str):
    length = len(bin_str) // 4
    return str(hex(int(bin_str, 2)))[2:].upper().zfill(length)
# end binStrToHexStr()

def hexStrToBinStr(hex_str):
    return bin(int(hex_str, 16))[2:].zfill(64)
# end hexStrToBinStr()

class DES:
    ### all operations only work in binary string, e.g., '01010101' ###
    
    ### tables for subkeys###
    __pc1 = [56, 48, 40, 32, 24, 16,  8,  0,
             57, 49, 41, 33, 25, 17,  9,  1,
             58, 50, 42, 34, 26, 18, 10,  2,
             59, 51, 43, 35, 62, 54, 46, 38,
             30, 22, 14,  6, 61, 53, 45, 37,
             29, 21, 13,  5, 60, 52, 44, 36,
             28, 20, 12,  4, 27, 19, 11,  3
    ] # permuted choice 1 (56)

    __left_rotations = [1, 1, 2, 2, 2, 2, 2, 2,
                        1, 2, 2, 2, 2, 2, 2, 1
    ] # num of left rotations in different iteration (16)

    __pc2 = [13, 16, 10, 23,  0,  4,  2, 27,
             14,  5, 20,  9, 22, 18, 11,  3,
             25,  7, 15,  6, 26, 19, 12,  1,
             40, 51, 30, 36, 46, 54, 29, 39,
             50, 44, 32, 47, 43, 48, 38, 55,
             33, 52, 45, 41, 49, 35, 28, 31
    ] # permuted choice 2 (48)

    ### tables for encryption/decryption ###
    __ip = [57, 49, 41, 33, 25, 17,  9, 1,
            59, 51, 43, 35, 27, 19, 11, 3,
            61, 53, 45, 37, 29, 21, 13, 5,
            63, 55, 47, 39, 31, 23, 15, 7,
            56, 48, 40, 32, 24, 16,  8, 0,
            58, 50, 42, 34, 26, 18, 10, 2,
            60, 52, 44, 36, 28, 20, 12, 4,
            62, 54, 46, 38, 30, 22, 14, 6
    ] # initial permutation (64)

    __e = [31,  0,  1,  2,  3,  4,  3,  4,
           5,  6,  7,  8,  7,  8,  9, 10,
           11, 12, 11, 12, 13, 14, 15, 16,
           15, 16, 17, 18, 19, 20, 19, 20,
           21, 22, 23, 24, 23, 24, 25, 26,
           27, 28, 27, 28, 29, 30, 31,  0
    ] # Expansion table for turning 32 bit blocks into 48 bits (48)

    __sbox = [
        # S1
        [[14,  4, 13,  1,  2, 15, 11,  8,  3, 10,  6, 12,  5,  9,  0,  7],
         [ 0, 15,  7,  4, 14,  2, 13,  1, 10,  6, 12, 11,  9,  5,  3,  8],
         [ 4,  1, 14,  8, 13,  6,  2, 11, 15, 12,  9,  7,  3, 10,  5,  0],
         [15, 12,  8,  2,  4,  9,  1,  7,  5, 11,  3, 14, 10,  0,  6, 13]
        ],

        # S2
        [[15,  1,  8, 14,  6, 11,  3,  4,  9,  7,  2, 13, 12,  0,  5, 10],
         [ 3, 13,  4,  7, 15,  2,  8, 14, 12,  0,  1, 10,  6,  9, 11,  5],
         [ 0, 14,  7, 11, 10,  4, 13,  1,  5,  8, 12,  6,  9,  3,  2, 15],
         [13,  8, 10,  1,  3, 15,  4,  2, 11,  6,  7, 12,  0,  5, 14,  9]
        ],

        # S3
        [[10,  0,  9, 14,  6,  3, 15,  5,  1, 13, 12,  7, 11,  4,  2,  8],
         [13,  7,  0,  9,  3,  4,  6, 10,  2,  8,  5, 14, 12, 11, 15,  1],
         [13,  6,  4,  9,  8, 15,  3,  0, 11,  1,  2, 12,  5, 10, 14,  7],
         [ 1, 10, 13,  0,  6,  9,  8,  7,  4, 15, 14,  3, 11,  5,  2, 12]
        ],

        # S4
        [[ 7, 13, 14,  3,  0,  6,  9, 10,  1,  2,  8,  5, 11, 12,  4, 15],
         [13,  8, 11,  5,  6, 15,  0,  3,  4,  7,  2, 12,  1, 10, 14,  9],
         [10,  6,  9,  0, 12, 11,  7, 13, 15,  1,  3, 14,  5,  2,  8,  4],
         [ 3, 15,  0,  6, 10,  1, 13,  8,  9,  4,  5, 11, 12,  7,  2, 14]
        ],

        # S5
        [[ 2, 12,  4,  1,  7, 10, 11,  6,  8,  5,  3, 15, 13,  0, 14,  9],
         [14, 11,  2, 12,  4,  7, 13,  1,  5,  0, 15, 10,  3,  9,  8,  6],
         [ 4,  2,  1, 11, 10, 13,  7,  8, 15,  9, 12,  5,  6,  3,  0, 14],
         [11,  8, 12,  7,  1, 14,  2, 13,  6, 15,  0,  9, 10,  4,  5,  3]
        ],

        # S6
        [[12,  1, 10, 15,  9,  2,  6,  8,  0, 13,  3,  4, 14,  7,  5, 11],
         [10, 15,  4,  2,  7, 12,  9,  5,  6,  1, 13, 14,  0, 11,  3,  8],
         [ 9, 14, 15,  5,  2,  8, 12,  3,  7,  0,  4, 10,  1, 13, 11,  6],
         [ 4,  3,  2, 12,  9,  5, 15, 10, 11, 14,  1,  7,  6,  0,  8, 13]
        ],

        # S7
        [[ 4, 11,  2, 14, 15,  0,  8, 13,  3, 12,  9,  7,  5, 10,  6,  1],
         [13,  0, 11,  7,  4,  9,  1, 10, 14,  3,  5, 12,  2, 15,  8,  6],
         [ 1,  4, 11, 13, 12,  3,  7, 14, 10, 15,  6,  8,  0,  5,  9,  2],
         [ 6, 11, 13,  8,  1,  4, 10,  7,  9,  5,  0, 15, 14,  2,  3, 12]
        ],

        # S8
        [[13,  2,  8,  4,  6, 15, 11,  1, 10,  9,  3, 14,  5,  0, 12,  7],
         [ 1, 15, 13,  8, 10,  3,  7,  4, 12,  5,  6, 11,  0, 14,  9,  2],
         [ 7, 11,  4,  1,  9, 12, 14,  2,  0,  6, 10, 13, 15,  3,  5,  8],
         [ 2,  1, 14,  7,  4, 10,  8, 13, 15, 12,  9,  0,  3,  5,  6, 11]
        ],
    ] # S-boxes

    __p = [15,  6, 19, 20, 28, 11, 27, 16,
            0, 14, 22, 25,  4, 17, 30,  9,
            1,  7, 23, 13, 31, 26,  2,  8, 
           18, 12, 29,  5, 21, 10,  3, 24
    ] # permutation function used on the output of the S-boxes (32)

    __fp = [39,  7, 47, 15, 55, 23, 63, 31,
            38,  6, 46, 14, 54, 22, 62, 30,
            37,  5, 45, 13, 53, 21, 61, 29,
            36,  4, 44, 12, 52, 20, 60, 28,
            35,  3, 43, 11, 51, 19, 59, 27,
            34,  2, 42, 10, 50, 18, 58, 26,
            33,  1, 41,  9, 49, 17, 57, 25,
            32,  0, 40,  8, 48, 16, 56, 24
    ] # final permutation IP^-1 (48)

    __block_size = 64 # bits
    ENCRYPT = 'DES_ENCRYPT'
    DECRYPT = 'DES_DECRYPT'

    def __init__(self, key):
        self.__key = key # 64 bits
        self.__sub_keys = [] # 48 bits
        self.__generateSubKeys()
    # end __init__()

    def pad(self, data):
        return data + ((DES.__block_size - len(data) % DES.__block_size) * '0')
    # end pad()

    def unpad(self, data):
        return ''.join([data[i:i+8] for i in range(0, len(data), 8) if data[i:i+8] != '00000000'])
    # end unpad()

    def __permutate(self, table, block):
        result = ''
        for i in table:result += block[i]
        return result
    # end __permutate()

    def __generateSubKeys(self):
        key_56 = self.__permutate(DES.__pc1, self.__key) # convert original 64-bit key to 56-bit key
        c = key_56[:len(key_56)//2] # 28 bits
        d = key_56[len(key_56)//2:] # 28 bits

        for i in range(16):
            # left rotation
            c = c[DES.__left_rotations[i]:] + c[:DES.__left_rotations[i]]
            d = d[DES.__left_rotations[i]:] + d[:DES.__left_rotations[i]]
            # permutation => turning 56-bit (c + d) to 48-bit sub key
            self.__sub_keys.append(self.__permutate(DES.__pc2, c + d))
        # end for
        
    # end __generateSubKeys()

    def __f(self, r, sub_key):
        r = self.__permutate(DES.__e, r) # to 48 bits
        r = f'{int(r, 2) ^ int(sub_key, 2):b}'.zfill(48)
        b = [r[i:i+6] for i in range(0, len(r), 6)]

        # Substitution => turning to 32-bit result
        result = ''
        for index, item in enumerate(b):
            row = int(item[0] + item[-1], 2)
            column = int(item[1:5], 2)
            result += f'{DES.__sbox[index][row][column]:b}'.zfill(4)
        # end for

        # Permutation
        return self.__permutate(DES.__p, result)
    # end __f()

    def __cryptBlock(self, type, block): # encrypt/decrypt a block
        block = self.__permutate(DES.__ip, block)
        cur_l, cur_r = '', ''
        pre_l = block[:len(block)//2]
        pre_r = block[len(block)//2:]

        iter_range = None
        if type == DES.ENCRYPT: iter_range = range(16)
        else: iter_range = reversed(range(16))

        for i in iter_range:
            cur_l = pre_r
            cur_r = f'{int(pre_l, 2) ^ int(self.__f(pre_r, self.__sub_keys[i]), 2):b}'.zfill(32)
            pre_l, pre_r = cur_l, cur_r
        # end for
        
        return self.__permutate(DES.__fp, cur_r + cur_l)
    # end __cryptBlock()

    def cryptData(self, type, data): # encrypt/decrypt data
        # split data into 64-bit blocks
        blocks = [data[i:i+DES.__block_size] for i in range(0, len(data), DES.__block_size)]

        # encrypt/decrypt data blocks separately
        crypted_data = ''
        for block in blocks:
            crypted_data += self.__cryptBlock(type, block)
        # end for

        return crypted_data
    # end cryptData()

    def encrypt(self, data):
        if (len(data) % DES.__block_size) == 0: return self.cryptData(DES.ENCRYPT, data)
        else: return self.cryptData(DES.ENCRYPT, self.pad(data))
    # end encrypt()

    def decrypt(self, data):
        if (len(data) % DES.__block_size) != 0: raise Exception('Invalid data length for decryption')
        else: return self.unpad(self.cryptData(DES.DECRYPT, data))
    # end decrypt()

# end class DES

class TripleDES:
    def __init__(self, key1, key2, key3):
        self.des1 = DES(key1)
        self.des2 = DES(key2)
        self.des3 = DES(key3)
    # end __init__()

    def encrypt(self, data): # d1(encrypt)-d2(decrypt)-d3(encrypt)
        return self.des3.encrypt(self.des2.decrypt(self.des1.encrypt(data)))
    # end encrypt()

    def decrypt(self, data): # d3(decrypt)-d2(encrypt)-d1(decrypt)
        return self.des1.decrypt(self.des2.encrypt(self.des3.decrypt(data)))
    # end decrypt()

# end class TripleDES

if __name__ == '__main__':
    while True:
        try:
            # get mode
            print('-Enter mode-')
            print('(1) Encrypt')
            print('(2) Decrypt')
            mode = int(input('Mode: '))
            
            if mode not in {1, 2}:
                raise Exception('Invalid mode!')

            # get keys
            print()
            print('-Enter keys-')
            key1 = getCorrectKeyInput(1)
            key2 = getCorrectKeyInput(2)
            key3 = getCorrectKeyInput(3)
            print()

            # triple des setup
            t_des = TripleDES(key1, key2, key3)

            if mode == 1: # encryption
                # get plaintext
                print('-Enter plaintext-')
                data = textToBinStr(input('Enter plaintext: '))
                print()

                # before cryption
                print('-Before cryption-')
                print(f'Text: {binStrToText(data)}')
                print(f'Hexadecimal: {binStrToHexStr(data)}')
                print(f'Binary: {data}')
                print()

                # encryption
                encrypted_data = t_des.encrypt(data)
                print('-Encryption-')
                print(f'Text: {binStrToText(encrypted_data)}')
                print(f'Hexadecimal: {binStrToHexStr(encrypted_data)}')
                print(f'Binary: {encrypted_data}')
                print()
            elif mode == 2: # decryption
                # get 16 hex numbers
                print('-Enter 16 HEX numbers-')
                data = hexStrToBinStr(input('Enter 16 HEX numbers: '))
                print()

                # before cryption
                print('-Before cryption-')
                print(f'Text: {binStrToText(data)}')
                print(f'Hexadecimal: {binStrToHexStr(data)}')
                print(f'Binary: {data}')
                print()

                # decryption
                decrypted_data = t_des.decrypt(data)
                print('-Decryption-')
                print(f'Text: {binStrToText(decrypted_data)}')
                print(f'Hexadecimal: {binStrToHexStr(decrypted_data)}')
                print(f'Binary: {decrypted_data}')
                print()
        except KeyboardInterrupt:
            print('\nERROR: Interrupted by user\n')
            break
        except Exception as e:
            print(f'\nERROR: {e}\n')
    # end while
# end if
