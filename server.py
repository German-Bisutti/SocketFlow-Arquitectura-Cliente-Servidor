import socket
import threading
import mysql.connector
# HILO PARA HABLAR CON EL SERVIDOR
# Permite que el servidor escriba mensajes desde la consola y los envíe a todos los clientes conectados.

def enviar_mensajes(lista_clientes, lock_clientes):
    while True:
        mensaje = input("\nServidor: ")

        # Obtenemos una copia de los clientes conectados
        with lock_clientes:
            clientes = lista_clientes.copy()

        if not clientes:
            print("No hay clientes conectados.")
            continue

        # Enviamos el mensaje a todos los clientes
        for cliente_conn, cliente_addr, nombre_usr in clientes:
            try:
                cliente_conn.sendall(
                    f"Servidor: {mensaje}".encode('utf-8')
                )
            except OSError:
                print(f"No se pudo enviar el mensaje a {nombre_usr}.")


# FUNCION DEL HILO DE CADA CLIENTE
def manejar_cliente(conn, addr, lista_clientes, lock_clientes):

    print(f"\nNUEVA CONEXIÓN: {addr}")

    db = None
    cursor = None
    usuario = None
    autenticado = False

    try:
        # 1. RECIBIR CREDENCIALES
        credenciales = conn.recv(1024).decode('utf-8')

        # Validar formato
        if not credenciales or "," not in credenciales:
            conn.sendall(
                "Formato incorrecto. Debes enviar: usuario,contraseña".encode('utf-8')
            )
            return

        usuario_ingresado, pass_ingresada = credenciales.split(",", 1)

        usuario = usuario_ingresado.strip()

        # 2. CONEXION A MYSQL
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="redes_tp_final"
        )

        cursor = db.cursor()

        # 3. VALIDAR CREDENCIALES
        sql = """SELECT * FROM usuarios WHERE nombre_usuario = %s AND contrasena = %s """

        cursor.execute(sql, (usuario, pass_ingresada.strip()))
        resultado = cursor.fetchone()

        if resultado:
            conn.sendall(
                "¡Bienvenido al servidor! Autenticación exitosa.".encode('utf-8')
            )

            # Agregamos al cliente autenticado a la lista
            with lock_clientes:
                lista_clientes.append((conn, addr, usuario))

            autenticado = True

            print(f"[{addr}] Autenticado como: {usuario}")

        else:
            conn.sendall(
                "Error: Usuario o contraseña incorrectos. Desconectando...".encode('utf-8')
            )
            print(f"[{addr}] Autenticación fallida.")
            return

    except Exception as e:
        print(f"[{addr}] Error durante la autenticación: {e}")

        try:
            conn.sendall(
                "Error interno del servidor en la autenticación.".encode('utf-8')
            )
        except OSError:
            pass

        return

    finally:
        # Cerramos la conexión a MySQL
        if cursor is not None:
            cursor.close()

        if db is not None and db.is_connected():
            db.close()

    # 4. RECEPCION DE MENSAJES DEL CLIENTE
    while True:
        try:
            mensaje = conn.recv(1024).decode('utf-8')

            if not mensaje:
                break

            comando = mensaje.strip().lower()

            # COMANDO /ADIOS
            if comando == "/adios":
                conn.sendall(
                    "Hasta luego. Te has desconectado del servidor.".encode('utf-8')
                )
                print(f"[{addr}] Solicitó desconectarse.")
                break

            # COMANDO /USUARIOS
            elif comando == "/usuarios" or comando == "/users":

                print(f"[{addr}] Solicitó la lista de usuarios.")

                lista_str = "Usuarios conectados actualmente:\n"

                with lock_clientes:
                    clientes = lista_clientes.copy()

                for cliente_conn, cliente_addr, nombre_usr in clientes:
                    lista_str += f"- {nombre_usr} ({cliente_addr})\n"

                conn.sendall(lista_str.encode('utf-8'))

            else:
                # RESPUESTA ECO (provisoria)
                print(f"[{usuario}] dice: {mensaje}")

                conn.sendall(f"Eco: {mensaje}".encode('utf-8'))

        except (ConnectionResetError, OSError):
            break

    # 5. ELIMINAR CLIENTE DE LA LISTA
    if autenticado:
        with lock_clientes:
            for cliente in lista_clientes:
                if cliente[0] == conn:
                    lista_clientes.remove(cliente)
                    break

    conn.close()

    print(f"\nDESCONEXIÓN: El cliente {addr} se ha ido.")

    with lock_clientes:
        cantidad = len(lista_clientes)

    print(f"CLIENTES ACTIVOS: Quedan {cantidad} cliente(s).")


# FUNCION PRINCIPAL DEL SERVIDOR
def iniciar_servidor():

    # 1. CREAR SOCKET DEL SERVIDOR
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(('localhost', 5051))

    server.listen()

    # Lista compartida de clientes autenticados
    clientes_activos = []

    # Candado para proteger la lista compartida
    lock_clientes = threading.Lock()

    print("INICIO: Servidor escuchando en el puerto 5051...")

    # 2. CREAR HILO DE ENVIO DEL SERVIDOR
    hilo_envio = threading.Thread(
        target=enviar_mensajes,
        args=(clientes_activos, lock_clientes),
        daemon=True
    )

    hilo_envio.start()

    # 3. ACEPTAR NUEVOS CLIENTES
    while True:

        conn, addr = server.accept()

        # Creamos un hilo para atender a cada cliente
        hilo = threading.Thread(
            target=manejar_cliente,
            args=(conn, addr, clientes_activos, lock_clientes)
        )

        hilo.start()


if __name__ == "__main__":
    iniciar_servidor()
