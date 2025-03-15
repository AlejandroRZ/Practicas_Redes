# cliente_ahorcado.py
import socket

HOST = 'localhost'
PORT = 12001

class AhorcadoClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))

    def start(self):
        while True:
            mensaje = self.client_socket.recv(1024).decode()
            if "Adivina una letra" in mensaje:
                print(mensaje, end="")
                letra = input().strip()
                self.client_socket.send(letra.encode())
            else:
                print(mensaje)
                if "Ganaste" in mensaje or "Perdiste" in mensaje:
                    break

        self.client_socket.close()

if __name__ == "__main__":
    client = AhorcadoClient()
    client.start()
