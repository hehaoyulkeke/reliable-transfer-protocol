import argparse
import socket

THREOLD = 1024
EOF = (1).to_bytes(1, byteorder="little")

def read_file(filename):
    with open(filename, 'rb') as f:
        return f.read()

def process_data(data):
    seq = 1
    while len(data) > THREOLD:
        packet = seq.to_bytes(2, byteorder="little") + (0).to_bytes(1, byteorder="little") + data[:THREOLD]
        data = data[THREOLD:]
        seq += 1
        yield packet
    if len(data) > 0:
        packet = seq.to_bytes(2, byteorder="little") + EOF + data
        yield packet
    else:
        packet = seq.to_bytes(2, byteorder='little') + EOF + b''
        yield packet

def run(args):
    host = args.remotehost
    port = args.port
    filename = args.filename

    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = read_file(filename)
    for packet in process_data(data):
        conn.sendto(packet, (host, port))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('remotehost', type=str)
    parser.add_argument('port', type=int)
    parser.add_argument('filename', type=str)
    args = parser.parse_args()
    run(args)
