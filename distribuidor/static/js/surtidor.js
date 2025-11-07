// Initialize Lucide icons
lucide.createIcons();

// Conectar a WebSocket
const socket = io();

socket.on('connect', () => {
    console.log('Conectado a WebSocket del Surtidor');
});

socket.on('disconnect', () => {
    console.log('Desconectado de WebSocket');
});

// Obtener variables del window (pasadas desde el template HTML)
const surtidorId = window.SURTIDOR_ID;
const surtidorNum = surtidorId.split('.')[1];
let estadoActual = 'LIBRE';
const labels = {
    '93': 'Gasolina 93',
    '95': 'Gasolina 95',
    '97': 'Gasolina 97',
    'diesel': 'Diesel',
    'kerosene': 'Kerosene'
};

// Escuchar cambios de estado de surtidores en tiempo real
socket.on('surtidor_estado', (data) => {
    if (data.surtidor_id === surtidorId) {
        console.log('Cambio de estado en tiempo real:', data);
        actualizarEstadoEnTiempoReal(data.estado);
    }
});

// Escuchar nuevas transacciones para actualizar contadores
socket.on('nueva_transaccion', (data) => {
    if (data.surtidor_id === surtidorId) {
        console.log('Nueva transacción en este surtidor:', data);
        cargarEstado(); // Recargar para actualizar contadores
    }
});

function actualizarEstadoEnTiempoReal(nuevoEstado) {
    estadoActual = nuevoEstado;

    const display = document.getElementById('estado-display');
    const estadoClean = nuevoEstado.toLowerCase().replace('_', '-');

    if (nuevoEstado === 'LIBRE') {
        display.innerHTML = '<i data-lucide="check-circle"></i> LIBRE';
    } else {
        display.innerHTML = '<i data-lucide="loader"></i> EN OPERACIÓN';
    }

    display.className = `estado-display estado-${estadoClean}`;
    lucide.createIcons();

    // Update button
    const btn = document.getElementById('btn-dispensar');
    btn.disabled = nuevoEstado !== 'LIBRE';
}

async function cargarEstado() {
    try {
        const response = await fetch(`/api/surtidor/${surtidorNum}/estado`);
        const data = await response.json();

        estadoActual = data.estado;

        // Update estado display
        const display = document.getElementById('estado-display');
        const estadoClean = data.estado.toLowerCase().replace('_', '-');

        if (data.estado === 'LIBRE') {
            display.innerHTML = '<i data-lucide="check-circle"></i> LIBRE';
        } else {
            display.innerHTML = '<i data-lucide="loader"></i> EN OPERACIÓN';
        }

        display.className = `estado-display estado-${estadoClean}`;
        lucide.createIcons();

        // Update button
        const btn = document.getElementById('btn-dispensar');
        btn.disabled = data.estado !== 'LIBRE';

        // Update contadores
        if (data.contadores) {
            const html = Object.entries(data.contadores).map(([tipo, stats]) => `
                <div class="contador-card">
                    <div class="contador-valor">${(stats.litros || 0).toFixed(1)}</div>
                    <div class="contador-label">${labels[tipo] || tipo}</div>
                </div>
            `).join('');
            document.getElementById('contadores-grid').innerHTML = html;
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function cargarPrecios() {
    try {
        const response = await fetch('/api/estado');
        const data = await response.json();
        const precios = data.precios || {};

        const html = Object.entries(precios).map(([tipo, precio]) => `
            <div class="precio-card">
                <span class="precio-label">${labels[tipo] || tipo}</span>
                <span class="precio-valor">$${precio}</span>
            </div>
        `).join('');

        document.getElementById('precios-grid').innerHTML = html;
    } catch (error) {
        console.error('Error:', error);
    }
}

async function dispensar() {
    const tipo = document.getElementById('tipo-combustible').value;
    const litros = parseFloat(document.getElementById('litros').value);

    if (!litros || litros <= 0) {
        mostrarMensaje('Ingrese una cantidad válida de litros', 'error');
        return;
    }

    if (litros > 100) {
        mostrarMensaje('La cantidad máxima es 100 litros', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/surtidor/${surtidorNum}/dispensar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo_combustible: tipo, litros: litros })
        });

        const result = await response.json();

        if (response.ok) {
            mostrarMensaje(`Dispensando ${litros}L de ${labels[tipo]}...`, 'success');
        } else {
            mostrarMensaje(result.message || 'Error al dispensar', 'error');
        }
    } catch (error) {
        mostrarMensaje('Error de conexión con el servidor', 'error');
    }
}

function mostrarMensaje(texto, tipo) {
    const msg = document.getElementById('mensaje');
    msg.textContent = texto;
    msg.className = `mensaje ${tipo}`;
    msg.style.display = 'block';
    setTimeout(() => {
        msg.style.display = 'none';
    }, 4000);
}

async function cargarDatos() {
    await cargarEstado();
    await cargarPrecios();
}

// Carga inicial
cargarDatos();

// Polling de respaldo cada 5 segundos (por si falla WebSocket)
setInterval(cargarEstado, 5000);
setInterval(cargarPrecios, 10000);
