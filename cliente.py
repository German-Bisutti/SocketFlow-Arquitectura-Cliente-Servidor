import socket

def funcion_cliente():
    host = "127.0.0.1" # Es la ip del servidor
    port = 5051 # Puerto en el que escucha el servidor
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creo el socket
    try: #Intento conectarme al servidor
    
        s.connect((host, port)) # conecto al servidor pasando la ip y el puerto
        print("Conectado al servidor")
        print("\n=== AUTENTICACIÓN REQUERIDA ===")
        print("Por favor, ingresa tus credenciales en el formato: usuario,contraseña")
        print("Ejemplo: admin,1234")
        credenciales = input("Credenciales: ")
        s.send(credenciales.encode('utf-8'))

        # Recibimos la respuesta de validación del servidor
        respuesta_login = s.recv(1024).decode('utf-8')
        print(respuesta_login)
        # Si la autenticación falla, cerramos el cliente
        if "Error" in respuesta_login or "Formato" in respuesta_login:
            s.close()
            return

        print("\n--- INICIO DEL CHAT ---")
        print("Comandos disponibles: /users (para ver usuarios), /adios (para salir)\n")
        
        while True: #Bucle infinito para enviar y recibir mensajes
            msg = input(">")   #ingreso el mensaje por teclado
            s.send(msg.encode('utf-8')) #mando el mensaje 
            if msg.strip().lower() == "/adios": # Si el mensaje es /adios o /ADIOS o " /adios " (con espacios)
                break # Cierro la conexion y salgo del bucle
            msg = s.recv(1024).decode('utf-8') # Recibo el mensaje del servidor y lo decodifico
            print(msg) # Imprimo el mensaje recibido del servidor

    except ConnectionRefusedError: # Si el servidor no está corriendo o no acepta conexiones
        print("No se pudo conectar al servidor(sevidor rechazo la conexion)")
    finally: # Cierro la conexion
         s.close()
         print("Conexión cerrada.")
funcion_cliente()