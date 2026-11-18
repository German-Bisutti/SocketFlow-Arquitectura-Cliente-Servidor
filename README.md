# Chat Cliente-Servidor TCP con MySQL

Trabajo Práctico Integrador de Programación sobre Redes.

Autor: [Tu nombre y apellido]

## De qué se trata

Es un chat hecho con sockets TCP en Python. Un servidor atiende a varios clientes al mismo tiempo (un hilo por cada uno) y los usuarios tienen que loguearse antes de poder usarlo. Las credenciales se validan contra una base de datos MySQL.

Además del chat, el servidor entiende algunos comandos que empiezan con `/`. Dos de ellos consultan la API pública de GitHub y guardan lo que encuentran en la base de datos.

## Qué hay que tener instalado

- Python 3
- XAMPP (para tener MySQL andando en localhost)
- Dos librerías de Python:

```bash
pip install mysql-connector-python requests
```

`socket`, `threading`, `hashlib` y `datetime` vienen con Python, no hace falta instalarlas.

## Preparar la base de datos

1. Abrir XAMPP y arrancar el módulo **MySQL**.
2. Entrar a phpMyAdmin (`http://localhost/phpmyadmin`), ir a la pestaña SQL y ejecutar esto:

```sql
CREATE DATABASE redes_tp_final;
USE redes_tp_final;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL,
    contrasena VARCHAR(64) NOT NULL
);

CREATE TABLE repositorios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100),
    nombre_repo VARCHAR(255),
    url_repo VARCHAR(255),
    fecha_guardado DATETIME
);

CREATE TABLE followers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100),
    nombre_follower VARCHAR(100),
    fecha_guardado DATETIME
);

INSERT INTO usuarios (nombre_usuario, contrasena)
VALUES ('admin', SHA2('1234', 256));
```

Las contraseñas **no se guardan en texto plano**: en la tabla va el hash SHA-256 y el servidor compara contra ese hash. Por eso se usa `SHA2(..., 256)` al insertar. Para crear otro usuario es lo mismo:

```sql
INSERT INTO usuarios (nombre_usuario, contrasena)
VALUES ('maria', SHA2('abcd', 256));
```

## Cómo ejecutarlo

Hacen falta como mínimo dos terminales abiertas en la carpeta del proyecto.

**Terminal 1: servidor**

```bash
python server.py
```

Tiene que aparecer `INICIO: Servidor escuchando en el puerto 5051...`

**Terminal 2 (y las que quieras): cliente**

```bash
python cliente.py
```

El cliente pide las credenciales con el formato `usuario,contraseña`:

```
Credenciales: admin,1234
```

Si son correctas, el servidor responde con un mensaje de bienvenida y ya se puede escribir. Si son incorrectas, avisa y cierra la conexión.

Para probar el multihilo, abrir una tercera terminal con otro cliente y entrar con otro usuario.

## Credenciales de prueba

| Usuario | Contraseña |
|---------|------------|
| admin   | 1234       |

## Comandos

Todo mensaje que empiece con `/` se toma como comando. Si no empieza con `/`, es un mensaje de chat para el servidor.

| Comando | Qué hace |
|---------|----------|
| `/usuarios` | Muestra los usuarios conectados en ese momento |
| `/hora` | Devuelve la fecha y hora del servidor |
| `/todos <mensaje>` | Manda el mensaje a todos los demás clientes conectados |
| `/repos <usuario>` | Busca los repositorios públicos de ese usuario de GitHub y los guarda en la tabla `repositorios` |
| `/followers <usuario>` | Busca los followers de ese usuario de GitHub y los guarda en la tabla `followers` |
| `/adios` | Se despide y cierra la conexión |

Ejemplos:

```
> /hora
> /todos Hola a todos
> /repos German-Bisutti
> /followers German-Bisutti
> /adios
```

Cosas a tener en cuenta:

- `/repos` y `/followers` traen como máximo 100 resultados y en pantalla se muestran los primeros 20. En la base se guardan todos los que trajo.
- La API de GitHub sin autenticar permite unas 60 consultas por hora. Si da error de golpe, probablemente sea por eso.
- `/todos` no se lo manda a quien lo escribe, solo a los demás.

## Cómo funciona

**Servidor.** Crea un socket TCP en el puerto 5051 y se queda esperando conexiones con `accept()`. Cada vez que entra un cliente se crea un hilo nuevo que se ocupa solo de ese cliente, así el socket principal puede seguir aceptando a otros sin bloquearse. Hay además un hilo extra que lee lo que escribe el administrador en la consola del servidor y se lo manda a todos los clientes.

**Autenticación.** Lo primero que hace el cliente es mandar `usuario,contraseña`. El servidor hashea la contraseña con SHA-256, busca esa combinación en la tabla `usuarios` y, si existe, agrega al cliente a la lista de conectados. Si no existe, le avisa y cierra el socket.

**Cliente.** Tiene un hilo aparte que escucha todo el tiempo lo que manda el servidor. Gracias a eso se pueden recibir mensajes (por ejemplo un `/todos` de otro usuario) mientras uno está escribiendo, sin que el `input()` bloquee la recepción.

**Lista de conectados.** Es una lista compartida entre todos los hilos con tuplas `(socket, dirección, nombre de usuario)`. Se usa para `/usuarios`, `/todos` y para los mensajes del administrador.

**Desconexión.** Con `/adios`, o si el cliente cierra la terminal de golpe, el servidor lo saca de la lista y cierra su socket sin afectar a los demás.

## Estructura del proyecto

```
.
├── server.py     # Servidor concurrente
├── cliente.py    # Cliente
└── README.md
```

## Problemas comunes

- **`Can't connect to MySQL server`**: MySQL no está iniciado en XAMPP.
- **`Usuario o contraseña incorrectos` con credenciales que sí existen**: la contraseña en la tabla no está hasheada. Hay que insertarla con `SHA2('...', 256)`.
- **`ConnectionRefusedError` en el cliente**: el servidor no está corriendo todavía, o no es el mismo puerto.
- **`Address already in use` al abrir el servidor**: quedó otro servidor abierto en el puerto 5051. Cerrarlo y volver a probar.
