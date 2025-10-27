import socket
import threading
import json
import time
import sqlite3
import os
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

DISTRIBUIDOR_ID = os.getenv('DISTRIBUIDOR_ID', '1')
CASA_MATRIZ_HOST = os.getenv('CASA_MATRIZ_HOST', 'casa-matriz')
CASA_MATRIZ_PORT = int(os.getenv('CASA_MATRIZ_PORT', '5001'))
TCP_PORT_LOCAL = int(os.getenv('TCP_PORT_LOCAL', '6000'))
WEB_PORT = int(os.getenv('WEB_PORT', '8000'))
HOST = '0.0.0.0'

COMBUSTIBLES = ['93', '95', '97', 'diesel', 'kerosene']

precios_actuales = {c: 0 for c in COMBUSTIBLES}
surtidores_conectados = {}
lock_surtidores = threading.Lock()
lock_db = threading.Lock()
conexion_casa_matriz = None
modo_autonomo = True

DB_PATH = f'/data/distribuidor_{DISTRIBUIDOR_ID}.db'
LOG_PATH = f'/data/transacciones_{DISTRIBUIDOR_ID}.log'


def init_database():
    with lock_db:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS surtidores (
                id TEXT PRIMARY KEY,
                estado TEXT DEFAULT 'LIBRE',
                litros_93 REAL DEFAULT 0,
                litros_95 REAL DEFAULT 0,
                litros_97 REAL DEFAULT 0,
                litros_diesel REAL DEFAULT 0,
                litros_kerosene REAL DEFAULT 0,
                cargas_93 INTEGER DEFAULT 0,
                cargas_95 INTEGER DEFAULT 0,
                cargas_97 INTEGER DEFAULT 0,
                cargas_diesel INTEGER DEFAULT 0,
                cargas_kerosene INTEGER DEFAULT 0,
                activo INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                surtidor_id TEXT,
                tipo_combustible TEXT,
                timestamp TEXT,
                litros REAL,
                precio_por_litro REAL,
                total REAL,
                sincronizado INTEGER DEFAULT 0,
                FOREIGN KEY (surtidor_id) REFERENCES surtidores(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS precios_historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_combustible TEXT,
                precio REAL,
                timestamp TEXT,
                origen TEXT
            )
        ''')
        
        for i in range(1, 5):
            surtidor_id = f"{DISTRIBUIDOR_ID}.{i}"
            cursor.execute(
                'INSERT OR IGNORE INTO surtidores (id) VALUES (?)',
                (surtidor_id,)
            )
        
        conn.commit()
        conn.close()
        print(f"Base de datos inicializada: {DB_PATH}")


def log_transaccion(transaccion):
    try:
        with open(LOG_PATH, 'a') as f:
            f.write(json.dumps(transaccion) + '\n')
    except Exception as e:
        print(f"Error escribiendo log: {e}")


def backup_database():
    while True:
        time.sleep(300)
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'/data/backup_distribuidor_{DISTRIBUIDOR_ID}_{timestamp}.db'
            
            with lock_db:
                conn = sqlite3.connect(DB_PATH)
                backup_conn = sqlite3.connect(backup_path)
                conn.backup(backup_conn)
                backup_conn.close()
                conn.close()
            
            print(f"Backup realizado: {backup_path}")
        except Exception as e:
            print(f"Error en backup: {e}")


def sincronizar_transacciones_pendientes():
    if not conexion_casa_matriz or modo_autonomo:
        return
    
    try:
        with lock_db:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, surtidor_id, tipo_combustible, timestamp, litros, precio_por_litro, total
                FROM transacciones
                WHERE sincronizado = 0
                ORDER BY timestamp
            ''')
            
            transacciones_pendientes = cursor.fetchall()
            
            if transacciones_pendientes:
                print(f"Sincronizando {len(transacciones_pendientes)} transacciones pendientes con Casa Matriz", flush=True)
                
                for row in transacciones_pendientes:
                    trans_id, surtidor_id, tipo_combustible, timestamp, litros, precio_por_litro, total = row
                    
                    mensaje = {
                        'tipo': 'reporte_transaccion',
                        'transaccion': {
                            'surtidor_id': surtidor_id,
                            'distribuidor_id': DISTRIBUIDOR_ID,
                            'tipo_combustible': tipo_combustible,
                            'timestamp': timestamp,
                            'litros': litros,
                            'precio_por_litro': precio_por_litro,
                            'total': total
                        }
                    }
                    
                    try:
                        conexion_casa_matriz.send(json.dumps(mensaje).encode('utf-8'))
                        cursor.execute('UPDATE transacciones SET sincronizado = 1 WHERE id = ?', (trans_id,))
                    except Exception as e:
                        print(f"Error sincronizando transacción {trans_id}: {e}", flush=True)
                        break
                
                conn.commit()
                print("Sincronización de transacciones completada", flush=True)
            
            conn.close()
    except Exception as e:
        print(f"Error en sincronización de transacciones: {e}", flush=True)


