def header_parser(data):
    """
    Parses the header of a packet to extract sequence and acknowledgment numbers, and flag statuses.
    
    Arguments:
    data: The packet data as a byte sequence.

    Returns:
    dict: A dictionary containing the sequence number, acknowledgment number, and flags (SYN, ACK, FIN, RESET) total 6 byte.
    """
    seq_number = int.from_bytes(data[:2], 'big')
    ack_number = int.from_bytes(data[2:4], 'big')
    flags = int.from_bytes(data[4:6], 'big')
    syn = flags & 0b001
    ack = (flags & 0b010) >> 1
    fin = (flags & 0b100) >> 2
    reset = (flags & 0b1000) >> 3 
    return {'seq_number': seq_number, 'ack_number': ack_number, 'syn': syn, 'ack': ack, 'fin': fin, 'reset': reset}

def create_header(seq_number=0, ack_number=0, syn=False, ack=False, fin=False, reset=False):
    """
    Creates a header for a packet with the given sequence and acknowledgment numbers, and flag statuses.
    
    Arguments:
    seq_number: The sequence number (default is 0).
    ack_number: The acknowledgment number (default is 0).
    syn: SYN flag (default is False).
    ack: ACK flag (default is False).
    fin: FIN flag (default is False).
    reset: RESET flag NOT USED.

    Returns:
    bytes: The constructed header as a byte sequence total of 6 byte.
    """
    flags = (syn << 0) | (ack << 1) | (fin << 2) | (reset << 3)
    flags_bytes = flags.to_bytes(2, 'big')
    header = seq_number.to_bytes(2, 'big') + ack_number.to_bytes(2, 'big') + flags_bytes
    return header