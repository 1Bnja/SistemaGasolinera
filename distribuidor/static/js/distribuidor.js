// Initialize Lucide icons
        lucide.createIcons();
        
        const distribuidorId = '{{ distribuidor_id }}';
        
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
                        <a href="/surtidor/${surtidorNum}" class="surtidor-card">
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
        
        cargarDatos();
        setInterval(cargarDatos, 2000);