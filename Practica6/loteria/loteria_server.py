# servidor_loteria.py
import socket
import threading
import random
import time

HOST = 'localhost'
PORT = 12002
CARTAS = ["el gallo", "el diablito", "la dama", "el catrín", "el paraguas", "la sirena",
          "la escalera", "la botella", "el barril", "el árbol", "el melón", "el valiente",
          "el gorrito", "la muerte", "la pera", "la bandera", "el bandolón", "el violoncello",
          "la garza", "el pájaro", "la mano", "la bota", "la luna", "el cotorro"]

class LoteriaServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(1)
        print(f"Servidor de Lotería escuchando en {HOST}:{PORT}")

    def handle_client(self, client_socket):
        tablero_cliente = random.sample(CARTAS, 9)  # Tablero de cliente de 3x3
        cartas_cantadas = set()

        client_socket.send(f"Tu tablero: {', '.join(tablero_cliente)}\n".encode())
        client_socket.send("Empieza el juego de Lotería!\n".encode())

        while True:
            carta = random.choice(CARTAS)
            if carta in cartas_cantadas:
                continue
            cartas_cantadas.add(carta)
            client_socket.send(f"Tu tablero: {', '.join(tablero_cliente)}\n".encode())
            client_socket.send(f"Carta: {carta}\n".encode())
            respuesta = client_socket.recv(1024).decode().strip().lower()

            if respuesta == "si" and carta in tablero_cliente:
                tablero_cliente.remove(carta)
                if len(tablero_cliente) == 0:
                    client_socket.send("¡Ganaste! Has completado tu tablero.\n".encode())
                    break
            elif respuesta != "si" and carta in tablero_cliente:
                client_socket.send("Error: tienes esa carta en tu tablero.\n".encode())
            elif respuesta == "si" and carta not in tablero_cliente:
                client_socket.send("Error: no tienes esa carta en tu tablero.\n".encode())
            time.sleep(1)

        client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexión establecida con {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

if __name__ == "__main__":
    server = LoteriaServer()
    server.start()
