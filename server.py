import socket  # Módulo para crear conexiones de red (sockets TCP)
import threading # Módulo para trabajar con hilos (varios clientes a la vez)
import mysql.connector # Módulo para conectarse a la base de datos MySQL
from datetime import datetime    # Clase para obtener la fecha y hora actual (usada en /hora)
import requests # Módulo para hacer peticiones HTTP (usado en /repos y /followers)
MAX_MOSTRAR = 20 # Cantidad máxima de repositorios o followers a mostrar en la consola del cliente
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

# Permite consultar los followers de un usuario de GitHub mediante la API pública
def obtener_followers(nombre_usuario):
    url = f"https://api.github.com/users/{nombre_usuario}/followers"  # Dirección de la API
    respuesta = requests.get(url, params={"per_page": 100})  # Pedimos hasta 100 resultados
    if respuesta.status_code != 200:  # Si no salió bien
        return None
    return respuesta.json()  # Convertimos el JSON en una lista de Python

# Permite consultar los repositorios de un usuario de GitHub mediante la API pública
def obtener_repositorios(nombre_usuario):
    url = f"https://api.github.com/users/{nombre_usuario}/repos"  # Dirección de la API
    respuesta = requests.get(url, params={"per_page": 100})  # per_page=100 porque por defecto trae solo 30
    if respuesta.status_code != 200:  # 200 = todo bien; otro código = usuario inexistente o error
        return None
    return respuesta.json()  # Convertimos el JSON en una lista de Python

# Permite guardar los followers de un usuario de GitHub en la base de datos MySQL
def guardar_followers(usuario_github, followers):
    db = mysql.connector.connect(host="localhost", user="root", password="", database="redes_tp_final")  # Conexión a MySQL
    cursor = db.cursor()  # Cursor para ejecutar consultas
 
    for follower in followers:  # Una vuelta por cada follower
        cursor.execute(
            "INSERT INTO followers (usuario, nombre_follower, fecha_guardado) VALUES (%s, %s, NOW())",
            (usuario_github, follower["login"])  # "login" es el nombre del follower en el JSON
        )
 
    db.commit()  # Confirmamos los cambios
    cursor.close()  # Cerramos el cursor
    db.close()  # Cerramos la conexión
 
# Permite guardar los repositorios de un usuario de GitHub en la base de datos MySQL
def guardar_repositorios(usuario_github, repos):
    db = mysql.connector.connect(host="localhost", user="root", password="", database="redes_tp_final")  # Conexión a MySQL
    cursor = db.cursor()  # Cursor para ejecutar consultas
 
    for repo in repos:  # Una inserción por cada repositorio
        cursor.execute(
            "INSERT INTO repositorios (usuario, nombre_repo, url_repo, fecha_guardado) VALUES (%s, %s, %s, NOW())",  # NOW() = fecha actual
            (usuario_github, repo["name"], repo["html_url"])  # Nombre y URL vienen en el JSON de GitHub
        )
 
    db.commit()  # Confirmamos los cambios (sin esto no se guardan)
    cursor.close()  # Cerramos el cursor
    db.close()  # Cerramos la conexión

