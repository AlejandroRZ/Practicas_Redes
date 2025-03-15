from vlsm import vlsm
continuar = True

while continuar:
    file = input('Ingresa a ruta del archivo: ')
    with open(file, 'r') as f:
        n = int(f.readline().strip())

        ejemplos = []

        for _ in range(n):
            ip = f.readline().strip()
            mask = f.readline().strip()
            subnets_raw = f.readline().strip()
            subnets = []
            # Primero separamos por espacio
            for sub in subnets_raw.split(' '):
                # Ahora separamos por coma para tener un arreglo de la forma [(a,b)]
                # donde 'a' es el identificador y 'b' los hosts que necesita
                host_to_add = sub.split(',')
                subnets.append((host_to_add[0], int(host_to_add[1])))

            ejemplos.append((ip, mask, subnets))
    for ej in ejemplos:
        print('Iniciando vlsm...')
        res = vlsm(ej[0], ej[1], ej[2])
        for nombre, info in res.items():
            print(f"Subred: {nombre}")
            for campo, valor in info.items():
                print(f"{campo}: {valor}")
            print('----------')
        print('+++++++++++++++')
    op = input('Si deseas usar vlsm de nuevo presiona 1 o presiona otra tecla para terminar: \n')
    continuar = '1' == op