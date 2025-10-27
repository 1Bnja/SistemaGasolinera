import socket
import threading
import json
import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

TCP_PORT = 5001
WEB_PORT = 5000
HOST = '0.0.0.0'

COMBUSTIBLES = ['93', '95', '97', 'diesel', 'kerosene']

precios_actuales = {
    '93': 1450,
    '95': 1580,
    '97': 1690,
    'diesel': 1320,
    'kerosene': 1100
}

distribuidores_conectados = {}
lock_distribuidores = threading.Lock()


class DistribuidorConnection:
    def __init__(self, conn, addr, distribuidor_id):
        self.conn = conn
        self.addr = addr
        self.distribuidor_id = distribuidor_id
        self.ultima_conexion = datetime.now()
        self.activo = True
        self.surtidores = 4
        self.transacciones = []


def handle_distribuidor(conn, addr):
    distribuidor_id = None
    try:
        data = conn.recv(1024).decode('utf-8')
        msg = json.loads(data)
        
        if msg['tipo'] == 'registro':
            distribuidor_id = msg['distribuidor_id']
            
            with lock_distribuidores:
                distribuidores_conectados[distribuidor_id] = DistribuidorConnection(
                    conn, addr, distribuidor_id
                )
            
            print(f"Distribuidor {distribuidor_id} conectado desde {addr}", flush=True)
            
            enviar_precios(conn, distribuidor_id)
            
            while True:
                data = conn.recv(4096).decode('utf-8')
                if not data:
                    break
                
                mensaje = json.loads(data)
                procesar_mensaje_distribuidor(distribuidor_id, mensaje)
                
    except Exception as e:
        print(f"Error con distribuidor {distribuidor_id}: {e}")
    finally:
        if distribuidor_id:
            with lock_distribuidores:
                if distribuidor_id in distribuidores_conectados:
                    distribuidores_conectados[distribuidor_id].activo = False
                    print(f"Distribuidor {distribuidor_id} desconectado")
        conn.close()


def enviar_precios(conn, distribuidor_id):
    try:
        mensaje = {
            'tipo': 'actualizacion_precios',
            'precios': precios_actuales,
            'timestamp': datetime.now().isoformat()
        }
        conn.send(json.dumps(mensaje).encode('utf-8'))
        print(f"Precios enviados a Distribuidor {distribuidor_id}")
    except Exception as e:
        print(f"Error enviando precios a {distribuidor_id}: {e}")


def broadcast_precios():
    with lock_distribuidores:
        for dist_id, dist in distribuidores_conectados.items():
            if dist.activo:
                try:
                    enviar_precios(dist.conn, dist_id)
                except Exception as e:
                    print(f"Error broadcasting a {dist_id}: {e}")
                    dist.activo = False


def procesar_mensaje_distribuidor(distribuidor_id, mensaje):
    tipo = mensaje.get('tipo')
    
    if tipo == 'reporte_transaccion':
        with lock_distribuidores:
            if distribuidor_id in distribuidores_conectados:
                distribuidores_conectados[distribuidor_id].transacciones.append(mensaje['transaccion'])
        print(f"Transacción recibida de Distribuidor {distribuidor_id}")
    
    elif tipo == 'heartbeat':
        with lock_distribuidores:
            if distribuidor_id in distribuidores_conectados:
                distribuidores_conectados[distribuidor_id].ultima_conexion = datetime.now()


def servidor_tcp():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, TCP_PORT))
    server.listen(5)
    print(f"Servidor TCP Casa Matriz escuchando en puerto {TCP_PORT}", flush=True)
    
    while True:
        conn, addr = server.accept()
        print(f"Nueva conexión TCP desde {addr}", flush=True)
        thread = threading.Thread(target=handle_distribuidor, args=(conn, addr))
        thread.daemon = True
        thread.start()

@app.route('/')
def index():
    return render_template('casa_matriz.html')


@app.route('/api/precios', methods=['GET'])
def get_precios():
    return jsonify(precios_actuales)


@app.route('/api/precios', methods=['POST'])
def actualizar_precios():
    try:
        nuevos_precios = request.json
        
        for combustible in COMBUSTIBLES:
            if combustible in nuevos_precios:
                precios_actuales[combustible] = int(nuevos_precios[combustible])
        
        broadcast_precios()
        
        return jsonify({
            'status': 'success',
            'message': 'Precios actualizados y propagados',
            'precios': precios_actuales
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/distribuidores', methods=['GET'])
def get_distribuidores():
    with lock_distribuidores:
        distribuidores = []
        for dist_id, dist in distribuidores_conectados.items():
            distribuidores.append({
                'id': dist_id,
                'activo': dist.activo,
                'ultima_conexion': dist.ultima_conexion.isoformat(),
                'surtidores': dist.surtidores,
                'total_transacciones': len(dist.transacciones)
            })
        return jsonify(distribuidores)


@app.route('/api/reporte', methods=['GET'])
def generar_reporte():
    with lock_distribuidores:
        reporte = {
            'timestamp': datetime.now().isoformat(),
            'distribuidores_activos': sum(1 for d in distribuidores_conectados.values() if d.activo),
            'total_distribuidores': len(distribuidores_conectados),
            'ventas_por_combustible': {c: {'litros': 0, 'transacciones': 0, 'ingresos': 0} for c in COMBUSTIBLES},
            'transacciones': []
        }
        
        for dist in distribuidores_conectados.values():
            for trans in dist.transacciones:
                combustible = trans.get('tipo_combustible', 'desconocido')
                if combustible in reporte['ventas_por_combustible']:
                    reporte['ventas_por_combustible'][combustible]['litros'] += trans.get('litros', 0)
                    reporte['ventas_por_combustible'][combustible]['transacciones'] += 1
                    reporte['ventas_por_combustible'][combustible]['ingresos'] += trans.get('total', 0)
                
                reporte['transacciones'].append(trans)
        
        return jsonify(reporte)


if __name__ == '__main__':
    tcp_thread = threading.Thread(target=servidor_tcp)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    print(f"Servidor Web Casa Matriz iniciando en puerto {WEB_PORT}", flush=True)
    print(f"Acceder a: http://localhost:{WEB_PORT}", flush=True)
    
    app.run(host=HOST, port=WEB_PORT, debug=False, threaded=True)
