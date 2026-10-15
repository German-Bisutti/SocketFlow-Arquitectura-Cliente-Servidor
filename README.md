# 🌐 SocketFlow: Arquitectura Cliente-Servidor

![Python](https://img.shields.io/badge/Python-3.14+-blue?style=for-the-badge&logo=python&logoColor=white)
![Sockets](https://img.shields.io/badge/Protocolo-TCP-success?style=for-the-badge)
![Threading](https://img.shields.io/badge/Concurrencia-Multihilo-orange?style=for-the-badge)

> Implementación de un servidor concurrente multihilo y cliente TCP en Python. Explorando el ciclo de vida de los sockets, la gestión de conexiones y el control de flujo en la Capa de Transporte.

Bienvenido a **SocketFlow**, un entorno de experimentación de red. Este proyecto demuestra cómo un servidor puede mantener su socket principal en modo escucha mientras genera hilos (threads) independientes con descriptores únicos para atender a múltiples clientes de forma simultánea sin bloquear la red.

## ✨ Características Destacadas

* **🤝 Concurrencia Real:** Soporte para múltiples conexiones en paralelo utilizando la librería nativa `threading`.
* **🛠️ Comandos Especiales Integrados:**
  * `/users`: Devuelve una lista dinámica con las direcciones IP y puertos de todos los clientes activos.
  * `/adios`: Permite una desconexión limpia, cerrando el túnel y actualizando los registros del servidor.
* **🛡️ Tolerancia a Fallos:** Manejo de excepciones (`ConnectionResetError`, `ConnectionAbortedError`) para evitar que el servidor colapse si un cliente cierra la terminal de manera abrupta.

## 🚀 Cómo probar el proyecto

Para ver la concurrencia en acción, necesitas ejecutar el servidor y múltiples clientes en terminales separadas.

### 1. Iniciar el Servidor
Abre una terminal en la ruta del proyecto y ejecuta:
```bash
python server.py