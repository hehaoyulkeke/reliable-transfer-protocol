import argparse
import socket
import time

THREOLD = 1024

def read_file(filename):
    ls = []
    size = 0
    with open(filename, 'rb') as f:
        while True:
            n = f.read(THREOLD)
            if len(n) > 0:
                ls.append(n)
                size += len(n)
            else:
                break
    return [None]+ls, size/1000

def make_packet(seq, eof, data):
    return seq.to_bytes(2, byteorder="little") + eof.to_bytes(1, byteorder="little") + data

def run(args):
    host = args.remotehost
    port = args.port
    filename = args.filename
    retry_timeout = args.retryTimeout
    window_size = args.windowSize
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    conn.settimeout(retry_timeout/1000)
    file_data, file_size = read_file(filename)
    base = 1
    next_seq = 1
    start_time = time.time()
    end_time = time.time()

    def slide_window():
        nonlocal base, end_time
        while True:
            try:
                response = conn.recv(THREOLD)
                end_time = time.time()
                ackno = int.from_bytes(response, byteorder='little', signed=False)
                base = ackno+1
                break
            except socket.timeout:
                for i in range(base, next_seq):
                    eof = 1 if i == len(file_data)-1 else 0
                    packet = make_packet(i, eof, file_data[i])
                    conn.sendto(packet, (host, port))

    while next_seq < len(file_data):
        while next_seq < base+window_size and next_seq < len(file_data):
            eof = 1 if next_seq == len(file_data)-1 else 0
            packet = make_packet(next_seq, eof, file_data[next_seq])
            conn.sendto(packet, (host, port))
            next_seq += 1
        # wait timeout
        slide_window()
    
    while base < next_seq:
        slide_window()
    
    print('{}'.format(file_size/(end_time-start_time)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('remotehost', type=str)
    parser.add_argument('port', type=int)
    parser.add_argument('filename', type=str)
    parser.add_argument('retryTimeout', type=int)
    parser.add_argument('windowSize', type=int)
    args = parser.parse_args()
    run(args)