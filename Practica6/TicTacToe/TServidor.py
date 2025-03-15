import socket
import threading
import sys
import signal
import time
import queue
import random

HOST = 'localhost'
PORT = 12001

class socketReceiver(threading.Thread):
    
    def __init__(self, socket):
        """
        Inicializa el hilo socketReceiver.
        Args:
            socket (socket.socket): El socket en el que el servidor escuchará los mensajes entrantes.
        """
        super().__init__()
        self.socket=socket
        self.threads={}
        self.lock=threading.Lock()
        self.stopper = threading.Event()
    
    def run(self):
        """
        Ejecuta el hilo, escuchando mensajes entrantes en el socket.
        
        - Si un mensaje es una solicitud de nuevo juego ("0 X" o "0 O"), se genera un hilo ClientReplier.
        - Si el mensaje pertenece a un juego existente, se pasa al ClientReplier correspondiente.
        - Ignora mensajes si el servidor no ha abierto un juego con el cliente.
        - Cierra el socket al finalizar la ejecución.
        """
        print('El servidor esta listo para recibir mensajes')
        while not self.stopper.is_set():
            try:
                message, clientAddress = self.socket.recvfrom(2048)
            except socket.timeout:
                continue
            except ConnectionError as e:
                continue
            except:
                self.stop()
            
            message = message.decode()

            # solo crea un hilo de trabajo si el cliente solicita un nuevo juego
            if message in ("0 X","0 O"):
                if clientAddress not in self.threads:
                    thread = ClientReplier(self.socket,clientAddress,message)        
                    self.threads[clientAddress] = thread
                    thread.start()
                
                elif not self.threads[clientAddress].is_alive():
                    self.threads[clientAddress].join()
                    thread = ClientReplier(self.socket,clientAddress,message)
                    self.threads[clientAddress]=thread
                    thread.start()
                else:
                    self.threads[clientAddress].put(message)
                continue

            # si el servidor no ha abierto ya un juego con el cliente, ignora al cliente
            try:
                thread = self.threads[clientAddress]
            except KeyError:
                ##Si el cliente no inicio un juego, continua
                continue
            else:
                if thread.is_alive():
                    thread.put(message)

        for k in self.threads:
            self.threads[k].stop()
        print("Cerrando socket ...")
        self.socket.close()

    def stop(self):
        '''Detiene la ejecución del hilo'''
        self.stopper.set()
    
    def removeDeadThreads(self):
        """
        Elimina los hilos muertos del diccionario de hilos.
        """
        dead_thread_keys = [k for k in self.threads if not self.threads[k].is_alive()]
        with self.lock:
            for k in dead_thread_keys:
                t = self.threads.pop(k)
                t.join()

class ClientReplier(threading.Thread):
    '''
    Representa un hilo que recibe mensajes para un cliente en particular
    '''
    def __init__(self, socket, clientAddress,first_request):
        """
        Inicializa el hilo ClientReplier.
        
        Args:
            socket (socket.socket): El socket en el que se enviarán los mensajes al cliente.
            clientAddress (tuple): Dirección del cliente (IP, puerto).
            first_request (str): Solicitud inicial del cliente.
        """
        super().__init__()
        self.socket=socket
        self.clientAddress=clientAddress
        self.queue=queue.Queue()
        self.stopper=threading.Event()
        self.first_request=first_request
    
    def put(self,message):
        '''Coloca un mensaje en cola'''
        self.queue.put(message)
    
    def send(self, message):
        '''Envia un mensaje al cliente'''
        self.socket.sendto(message.encode(), self.clientAddress)


    def run(self):
        '''Ejecuta el hilo manejando la lógica del juego para el cliente'''
        print(str(self.clientAddress)+" ha iniciado el juego.")
        MAX_NUMBER_OF_PING = 5
        numPings=0
        IN_PROGRESS, CLIENT_WIN, SERVER_WIN, TIE = '0','1','2','3'
        id, clientSymbol = self.first_request.split(" ")
        id = int(id)
        move = 0 if clientSymbol == "X" else random.choice((1,2,3,4,5,6,7,8,9))
        status = IN_PROGRESS
        last_reply = str(id)+" "+str(move)+" "+status
        # el estado del juego
        cMoves = set()
        sMoves = {move}
 
        self.send(last_reply)
        while not self.stopper.is_set():
            try:
                message = self.queue.get(timeout=1)
            except queue.Empty:
                # tiempo de espera
                if numPings <= MAX_NUMBER_OF_PING:
                    self.send("ping")
                    numPings += 1
                else:
                    print(str(self.clientAddress))
                    self.stop()
                continue
            numPings = 0

            try:
                message_id = int(message.split(" ")[0])
            except ValueError:
                continue
            else:
                if message_id-id == 0:
                    # solicitud replicada
                    self.send(last_reply)
                    continue
                elif message_id-id != 1:
                    continue
            
            if message.split(" ")[1] == "close":
                self.stop()
                break
            id = message_id
            try:
                clientMove = int(message.split(" ")[1])
            except (ValueError, IndexError):
                # formato incorrecto
                continue
            cMoves|={clientMove}
            winning_sets=[
                {1,2,3}, {4,5,6}, {7,8,9}, {1,4,7},
                {2,5,8}, {3,6,9}, {3,5,7}, {1,5,9} ]
            cWins=any(elem.issubset(cMoves) for elem in winning_sets)
            availableMoves ={1,2,3,4,5,6,7,8,9}-cMoves-sMoves
            # el cliente ha ganado o no quedan más movimientos disponibles
            if cWins or len(availableMoves) == 0:
                move=0
                status = CLIENT_WIN if cWins else TIE
                last_reply = str(id)+" "+str(move)+" "+status
                self.send(last_reply)
            else:
                # el servidor realiza un movimiento
                move = random.sample(list(availableMoves), 1)[0]
                availableMoves-={move}
                sMoves|={move}
                sWins=any(elem.issubset(sMoves) for elem in winning_sets)
            status = CLIENT_WIN if cWins else SERVER_WIN if sWins else TIE if len(availableMoves)==0 else IN_PROGRESS
            
            last_reply = str(id)+" "+str(move)+" "+status
            self.send(last_reply)   
            # while loop ends
        print(str(self.clientAddress)+" sale del juego.")

    def stop(self):
        self.stopper.set()


if __name__ == "__main__":
    serverPort = PORT
    serverHost = HOST
    serverSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('',serverPort))
    serverSocket.settimeout(1)

    thread_receiver = socketReceiver(serverSocket)
    thread_receiver.start()

    def cleanup():
        thread_receiver.stop()
        thread_receiver.join()
    
    def signal_handler(sig, frame):
        print("Se ha producido una interrupcion")
        cleanup()
        
    signal.signal(signal.SIGINT,signal_handler)
    
    while thread_receiver.is_alive():
        thread_receiver.removeDeadThreads()
        sys.stdout.write("#Juegos activos = %d \r" % (len(thread_receiver.threads)))
        sys.stdout.flush()
        time.sleep(1)



   

