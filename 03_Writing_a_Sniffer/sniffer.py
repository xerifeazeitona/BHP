import socket
import os

# host to listen on
HOST = '192.168.69.116'

def main():
    if os.name == 'nt':
        # if host is windows, sniff all incoming packets
        socket_protocol = socket.IPPROTO_IP
    else:
        # if host is linux/mac sniff only ICMP packets
        socket_protocol = socket.IPPROTO_ICMP

    # create raw socket 
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    # bind to public interface
    sniffer.bind((HOST, 0))
    # include the IP header in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # if windows, enable promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # print entire raw packet with no decoding
    print(sniffer.recvfrom(65565))

    # if we're on windows, turn off promiscuous mode
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

if __name__ == '__main__':
    main()
