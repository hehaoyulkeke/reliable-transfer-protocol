import argparse
import socket

THREOLD = 1024*2
EOF = 1
expected_seq = 1
N = 0
window = {}

def handle(conn, file, seq, data, addr):
    global expected_seq, N, window
    ok = False
    if expected_seq <= seq <= expected_seq+N-1:
        ackno = seq
        # in recv window
        if seq not in window:
            window[seq] = data
        if expected_seq == seq:
            # check cache
            while expected_seq in window:
                file.write(window[expected_seq])
                del window[expected_seq]
                expected_seq += 1
            ok = True
    elif expected_seq-N <= seq <= expected_seq-1:
        # already ack packet
        ackno = seq
    else:
        # ignore other packet
        return ok
    reponse = ackno.to_bytes(2, byteorder='little')
    conn.sendto(reponse, addr)
    return ok


def run(args):
    port = args.port
    filename = args.filename
    global N
    N = args.windowSize
    file = open(filename, 'wb')
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    conn.bind(('localhost', port))
    
    while True:
        packet, addr = conn.recvfrom(THREOLD)
        seq, eof, data = packet[:2], packet[2].to_bytes(1, byteorder='little'), packet[3:]
        seq = int.from_bytes(seq, byteorder='little')
        eof = int.from_bytes(eof, byteorder='little')
        ok = handle(conn, file, seq, data, addr)
        if eof == EOF and ok:
            break
    file.close()
    conn.close()
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    parser.add_argument('filename', type=str)
    parser.add_argument('windowSize', type=int)
    args = parser.parse_args()
    run(args)
