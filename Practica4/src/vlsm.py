def obtener_bits_y_hosts(hosts):
    """
    Regresa los bits a utilizar de acuerdo a la formula
    2^n > S 
    Y el numero de hosts utiles de acuerdo a la formula
    2^n-2
    params: 
    hosts -> Entero con la cantidad de hosts requerida
    returns:
    (bits, hosts)
    """
    n = 0
    while 2**n < hosts + 2:  # Include network and broadcast addresses
        n += 1
    return (n, 2**n - 2)


def obtener_mascara(bits_mascara):
    """
    Calcula la máscara de subred a partir de los bits disponibles para hosts.
    """
    bits = '1' * (32 - bits_mascara) + '0' * bits_mascara
    octetos = [int(bits[i:i+8], 2) for i in range(0, 32, 8)]
    return octetos


def ip_a_binario(ip):
    """
    Convierte una IP decimal a binario.
    """
    return ''.join([bin(int(oct))[2:].zfill(8) for oct in ip.split('.')])


def binario_a_ip(bin_ip):
    """
    Convierte una IP en formato binario a formato decimal.
    """
    return '.'.join([str(int(bin_ip[i:i+8], 2)) for i in range(0, 32, 8)])


def sumar_ip(bin_ip, incremento):
    """
    Suma una cantidad a una IP binaria y devuelve la nueva IP.
    """
    return bin(int(bin_ip, 2) + incremento)[2:].zfill(32)


def vlsm(ip, original_mask, subnets):
    """
    Funcion que dada una direccion IP, una mascara de red y una lista de subredes
    devuelve las direcciones de las subredes con todos los detalles.
    """
    # Cuantos bits usa la mascara
    original_mask_bits = sum([bin(int(octet)).count('1') for octet in original_mask.split('.')])
    # Paso 1: Convertimos la IP a binario
    ip_bin = ip_a_binario(ip)
    
    # Paso 2: Ordenamos las subredes de mayor a menor
    sorted_subnets = sorted(subnets, key=lambda x: x[1], reverse=True)
    
    # Paso 3: Almacenamos los resultados de cada subred
    div_subnets = {}
    ip_actual = ip_bin[:original_mask_bits] + '0' * (32 - original_mask_bits)
    
    for sub in sorted_subnets:
        nombre, hosts_necesarios = sub
        
        # Paso 4: Calculamos los bits y hosts útiles
        bits_requeridos, hosts_utiles = obtener_bits_y_hosts(hosts_necesarios)
        bits_red = 32 - bits_requeridos
        
        # Obtenemos la máscara de subred
        mascara = obtener_mascara(bits_requeridos)
        mascara_str = '.'.join(map(str, mascara))
        
        # Calculamos ID de red
        id_red = binario_a_ip(ip_actual[:bits_red] + '0' * bits_requeridos)
        
        # La primera direccion util
        primera_ip = binario_a_ip(sumar_ip(ip_actual, 1))
        
        # La ultima IP sumamos la red mas los hosts utiles
        ultima_ip = binario_a_ip(sumar_ip(ip_actual[:bits_red] + '0' * bits_requeridos, hosts_utiles))
        
        broadcast = binario_a_ip(ip_actual[:bits_red] + '1' * bits_requeridos)
        
        # Guardar la información de la subred
        div_subnets[nombre] = {
            'ID de Red': id_red,
            'Máscara de Red': mascara_str,
            'Primera IP Útil': primera_ip,
            'Última IP Útil': ultima_ip,
            'Broadcast': broadcast
        }
        
        # Actualizar la IP para la siguiente subred
        ip_actual = sumar_ip(ip_actual[:bits_red] + '0' * bits_requeridos, hosts_utiles + 2)
    return div_subnets
    

# Ejemplo de uso
ip_inicial = "192.168.1.0"
mascara_inicial = "255.255.255.0"
subredes = [("A", 25), ("B", 10), ("C", 50), ("D", 80)]

vlsm(ip_inicial, mascara_inicial, subredes)
