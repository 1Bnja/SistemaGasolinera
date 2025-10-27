# Sistema Distribuido de Gestión de Combustibles
## Proyecto 2 - Sistemas Distribuidos - Universidad de Talca

### Descripción
Sistema distribuido de tres niveles para la gestión de estaciones de servicio con 5 tipos de combustible:
- Gasolina 93
- Gasolina 95
- Gasolina 97
- Diesel
- Kerosene

### Arquitectura
```
                          🏢 Casa Matriz (Nivel 3)
                        TCP: 5001 | Web: 5000
                                  |
                ┌─────────────────┼─────────────────┐
                |                 |                 |
         🏪 Distribuidor 1   Distribuidor 2   Distribuidor 3
          TCP: 6001           TCP: 6002         TCP: 6003
          Web: 8001           Web: 8002         Web: 8003
                |                 |                 |
        ┌───┬───┼───┬───   ───┬───┼───┬───   ───┬───┼───┬───
        |   |   |   |       |   |   |   |       |   |   |   |
       ⛽  ⛽  ⛽  ⛽        ⛽  ⛽  ⛽  ⛽        ⛽  ⛽  ⛽  ⛽
      1.1 1.2 1.3 1.4     2.1 2.2 2.3 2.4     3.1 3.2 3.3 3.4
     9101-9104           9201-9204           9301-9304

    Cada surtidor maneja 5 tipos de combustible:
    93, 95, 97, Diesel, Kerosene
```

### Tecnologías
- **Lenguaje**: Python 3.11
- **Framework Web**: Flask
- **Base de Datos**: SQLite
- **Comunicación**: TCP Sockets + HTTP/REST
- **Contenedores**: Docker + Docker Compose
- **Formato de Datos**: JSON

### Puertos
- **Casa Matriz**: 
  - Web: 5000
  - TCP: 5001
- **Distribuidores**:
  - Distribuidor 1: Web 8001, TCP 6001
  - Distribuidor 2: Web 8002, TCP 6002
  - Distribuidor 3: Web 8003, TCP 6003
- **Surtidores**: 9101-9304 (12 surtidores)

### Instalación y Ejecución

1. **Iniciar el sistema completo**:
   ```bash
   docker-compose up --build
   ```

2. **Acceder a las interfaces**:
   - **Página de Navegación Principal**: Abre `INDEX.html` en tu navegador
   - **Casa Matriz**: http://localhost:5000
   - **Distribuidores**:
     - Distribuidor 1: http://localhost:8001
     - Distribuidor 2: http://localhost:8002
     - Distribuidor 3: http://localhost:8003
   - **Surtidores**: http://localhost:9101 a http://localhost:9304

3. **Ver todas las URLs**: Consulta `URLS_ACCESO.md` para el listado completo

### Navegación en el Sistema

El sistema incluye navegación integrada:
- **Desde Casa Matriz**: Enlaces directos a los 3 distribuidores
- **Desde Distribuidores**: Enlace a Casa Matriz + enlaces a sus 4 surtidores
- **Desde Surtidores**: Enlace de retorno a su distribuidor padre

### Documentación Adicional
- **GUIA_USO.md**: Guía detallada de uso del sistema
- **INICIO_RAPIDO.md**: Guía de inicio rápido
- **SCRIPTS.md**: Scripts útiles para operación
- **URLS_ACCESO.md**: Listado completo de URLs e IPs
- **INDEX.html**: Página de navegación visual con enlaces a todos los componentes

### Características Principales
- ✅ Actualización centralizada de precios para 5 combustibles
- ✅ Operación autónoma de distribuidores
- ✅ Persistencia con SQLite
- ✅ Respaldo dual (DB + logs)
- ✅ Sincronización automática
- ✅ Interfaces web interactivas con navegación integrada
- ✅ Arquitectura completamente contenedorizada
- ✅ 16 contenedores coordinados (1 Casa Matriz + 3 Distribuidores + 12 Surtidores)