def conectar_casa_matriz():
    global conexion_casa_matriz, modo_autonomo
    
    while True:
        try:
            print(f"Intentando conectar con Casa Matriz {CASA_MATRIZ_HOST}:{CASA_MATRIZ_PORT}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((CASA_MATRIZ_HOST, CASA_MATRIZ_PORT))
            
            mensaje_registro = {
                'tipo': 'registro',
                'distribuidor_id': DISTRIBUIDOR_ID
            }
            sock.send(json.dumps(mensaje_registro).encode('utf-8'))
            
            conexion_casa_matriz = sock
            modo_autonomo = False
            print(f"Conectado a Casa Matriz", flush=True)
            
            sincronizar_transacciones_pendientes()
            
            while True:
                data = sock.recv(4096).decode('utf-8')
                if not data:
                    break
                
                mensaje = json.loads(data)
                procesar_mensaje_casa_matriz(mensaje)
                
        except Exception as e:
            print(f"Error conexión Casa Matriz: {e}", flush=True)
            modo_autonomo = True
            conexion_casa_matriz = None
            time.sleep(5)


def procesar_mensaje_casa_matriz(mensaje):
    tipo = mensaje.get('tipo')
    
    if tipo == 'actualizacion_precios':
        actualizar_precios_locales(mensaje['precios'])


def actualizar_precios_locales(precios_corporativos):
    global precios_actuales
    factor_utilidad = 1.05
    
    for combustible, precio in precios_corporativos.items():
        if combustible in COMBUSTIBLES:
            precio_local = int(precio * factor_utilidad)
            precios_actuales[combustible] = precio_local
            
            with lock_db:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO precios_historico (tipo_combustible, precio, timestamp, origen) VALUES (?, ?, ?, ?)',
                    (combustible, precio_local, datetime.now().isoformat(), 'casa_matriz')
                )
                conn.commit()
                conn.close()
    
    propagar_precios_surtidores()
    print(f"Precios actualizados: {precios_actuales}")


def propagar_precios_surtidores():
    mensaje = {
        'tipo': 'actualizacion_precios',
        'precios': precios_actuales,
        'timestamp': datetime.now().isoformat()
    }
    
    with lock_surtidores:
        for surtidor_id, surtidor in surtidores_conectados.items():
            try:
                surtidor['conn'].send(json.dumps(mensaje).encode('utf-8'))
                print(f"Precios enviados a Surtidor {surtidor_id}")
            except Exception as e:
                print(f"Error enviando a {surtidor_id}: {e}")


def handle_surtidor(conn, addr):
    surtidor_id = None
    try:
        data = conn.recv(1024).decode('utf-8')
        msg = json.loads(data)
        
        if msg['tipo'] == 'registro':
            surtidor_id = msg['surtidor_id']
            
            with lock_surtidores:
                surtidores_conectados[surtidor_id] = {
                    'conn': conn,
                    'addr': addr,
                    'estado': 'LIBRE'
                }
            
            print(f"Surtidor {surtidor_id} conectado")
            
            if precios_actuales['93'] > 0:
                mensaje_precios = {
                    'tipo': 'actualizacion_precios',
                    'precios': precios_actuales,
                    'timestamp': datetime.now().isoformat()
                }
                conn.send(json.dumps(mensaje_precios).encode('utf-8'))
            
            while True:
                data = conn.recv(4096).decode('utf-8')
                if not data:
                    break
                
                mensaje = json.loads(data)
                procesar_mensaje_surtidor(surtidor_id, mensaje)
                
    except Exception as e:
        print(f"Error con surtidor {surtidor_id}: {e}")
    finally:
        if surtidor_id:
            with lock_surtidores:
                if surtidor_id in surtidores_conectados:
                    del surtidores_conectados[surtidor_id]
                    print(f"Surtidor {surtidor_id} desconectado")
        conn.close()


def procesar_mensaje_surtidor(surtidor_id, mensaje):
    tipo = mensaje.get('tipo')
    
    if tipo == 'cambio_estado':
        with lock_surtidores:
            if surtidor_id in surtidores_conectados:
                surtidores_conectados[surtidor_id]['estado'] = mensaje['estado']
        
        with lock_db:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE surtidores SET estado = ? WHERE id = ?',
                (mensaje['estado'], surtidor_id)
            )
            conn.commit()
            conn.close()
    
    elif tipo == 'transaccion':
        registrar_transaccion(surtidor_id, mensaje['transaccion'])


