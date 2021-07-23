import sys
import socket
import threading


# create a printable character representation of the first 256 integers.
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
    """
    Provides a way to watch the communication going through the proxy
    in real time.
    """
    # if src is a byte string, decode to regular string
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        # grab a piece of the string to dump and put it into the word variable
        word = str(src[i:i+length])

        # substitute the string representation of each character for the
        # corresponding character in the raw string
        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        # add to results the hex value of the index of the first byte in the
        # word, the hex value of the word, and its printable representation
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results
