import socket
import threading
# FUNCION DEL HILO DE RECEPCION
# Se ejecuta independientemente para recibir mensajes del servidor.
def recibir_mensajes(s):
    while True:
        try:
            # Esperamos recibir un mensaje del servidor
            mensaje = s.recv(1024).decode('utf-8')

            # Si el mensaje está vacío, el servidor cerró la conexión
            if not mensaje:
                break

            # Mostramos el mensaje recibido
            print(f"\n{mensaje}")
            print("> ", end="", flush=True)

        except OSError:
            break


def funcion_cliente():
    host = "127.0.0.1"  # IP del servidor
    port = 5051  # Puerto en el que escucha el servidor
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creo el socket

    try:
        # Intento conectarme al servidor
        s.connect((host, port))

        print("Conectado al servidor")
        print("\n=== AUTENTICACIÓN REQUERIDA ===")
        print("Por favor, ingresa tus credenciales en el formato: usuario,contraseña")
        print("Ejemplo: admin,1234")

        credenciales = input("Credenciales: ")
        s.sendall(credenciales.encode('utf-8'))

        # Recibimos la respuesta de validación del servidor
        respuesta_login = s.recv(1024).decode('utf-8')
        print(respuesta_login)

        # Si la autenticación falla, cerramos el cliente
        if "Error" in respuesta_login or "Formato" in respuesta_login:
            return

        print("\n--- INICIO DEL CHAT ---")
        print("Comandos disponibles: /usuarios, /adios\n")

        # Creamos un hilo para recibir mensajes del servidor
        hilo = threading.Thread(
            target=recibir_mensajes,
            args=(s,),
            daemon=True
        )

        # Iniciamos el hilo de recepción
        hilo.start()

        # Bucle principal para enviar mensajes al servidor
        while True:

            msg = input(">")

            # Enviamos el mensaje al servidor
            s.sendall(msg.encode('utf-8'))

            # Si el mensaje es /adios, salimos del bucle
            if msg.strip().lower() == "/adios":
                hilo.join()
                break

    except ConnectionRefusedError:
        print("No se pudo conectar al servidor (servidor rechazó la conexión).")

    except OSError as e:
        print(f"Error de conexión: {e}")

    finally:
        # Cerramos la conexión
        s.close()
        print("Conexión cerrada.")


funcion_cliente()
