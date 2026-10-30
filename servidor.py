import itertools
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HOST = '127.0.0.1'
PORT = 65432                              # Puerto del Master (el que usa el cliente)
WORKER_PORTS = [65433, 65434, 65435]      # Un puerto por worker
HILOS_POR_WORKER = 3                      # Pool de hilos de cada worker
HILOS_MASTER = 20                         # Pool del master para atender clientes
TIMEOUT = 10                              # Segundos de espera máxima por socket
BUFFER = 1024



# Utilidades

def recibir_todo(conn):
    """Lee del socket hasta que el otro extremo cierra su lado de escritura."""
    partes = []
    while True:
        chunk = conn.recv(BUFFER)
        if not chunk:
            break
        partes.append(chunk)
    return b''.join(partes).decode('utf-8')



# Workers

def procesar_tarea(conn, addr, nombre_worker):
    """Se ejecuta en un hilo del pool del worker."""
    conn.settimeout(TIMEOUT)
    try:
        tarea = recibir_todo(conn)
        if not tarea:
            return

        hilo = threading.current_thread().name
        print(f"[{nombre_worker}] ({hilo}) Procesando: '{tarea}'")

        # Simulamos un procesamiento pesado (compresión, cálculo, etc.)
        time.sleep(2)

        resultado = f"Tarea '{tarea}' procesada con éxito por {nombre_worker}."
        conn.sendall(resultado.encode('utf-8'))
        print(f"[{nombre_worker}] ({hilo}) Tarea finalizada.")
    except Exception as e:
        print(f"[-] [{nombre_worker}] Error con {addr}: {e}")
    finally:
        conn.close()


def iniciar_worker(nombre, puerto):
    """Crea un worker: socket propio + pool de hilos propio."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, puerto))
    srv.listen()

    def bucle():
        pool = ThreadPoolExecutor(
            max_workers=HILOS_POR_WORKER,
            thread_name_prefix=f"{nombre}-hilo",
        )
        while True:
            conn, addr = srv.accept()
            pool.submit(procesar_tarea, conn, addr, nombre)

    threading.Thread(target=bucle, name=nombre, daemon=True).start()
    print(f"[*] {nombre} escuchando en {HOST}:{puerto} "
          f"(pool de {HILOS_POR_WORKER} hilos)")



# Master (balanceador / distribuidor)

_turno = itertools.cycle(range(len(WORKER_PORTS)))
_turno_lock = threading.Lock()


def siguiente_worker():
    with _turno_lock:
        return next(_turno)


def enviar_a_worker(indice, tarea):
    """Reenvía la tarea a un worker y devuelve su respuesta."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as w:
        w.settimeout(TIMEOUT)
        w.connect((HOST, WORKER_PORTS[indice]))
        w.sendall(tarea.encode('utf-8'))
        w.shutdown(socket.SHUT_WR)       # Indica fin de la tarea
        return recibir_todo(w)


def atender_cliente(conn, addr):
    """Recibe la tarea del cliente y la distribuye a un worker (Round-Robin)."""
    conn.settimeout(TIMEOUT)
    try:
        tarea = recibir_todo(conn)
        if not tarea:
            return
        print(f"[Master] Tarea de {addr}: '{tarea}'")

        inicio = siguiente_worker()
        respuesta = None

        # Si un worker está caído, se prueba con el siguiente
        for desplazamiento in range(len(WORKER_PORTS)):
            indice = (inicio + desplazamiento) % len(WORKER_PORTS)
            try:
                print(f"[Master] Delegando al Worker {indice + 1}...")
                respuesta = enviar_a_worker(indice, tarea)
                break
            except (ConnectionRefusedError, socket.timeout, OSError) as e:
                print(f"[-] [Master] Worker {indice + 1} no disponible: {e}")

        if respuesta is None:
            respuesta = "Error: ningún worker disponible."

        conn.sendall(respuesta.encode('utf-8'))
    except Exception as e:
        print(f"[-] [Master] Error con {addr}: {e}")
    finally:
        conn.close()


def iniciar_servidor():
    for i, puerto in enumerate(WORKER_PORTS, start=1):
        iniciar_worker(f"Worker {i}", puerto)

    with ThreadPoolExecutor(max_workers=HILOS_MASTER) as pool_master:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()

            print(f"[*] Master escuchando en {HOST}:{PORT}")
            print("[*] Esperando tareas de los clientes...\n")

            while True:
                # El hilo principal solo acepta conexiones
                conn, addr = s.accept()
                pool_master.submit(atender_cliente, conn, addr)


if __name__ == '__main__':
    try:
        iniciar_servidor()
    except KeyboardInterrupt:
        print("\n[*] Servidor detenido.")