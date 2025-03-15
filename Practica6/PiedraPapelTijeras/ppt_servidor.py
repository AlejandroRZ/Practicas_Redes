import socket
import threading
import random

# Configuración del servidor
server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 5555
clients = []
clients_names = []
server_choices = ['piedra', 'papel', 'tijeras']

def start_server():
    '''
    Inicia el servidor y permite que se acepten nuevas conexiones
    '''
    global server, HOST_ADDR, HOST_PORT

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(10) 
    
    print("\nIniciando servidor ..."  + "\n"
            "HOST: " + str(HOST_ADDR) + "\n"
            "PORT: " + str(HOST_PORT) + "\n"
            "Esperando por clientes ...  \n")
    
    threading.Thread(target=accept_clients, args=(server,)).start()

def accept_clients(the_server):
    '''
    Acepta nuevos clientes. Con cada cliente nuevo se inicia un hilo para gestionar la comunicación.
    '''
    while True:
        client, addr = the_server.accept()
        clients.append(client)
        threading.Thread(target=send_receive_client_message, args=(client, addr)).start()

def send_receive_client_message(client_connection, client_ip_addr):
    '''
    Metodo que nos ayuda a mandar y recibir mensajes con el cliente
    '''
    global clients, clients_names, server_choices
    client_name = client_connection.recv(4096).decode()
    
    # Guardar y mostrar el nombre del cliente que se conecta
    clients_names.append(client_name)  
    print(f"Se ha conectado un cliente al servidor: {client_name}")

    client_connection.send(f"Bienvenid@ {client_name}! Vamos a jugar piedra, papel o tijeras!".encode())

    while True:
        data = client_connection.recv(4096).decode()
        if data.startswith("elige"):  # El cliente envía su elección del juego
            client_throw = data[6:]
            server_throw = random.choice(server_choices)
            client_connection.send(server_throw.encode())
        elif data.startswith("desconectar"):  # El cliente se desconecta
            handle_disconnect(client_connection)
            break

    idx = get_client_index(clients, client_connection)
    # Mostrar en la terminal que el cliente se ha desconectado
    print(f"Cliente desconectado: {clients_names[idx]}")
    del clients_names[idx]
    del clients[idx]

def handle_disconnect(client_connection):
    '''
    Cierra la conexión con el cliente que se ha desconectado
    '''
    client_connection.close()

def get_client_index(client_list, curr_client):
    '''
    Obtiene el índice del cliente actual en la lista de clientes.
    '''
    for idx, conn in enumerate(client_list):
        if conn == curr_client:
            return idx
    return -1

# Inicia el servidor
if __name__ == "__main__":
    start_server()
