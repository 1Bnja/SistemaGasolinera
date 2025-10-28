// Initialize Lucide icons
lucide.createIcons();

let preciosActuales = {};
const TIPOS_COMBUSTIBLE = ['93', '95', '97', 'diesel', 'kerosene'];

async function cargarPrecios() {
    try {
        const response = await fetch('/api/precios');
        const data = await response.json();
        preciosActuales = data;
        renderPrecios();
    } catch (error) {
        console.error('Error al cargar precios:', error);
    }
}

function renderPrecios() {
    const form = document.getElementById('precios-form');
    const labels = {
        '93': 'Gasolina 93',
        '95': 'Gasolina 95',
        '97': 'Gasolina 97',
        'diesel': 'Diesel',
        'kerosene': 'Kerosene'
    };
    
    form.innerHTML = TIPOS_COMBUSTIBLE.map(tipo => `
        <div class="precio-item">
            <span class="precio-label">${labels[tipo]}</span>
            <input type="number" id="precio-${tipo}" class="precio-input"
                   value="${preciosActuales[tipo] || 0}" step="1" min="0">
        </div>
    `).join('');
}

async function actualizarPrecios() {
    const nuevosPrecios = {};
    TIPOS_COMBUSTIBLE.forEach(tipo => {
        const input = document.getElementById(`precio-${tipo}`);
        nuevosPrecios[tipo] = parseFloat(input.value) || 0;
    });
    
    try {
        const response = await fetch('/api/precios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nuevosPrecios)
        });
        const result = await response.json();
        mostrarMensaje('mensaje-precios', 'Precios actualizados correctamente', 'success');
        await cargarDatos();
    } catch (error) {
        mostrarMensaje('mensaje-precios', 'Error al actualizar precios', 'error');
    }
}

async function cargarDistribuidores() {
    try {
        const response = await fetch('/api/distribuidores');
        const data = await response.json();
        const list = document.getElementById('distribuidores-list');
        const distributors = Array.isArray(data) ? data : [];
        
        if (distributors.length === 0) {
            list.innerHTML = '<p style="color: var(--text-tertiary); text-align: center; padding: 2rem;">No hay distribuidores conectados</p>';
            return;
        }
        
        list.innerHTML = distributors.map(d => `
            <div class="distribuidor-item">
                <div class="dist-header">
                    <span class="dist-id">
                        <i data-lucide="store"></i>
                        Distribuidor ${d.id}
                    </span>
                    <span class="dist-status ${d.activo ? 'activo' : 'inactivo'}">
                        <i data-lucide="${d.activo ? 'circle' : 'circle-off'}"></i>
                        ${d.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </div>
                <div class="dist-info">
                    ${d.surtidores || 4} surtidores • ${d.total_transacciones || 0} transacciones
                </div>
            </div>
        `).join('');
        
        lucide.createIcons();
    } catch (error) {
        console.error('Error al cargar distribuidores:', error);
    }
}

async function cargarEstadisticas() {
    try {
        const response = await fetch('/api/reporte');
        const data = await response.json();
        const trans = data.transacciones || [];
        
        document.getElementById('total-transacciones').textContent = trans.length;
        
        const totalLitros = trans.reduce((sum, t) => sum + (t.litros || 0), 0);
        document.getElementById('total-litros').textContent = totalLitros.toFixed(1);
        
        const totalIngresos = trans.reduce((sum, t) => sum + (t.total || 0), 0);
        document.getElementById('total-ingresos').textContent = `$${totalIngresos.toLocaleString('es-CL')}`;
        
        // Resumen por combustible
        const porCombustible = {};
        TIPOS_COMBUSTIBLE.forEach(tipo => {
            porCombustible[tipo] = { cantidad: 0, litros: 0, monto: 0 };
        });
        
        trans.forEach(t => {
            if (porCombustible[t.tipo_combustible]) {
                porCombustible[t.tipo_combustible].cantidad++;
                porCombustible[t.tipo_combustible].litros += t.litros || 0;
                porCombustible[t.tipo_combustible].monto += t.total || 0;
            }
        });
        
        const labels = {
            '93': 'Gasolina 93',
            '95': 'Gasolina 95',
            '97': 'Gasolina 97',
            'diesel': 'Diesel',
            'kerosene': 'Kerosene'
        };
        
        const summary = document.getElementById('fuel-summary');
        summary.innerHTML = '<div class="fuel-stats">' + TIPOS_COMBUSTIBLE.map(tipo => {
            const stats = porCombustible[tipo];
            const className = tipo.startsWith('9') ? 'g' + tipo : tipo;
            return `
                <div class="fuel-card ${className}">
                    <div class="fuel-type">${labels[tipo]}</div>
                    <div class="fuel-amount">${stats.cantidad}</div>
                    <div class="fuel-unit">${stats.litros.toFixed(1)}L • $${stats.monto.toLocaleString('es-CL')}</div>
                </div>
            `;
        }).join('') + '</div>';
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
    }
}

