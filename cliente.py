import socket
import sys

HOST = '127.0.0.1'
PORT = 65432
TIMEOUT = 15
BUFFER = 1024


def enviar_tarea(tarea):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)
        try:
            s.connect((HOST, PORT))
            print(f"[*] Conectado al servidor {HOST}:{PORT}")

            s.sendall(tarea.encode('utf-8'))
            s.shutdown(socket.SHUT_WR)   # Avisa que terminó de enviar la tarea
            print(f"[*] Tarea enviada: '{tarea}'. Esperando resultado...")

            partes = []
            while True:
                chunk = s.recv(BUFFER)
                if not chunk:
                    break
                partes.append(chunk)

            resultado = b''.join(partes).decode('utf-8')
            print(f"[+] Resultado recibido: {resultado}")

        except ConnectionRefusedError:
            print("[-] Error: no se pudo conectar. Verificá que servidor.py esté corriendo.")
        except socket.timeout:
            print("[-] Error: el servidor tardó demasiado en responder.")


if __name__ == '__main__':
    mensaje = sys.argv[1] if len(sys.argv) > 1 else "Procesar lote de datos estándar"
    enviar_tarea(mensaje)