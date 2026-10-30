import socket
from concurrent.futures import ThreadPoolExecutor
import time

HOST = '127.0.0.1'
PORT = 65432

def worker_procesar_tarea(conn, addr, tarea_datos):
    """
    Función que representa el Worker. 
    Se ejecuta en un hilo separado para no bloquear el servidor.
    """
    print(f"[Worker] Iniciando procesamiento para {addr}...")
    
    # Simulamos un procesamiento pesado (ej. compresión de imagen, cálculo)
    time.sleep(2) 
    
    resultado = f"Tarea '{tarea_datos}' procesada con éxito por el worker."
    
    try:
        conn.sendall(resultado.encode('utf-8'))
    except Exception as e:
        print(f"[-] Error enviando resultado a {addr}: {e}")
    finally:
        conn.close()
        print(f"[Worker] Conexión cerrada con {addr}.")

def iniciar_servidor():
    # Limitamos el pool a 5 workers (hilos) simultáneos
    with ThreadPoolExecutor(max_workers=5) as executor:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Permite reutilizar el puerto inmediatamente si se reinicia el script
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            
            print(f"[*] Servidor Master escuchando en {HOST}:{PORT}")
            print("[*] Esperando tareas de los clientes...\n")
            
            while True:
                # El hilo principal solo se encarga de aceptar conexiones
                conn, addr = s.accept()
                print(f"[Master] Nueva conexión recibida de {addr}")
                
                # Recibimos el payload inicial de la tarea
                datos = conn.recv(1024).decode('utf-8')
                
                if datos:
                    print(f"[Master] Tarea recibida: '{datos}'. Delegando al pool de workers...")
                    # Delegamos la conexión y los datos a un hilo worker disponible
                    executor.submit(worker_procesar_tarea, conn, addr, datos)

if __name__ == '__main__':
    iniciar_servidor()