import socket
import threading
VERDE = "\033[92m"  # mensajes correctos
ROJO = "\033[91m"  # errores
CIAN = "\033[96m"  # mensajes que llegan del servidor
AMARILLO = "\033[93m"  # títulos e información
RESET = "\033[0m"  # Vuelve al color normal
# FUNCION DEL HILO DE RECEPCION
# Se ejecuta independientemente para recibir mensajes del servidor.
def recibir_mensajes(s):
    while True: # Se repite siempre, escuchando al servidor
        try:
            # Esperamos recibir un mensaje del servidor
            mensaje = s.recv(8192).decode('utf-8') # Recibe hasta 8192 bytes y los pasa a texto

            # Si el mensaje está vacío, el servidor cerró la conexión
            if not mensaje:
                break

            # Mostramos el mensaje recibido
            print(f"\n{CIAN}{mensaje}{RESET}")
            print("> ", end="", flush=True)

        except OSError:
            break


def funcion_cliente():
    host = "127.0.0.1"  # IP del servidor
    port = 5051  # Puerto en el que escucha el servidor
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creo el socket

    try:
        # Intento conectarme al servidor
        s.connect((host, port)) # Se conecta a la IP y puerto del servidor

        print(f"{VERDE}Conectado al servidor{RESET}")
        print(f"\n{AMARILLO}=== AUTENTICACIÓN REQUERIDA ==={RESET}")
        print("Por favor, ingresa tus credenciales en el formato: usuario,contraseña")
        print("Ejemplo: admin,1234")

        credenciales = input("Credenciales: ")
        s.sendall(credenciales.encode('utf-8'))

        # Recibimos la respuesta de validación del servidor
        respuesta_login = s.recv(1024).decode('utf-8') # Esperamos la respuesta del login
        if "Error" in respuesta_login or "Formato" in respuesta_login:  # Si es un mensaje de error se muestra en rojo
            print(f"{ROJO}{respuesta_login}{RESET}")
        else:
            print(f"{VERDE}{respuesta_login}{RESET}") # Si no es error se muestra en verde

        # Si la autenticación falla, cerramos el cliente
        if "Error" in respuesta_login or "Formato" in respuesta_login:
            return

        print(f"\n{AMARILLO}--- INICIO DEL CHAT ---{RESET}")
        print("Comandos disponibles: /comandos, /usuarios, /hora, /todos, /repos, /followers, /adios\n")

        # Creamos un hilo para recibir mensajes del servidor
        hilo = threading.Thread(
            target=recibir_mensajes, # Función que va a ejecutar el hilo
            args=(s,), # Argumento que recibe esa función: el socket
            daemon=True # Se cierra solo cuando termina el programa
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
        print(f"{ROJO}No se pudo conectar al servidor (servidor rechazó la conexión).{RESET}")

    except OSError as e:
        print(f"{ROJO}Error de conexión: {e}{RESET}")

    finally:
        # Cerramos la conexión
        s.close()
        print("Conexión cerrada.")


funcion_cliente()