async function iniciarSimulacion() {
    try {
        const response = await fetch('/api/simulacion/global/iniciar', { method: 'POST' });
        const result = await response.json();
        mostrarMensaje('mensaje-simulacion', 'Simulación iniciada en todos los distribuidores', 'success');
        await actualizarEstadoSimulacion();
    } catch (error) {
        mostrarMensaje('mensaje-simulacion', 'Error al iniciar simulación', 'error');
    }
}

async function detenerSimulacion() {
    try {
        const response = await fetch('/api/simulacion/global/detener', { method: 'POST' });
        const result = await response.json();
        mostrarMensaje('mensaje-simulacion', 'Simulación detenida en todos los distribuidores', 'success');
        await actualizarEstadoSimulacion();
    } catch (error) {
        mostrarMensaje('mensaje-simulacion', 'Error al detener simulación', 'error');
    }
}

async function reiniciarSimulacion() {
    await detenerSimulacion();
    setTimeout(async () => {
        await iniciarSimulacion();
    }, 1000);
}

async function actualizarEstadoSimulacion() {
    try {
        const response = await fetch('/api/simulacion/global/estado');
        const data = await response.json();
        const statusDiv = document.getElementById('simulacion-status');
        const estados = data.estados || {};
        
        const estadosArray = Object.entries(estados).map(([key, activa]) => ({
            nombre: key.replace('distribuidor_', 'Distribuidor '),
            activa: activa
        }));
        
        if (estadosArray.length === 0) {
            statusDiv.innerHTML = '';
            return;
        }
        
        statusDiv.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem;">
                ${estadosArray.map(e => `
                    <div style="padding: 0.875rem; background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: 8px; text-align: center;">
                        <div style="font-size: 0.8125rem; color: var(--text-secondary); margin-bottom: 0.5rem;">${e.nombre}</div>
                        <div style="font-weight: 600; color: ${e.activa ? 'var(--success)' : 'var(--text-tertiary)'}; display: flex; align-items: center; justify-content: center; gap: 0.375rem;">
                            <i data-lucide="${e.activa ? 'play-circle' : 'pause-circle'}" style="width: 16px; height: 16px;"></i>
                            ${e.activa ? 'Activa' : 'Detenida'}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        lucide.createIcons();
    } catch (error) {
        console.error('Error al obtener estado:', error);
    }
}

async function confirmarBorrarDatos() {
    if (confirm('¿Estás seguro de borrar TODOS los datos? Esta acción no se puede deshacer.')) {
        try {
            const response = await fetch('/api/borrar-todos-datos', { method: 'POST' });
            const result = await response.json();
            mostrarMensaje('mensaje-borrar', 'Todos los datos han sido eliminados correctamente', 'success');
            await cargarDatos();
        } catch (error) {
            mostrarMensaje('mensaje-borrar', 'Error al borrar datos', 'error');
        }
    }
}

function mostrarMensaje(elementId, mensaje, tipo) {
    const elem = document.getElementById(elementId);
    elem.textContent = mensaje;
    elem.className = `mensaje ${tipo}`;
    elem.style.display = 'block';
    setTimeout(() => {
        elem.style.display = 'none';
    }, 4000);
}

async function cargarDatos() {
    await cargarPrecios();
    await cargarDistribuidores();
    await cargarEstadisticas();
    await actualizarEstadoSimulacion();
}

cargarDatos();
setInterval(cargarDatos, 3000);
