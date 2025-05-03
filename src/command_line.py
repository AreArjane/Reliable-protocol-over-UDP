
import argparse
import ipaddress
from enum import Enum

class Parser(Enum):
    SERVER = "server"
    CLIENT = "client"
    ERROR = "error"
    UNDEFINED = "undefined"


class CommandPraser:

    
    @staticmethod
    def check_port(val):
        """
        Checks if the provided port is within the valid range [1024, 65535].
        Arguments:
        val: The port number as a string.

        Returns:
        int: The port number if valid.

        Raises:
        argparse.ArgumentTypeError: If the port is not an integer or not within the valid range.
        """
        try:
            value = int(val)
        except ValueError:
            raise argparse.ArgumentTypeError('An integer are required for port number')
        if value not in range(1024, 65535 + 1):
            raise argparse.ArgumentTypeError("Invalid port. It must be within the range [1024,65535]")
        return value
    @staticmethod
    def check_ip(address):
        """
        Validates if the provided address is a valid IP address.
        Arguments:
        address: The IP address as a string.

        Returns:
        ipaddress: The validated IP address.

        Raises:
        argparse.ArgumentTypeError: If the IP address is not valid.
        """
        try:
            val = ipaddress.ip_address(address)
            ip = str(val)
            if val:
                return val
            else:
                raise ValueError
        except ValueError:
            raise argparse.ArgumentTypeError("It must be in the dotted decimal notation format, e.g. 10.0.1.2")
        
    @staticmethod
    def ParserArgument(*args, **kwargs):
        """
        Parses command-line arguments to configure the server or client mode.
        Arguments:
        *args, **kwargs: Variable length argument list and keyword arguments.

        Returns:
        dict: Parsed arguments and their values.

        Raises:
        argparse.ArgumentTypeError: If invalid arguments are provided or required arguments are missing.
        """
        parser = argparse.ArgumentParser(
            prog="Reliable Transport Protocol (DRTP)",
            description="Transfer file from client to server with custom UDP protocol",
            formatter_class=argparse.RawTextHelpFormatter,
            epilog="**************************************************************************************************************\n"
            +"\nclient or server mode following options: -i, -p, -f are required\n"
            +"\nIn progressing server or client IP and PORT required to be identical\n" 
            +"\nDiscard package for once -d avaliable within server mode, -w scaling-windows avaliable within client mode\n\n"
            +"**************************************************************************************************************"
    )   
        
        parser.add_argument("-s", "--server", help="enable server mode",action="store_true")
        parser.add_argument("-c", "--client",help="enable client mode", action="store_true")
        parser.add_argument("-i", "--ip", help="IP address to connected", type=CommandPraser.check_ip,default="10.0.1.2", required=True)
        parser.add_argument("-p", "--port", help="Port Number for connection client and server should be on same port",default=8088,type=CommandPraser.check_port, required=False)
        parser.add_argument("-f", "--filename", help="filename save with server and transfered from client",required=True, type=str)
        parser.add_argument("-w", "--window",help="sliding windows size in client mode default 3, choose 4 or 5", type=int, default=3)
        parser.add_argument("-d", "--discard",help="custom test case, -d 11 for discarding a package with the seq number 11 in server for once", type=int)

        try:
            args = parser.parse_args(*args)
        
            result = {
                'mode' : Parser.UNDEFINED,
                'ip' : str(args.ip),
                'port': args.port,
                'file': args.filename,
                'window_size' : args.window,
                'discard' : getattr(args, 'discard', None)
            }


            if args.server:
                result['mode'] = Parser.SERVER    
            elif args.client:
                result['mode'] = Parser.CLIENT
                if args.discard: 
                    raise argparse.ArgumentTypeError("Discard package only in server mode")
            else:
                raise argparse.ArgumentTypeError("Either server mode (-s) or client mode (-c) must be specified")
            
        
            return result
        
        except Exception as e:
            print(e)
            return {'mode' : Parser.ERROR, 'error': str(e)}
        
            
if __name__ == "__main__":
    import sys
    result = CommandPraser.ParserArgument(sys.argv[1:])
    print(result)
        

