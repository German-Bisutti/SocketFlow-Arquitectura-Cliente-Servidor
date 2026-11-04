import socket
import threading
import mysql.connector
# FUNCIÓN DEL HILO (THREAD)
# Esta función es el "trabajo" que hará el hilo. 
# Se ejecuta de forma independiente por cada cliente que se conecte.

def manejar_cliente(conn, addr, lista_clientes): # conn = socket del cliente, addr = dirección del cliente, lista_clientes = lista global de clientes
    print(f"\nNUEVA CONEXIÓN El cliente con IP y puerto {addr} se ha conectado.")
    # Verificacion de credenciales del cliente
    try:
        # Esperamos que el cliente envíe su nombre de usuario y contraseña (Formato: usuario,contraseña)
        credenciales = conn.recv(1024).decode('utf-8')
        
        # Validación de formato
        if not credenciales or "," not in credenciales:
            conn.send("Formato incorrecto. Debes enviar: usuario,contraseña".encode('utf-8'))
            conn.close()
            print(f"[{addr}] Desconectado por formato de credenciales inválido.")
            return # Terminamos el hilo para este cliente
            
        usuario_ingresado, pass_ingresada = credenciales.split(",", 1)
        
        # 2. Conexión a la base de datos MySQL local
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="redes_tp_final"
        )
        cursor = db.cursor()
        
        # 3. Consulta SQL para verificar si el usuario y contraseña coinciden
        sql = "SELECT * FROM usuarios WHERE nombre_usuario = %s AND contrasena = %s"
        # Usamos .strip() por si el cliente agregó espacios accidentalmente
        cursor.execute(sql, (usuario_ingresado.strip(), pass_ingresada.strip()))
        resultado = cursor.fetchone() # Obtiene la primera fila que coincida
        
        if resultado:
            # SI SON VÁLIDOS: Enviamos mensaje de bienvenida
            conn.send("¡Bienvenido al servidor! Autenticación exitosa.".encode('utf-8'))
            
            # Guardamos al cliente autenticado en la lista global
            # Ahora la lista guarda: (socket, direccion, nombre_de_usuario)
            lista_clientes.append((conn, addr, usuario_ingresado.strip()))
            print(f"[{addr}] Autenticado exitosamente como: {usuario_ingresado.strip()}")
        else:
            # SI SON INCORRECTOS: Informamos y cerramos sesión
            conn.send("Error: Usuario o contraseña incorrectos. Desconectando...".encode('utf-8'))
            conn.close()
            print(f"[{addr}] Autenticación fallida para el usuario: {usuario_ingresado.strip()}")
            return # Terminamos el hilo
            
    except Exception as e:
        print(f"[{addr}] Error en la base de datos: {e}")
        conn.send("Error interno del servidor en la autenticación.".encode('utf-8'))
        conn.close()
        return
    finally:
        # Aseguramos cerrar la conexión a la base de datos para no saturarla
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

    conectado = True
    # Bucle individual de este cliente: se queda escuchando lo que este cliente envíe
    while conectado:
        try:
            # Esperamos recibir un mensaje (el hilo se pausa aquí hasta que llegue algo)
            mensaje = conn.recv(1024).decode('utf-8')
            
            # Si el mensaje está vacío, significa que el cliente cerró la conexión de golpe
            if not mensaje:
                break
            
            # Limpiamos espacios al principio/final y pasamos a minúsculas
            # Esto es para que "/adios", "/ADIOS" o " /adios " funcionen igual
            comando = mensaje.strip().lower()

            # COMANDOS
            if comando == "/adios":
                print(f"[{addr}] solicitó desconexión enviando /adios.")
                # El 'break' rompe este bucle while y nos manda directo a la fase de cierre abajo
                break 

            elif comando == "/users":
                print(f"[{addr}] solicitó la lista de usuarios.")
                lista_str = "Usuarios conectados actualmente:\n"
                
                for cliente_conn, cliente_addr, nombre_usr in lista_clientes:
                    lista_str += f"- {nombre_usr} ({cliente_addr})\n"
                conn.send(lista_str.encode('utf-8'))
                
            else:
                # Si no es un comando, hacemos el comportamiento normal de ECO
                print(f"[{addr}] dice: {mensaje}") # Imprimimos en consola del servidor lo que el cliente envió
                # Le devolvemos el mismo mensaje al cliente
                conn.send(f"Eco: {mensaje}".encode('utf-8'))
                
        except ConnectionResetError:
            # Si el cliente cierra la terminal bruscamente o se desconecta sin enviar /adios, se lanza esta excepción
            break

    # Cerramos el socket exclusivamente de este cliente
    conn.close()
    
    # Buscamos a este cliente en la lista global y lo borramos
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
        
        # 5. CREACIÓN DEL HILO
        # Le decimos al SO: "Ejecuta 'manejar_cliente' en paralelo. 
        # Pásale los datos de este cliente específico (conn, addr) y la lista"
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr, clientes_activos))
        
        # 6. Iniciamos el hilo. El bucle principal vuelve inmediatamente arriba al accept()
        hilo.start()
        
        print(f"CLIENTES ACTIVOS Total de conexiones: {len(clientes_activos)}")

if __name__ == "__main__":
    iniciar_servidor()