def registrar_transaccion(surtidor_id, transaccion):
    with lock_db:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        tipo_combustible = transaccion['tipo_combustible']
        litros = transaccion['litros']
        precio = transaccion['precio_por_litro']
        total = transaccion['total']
        
        total_calculado = litros * precio
        if abs(total - total_calculado) > 1:
            print(f"ADVERTENCIA: Inconsistencia en transaccion. Total esperado: {total_calculado}, recibido: {total}")
            total = total_calculado
        
        cursor.execute('''
            INSERT INTO transacciones 
            (surtidor_id, tipo_combustible, timestamp, litros, precio_por_litro, total, sincronizado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            surtidor_id,
            tipo_combustible,
            transaccion['timestamp'],
            litros,
            precio,
            total,
            0
        ))
        
        transaccion_id = cursor.lastrowid
        
        cursor.execute(f'''
            UPDATE surtidores 
            SET litros_{tipo_combustible} = litros_{tipo_combustible} + ?,
                cargas_{tipo_combustible} = cargas_{tipo_combustible} + 1
            WHERE id = ?
        ''', (litros, surtidor_id))
        
        cursor.execute(f'SELECT litros_{tipo_combustible} FROM surtidores WHERE id = ?', (surtidor_id,))
        total_litros = cursor.fetchone()[0]
        
        conn.commit()
    
    log_transaccion({**transaccion, 'surtidor_id': surtidor_id, 'distribuidor_id': DISTRIBUIDOR_ID})
    
    if conexion_casa_matriz and not modo_autonomo:
        try:
            mensaje = {
                'tipo': 'reporte_transaccion',
                'transaccion': {**transaccion, 'surtidor_id': surtidor_id, 'distribuidor_id': DISTRIBUIDOR_ID}
            }
            conexion_casa_matriz.send(json.dumps(mensaje).encode('utf-8'))
            
            with lock_db:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('UPDATE transacciones SET sincronizado = 1 WHERE id = ?', (transaccion_id,))
                conn.commit()
                conn.close()
        except Exception as e:
            print(f"Error enviando transacción a Casa Matriz: {e}")
    
    conn.close()
    
    print(f"Transacción registrada: Surtidor {surtidor_id}, {tipo_combustible}, {litros:.2f}L, Total acumulado: {total_litros:.2f}L")


def servidor_tcp_local():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, TCP_PORT_LOCAL))
    server.listen(5)
    print(f"Servidor TCP Distribuidor {DISTRIBUIDOR_ID} escuchando en puerto {TCP_PORT_LOCAL}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_surtidor, args=(conn, addr))
        thread.daemon = True
        thread.start()


@app.route('/')
def index():
    return render_template('distribuidor.html', distribuidor_id=DISTRIBUIDOR_ID)


@app.route('/api/estado', methods=['GET'])
def get_estado():
    with lock_db:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM surtidores')
        surtidores = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT COUNT(*) as total FROM transacciones')
        total_trans = cursor.fetchone()['total']
        
        conn.close()
    
    return jsonify({
        'distribuidor_id': DISTRIBUIDOR_ID,
        'modo_autonomo': modo_autonomo,
        'precios': precios_actuales,
        'surtidores': surtidores,
        'total_transacciones': total_trans
    })


@app.route('/api/transacciones', methods=['GET'])
def get_transacciones():
    limit = request.args.get('limit', 50, type=int)
    
    with lock_db:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM transacciones ORDER BY id DESC LIMIT ?',
            (limit,)
        )
        transacciones = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
    
    return jsonify(transacciones)


@app.route('/api/transacciones/limpiar', methods=['POST'])
def limpiar_transacciones():
    try:
        with lock_db:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transacciones')
            conn.commit()
            conn.close()
        
        print(f"Base de datos limpiada - Distribuidor {DISTRIBUIDOR_ID}", flush=True)
        return jsonify({'status': 'success', 'message': 'Transacciones eliminadas'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    init_database()
    
    backup_thread = threading.Thread(target=backup_database)
    backup_thread.daemon = True
    backup_thread.start()
    
    cm_thread = threading.Thread(target=conectar_casa_matriz)
    cm_thread.daemon = True
    cm_thread.start()
    
    tcp_thread = threading.Thread(target=servidor_tcp_local)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    print(f"Servidor Web Distribuidor {DISTRIBUIDOR_ID} iniciando en puerto {WEB_PORT}")
    
    app.run(host=HOST, port=WEB_PORT, debug=False, threaded=True)
