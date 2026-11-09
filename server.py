import socket  # Módulo para crear conexiones de red (sockets TCP)
import threading # Módulo para trabajar con hilos (varios clientes a la vez)
import mysql.connector # Módulo para conectarse a la base de datos MySQL
from datetime import datetime    # Clase para obtener la fecha y hora actual (usada en /hora)

# HILO PARA HABLAR CON EL SERVIDOR

# Permite que el administrador escriba en la consola del servidor y que ese mensaje se envíe a todos los clientes conectados.
def enviar_mensajes(lista_clientes, lock_clientes):
    while True:
        mensaje = input("\nServidor: ")

         # Bloqueamos la lista para que nadie la modifique mientras la copiamos
        with lock_clientes:
            clientes = lista_clientes.copy() # Hacemos una copia para poder recorrerla sin el candado

        if not clientes:
            print("No hay clientes conectados.")
            continue

        # Recorremos cada cliente (socket, dirección, nombre)
        for cliente_conn, cliente_addr, nombre_usr in clientes:
            try: # Intentamos enviar el mensaje
                cliente_conn.sendall( # sendall envía todos los bytes del mensaje
                    f"Servidor: {mensaje}".encode('utf-8') # Convertimos el texto a bytes con UTF-8
                )
            except OSError: # Si el socket ya estaba cerrado o falló
                print(f"No se pudo enviar el mensaje a {nombre_usr}.")

# Permite ejecutar comando /todos "mensaje" para enviar mensaje a todos y te dice cuantos lo recibieron
def difundir_mensaje(texto, remitente_conn, lista_clientes, lock_clientes):
    
    with lock_clientes: # Bloqueamos la lista compartida
        clientes = lista_clientes.copy() # Copiamos la lista y soltamos el candado enseguida

    enviados = 0 # Contador de mensajes enviados con éxito

    for cliente_conn, cliente_addr, nombre_usr in clientes: # Recorremos todos los clientes conectados
        if cliente_conn is remitente_conn: # Si es el mismo socket que el de quien escribió
            continue  # Lo salteamos (no recibe su propio mensaje)
        try: # Intentamos enviar
            cliente_conn.sendall(texto.encode('utf-8')) # Enviamos el texto codificado en bytes
            enviados += 1 # Sumamos uno al contador si se envió bien
        except OSError: # Si falla el envío
            print(f"No se pudo enviar el mensaje a {nombre_usr}.")

    return enviados # Devolvemos cuántos lo recibieron

