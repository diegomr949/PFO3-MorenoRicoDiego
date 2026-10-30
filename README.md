# PFO 3: Rediseño como Sistema Distribuido (Cliente-Servidor)

**Materia:** Programación sobre Redes  
**Comisión:** E  
**Alumno:** Moreno Rico Diego Emilio  

---

## Arquitectura del Sistema
El siguiente diagrama detalla la infraestructura distribuida de la aplicación, contemplando la capa de presentación, el balanceador de carga, el cluster de workers para procesamiento, la cola de mensajes (RabbitMQ) y el almacenamiento persistente (PostgreSQL y Amazon S3).

![Diagrama de Arquitectura del Sistema](PFO3%20Diagrama.drawio.png)

## Implementación de Sockets y Workers
El proyecto incluye un servidor concurrente que implementa un `ThreadPoolExecutor` para procesar tareas en segundo plano sin bloquear el Event Loop principal, simulando el comportamiento de los nodos *workers* de la arquitectura distribuida.

### Instrucciones de Ejecución

1. **Iniciar el servidor:**
   Abrir una terminal en la raíz del proyecto y ejecutar:
   ```bash
   python servidor.py