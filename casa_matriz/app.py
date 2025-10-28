import socket
import threading
import json
import requests
import sqlite3
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

TCP_PORT = 5001
WEB_PORT = 5000
HOST = '0.0.0.0'
DB_PATH = '/data/casa_matriz.db'

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
lock_db = threading.Lock()


def init_database():
    with lock_db:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                distribuidor_id TEXT NOT NULL,
                surtidor_id TEXT NOT NULL,
                tipo_combustible TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                litros REAL NOT NULL,
                precio_por_litro REAL NOT NULL,
                total REAL NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS precios (
                combustible TEXT PRIMARY KEY,
                precio REAL NOT NULL,
                actualizado TEXT NOT NULL
            )
        ''')
        
        for combustible, precio in precios_actuales.items():
            cursor.execute('''
                INSERT OR REPLACE INTO precios (combustible, precio, actualizado)
                VALUES (?, ?, ?)
            ''', (combustible, precio, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    print("Base de datos Casa Matriz inicializada", flush=True)


def cargar_precios_db():
    global precios_actuales
    with lock_db:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT combustible, precio FROM precios')
        rows = cursor.fetchall()
        conn.close()
        
        if rows:
            for combustible, precio in rows:
                precios_actuales[combustible] = precio
            print(f"Precios cargados desde DB: {precios_actuales}", flush=True)


def guardar_transaccion_db(transaccion):
    with lock_db:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transacciones 
            (distribuidor_id, surtidor_id, tipo_combustible, timestamp, litros, precio_por_litro, total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaccion.get('distribuidor_id', ''),
            transaccion.get('surtidor_id', ''),
            transaccion['tipo_combustible'],
            transaccion['timestamp'],
            transaccion['litros'],
            transaccion['precio_por_litro'],
            transaccion['total']
        ))
        
        conn.commit()
        conn.close()


def obtener_transacciones_db():
    with lock_db:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT distribuidor_id, surtidor_id, tipo_combustible, timestamp, litros, precio_por_litro, total
            FROM transacciones
            ORDER BY timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        transacciones = []
        for row in rows:
            transacciones.append({
                'distribuidor_id': row[0],
                'surtidor_id': row[1],
                'tipo_combustible': row[2],
                'timestamp': row[3],
                'litros': row[4],
                'precio_por_litro': row[5],
                'total': row[6]
            })
        
        return transacciones


def actualizar_precios_db():
    with lock_db:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for combustible, precio in precios_actuales.items():
            cursor.execute('''
                INSERT OR REPLACE INTO precios (combustible, precio, actualizado)
                VALUES (?, ?, ?)
            ''', (combustible, precio, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()


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
        transaccion = mensaje['transaccion']
        with lock_distribuidores:
            if distribuidor_id in distribuidores_conectados:
                distribuidores_conectados[distribuidor_id].transacciones.append(transaccion)
        
        guardar_transaccion_db(transaccion)
        print(f"Transacción recibida y guardada de Distribuidor {distribuidor_id}")
    
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
        
        actualizar_precios_db()
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
    transacciones_db = obtener_transacciones_db()
    
    with lock_distribuidores:
        reporte = {
            'timestamp': datetime.now().isoformat(),
            'distribuidores_activos': sum(1 for d in distribuidores_conectados.values() if d.activo),
            'total_distribuidores': len(distribuidores_conectados),
            'ventas_por_combustible': {c: {'litros': 0, 'transacciones': 0, 'ingresos': 0} for c in COMBUSTIBLES},
            'transacciones': transacciones_db
        }
        
        for trans in transacciones_db:
            combustible = trans.get('tipo_combustible', 'desconocido')
            if combustible in reporte['ventas_por_combustible']:
                reporte['ventas_por_combustible'][combustible]['litros'] += trans.get('litros', 0)
                reporte['ventas_por_combustible'][combustible]['transacciones'] += 1
                reporte['ventas_por_combustible'][combustible]['ingresos'] += trans.get('total', 0)
        
        return jsonify(reporte)


@app.route('/api/borrar-todos-datos', methods=['POST'])
def borrar_todos_datos():
    try:
        with lock_db:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM transacciones')
            cursor.execute('DELETE FROM precios')
            
            for combustible, precio in precios_actuales.items():
                cursor.execute('''
                    INSERT INTO precios (combustible, precio, actualizado)
                    VALUES (?, ?, ?)
                ''', (combustible, precio, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
        
        with lock_distribuidores:
            for dist in distribuidores_conectados.values():
                dist.transacciones.clear()
        
        mensaje_broadcast = {
            'tipo': 'borrar_datos',
            'timestamp': datetime.now().isoformat()
        }
        
        with lock_distribuidores:
            for dist_id, dist in distribuidores_conectados.items():
                if dist.activo:
                    try:
                        dist.conn.send(json.dumps(mensaje_broadcast).encode('utf-8'))
                        print(f"Comando de borrado enviado a Distribuidor {dist_id}")
                    except Exception as e:
                        print(f"Error enviando comando de borrado a {dist_id}: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Todos los datos han sido borrados en Casa Matriz y se notificó a los distribuidores'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/simulacion/global/iniciar', methods=['POST'])
def iniciar_simulacion_global():
    try:
        import requests
        resultados = []
        
        for i in range(1, 4):
            try:
                url = f'http://distribuidor-{i}:8000/api/simulacion/iniciar'
                response = requests.post(url, timeout=2)
                result = response.json()
                resultados.append(f"Distribuidor {i}: {result.get('message', 'OK')}")
            except Exception as e:
                resultados.append(f"Distribuidor {i}: Error - {str(e)}")
        
        return jsonify({
            'status': 'success',
            'message': 'Comando de iniciar simulación enviado a todos los distribuidores',
            'resultados': resultados
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/simulacion/global/detener', methods=['POST'])
def detener_simulacion_global():
    try:
        import requests
        resultados = []
        
        for i in range(1, 4):
            try:
                url = f'http://distribuidor-{i}:8000/api/simulacion/detener'
                response = requests.post(url, timeout=2)
                result = response.json()
                resultados.append(f"Distribuidor {i}: {result.get('message', 'OK')}")
            except Exception as e:
                resultados.append(f"Distribuidor {i}: Error - {str(e)}")
        
        return jsonify({
            'status': 'success',
            'message': 'Comando de detener simulación enviado a todos los distribuidores',
            'resultados': resultados
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/simulacion/global/estado', methods=['GET'])
def estado_simulacion_global():
    try:
        import requests
        estados = {}
        
        for i in range(1, 4):
            try:
                url = f'http://distribuidor-{i}:8000/api/simulacion/estado'
                response = requests.get(url, timeout=2)
                result = response.json()
                estados[f'distribuidor_{i}'] = result.get('activa', False)
            except Exception as e:
                estados[f'distribuidor_{i}'] = False
        
        return jsonify({
            'estados': estados,
            'alguna_activa': any(estados.values())
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    init_database()
    cargar_precios_db()
    
    tcp_thread = threading.Thread(target=servidor_tcp)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    print(f"Servidor Web Casa Matriz iniciando en puerto {WEB_PORT}", flush=True)
    print(f"Acceder a: http://localhost:{WEB_PORT}", flush=True)
    
    app.run(host=HOST, port=WEB_PORT, debug=False, threaded=True)
