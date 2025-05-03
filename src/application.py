from socket import *
from command_line import CommandPraser
import time
from datetime import datetime
import os
from header import header_parser, create_header

class DRTProtocol:
    
   @staticmethod
   def server_invoke(ip, port, output_filename, discard_sq):
        """
        Starts the server to receive data packets and handle connections.
        
        Arguments:
        ip: IP address of the server.
        port: Port number of the server.
        output_filename: The file to save the received data.
        discard_sq: Sequence number of the packet to discard for once.

        Returns:
        ACK to the client with the DRTP and the file received from the client
        """
        server_socket = socket(AF_INET, SOCK_DGRAM)
        server_socket.bind((ip, port))
        print("Server is listening on {}:{}".format(ip, port))
        discarded_package = set()
        ack_pack = set()
        expected_seq = 1

        while True:
            data, addr = server_socket.recvfrom(1000)
            header = header_parser(data)
           
            if header['syn']:
                print("SYN packet is received")
                syn_ack = create_header(syn=True, ack=True)
                server_socket.sendto(syn_ack, addr)
                print("SYN-ACK packet is sent")
                continue
            if header['ack'] and not header['syn'] and header['ack_number'] == 0:
                print("ACK packet is received")
                print("Connection established")
                print(header['seq_number'])
                print(header['ack_number'])
                print(header['ack'])
                break
            if header['ack'] and not header['syn'] and header['ack_number'] == 1:
                print("ACK packet is received")
                print("Connection established")
                print(header['seq_number'])
                print(header['ack_number'])
                print(header['ack'])
                server_socket.close()
                break

        try:
            start_time = time.time()
            total_data = 0
            
            with open(output_filename, 'wb') as output_file:
                while True:
                    data, addr = server_socket.recvfrom(1000)
                    header = header_parser(data)

                    if discard_sq is not None and header['seq_number'] == discard_sq and discard_sq not in discarded_package:
                        print("Packet with seq_number {} is discarded".format(header['seq_number']))
                        ack = create_header(ack=True, ack_number=expected_seq - 1)
                        server_socket.sendto(ack, addr)
                        discarded_package.add(discard_sq)
                        continue

                    if len(data) == 0:
                        print("No data received. Closing connection.")
                        break

                    if header['fin']:
                        print('FIN packet is received')
                        fin_ack = create_header(ack=True, fin=True)
                        server_socket.sendto(fin_ack, addr)
                        print("FIN ACK packet is sent")
                        break

                    if header['seq_number'] == 0:
                        print("Received packet with invalid data length, closing connection.")
                        break

                    if header['seq_number'] == expected_seq or header['seq_number'] in discarded_package:
                        print("{} -- packet {} is received".format(datetime.now().strftime("%H:%M:%S.%f"), header['seq_number']))
                        ack = create_header(ack=True, ack_number=header['seq_number'])
                        server_socket.sendto(ack, addr)
                        print("{} -- sending ack for the received {}".format(datetime.now().strftime("%H:%M:%S.%f"), header['seq_number']))
                        ack_pack.add(header['seq_number'])
                        output_file.write(data[6:])
                        expected_seq += 1
                    else:
                        print("{} -- out of order packet {} is received".format(datetime.now().strftime("%H:%M:%S.%f"), header['seq_number']))
                        

                    total_data += len(data) - 6

            end_time = time.time()
            duration = end_time - start_time
            throughput = (total_data / duration) * 8 / (1000 * 1000)
            print("The throughput is {:.2f} Mbps".format(throughput))

        except Exception as e:
            print(f"An error occurred: {e}")
            server_socket.close()
            
        finally:
            print("Connection closed")
            server_socket.close()
    

   @staticmethod
   def client_send(ip, port, filename, window_size):
        """
        Starts the client to send data packets to the server.
        
        Arguments:
        ip: IP address of the server.
        port: Port number of the server.
        filename: The file to send to the server.
        window_size: Size of the sliding window.

        Send:
        send file in form of chunk 994 data  + 6 header byte to the server with DRTP.
        
        """
        client_sd = socket(AF_INET, SOCK_DGRAM)
        client_sd.settimeout(0.5)
        file_size = os.path.getsize(filename)

        try:
            print(os.path.getsize(filename))
            print(os.path.exists(filename))
            syn_packet = create_header(syn=True)
            client_sd.sendto(syn_packet, (ip, port))
            print("\nConnection Establisht Phase:\n")
            print("SYN packet is sent")
            data, _ = client_sd.recvfrom(1000)
            header = header_parser(data)

            if header['syn'] and header['ack'] and file_size != 0:
                print("SYN-ACK packet is received")
                ack_packet = create_header(ack=True)
                client_sd.sendto(ack_packet, (ip, port))
                print("ACK packet is sent")
                print("\nConnection established\n")
                
            elif header['syn'] and header['ack'] and file_size == 0:
                print("SYN-ACK packet is received")
                ack_packet = create_header(ack_number=1,ack=True)
                client_sd.sendto(ack_packet, (ip, port))
                print("ACK packet is sent")
                print("\nConnection esablished with zero file\n")
                return

            # Define variables
            chunks = 994
            seqences = num_loop(file_size, chunks)
            sequence_number = 1
            base = 1
            next_seq_num = 1
            buffer = {}
            file_end = False
            sliding = set()
            sliding_number = 0
            ack_pack = set()
            expected_seq = 1

            if file_size != 0:
                with open(filename, 'rb') as file:
                    while True:
                        while next_seq_num < base + window_size and not file_end:
                            chunk = file.read(chunks)
                            
                            if not chunk:
                                file_end = True
                                break

                            if sliding_number < window_size:
                                sliding_number +=1
                                sliding.add(sliding_number)

                            elif next_seq_num > window_size:
                                sliding.pop()
                                sliding.add(next_seq_num)

                            data_packet = create_header(seq_number=next_seq_num) + chunk
                            client_sd.sendto(data_packet, (ip, port))
                            print("{} -- packet with seq = {} is sent, sliding window = {}".format(datetime.now().strftime("%H:%M:%S.%f"), next_seq_num, sliding))
                            next_seq_num += 1
                            
                        
                        try:
                            

                            ack_data, _ = client_sd.recvfrom(1000)
                            ack_header = header_parser(ack_data)
                            ack_number = ack_header['ack_number']
                            
                
                            ack_pack.add(base)
                                            
                    
                            if  ack_number not in ack_pack and ack_number > next_seq_num - window_size or ack_number == 0 or ack_number != expected_seq:
                                    print("{} -- RTO occured".format(datetime.now().strftime("%H:%M:%S.%f")))
                                    retransmitted = next_seq_num - window_size
                                    for _ in range(retransmitted , next_seq_num):
                                        data_packet = create_header(seq_number=retransmitted) + chunk
                                        client_sd.sendto(data_packet, (ip, port))
                                        print("{} -- Retransmitted packet with seq = {} is sent".format(datetime.now().strftime("%H:%M:%S.%f"), retransmitted))
                                        retransmitted = retransmitted + 1
                            
                            if ack_number != 0 and ack_number == expected_seq:
                                print("{} -- ACK for packet = {} is received".format(datetime.now().strftime("%H:%M:%S.%f"), ack_header['ack_number']))
                                base += 1
                                expected_seq += 1
               
                        except timeout:
                             print("Timeout occurred, resending packets")
    
                        if file_end and base == next_seq_num:
                            print("\nDATA Finished\n\n")
                            break

            if os.path.getsize(filename) != 0:
                fin_packet = create_header(fin=True)
                client_sd.sendto(fin_packet, (ip, port))
                print("\n\nConnection Teardown:\n\nFIN packet is sent")

                data, _ = client_sd.recvfrom(1000)
                header = header_parser(data)
                if header['fin'] and header['ack']:
                   print("FIN-ACK packet is received")
                   client_sd.close()
                   print("Connection closes")
                else:
                   print("Failed to close connection")
            else:
                return

        except Exception as e:
            print(f"Connection failed:{e}")
            client_sd.close()
   


#function conver the data size of the file if it 9555 kb it will be equals to 10 seq
#use for depugging
def num_loop(filesize, chunksize):
    loop_cal = filesize // chunksize
    if loop_cal % chunksize != 0:
        loop_cal += 1
    return loop_cal



if __name__ == "__main__":
    
    result = CommandPraser.ParserArgument()
    mode = result.get('mode')
    ip = result.get('ip')
    port = result.get('port')
    window_size = result.get('window_size')
    filename = result.get('file')
    discard = result.get('discard')
    protocol = DRTProtocol()

    if mode.name.lower() == "server":
        protocol.server_invoke(ip, port, filename, discard)
    elif mode.name.lower() == "client":
        protocol.client_send(ip, port, filename, window_size)
