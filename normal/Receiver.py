import argparse
import socket

THREOLD = 1024*2
EOF = (1).to_bytes(1, byteorder="little")


def run(args):
    port = args.port
    filename = args.filename
    file = open(filename, 'wb')
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    conn.bind(('localhost', port))
    while True:
        packet, _ = conn.recvfrom(THREOLD)
        seq, eof, data = packet[:2], packet[2].to_bytes(1, byteorder='little'), packet[3:]
        if eof != EOF:
            file.write(data)
        else:
            file.write(data)
            break
    file.close()
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    parser.add_argument('filename', type=str)
    args = parser.parse_args()
    run(args)
