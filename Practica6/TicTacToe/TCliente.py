import argparse
import socket
import threading
import queue
import signal

HOST = 'localhost'
PORT = 12001

class SocketThread(threading.Thread):

    """
    La clase SocketThread representa un hilo que maneja la comunicación con un servidor mediante el protocolo UDP.
    Este hilo se ejecuta en segundo plano para enviar y recibir mensajes, manejar respuestas, y gestionar errores.
    Utiliza una cola para almacenar los mensajes recibidos, y proporciona mecanismos para detener el hilo de manera segura.

    Atributos:
        serverAddress (tuple): Dirección del servidor que consiste en el nombre y puerto.
        stopper (threading.Event): Evento utilizado para detener el hilo.
        messages_received (queue.Queue): Cola para almacenar los mensajes recibidos del servidor.
        clientSocket (socket.socket): Socket UDP utilizado para la comunicación con el servidor.
        uniqueId (int): Identificador único de cada mensaje enviado, para asegurar que las respuestas correspondan al mensaje.
    """

    class Error(Exception):
        pass
    class SocketError(Error):
        pass

    def __init__(self,serverName,serverPort):
        """
        Inicializa una instancia de la clase SocketThread.

        Args:
            serverName (str): Nombre o dirección IP del servidor.
            serverPort (int): Puerto del servidor.

        El constructor crea un socket UDP, configura un tiempo de espera para las respuestas del servidor,
        y prepara un mecanismo para detener el hilo. También inicializa una cola para almacenar los mensajes
        recibidos y un identificador único para gestionar las solicitudes y respuestas correctamente.

        Atributos:
            serverAddress (tuple): La dirección y puerto del servidor en forma de tupla.
            stopper (threading.Event): Se utiliza para controlar cuándo detener el hilo.
            messages_received (queue.Queue): Cola que almacena los mensajes recibidos del servidor.
            clientSocket (socket.socket): Socket creado para la comunicación UDP con el servidor.
            uniqueId (int): Identificador único para las solicitudes enviadas.
        """
        super().__init__()
        self.serverAddress=(serverName, serverPort)
        self.stopper=threading.Event()
        self.messages_received=queue.Queue()
        self.clientSocket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clientSocket.settimeout(1)
        self.uniqueId=0

    def run(self):
        '''
            Método que se ejecuta cuando se inicia el hilo. El hilo entra en un bucle que permanece
            activo hasta que se recibe una señal para detenerse.

            Durante la ejecución, el hilo espera recibir mensajes del servidor a través del socket. Si
            recibe un mensaje 'ping', responde con 'pong' sin almacenarlo en la cola. Si el mensaje no
            cumple con el formato esperado, es descartado. Los mensajes válidos se almacenan en la cola
            para ser procesados más tarde.

            El método maneja excepciones como el tiempo de espera del socket y detiene el hilo en caso
            de errores inesperados.
        '''
        while not self.stopper.is_set():
            try:
                serverResponse,serverAddress = self.clientSocket.recvfrom(2048)
            except socket.timeout:
                continue
            except Exception as e:
                self.stop()
                break
            serverResponse = serverResponse.decode()
            if serverResponse == 'ping':
                self.send('pong')
            else:
                try:
                    id, move, status = [int(s) for s in serverResponse.split(" ")]
                except:
                    continue
                self.messages_received.put(serverResponse)
        self._close()
    
    # manda un mensaje al servidor 
    def send(self, message):
        try:
            self.clientSocket.sendto(message.encode(),self.serverAddress)
        except:
            self.stop()

    
    # Esta funcion esperara por un mensaje del servidor 
    def receive(self, timeout=None):
        if self.stopper.is_set():
           raise SocketThread.SocketError
        else:
            try:
                message = self.messages_received.get(timeout=timeout)
            except queue.Empty:
                raise TimeoutError
            return message

    # Mandará un mensaje al servidor experando una respuesta 
    def request(self, message):
        id = self.uniqueId
        self.uniqueId += 1
        message = str(id)+" "+message
        max_num_tries = 10
        num_tries = 0
        self.send(message)
        while num_tries < max_num_tries and not self.stopper.is_set():
            try:
                response = self.receive(0.5)
            except TimeoutError:
                self.send(message)
                num_tries += 1
                continue
            except SocketThread.SocketError:
                break
            else:
                responseId = response.split(" ")[0]
                if responseId != str(id):
                    continue
                return response[len(responseId)+1:]
        print("El servidor no se encuentra disponible")
        raise SocketThread.SocketError

    def _close(self):
        '''
        Envia un mensaje de cierre al servidor y cierra el socket
        '''
        id = self.uniqueId
        self.uniqueId += 1
        message = str(id)+" close"
        self.send(message)
        self.clientSocket.close()

    def stop(self):
        '''
        Detiene la ejecución del hilo y cierra el socket de comunicación con el servidor.
        '''
        self.stopper.set()
        

