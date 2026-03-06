from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread


def print_memory(mem):
    #Prints memory usage sent by client
    print(f"Memory used by client: {mem}%")
    #schrijf de memory naar het log bestand
    try:
        # Read the last line to get the last X value
        with open("example.txt", "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                last_x = int(last_line.split(",")[0])
            else:
                last_x = 0
    except FileNotFoundError:
        last_x = 0  # File does not exist yet
    
    new_x = last_x + 1

    # Append the new value to the file
    with open("example.txt", "a") as f:
        f.write(f"{new_x},{mem}\n")
    return True

LOGFILE = "failed_logins.log"

def receive_failed_logins(hostname, count, timestamp):
    logline = f"{count}"

    #schrijf de memory naar het log bestand
    try:
        # Read the last line to get the last X value
        with open("failed_logins.log", "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                last_x = int(last_line.split(",")[0])
            else:
                last_x = 0
    except FileNotFoundError:
        last_x = 0  # File does not exist yet
    
    new_x = last_x + 1

    with open(LOGFILE, "a") as f:
        f.write(f"{new_x},{logline}\n")

    return True

def start_server(host="localhost", port=8000):
    #Start the XML-RPC server
    server = SimpleXMLRPCServer((host, port))
    server.register_function(print_memory, "print_memory")
    server.register_function(receive_failed_logins, "receive_failed_logins")
    print(f"Server listening on port {port}")
    # Run server forever in a separate thread so plotting can run
    t = Thread(target=server.serve_forever, daemon=True)
    t.start()