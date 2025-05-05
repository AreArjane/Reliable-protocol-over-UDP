# Data Reliable Transfer Protocol with UDP

This application implements a custom protocol for transferring data using UDP sockets. The protocol ensures reliable data transfer by keeping track of acknowledgment numbers and sequence numbers, and it performs a handshake to establish connections between the client and server.

## Features

- Reliable data transfer over UDP
- Custom protocol with sequence and acknowledgment tracking
- Handshake mechanism for connection establishment
- Optional packet discard for testing purposes
- Configurable sliding window size for data transfer

## Prerequisites

- Python 3.x

## Usage

### Server
To run the server, use the following command:
```bash
python3 application.py -s -i <IP_ADDRESS> -p <PORT> -f <OUTPUT_FILENAME>
``` 

* -s, --server: Enable server mode.
* -i, --ip: IP address to bind the server.
* -p, --port: Port number to bind the server (default 8080).
* -f, --filename: The filename to save the data received from the client.
* -d, --discard (optional): Discard a packet with the given sequence number for testing purposes.

Example: 

```bash 
python3 application.py -s -i 127.0.0.1 -p 8088 -f received_file.jpg
```

### Client
To run the client, use the following command:

```bash
python3 application.py -c -i <IP_ADDRESS> -p <PORT> -f <FILENAME>
```

* -c, --client: Enable client mode.
* -i, --ip: IP address of the server.
* -p, --port: Port number of the server (default 8080).
* -f, --filename: The filename to be sent to the server.
* -w, --window (optional): Sliding window size for data transfer (default is 3).

## Explanation of Parameters
 - IP Address and Port: Both the client and server should use the same IP address and port to establish a connection.
 - Filename: Specifies the file to be sent (client) or received (server).
 -  Discard Option: Used in server mode to discard a packet with a specific sequence number for testing retransmission logic.
- Sliding Window Size: Specifies the number of packets that can be sent before waiting for acknowledgments. This is only used in client mode and defaults to 3.

## How it Works

1. Server Initialization: The server starts and listens for incoming connections on the specified IP address and port.
2. Client Initialization: The client starts and connects to the server using the specified IP address and port.
3. Handshake: The client and server perform a handshake to establish a connection.
4. Data Transfer: The client sends the file to the server in chunks, using a sliding window protocol. The server acknowledges each received packet.
5. Packet Discard (Optional): The server can be configured to discard a specific packet for testing purposes.
6. Connection Termination: Once all data is transferred, the client and server perform a connection termination handshake.

## Example

To test the application, with the package discard:

### Run the Server:

```bash 
python3 application.py -s -i 127.0.0.1 -p 8088 -f received_file.txt -d 5
```


To test the application, with the windows-sliding

### Run the client:

```bash 
python3 application.py -c -i 127.0.0.1 -p 8088 -f received_file.txt -w 5
```

## Conclusion

This application demonstrates reliable data transfer over UDP using a custom protocol with sequence and acknowledgment tracking. It includes features for establishing connections, transferring data with a sliding window, and testing packet loss handling.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with tests and documentation.

---

## License

MIT License © 2025
