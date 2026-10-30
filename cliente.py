import socket
import sys

HOST = '127.0.0.1'
PORT = 65432

def enviar_tarea(tarea):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"[*] Conectado al servidor {HOST}:{PORT}")
            
            # Enviar la tarea al servidor
            s.sendall(tarea.encode('utf-8'))
            print(f"[*] Tarea enviada: '{tarea}'. Esperando resultado...")
            
            # Bloquea hasta recibir la respuesta del worker
            datos = s.recv(1024)
            print(f"[+] Resultado recibido del servidor: {datos.decode('utf-8')}")
            
        except ConnectionRefusedError:
            print("[-] Error: No se pudo conectar. Verifica que servidor.py esté corriendo.")

if __name__ == '__main__':
    # Permite enviar la tarea como argumento por consola. Ej: python cliente.py "Generar PDF"
    mensaje = sys.argv[1] if len(sys.argv) > 1 else "Procesar lote de datos estándar"
    enviar_tarea(mensaje)