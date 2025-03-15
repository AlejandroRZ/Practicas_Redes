# cliente_loteria.py
import socket

HOST = 'localhost'
PORT = 12002

class LoteriaClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))

    def start(self):
        while True:
            mensaje = self.client_socket.recv(1024).decode()
            if "Carta:" in mensaje:
                print(mensaje)
                respuesta = input("¿Tienes esta carta en tu tablero? (si/no): ").strip().lower()
                self.client_socket.send(respuesta.encode())
            else:
                print(mensaje)
                if "Ganaste" in mensaje:
                    break

        self.client_socket.close()

if __name__ == "__main__":
    client = LoteriaClient()
    client.start()