def playTicTacToe(sockListener):
    """
    Función principal que gestiona la lógica del juego de Tic-Tac-Toe.

    Args:
        sockListener (SocketThread): El hilo que maneja la comunicación con el servidor.
        
    Este método maneja el flujo del juego, desde el inicio hasta el final. Se ocupa de enviar solicitudes al servidor,
    recibir respuestas, manejar los movimientos del jugador y del servidor, y actualizar el tablero. 
    """
    cMoves=set()
    sMoves=set()
    def waitForServerMove(clientMove):
        try:
            reply = sockListener.request(clientMove)
        except SocketThread.SocketError:
            raise
        else:
            serverMove, status = [int(s) for s in reply.split(" ")]
            IN_PROGRESS, CLIENT_WIN, SERVER_WIN, TIE = 0,1,2,3

            if status == IN_PROGRESS:
                sMoves.add(serverMove)
                render()
                return True
            elif status == CLIENT_WIN:
                print("¡Has ganado wiii!")
            elif status == SERVER_WIN:
                sMoves.add(serverMove)
                render()
                print("Buuu! Perdiste :(")
            elif status == TIE:
                if serverMove != 0:
                    sMoves.add(serverMove)
                    render()
                print("EMPATE")
        return False

    
    def waitForUserMove():
        """
        Espera y valida el movimiento del usuario.

        Este método pide al usuario que ingrese un movimiento válido (número entre 1 y 9). Si el movimiento es válido, lo añade al
        conjunto de movimientos del cliente (cMoves) y actualiza el tablero. Si el usuario ingresa un valor no válido, lo vuelve a
        solicitar hasta que se ingrese uno correcto.

        Returns:
            move (int): El movimiento válido que el usuario ha realizado.
        """
        def validateInput(move):
            try:
                move = int(move)
            except ValueError:
                print("Entrada no valida. Ingresa un número del 1 al 9.")
                return False
            availableMoves={1,2,3,4,5,6,7,8,9}-cMoves-sMoves
            if move in availableMoves:
                return True
            print("Entrada no valida. Las entradas válidas son " + str(availableMoves))
            return False

        while True:
            try:
                move = input("Ingresa cual será tu proximo movimiento: ")
            except:
                raise
                return
            if validateInput(move):
                break

        cMoves.add(int(move))
        render()
        return move


    #Muestra el tablero en consola y lo actualiza
    def render():
        xPos=cMoves 
        oPos=sMoves 
        O="O"
        X="X"
        _=" "
        board=[ _ for i in range(9)]
        for move in xPos:
            board[move-1]=X
        for move in oPos:
            board[move-1]=O
        out = ( ' {6} │ {7} │ {8} \n'
                '───┼───┼───\n'
                ' {3} │ {4} │ {5} \n'
                '───┼───┼───\n'
                ' {0} │ {1} │ {2} \n').format(*board)
        print(out)

    # Muestra el mensaje de bienvenida y el tablero de ejemplo
    def welcomeMessage():
        print("")
        print("Hola! Bienvenido al juego de TIC TAC TOE.\n Escoge una opción 1 - 9 \n")
        print(  " 7 │ 8 │ 9 \n"
                "───┼───┼───\n"
                " 4 │ 5 │ 6 \n"
                "───┼───┼───\n"
                " 1 │ 2 │ 3 \n")
        print("")


    def initializeGameWithServer():
        """
        Inicializa el juego de Tic-Tac-Toe con el servidor, enviando una solicitud para comenzar la partida
        y esperando la respuesta del servidor.
        Se envía el mensaje "X" al servidor
        """
        print("Invitando al servidor ...")
        try:
            reply = sockListener.request("X")
        except SocketThread.SocketError:
            raise
        else:
            serverMove, status = [int(s) for s in reply.split(" ")]
            if serverMove != 0:
                sMoves.add(serverMove)
 
    # Inicializa el juego tictactoe
    def start():
        def endGame():
            sockListener.stop()
            sockListener.join()
            print("Saliendo del juego ...")
        try:
            initializeGameWithServer()
        except SocketThread.SocketError:
            return endGame()

        welcomeMessage()
        render()
        clientTurn = True
        playerMove=None
        inProgress = True
        while inProgress:
            if clientTurn:
                print("Tu turno")
                try:
                    playerMove = waitForUserMove()
                except:
                    print("Interrumpido")
                    return endGame()
            else:
                print("Esperando el servidor ...")
                try:
                    inProgress = waitForServerMove(playerMove)
                except SocketThread.SocketError:
                    return endGame()

            clientTurn = not clientTurn
        
        print("Se ha cerrado el juego")
        return endGame()
    
    # Inicializamos el juego
    start()

     
if __name__ == "__main__":
    client_start = True  # el cliente inicia la partida
    sockListener = SocketThread(HOST, PORT)
    sockListener.start()
    # Inicia el juego de Tic-Tac-Toe
    playTicTacToe(sockListener)

    
    