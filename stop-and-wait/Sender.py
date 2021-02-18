import argparse
import socket
import time

THREOLD = 1024
EOF = 1

state = 0
retry_count = 0
start_time = None
end_time = None

def read_file(filename):
    with open(filename, 'rb') as f:
        return f.read()

def make_packet(seq, eof, data):
    return seq.to_bytes(2, byteorder="little") + eof.to_bytes(1, byteorder="little") + data

def handle(conn, packet, host, port):
    global state, start_time, end_time, retry_count
    if start_time is None:
        start_time = time.time()
    conn.sendto(packet, (host, port))
    while True:
        try:
            response = conn.recv(THREOLD)
            end_time = time.time()
            ackno = int.from_bytes(response, byteorder='little', signed=False)
            if state != ackno:
                # not desired, just wait
                continue
            else:
                state = 1 - state
                break
        except socket.timeout:
            # timeout resend
            conn.sendto(packet, (host, port))
            retry_count += 1


def run(args):
    host = args.remotehost
    port = args.port
    filename = args.filename
    retry_timeout = args.retryTimeout
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    conn.settimeout(retry_timeout/1000)
    data = read_file(filename)
    file_size = len(data)/1024

    while len(data) > THREOLD:
        packet = make_packet(state, 0, data[:THREOLD])
        data = data[THREOLD:]
        handle(conn, packet, host, port)
    if len(data) > 0:
        packet = make_packet(state, EOF, data)
        handle(conn, packet, host, port)
    
    print('{} {}'.format(retry_count, round(file_size/(end_time-start_time), 2)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('remotehost', type=str)
    parser.add_argument('port', type=int)
    parser.add_argument('filename', type=str)
    parser.add_argument('retryTimeout', type=int)
    args = parser.parse_args()
    run(args)