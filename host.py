from xmlrpc.server import SimpleXMLRPCServer
import matplotlib.pyplot as plt


#hiermee wordt in de log aan de serverkant het memory percentage geprint
def print_memory(mem):
    print(f"Memory used by client: {mem}")
    return True

#grafiek maken
plt.plot([1,2,3,4])
plt.ylabel('cpu_temperatuur')
plt.show()


#publiceer de server op poort 8000
server = SimpleXMLRPCServer(("localhost",8000))
server.register_function(print_memory, "print_memory")

#print het poortnummer
print("Server listening on port 8000")

#laat de server draaien tot deze stopt
server.serve_forever()


print(test)