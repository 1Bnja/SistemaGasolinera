import socket
import threading
import json
import os
import time
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

SURTIDOR_ID = os.getenv('SURTIDOR_ID', '1.1')
DISTRIBUIDOR_HOST = os.getenv('DISTRIBUIDOR_HOST', 'distribuidor-1')
DISTRIBUIDOR_PORT = int(os.getenv('DISTRIBUIDOR_PORT', '6001'))
WEB_PORT = int(os.getenv('WEB_PORT', '9000'))
HOST = '0.0.0.0'

COMBUSTIBLES = ['93', '95', '97', 'diesel', 'kerosene']

estado_actual = 'LIBRE'
precios = {c: 0 for c in COMBUSTIBLES}
conexion_distribuidor = None
lock_estado = threading.Lock()

contadores = {
    combustible: {'litros': 0, 'cargas': 0, 'monto': 0}
    for combustible in COMBUSTIBLES
}


def conectar_distribuidor():
    global conexion_distribuidor
    
    while True:
        try:
            print(f"Conectando con Distribuidor {DISTRIBUIDOR_HOST}:{DISTRIBUIDOR_PORT}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((DISTRIBUIDOR_HOST, DISTRIBUIDOR_PORT))
            
            mensaje_registro = {
                'tipo': 'registro',
                'surtidor_id': SURTIDOR_ID
            }
            sock.send(json.dumps(mensaje_registro).encode('utf-8'))
            
            conexion_distribuidor = sock
            print(f"Conectado a Distribuidor")
            
            while True:
                data = sock.recv(4096).decode('utf-8')
                if not data:
                    break
                
                mensaje = json.loads(data)
                procesar_mensaje_distribuidor(mensaje)
                
        except Exception as e:
            print(f"Error conexión Distribuidor: {e}")
            conexion_distribuidor = None
            time.sleep(5)


def procesar_mensaje_distribuidor(mensaje):
    global precios
    tipo = mensaje.get('tipo')
    
    if tipo == 'actualizacion_precios':
        if estado_actual == 'LIBRE':
            precios = mensaje['precios']
            print(f"Precios actualizados: {precios}")
        else:
            print(f"Precios pendientes (surtidor EN_OPERACION)")


def notificar_cambio_estado(nuevo_estado):
    global estado_actual
    
    with lock_estado:
        estado_actual = nuevo_estado
    
    if conexion_distribuidor:
        try:
            mensaje = {
                'tipo': 'cambio_estado',
                'estado': nuevo_estado,
                'surtidor_id': SURTIDOR_ID,
                'timestamp': datetime.now().isoformat()
            }
            conexion_distribuidor.send(json.dumps(mensaje).encode('utf-8'))
            print(f"Estado cambiado a: {nuevo_estado}")
        except Exception as e:
            print(f"Error notificando estado: {e}")


def enviar_transaccion(transaccion):
    if conexion_distribuidor:
        try:
            mensaje = {
                'tipo': 'transaccion',
                'transaccion': transaccion
            }
            conexion_distribuidor.send(json.dumps(mensaje).encode('utf-8'))
            print(f"Transacción enviada: {transaccion}")
        except Exception as e:
            print(f"Error enviando transacción: {e}")


def simular_dispensado(tipo_combustible, litros):
    global estado_actual
    
    notificar_cambio_estado('EN_OPERACION')
    
    time.sleep(2)
    
    precio_por_litro = precios.get(tipo_combustible, 0)
    total = litros * precio_por_litro
    
    transaccion = {
        'tipo_combustible': tipo_combustible,
        'litros': litros,
        'precio_por_litro': precio_por_litro,
        'total': total,
        'timestamp': datetime.now().isoformat(),
        'surtidor_id': SURTIDOR_ID
    }
    
    contadores[tipo_combustible]['litros'] += litros
    contadores[tipo_combustible]['cargas'] += 1
    contadores[tipo_combustible]['monto'] += total
    
    enviar_transaccion(transaccion)
    
    notificar_cambio_estado('LIBRE')
    
    return transaccion


@app.route('/')
def index():
    distribuidor_id = SURTIDOR_ID.split('-')[0] if '-' in SURTIDOR_ID else SURTIDOR_ID.split('.')[0]
    return render_template('surtidor.html', 
                          surtidor_id=SURTIDOR_ID,
                          distribuidor_id=distribuidor_id)


@app.route('/api/estado', methods=['GET'])
def get_estado():
    return jsonify({
        'surtidor_id': SURTIDOR_ID,
        'estado': estado_actual,
        'precios': precios,
        'contadores': contadores
    })


@app.route('/api/dispensar', methods=['POST'])
def dispensar():
    try:
        data = request.json
        tipo_combustible = data.get('tipo_combustible')
        litros = float(data.get('litros', 0))
        
        if tipo_combustible not in COMBUSTIBLES:
            return jsonify({'status': 'error', 'message': 'Tipo de combustible inválido'}), 400
        
        if litros <= 0:
            return jsonify({'status': 'error', 'message': 'Cantidad de litros inválida'}), 400
        
        if estado_actual != 'LIBRE':
            return jsonify({'status': 'error', 'message': 'Surtidor no disponible'}), 400
        
        def _dispensar():
            simular_dispensado(tipo_combustible, litros)
        
        thread = threading.Thread(target=_dispensar)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': f'Dispensando {litros}L de {tipo_combustible}'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    dist_thread = threading.Thread(target=conectar_distribuidor)
    dist_thread.daemon = True
    dist_thread.start()
    
    print(f"Servidor Web Surtidor {SURTIDOR_ID} iniciando en puerto {WEB_PORT}", flush=True)
    
    app.run(host=HOST, port=WEB_PORT, debug=False, threaded=True)
