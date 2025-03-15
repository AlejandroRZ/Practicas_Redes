# servidor_ahorcado.py
import socket
import threading
import random

HOST = 'localhost'
PORT = 12001
WORDS = [
    "python", "socket", "programacion", "juego", "ahorcado", "internet", "computadora", "teclado", 
    "raton", "monitor", "pantalla", "algoritmo", "desarrollo", "frontend", "backend", "sintaxis", 
    "modulo", "libreria", "servidor", "cliente", "concurrencia", "asynchronous", "variable", "funcion", 
    "clase", "objeto", "instancia", "constructor", "herencia", "metodo", "atributo", "interfaz", 
    "archivo", "directorio", "ruta", "compilar", "interpretar", "declaracion", "constante", "booleano", 
    "entero", "flotante", "cadena", "caracter", "arreglo", "matriz", "pila", "cola", "lista", "diccionario", 
    "json", "xml", "html", "css", "javascript", "java", "csharp", "ruby", "golang", "matematica", "fisica", 
    "quimica", "biologia", "zoologia", "botanica", "genetica", "ecologia", "anatomia", "fisiologia", 
    "microscopio", "telescopio", "planeta", "estrella", "galaxia", "universo", "energia", "fuerza", 
    "masa", "velocidad", "aceleracion", "gravedad", "electricidad", "magnetismo", "circuito", "resistencia", 
    "ohmio", "voltaje", "corriente", "amperio", "dinamometro", "mecanica", "termodinamica", "estadistica", 
    "probabilidad", "algebra", "geometria", "calculo", "ecuacion", "vector", "tensor", "matriz", "fractal", 
    "logaritmo", "exponencial", "sen", "cos", "tan", "derivada", "integral", "topologia", "infinitesimal", 
    "teorema", "conjetura", "prueba"
]


class AhorcadoServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen(1)
        print(f"Servidor de Ahorcado escuchando en {HOST}:{PORT}")

    def handle_client(self, client_socket):
        palabra = random.choice(WORDS)
        progreso = ["_"] * len(palabra)
        intentos_restantes = 6
        letras_adivinadas = set()

        client_socket.send("Bienvenido al juego de Ahorcado!\n".encode())

        while intentos_restantes > 0 and "_" in progreso:
            client_socket.send(f"Palabra: {' '.join(progreso)}\n".encode())
            client_socket.send(f"Intentos restantes: {intentos_restantes}\n".encode())
            client_socket.send("Adivina una letra: ".encode())
            letra = client_socket.recv(1024).decode().strip().lower()

            if letra in letras_adivinadas:
                client_socket.send("Ya has adivinado esa letra.\n".encode())
            elif letra in palabra:
                for i, l in enumerate(palabra):
                    if l == letra:
                        progreso[i] = letra
                letras_adivinadas.add(letra)
                client_socket.send("¡Correcto!\n".encode())
            else:
                intentos_restantes -= 1
                letras_adivinadas.add(letra)
                client_socket.send("Incorrecto.\n".encode())

        if "_" not in progreso:
            client_socket.send(f"¡Ganaste! La palabra era {palabra}\n".encode())
        else:
            client_socket.send(f"Perdiste. La palabra era {palabra}\n".encode())

        client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexión establecida con {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

if __name__ == "__main__":
    server = AhorcadoServer()
    server.start()
