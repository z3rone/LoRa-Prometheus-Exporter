import sys

def readBytes(byte_list):
    n = len(byte_list)-1
    val = 0
    if sys.byteorder != 'little':
        i = 0
        for b in byte_list:
            val += b << (8*i)
            i += 1
    else:
        i = n
        for b in byte_list:
            val += b << (8*i)
            i -= 1
    return val
