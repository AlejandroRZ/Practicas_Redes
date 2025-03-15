import socket
import threading

# Configuración del cliente
client = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 5555
welcome_event = threading.Event()  # Evento para sincronizar la bienvenida

def connect():
    '''
    Conecta al cliente con el servidor. Valida que se le de un nombre de usuario. 
    '''
    global your_details
    name = input("Ingresa tu nombre de usuario: ")
    if len(name) < 1:
        print("Error! Agrega un nombre de usuario, intenta de nuevo")
    else:
        connect_to_server(name)


def connect_to_server(name):
    '''
    Establece una conexión con el servidor utilizando sockets
    '''
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        print("Te has conectado con éxito al servidor: " + str(name))
        client.sendall(name.encode())
        # Mantiene un hilo para recibir mensajes del servidor
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        print("Error: No se puede conectar al host : " + HOST_ADDR + " en el puerto: " + str(HOST_PORT))


def receive_message_from_server(sck,m):
    '''
    Recibe mensajes del servidor de forma continua en un hilo separado.
    arg:
        sck (socket): El socket del cliente conectado
    '''
    from_server = sck.recv(4096)
    if from_server.startswith("Bienvenid@".encode()):
        print("Mensaje del servidor: " + from_server.decode())
        welcome_event.set() 


def throw_rock():
    '''
    Envía el movimiento piedra al servidor y recibe el movimiento del oponente
    '''
    global client
    msg = "elige roca"
    client.send(msg.encode())
    # mensaje del servidor 
    opp_throw = client.recv(1024).decode()
   
    print(f"\nTu jugada: piedra")
    print(f"Jugada del oponente (servidor): {opp_throw}")

    if opp_throw == 'piedra':
        print("Meh EMPATE")
    elif opp_throw == 'tijeras':
        print("Ganaste! :D")
    elif opp_throw == 'papel':
        print("Buu perdiste :(")


def throw_paper():
    '''
    Envía el movimiento papel al servidor y recibe el movimiento del oponente
    '''
    global client
    msg = "elige papel"
    client.send(msg.encode())
    opp_throw = client.recv(1024).decode()
    
    print(f"\nTu jugada: papel")
    print(f"Jugada del oponente (servidor): {opp_throw}")

    if opp_throw == 'papel':
        print("Meh EMPATE")
    elif opp_throw == 'roca':
        print("Ganaste! :D")
    elif opp_throw == 'tijeras':
        print("Buu perdiste :(")


def throw_scissors():
    '''
    Envía el movimiento tijeras al servidor y recibe el movimiento del oponente
    '''
    global client
    msg = "elige tijeras"
    client.send(msg.encode())
    opp_throw = client.recv(1024).decode()
    
    print(f"\nTu jugada: tijeras")
    print(f"Jugada del oponente (servidor): {opp_throw}")

    if opp_throw == 'tijeras':
        print("Meh EMPATE")
    elif opp_throw == 'papel':
        print("Ganaste! :D")
    elif opp_throw == 'piedra':
        print("Buu perdiste :(")


def on_closing():
    '''
    Maneja el cierre de la conexión del cliente.
    '''
    try:
        client.send('desconectar'.encode())
    except (socket.error, ConnectionResetError, AttributeError):
        print("Error de conexión, puede que el servidor ya haya cerrado la conexión")
    finally:
        try:
            client.close()
        except AttributeError:
            pass


# Ejecuta la conexión y el juego
if __name__ == "__main__":
    
    # Nos conectamos al servidor con un nombre de usuario 
    connect()
    
    # Espera hasta que se reciba la bienvenida del servidor
    welcome_event.wait()
    
    while True:
        print("\nElige tu jugada:")
        print("1. Piedra")
        print("2. Papel")
        print("3. Tijeras")
        print("4. Salir")
        choice = input("Selecciona una opción (1-4): ")

        if choice == '1':
            throw_rock()
        elif choice == '2':
            throw_paper()
        elif choice == '3':
            throw_scissors()
        elif choice == '4':
            on_closing()
            break
        else:
            print("Opción no válida. Intenta de nuevo.")
