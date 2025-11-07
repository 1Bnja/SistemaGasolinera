// Initialize Lucide icons
lucide.createIcons();

// Conectar a WebSocket
const socket = io();

socket.on('connect', () => {
    console.log('Conectado a WebSocket del Distribuidor');
});

socket.on('disconnect', () => {
    console.log('Desconectado de WebSocket');
});

// Escuchar cambios de estado de surtidores
socket.on('surtidor_estado', (data) => {
    console.log('Cambio de estado de surtidor:', data);
    actualizarSurtidorEnTiempoReal(data);
});

// Escuchar nuevas transacciones
socket.on('nueva_transaccion', (data) => {
    console.log('Nueva transacción:', data);
    cargarTransacciones(); // Recargar tabla de transacciones
    cargarEstado(); // Actualizar total de transacciones
});

// Escuchar cambios de precios en tiempo real
socket.on('precios_actualizados', (data) => {
    console.log('Precios actualizados en tiempo real:', data);
    cargarEstado(); // Recargar para mostrar nuevos precios
});

// Obtener variables del window (pasadas desde el template HTML)
const distribuidorId = window.DISTRIBUIDOR_ID || '1';

async function cargarEstado() {
    try {
        const response = await fetch('/api/estado');
        const data = await response.json();

        // Status banner
        const banner = document.getElementById('status-banner');
        if (data.modo_autonomo) {
            banner.className = 'status-banner autonomo';
            banner.innerHTML = '<i data-lucide="alert-triangle"></i> Modo Autónomo - Sin conexión con Casa Matriz';
        } else {
            banner.className = 'status-banner conectado';
            banner.innerHTML = '<i data-lucide="wifi"></i> Conectado a Casa Matriz';
        }
        lucide.createIcons();

        // Surtidores
        const surtidoresHtml = data.surtidores.map(s => {
            const surtidorNum = s.id.split('.')[1];
            const estado = s.estado.toLowerCase().replace('_', '-');
            const iconEstado = s.estado === 'LIBRE' ? 'check-circle' : 'loader';
            return `
                <a href="/surtidor/${surtidorNum}" class="surtidor-card" data-surtidor-id="${s.id}">
                    <div class="surtidor-header">
                        <span class="surtidor-id">
                            <i data-lucide="fuel"></i>
                            Surtidor ${s.id}
                        </span>
                        <span class="surtidor-status ${estado}">
                            <i data-lucide="${iconEstado}"></i>
                            ${s.estado === 'LIBRE' ? 'Libre' : 'En operación'}
                        </span>
                    </div>
                </a>
            `;
        }).join('');
        document.getElementById('surtidores-grid').innerHTML = surtidoresHtml;
        lucide.createIcons();

        // Info del sistema
        const preciosLabels = {
            '93': 'Gasolina 93',
            '95': 'Gasolina 95',
            '97': 'Gasolina 97',
            'diesel': 'Diesel',
            'kerosene': 'Kerosene'
        };

        const infoHtml = `
            <div class="info-box">
                <div class="info-label">Total Transacciones</div>
                <div class="info-value">${data.total_transacciones}</div>
            </div>
            <div class="info-box">
                <div class="info-label">Precios Actuales</div>
                <div class="price-list">
                    ${Object.entries(data.precios).map(([tipo, precio]) => `
                        <div class="price-item">
                            <span class="price-label">${preciosLabels[tipo] || tipo.toUpperCase()}</span>
                            <span class="price-value">$${precio}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        document.getElementById('info-sistema').innerHTML = infoHtml;
    } catch (error) {
        console.error('Error:', error);
    }
}

function actualizarSurtidorEnTiempoReal(data) {
    const surtidorCard = document.querySelector(`[data-surtidor-id="${data.surtidor_id}"]`);
    if (!surtidorCard) return;

    const estado = data.estado.toLowerCase().replace('_', '-');
    const iconEstado = data.estado === 'LIBRE' ? 'check-circle' : 'loader';
    const textoEstado = data.estado === 'LIBRE' ? 'Libre' : 'En operación';

    const statusElement = surtidorCard.querySelector('.surtidor-status');
    if (statusElement) {
        statusElement.className = `surtidor-status ${estado}`;
        statusElement.innerHTML = `
            <i data-lucide="${iconEstado}"></i>
            ${textoEstado}
        `;
        lucide.createIcons();
    }
}

async function cargarTransacciones() {
    try {
        const response = await fetch('/api/transacciones?limit=10');
        const transacciones = await response.json();

        const labels = {
            '93': 'Gasolina 93',
            '95': 'Gasolina 95',
            '97': 'Gasolina 97',
            'diesel': 'Diesel',
            'kerosene': 'Kerosene'
        };

        const tbody = document.getElementById('transacciones-tbody');

        if (transacciones.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5">
                        <div class="empty-state">
                            <div class="empty-state-icon">
                                <i data-lucide="inbox"></i>
                            </div>
                            <p>No hay transacciones registradas</p>
                        </div>
                    </td>
                </tr>
            `;
            lucide.createIcons();
            return;
        }

        tbody.innerHTML = transacciones.map(t => `
            <tr>
                <td><strong>${t.surtidor_id}</strong></td>
                <td>${labels[t.tipo_combustible] || t.tipo_combustible.toUpperCase()}</td>
                <td>${t.litros.toFixed(2)}L</td>
                <td style="color: var(--success); font-weight: 600;">$${t.total.toLocaleString('es-CL')}</td>
                <td>${new Date(t.timestamp).toLocaleString('es-CL', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                })}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function cargarDatos() {
    await cargarEstado();
    await cargarTransacciones();
}

// Carga inicial
cargarDatos();

// Polling de respaldo cada 5 segundos (por si falla WebSocket)
setInterval(cargarDatos, 5000);
