import socket
import threading
# FUNCIÓN DEL HILO (THREAD)
# Esta función es el "trabajo" que hará el hilo. 
# Se ejecuta de forma independiente por cada cliente que se conecte.

def manejar_cliente(conn, addr, lista_clientes): # conn = socket del cliente, addr = dirección del cliente, lista_clientes = lista global de clientes
    print(f"\nNUEVA CONEXIÓN El cliente con IP y puerto {addr} se ha conectado.")
    
    conectado = True
    # Bucle individual de este cliente: se queda escuchando lo que este cliente envíe
    while conectado:
        try:
            # 1. Esperamos recibir un mensaje (el hilo se pausa aquí hasta que llegue algo)
            mensaje = conn.recv(1024).decode('utf-8')
            
            # Si el mensaje está vacío, significa que el cliente cerró la conexión de golpe
            if not mensaje:
                break
            
            # 2. Limpiamos espacios al principio/final y pasamos a minúsculas
            # Esto es para que "/adios", "/ADIOS" o " /adios " funcionen igual
            comando = mensaje.strip().lower()

            # 3. Revisamos si el mensaje es un comando especial
            if comando == "/adios":
                print(f"[{addr}] solicitó desconexión enviando /adios.")
                # El 'break' rompe este bucle while y nos manda directo a la fase de cierre abajo
                break 
                
            elif comando == "/users":
                print(f"[{addr}] solicitó la lista de usuarios.")
                # Armamos un texto recorriendo la lista de clientes guardados
                lista_str = "Usuarios conectados actualmente:\n"
                for cliente_conn, cliente_addr in lista_clientes: # Recorremos la lista de clientes activos
                    lista_str += f"- {cliente_addr}\n" # Agregamos la dirección de cada cliente a la lista formateada
                
                # Le enviamos la lista formateada solo al cliente que la pidió
                conn.send(lista_str.encode('utf-8'))
                
            else:
                # 4. Si no es un comando, hacemos el comportamiento normal de ECO
                print(f"[{addr}] dice: {mensaje}") # Imprimimos en consola del servidor lo que el cliente envió
                # Le devolvemos el mismo mensaje al cliente
                conn.send(f"Eco: {mensaje}".encode('utf-8'))
                
        except ConnectionResetError:
            # Si el cliente cierra la terminal bruscamente o se desconecta sin enviar /adios, se lanza esta excepción
            break

    # 5. Cerramos el socket exclusivamente de este cliente
    conn.close()
    
    # 6. Buscamos a este cliente en la lista global y lo borramos
    for cliente in lista_clientes:
        if cliente[0] == conn: # Si el socket coincide, lo removemos
            lista_clientes.remove(cliente)
            break
            
    print(f"\nDESCONEXIÓN El cliente {addr} se ha ido.")
    print(f"CLIENTES ACTIVOS Quedan {len(lista_clientes)} cliente(s) conectado(s).")


# Función principal del servidor
def iniciar_servidor():
    # 1. Creamos el socket pasivo o de escucha (IPv4, TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. Enlazamos el socket a la IP local y al puerto 5051
    server.bind(('localhost', 5051))
    
    # 3. Ponemos al servidor a escuchar peticiones
    server.listen()
    
    # Lista donde guardaremos una tupla (socket, direccion) de cada conectado
    clientes_activos = []
    
    print("INICIO Servidor concurrente escuchando en el puerto 5051...")

    # 4. Bucle infinito principal: Su ÚNICA tarea es aceptar gente nueva
    while True:
        # Se queda bloqueado en accept() hasta que alguien intenta conectarse.
        # Retorna el nuevo socket (conn) dedicado a ese cliente, y el original sigue escuchando.
        conn, addr = server.accept()
        
        # Agregamos la tupla (conexión, dirección) a nuestra lista
        clientes_activos.append((conn, addr))
        
        # 5. CREACIÓN DEL HILO
        # Le decimos al SO: "Ejecuta 'manejar_cliente' en paralelo. 
        # Pásale los datos de este cliente específico (conn, addr) y la lista"
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr, clientes_activos))
        
        # 6. Iniciamos el hilo. El bucle principal vuelve inmediatamente arriba al accept()
        hilo.start()
        
        print(f"CLIENTES ACTIVOS Total de conexiones: {len(clientes_activos)}")

if __name__ == "__main__":
    iniciar_servidor()