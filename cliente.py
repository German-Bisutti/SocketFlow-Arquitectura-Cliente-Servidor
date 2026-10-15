import socket

def funcion_cliente():
    host = "127.0.0.1" # Es la ip del servidor
    port = 5051 # Puerto en el que escucha el servidor
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creo el socket
    try: #Intento conectarme al servidor
    
        s.connect((host, port)) # conecto al servidor pasando la ip y el puerto
        print("Conectado al servidor")

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