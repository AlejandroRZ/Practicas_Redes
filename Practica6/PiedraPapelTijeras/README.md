# Practica 6: Modelo cliente - servidor

Juego piedra, papel y tijeras utilizando el modelo CLIENTE - SERVIDOR


<table>
    <tr>
        <th>Equipo: DIA 2.0</th>
        <th>No de cuenta</th>
    </tr>
    <tr>
        <td>López Diego Gabriela</td>
        <td>318243485</td>
    </tr>
    <tr>
        <td>San Martín Macías Juan Daniel</td>
        <td>318181637</td>
    </tr>
    <tr>
        <td>Rivera Zavala Javier Alejandro</td>
        <td>311288876</td>
    </tr>
    <tr>
        <td>Ortiz Amaya Bruno Fernando</td>
        <td>318128676</td>
    </tr>
    <tr>
        <td>Juárez Ubaldo Juan Aurelio</td>
        <td>421095568</td>
    </tr>
</table>

### Explicación del algoritmo 

* Clase **`ppt_servidor.py`** 

Este archivo contiene la implementación del servidor que:

1. Escucha conexiones en una dirección IP y puerto específicos.
2. Acepta nuevos clientes y crea un hilo para gestionar la comunicación con cada uno.
3. Recibe las jugadas de los clientes, genera una jugada aleatoria como respuesta y envía los resultados a los clientes.
4. Muestra mensajes en la consola sobre los clientes que se conectan y desconectan.


* Clase **`ppt_cliente.py`**

1.  Se conecta al servidor y solicita al usuario que ingrese un nombre de usuario.
2. Espera un mensaje de bienvenida del servidor antes de permitir que el usuario elija su jugada.
3.  Envía la jugada seleccionada al servidor y recibe la jugada del oponente (servidor).
4. Imprime los resultados de la partida en la consola y permite al usuario elegir jugar nuevamente o salir.

### Bibliotecas Utilizadas

- **`socket`**: Esta biblioteca proporciona la funcionalidad necesaria para implementar la comunicación a través de redes. Permite crear sockets que pueden enviar y recibir datos entre el servidor y el cliente.
  
- **`threading`**: Utilizada para manejar múltiples conexiones simultáneamente. Permite que el servidor escuche nuevas conexiones y se comunique con varios clientes al mismo tiempo sin bloquear el hilo principal.

- **`random`**: Usada en el servidor para seleccionar aleatoriamente la jugada del servidor (piedra, papel o tijeras) al recibir la jugada del cliente.


Para ejecutar el juego **piedra, papel y tijeras** hay que ejecutar en orden los siguientes comandos en terminales diferentes (macOS/Linux)

1. python3 ppt_servidor.py 
2. python3 ppt_cliente.py 

Si te encuentras en windows 

1. python ppt_servidor.py 
2. python ppt_cliente.py 



### Ejemplo de ejecución con dos clientes conectados al servidor 

<img src=ej.png width="600">