# Permite ejecutar cada cliente uno por uno
def manejar_cliente(conn, addr, lista_clientes, lock_clientes):
    print(f"\nNUEVA CONEXIÓN: {addr}")  # Avisamos que llegó un cliente
 
    # 1. AUTENTICACIÓN
    credenciales = conn.recv(1024).decode('utf-8')  # Recibimos "usuario,contraseña"
 
    if "," not in credenciales:  # Si no tiene coma, el formato está mal
        conn.sendall("Formato incorrecto. Debes enviar: usuario,contraseña".encode('utf-8'))
        conn.close()  # Cerramos la conexión
        return  # Termina el hilo
 
    usuario, contrasena = credenciales.split(",", 1)  # Separamos en la primera coma
    usuario = usuario.strip()  # Sacamos espacios sobrantes
    contrasena = contrasena.strip()
 
    db = mysql.connector.connect(host="localhost", user="root", password="", database="redes_tp_final")  # Conexión a MySQL
    cursor = db.cursor()  # Cursor para ejecutar consultas
    cursor.execute(
        "SELECT * FROM usuarios WHERE nombre_usuario = %s AND contrasena = %s",  # Buscamos usuario y contraseña
        (usuario, contrasena)  # Los %s se reemplazan por estos valores
    )
    resultado = cursor.fetchone()  # Trae una fila, o None si no hay coincidencia
    cursor.close()  # Cerramos el cursor
    db.close()  # Cerramos la conexión
 
    if not resultado:  # Usuario o contraseña incorrectos
        conn.sendall("Error: Usuario o contraseña incorrectos. Desconectando...".encode('utf-8'))
        conn.close()  # Cerramos la sesión
        return  # Termina el hilo
 
    conn.sendall("¡Bienvenido al servidor! Autenticación exitosa.".encode('utf-8'))  # Mensaje de bienvenida
 
    with lock_clientes:  # Bloqueamos la lista compartida
        lista_clientes.append((conn, addr, usuario))  # Agregamos al cliente a los conectados
    print(f"[{addr}] Autenticado como: {usuario}")
 
    # 2. RECEPCIÓN DE MENSAJES Y COMANDOS
    while True:  # Atendemos al cliente hasta que se desconecte
        try:
            mensaje = conn.recv(1024).decode('utf-8')  # Esperamos un mensaje del cliente
 
            if not mensaje:  # Mensaje vacío = el cliente cerró la conexión
                break
 
            partes = mensaje.strip().split(" ", 1)  # Separamos comando y argumento: "/repos", "nombre del usuario"
            comando = partes[0].lower()  # El comando, en minúsculas
            argumento = partes[1].strip() if len(partes) > 1 else ""  # El resto del texto, o vacío si no hay
 
            if comando == "/adios":  # Despedida
                conn.sendall("Hasta luego. Te has desconectado del servidor.".encode('utf-8'))
                break  # Salimos del bucle para desconectar
 
            elif comando == "/usuarios":  # Lista de usuarios conectados
                lista_str = "Usuarios conectados:\n"  # Texto inicial
                with lock_clientes:  # Bloqueamos la lista mientras la recorremos
                    for cliente_conn, cliente_addr, nombre_usr in lista_clientes:
                        lista_str += f"- {nombre_usr}\n"  # Una línea por usuario
                conn.sendall(lista_str.encode('utf-8'))  # Enviamos la lista
 
            elif comando == "/hora":  # Hora actual del servidor
                hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Formato día/mes/año hora:min:seg
                conn.sendall(f"Hora del servidor: {hora}".encode('utf-8'))
 
            elif comando == "/todos":  # Mensaje para todos los conectados
                difundir_mensaje(f"[{usuario}]: {argumento}", lista_clientes, lock_clientes)
 
            elif comando == "/repos":  # Guardar repositorios de un usuario de GitHub
                repos = obtener_repositorios(argumento)  # Consultamos la API de GitHub
                if not repos:  # None (falló) o lista vacía
                    conn.sendall("No se encontraron repositorios.".encode('utf-8'))
                else:
                    guardar_repositorios(argumento, repos)  # Los guardamos en MySQL
                    conn.sendall(f"Se guardaron {len(repos)} repositorios de {argumento}.".encode('utf-8'))
 
            elif comando == "/followers":  # Guardar followers de un usuario de GitHub
                followers = obtener_followers(argumento)  # Consultamos la API de GitHub
                if not followers:  # None (falló) o lista vacía
                    conn.sendall("No se encontraron followers.".encode('utf-8'))
                else:
                    guardar_followers(argumento, followers)  # Los guardamos en MySQL
                    conn.sendall(f"Se guardaron {len(followers)} followers de {argumento}.".encode('utf-8'))
 
            elif comando.startswith("/"):  # Empieza con "/" pero no es ninguno de los anteriores
                conn.sendall("Comando no reconocido.".encode('utf-8'))
 
            else:  # Texto normal: chat con el servidor
                print(f"[{usuario}] dice: {mensaje}")  # Se muestra en la consola del servidor
 
        except (ConnectionResetError, OSError):  # Si el cliente se cae de golpe
            break
 
    # 3. DESCONEXIÓN
    with lock_clientes:  # Bloqueamos la lista compartida
        lista_clientes.remove((conn, addr, usuario))  # Sacamos al cliente de los conectados
    conn.close()  # Cerramos el socket
    print(f"DESCONEXIÓN: El cliente {addr} se ha ido.")
 

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
