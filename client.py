import xmlrpc.client
import psutil
import time

while True:
    #verbind met de sevrer
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000")
    #haal het percentage van gerbuikte geheugen op
    mem = psutil.virtual_memory()
    #stuur memory percentage naar de server
    proxy.print_memory(mem.percent)

    #wacht 1 seconde en stuur opnieuw
    time.sleep(1)


    test wessel