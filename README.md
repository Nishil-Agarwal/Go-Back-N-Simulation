# Go-Back-N-Simulation
In this implementation, we have created a simplified version of the Go-Back-N protocol using Python's socket library, enabling communication between two entities over a UDP network. The code simulates the operation of a sender and a receiver, ensuring reliable data transmission with features like packet dropping, timeouts, and acknowledgements, commonly used in real-world networking protocols. Let's break down the components and how they contribute to the functioning of Go-Back-N.
Overview of Go-Back-N Protocol

Go-Back-N is an automatic repeat request (ARQ) protocol that provides reliable data transmission over unreliable networks. In this protocol, the sender can send multiple frames (packets) without waiting for an acknowledgement (ACK) for each one, but the receiver must process frames in order. If the sender does not receive an acknowledgement within a specified timeout, it retransmits all frames starting from the last unacknowledged frame.
Our code simulates this process with a sliding window for the sender, packet generation and transmission, and acknowledgement handling on both sides.
Key Components of the Code

1.	Server and Client Sockets: The code sets up two entities (labelled as "Entity1" and "Entity2" for simplicity) that communicate over UDP using the socket module. The server (Entity1) binds a socket to a port and listens for incoming frames. The client sends the frames to the server. Both entities communicate using localhost.
2.	Sliding Window: The sliding window mechanism is implemented using the variables base and next_seq_number. The base keeps track of the sequence number of the earliest unacknowledged packet, while next_seq_number determines the sequence number of the next packet to be sent. The sender can transmit a number of frames (up to window_size) before receiving any acknowledgment, and once a packet is acknowledged, the window slides forward to allow new packets to be sent.
3.	Packet Generation: The gen_packet() function generates packets at random intervals and appends them to the outgoing queue. This simulates the real-world scenario where data packets are generated continuously at random times.
4.	Packet Transmission: The transmit() function manages the sending of packets. It checks if there is space in the window for new packets and sends them using the send_packet() function. Each packet is encapsulated with its sequence number and sent to the client. After sending a packet, the next_seq_number is incremented, and the sender waits for the next available slot in the window.
5.	Handling Acknowledgments: The handle_ack() function listens for incoming ACKs and processes them. When an acknowledgment for a particular packet is received, the sliding window is adjusted. If an ACK matches the base, it slides the window forward, allowing the sender to send new packets. If a timeout occurs (i.e., no ACK is received within a specified duration), the sender retransmits all packets in the current window.
6.	Receiving Packets: The receive() function is responsible for receiving packets from the sender. It checks if the sequence number of the received packet matches the expected sequence number. If it does, the packet is processed, and an ACK is sent back to the sender. If the packet is out of order (i.e., its sequence number does not match the expected one), it is discarded. This ensures that the receiver only accepts packets in the correct order.
7.	Ack Loss Simulation: A small probability of packet loss is introduced using the packet_drop_prob variable. If a randomly generated number exceeds this probability, the ack is dropped, simulating network unreliability. This feature is essential for testing the robustness of the protocol, as the sender must be able to handle lost packets by retransmitting them.

Protocol Workflow

The GBN protocol follows a loop where:

●	The sender generates and sends packets as long as there is space in the sliding window.

●	The receiver processes incoming packets and sends acknowledgements back to the sender.

●	If an acknowledgement is received, the sender slides the window and sends the next packet in the sequence.

●	If a packet is not acknowledged within the timeout, the sender retransmits all packets in the window.

The sender does not wait for individual acknowledgements instead it waits for the sliding window to adjust based on ACKs. If packets arrive out of order or are lost, the sender will eventually retransmit them, ensuring reliability.

Threading and Concurrency

The implementation uses Python’s threading module to simulate concurrent operations. Each entity runs in its thread, enabling multiple actions to occur simultaneously. The main threads in the code handle packet generation, transmission, acknowledgement reception, and packet receiving independently, which mirrors the concurrent nature of real-world communication protocols.

Measurements of average delay time and number of times frame sent:

We measured the total frames sent using a variable and got average frames sent by dividing total frames sent by the total amount of packets.
We measured times at which packets were sent and acks received in a dictionary using time.time(). Later we used these values to calculate avg delay.