# Permite ejecutar cada cliente uno por uno
def manejar_cliente(conn, addr, lista_clientes, lock_clientes):

    print(f"\nNUEVA CONEXIÓN: {addr}") # Avisamos que llegó un cliente nuevo

    db = None # Variable para la conexión a MySQL (todavía no existe)
    cursor = None # Variable para el cursor de MySQL (todavía no existe)
    usuario = None # Nombre del usuario (se completa al autenticar)
    autenticado = False # Indica si el cliente ya pasó el login

    try: # Autentificacion del cliente
        # 1. RECIBIR CREDENCIALES
        credenciales = conn.recv(1024).decode('utf-8') # Esperamos "usuario,contraseña" y lo pasamos de bytes a texto

        if not credenciales or "," not in credenciales: # Si llegó vacío o sin coma, el formato es incorrecto
            conn.sendall( # Le avisamos al cliente cuál es el formato correcto
                "Formato incorrecto. Debes enviar: usuario,contraseña".encode('utf-8')
            )
            return # Terminamos el hilo

        usuario_ingresado, pass_ingresada = credenciales.split(",", 1) # Dividimos en la primera coma: usuario y contraseña

        usuario = usuario_ingresado.strip() # Sacamos espacios sobrantes del nombre de usuario

        # 2. CONEXION A MYSQL
        db = mysql.connector.connect(# Abrimos conexión con la base de datos
            host="localhost", # El servidor MySQL está en esta misma PC
            user="root", # Usuario por defecto de XAMPP
            password="", # XAMPP no trae contraseña por defecto
            database="redes_tp_final" # Base de datos del trabajo práctico
        )

        cursor = db.cursor() # El cursor permite ejecutar consultas SQL

        # 3. VALIDAR CREDENCIALES
        sql = """SELECT * FROM usuarios WHERE nombre_usuario = %s AND contrasena = %s """ # %s son parámetros (evitan inyección SQL)

        cursor.execute(sql, (usuario, pass_ingresada.strip())) # Ejecutamos la consulta reemplazando los %s por los valores
        resultado = cursor.fetchone() # Traemos una fila; si no existe el usuario, devuelve None

        if resultado: # Si encontró al usuario con esa contraseña
            conn.sendall(
                "¡Bienvenido al servidor! Autenticación exitosa.".encode('utf-8') # Avisamos que el login fue correcto
            )

            # Agregamos al cliente autenticado a la lista
            with lock_clientes: # Bloqueamos la lista compartida
                lista_clientes.append((conn, addr, usuario)) # Agregamos al cliente autenticado

            autenticado = True # Marcamos que ya está autenticado

            print(f"[{addr}] Autenticado como: {usuario}") # Registramos el login en la consola del servidor

        else: # Si no coinciden usuario y contraseña
            conn.sendall(
                "Error: Usuario o contraseña incorrectos. Desconectando...".encode('utf-8') # Avisamos del error al cliente
            )
            print(f"[{addr}] Autenticación fallida.") # Registramos el intento fallido
            conn.close() # Cerramos la conexión con este cliente
            return # Terminamos el hilo

    except Exception as e: # Cualquier error inesperado (ej: MySQL apagado)
        print(f"[{addr}] Error durante la autenticación: {e}") # Mostramos el error en consola

        try: # Intentamos avisarle al cliente
            conn.sendall(
                "Error interno del servidor en la autenticación.".encode('utf-8')
            )
        except OSError: # Si el cliente ya se había ido, ignoramos el error
            pass
        return # Terminamos el hilo

    finally: # El finally se ejecuta SIEMPRE (haya error o no)
        # Cerramos la conexión a MySQL
        if cursor is not None: # Si se llegó a crear el cursor lo cerramos
            cursor.close()

        if db is not None and db.is_connected(): # Si se llegó a abrir la conexión y sigue abierta la cerramos (liberamos recursos de MySQL)
            db.close()
    
    # 4. RECEPCION DE MENSAJES DEL CLIENTE
    while True: # Bucle que atiende al cliente hasta que se desconecte
        try:
            mensaje = conn.recv(1024).decode('utf-8') # Esperamos un mensaje del cliente (bloquea hasta que llegue)

            if not mensaje: # Mensaje vacío = el cliente cerró la conexión
                break

            # Separamos comando y argumento, conservando el texto original
            partes = mensaje.strip().split(" ", 1) # Dividimos en el primer espacio: ["/todos", "Hola a todos"]
            comando = partes[0].lower() # Primera parte en minúsculas = el comando
            argumento = partes[1].strip() if len(partes) > 1 else "" # Segunda parte = el argumento (o vacío si no hay)

            # COMANDO /ADIOS
            if comando == "/adios":
                conn.sendall(
                    "Hasta luego. Te has desconectado del servidor.".encode('utf-8') # Despedimos al cliente
                )
                print(f"[{addr}] Solicitó desconectarse.") # Registramos la salida en consola
                break # Salimos del bucle para cerrar la conexión

            # COMANDO /USUARIOS
            elif comando == "/usuarios":

                print(f"[{addr}] Solicitó la lista de usuarios.") # Registramos el pedido

                lista_str = "Usuarios conectados actualmente:\n" # Texto inicial de la respuesta
 
                with lock_clientes: # Bloqueamos la lista compartida
                    clientes = lista_clientes.copy() # La copiamos para recorrerla tranquilos

                for cliente_conn, cliente_addr, nombre_usr in clientes: # Recorremos los clientes conectados
                    lista_str += f"- {nombre_usr} ({cliente_addr})\n" # Agregamos una línea por usuario

                conn.sendall(lista_str.encode('utf-8')) # Enviamos la lista completa al cliente que la pidió

            # COMANDO /HORA
            elif comando == "/hora":
 
                print(f"[{addr}] Solicitó la hora.") # Registramos el pedido en consola
 
                ahora = datetime.now() # Obtenemos la fecha y hora actuales del servidor
 
                hora_str = ahora.strftime("%d/%m/%Y %H:%M:%S") # Formato: día/mes/año horas:minutos:segundos
 
                conn.sendall( # Enviamos la hora al cliente que la pidió
                    f"Fecha y hora del servidor: {hora_str}".encode('utf-8')
                )

            # COMANDO /TODOS
            elif comando == "/todos":

                if not argumento: # Si escribió "/todos" sin mensaje
                    conn.sendall(
                        "Uso correcto: /todos <mensaje>".encode('utf-8') # Le explicamos cómo se usa
                    )
                    continue # Volvemos al inicio del while (esperar otro mensaje)

                print(f"[{usuario}] -> TODOS: {argumento}") # Registramos el mensaje en consola

                cantidad = difundir_mensaje( # Enviamos a todos menos al remitente
                    f"[{usuario} (a todos)]: {argumento}",
                    conn, # Socket del remitente (para excluirlo)
                    lista_clientes, # Lista compartida de clientes
                    lock_clientes # Candado de la lista
                )

                if cantidad == 0: # Si no había nadie más conectado
                    conn.sendall(
                        "No hay otros usuarios conectados para recibir tu mensaje.".encode('utf-8')
                    )
                else: # Si al menos uno lo recibió
                    conn.sendall(
                        f"Mensaje enviado a {cantidad} usuario(s).".encode('utf-8')
                    )

            # COMANDO /REPOS
            elif comando == "/repos":
                pass

            # COMANDO /FOLLOWERS
            elif comando == "/followers":
                pass

            else:
                if comando.startswith("/"): # Si empieza con "/" pero no es ninguno de los anteriores
                    conn.sendall(
                        "Comando no reconocido.".encode('utf-8') # Avisamos que no existe ese comando
                    )
                else: # Si es texto normal (sin "/")
                    print(f"[{usuario}] dice: {mensaje}") # Solo lo mostramos en la consola del servidor

        except (ConnectionResetError, OSError): # Si el cliente se cae o se corta la conexión
            break # Salimos del bucle

    # 5. ELIMINAR CLIENTE DE LA LISTA
    if autenticado: # Solo si el cliente estaba en la lista
        with lock_clientes: # Bloqueamos la lista compartida
            for cliente in lista_clientes: # Buscamos al cliente en la lista
                if cliente[0] == conn: # Lo identificamos por su socket
                    lista_clientes.remove(cliente) # Lo eliminamos de la lista
                    break # Dejamos de buscar (ya lo encontramos)

    conn.close() # Cerramos el socket de este cliente

    print(f"\nDESCONEXIÓN: El cliente {addr} se ha ido.")

    with lock_clientes: # Bloqueamos la lista para leer su tamaño
        cantidad = len(lista_clientes) # Contamos cuántos clientes quedan

    print(f"CLIENTES ACTIVOS: Quedan {cantidad} cliente(s).") # Mostramos cuántos quedan

