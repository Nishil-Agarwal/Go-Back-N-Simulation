import select
import socket 
import threading
import time
import random

# Sequence numbers and windows
packets=30
base = 0
next_seq_number = 0
window = []
outgoing_queue = []
ack_received = {}
expected_seq_number = 0

lock= threading.Lock()
sent_timestamp={}

# Server parameters 
server_IP = 'localhost'
peer_IP = 'localhost'
data_port = 12003  # this is this entity itself
ack_port = 12004  #stated in assignment) and copy pasted it in enity1 :)

peer_data_port=12000
peer_ack_port=12001

window_size = 7
N = 8
packet_drop_prob = 0.1
T1, T2, T3, T4 = 0.1,0.3,0.1, 0.4

Timeout = 1

# Sockets
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data_socket= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
ack_socket= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
data_socket.bind((server_IP, data_port))
ack_socket.bind((server_IP,ack_port))

total_frames=0
times={}
for i in range(packets):
    times[i]={"start":None,"end":None}

def gen_packet():
    """Generate packets at random intervals."""
    
    while True:
        packet = f"packet"
        outgoing_queue.append(packet)
        time.sleep(random.uniform(T1, T2))

def send_packet(packet, seq_num):
    """Encapsulate and send a packet as a frame."""
    global total_frames
    if seq_num<packets:

        total_frames+=1
        times[seq_num]["start"]=time.time()

    sent_timestamp[seq_num]=time.time()
    
    frame = f"{seq_num}: {packet}".encode()
    data_socket.sendto(frame,(peer_IP, peer_data_port))
    # print(f"E1: Sent: {seq_num}: {packet}")


def handle_ack():
    """Listen for ACKs and adjust the sliding window."""
    global base, ack_received, next_seq_number

    while base<(packets):
        # print(f"Waiting for ACK for base: {base}")

        # Use select to check for ACK with a timeout to avoid indefinite blocking
        ready = select.select([ack_socket], [], [], Timeout)  # Timeout in seconds
        
        if ready[0]:  # If there's data to read
            ack, addr = ack_socket.recvfrom(1024)
            ack_num = int(ack.decode().split(':')[1])
            # print(f"Received ACK: {ack_num}")

            # Check if the received ACK matches the base
            if ack_num == base:
                if base<packets:
                    times[base]["end"]=time.time()
                if time.time() - sent_timestamp[ack_num] < Timeout:
                    # print(f"E1 : ACK {ack_num} received before timeout")
                    ack_received[base] = True
                    with lock:
                        base += 1
            else:
                pass
                # print(f"ACK {ack_num} received but does not match base {base}")

        # If no data is ready within the timeout, check for frame timeout
        elif base in sent_timestamp and (time.time() - sent_timestamp[base] >= Timeout):
            with lock:
                next_seq_number = base  # Reset next_seq_number to base for retransmission
            print(f"Timeout occurred; resetting next_seq_number to base {base}")
    # print("Out of handle")


        

def transmit():
    """Manage the Go-Back-N sliding window and send frames."""
    global next_seq_number,base
    while base<(packets):
        if len(outgoing_queue) > 0 and next_seq_number - base  < window_size:
            # print(next_seq_number)
            packet = outgoing_queue.pop(0)
            
            window.append((next_seq_number, packet))
            send_packet(packet, next_seq_number)
            with lock:
                next_seq_number = next_seq_number + 1
            time.sleep(random.uniform(T3, T4))  # Queuing delay
    # print("Out of transmit")

def send_ack(ack_num):
    """Send an ACK for the given sequence number."""
    ack = f"ACK:{ack_num}".encode()
    ack_socket.sendto(ack, (peer_IP, peer_ack_port))
    # print(f"E1 : Sent: {ack.decode()}")
    ack_received[ack_num] = True  # Mark the ACK as sent


def receive():
    """Receive and process frames from the client."""
    global expected_seq_number,base
    while True:
        try:
            frame, _ = data_socket.recvfrom(1024)
            data = frame.decode().split(':')
            seq_num = int(data[0])
            packet = data[1]

            # print(f"E1 : Received: {packet} (seq: {seq_num})")

            if seq_num == expected_seq_number:
                # Process frame if it is the expected sequence number
                if random.random() > packet_drop_prob:
                    # Increment the expected sequence number only if packet is not dropped
                    expected_seq_number += 1
                    send_ack(seq_num)
                else:
                    print(f"E2 : Dropped frame {seq_num} (simulated packet loss)")

            # Handle retransmission of frames we've already acknowledged
            elif seq_num < expected_seq_number:
                # Resend ACK for already received frames
                send_ack(seq_num)
        except ConnectionResetError:
            pass
    print("Out of recieve")



gen_thread=threading.Thread(target=gen_packet)
handle_ack_thread=threading.Thread(target=handle_ack)
transmit_thread=threading.Thread(target=transmit)
receive_thread=threading.Thread(target=receive)

gen_thread.start()
handle_ack_thread.start()
transmit_thread.start()
receive_thread.start()

handle_ack_thread.join()
transmit_thread.join()

times[packets-1]["end"]=time.time()
print(f"Average number of times frames sent : {total_frames/packets}")

total_delay=0
# print(times)
for i in times:
    total_delay+=times[i]["end"]-times[i]["start"]

print(f"Average delay : {total_delay/packets}")