# FUNCION PRINCIPAL DEL SERVIDOR
def iniciar_servidor():

    # 1. CREAR SOCKET DEL SERVIDOR
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPv4, SOCK_STREAM = TCP

    server.bind(('localhost', 5051)) # Asociamos el socket a la dirección y puerto 5051

    server.listen() # Ponemos el socket a la escucha de conexiones

    clientes_activos = [] # Lista compartida de clientes autenticados

    lock_clientes = threading.Lock() # Candado que protege la lista compartida

    print("INICIO: Servidor escuchando en el puerto 5051...") # Avisamos que el servidor está listo

    # 2. CREAR HILO DE ENVIO DEL SERVIDOR
    hilo_envio = threading.Thread( # Creamos el hilo del administrador
        target=enviar_mensajes, # Función que ejecutará el hilo
        args=(clientes_activos, lock_clientes), # Argumentos que recibe esa función
        daemon=True # Daemon: se cierra solo cuando termina el programa
    )

    hilo_envio.start() # Arrancamos el hilo

    # 3. ACEPTAR NUEVOS CLIENTES
    while True: # Bucle infinito para aceptar clientes

        conn, addr = server.accept() # Espera una conexión; devuelve el socket y la dirección del cliente

        hilo = threading.Thread( # Creamos un hilo dedicado a este cliente
            target=manejar_cliente, # Función que atiende al cliente
            args=(conn, addr, clientes_activos, lock_clientes) # Argumentos de esa función
        )

        hilo.start() # Arrancamos el hilo (el while sigue aceptando otros)


if __name__ == "__main__":
    iniciar_servidor()
