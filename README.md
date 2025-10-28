# Sistema de Gestión de Gasolineras# 🏢 Sistema Distribuido de Gestión de Combustibles



Sistema distribuido para la gestión de precios y transacciones de combustible con arquitectura Casa Matriz - Distribuidores - Surtidores.

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)

[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)](https://flask.palletsprojects.com/)

[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)](https://www.sqlite.org/)

## Características

- **Casa Matriz**: Control centralizado de precios y monitoreo de transacciones

- **3 Distribuidores**: Gestión local con modo autónomo> Sistema distribuido de tres capas para la gestión integral de estaciones de servicio con arquitectura de microservicios

- **12 Surtidores**: 4 por distribuidor, multifunción (5 tipos de combustible)

- **Sincronización en tiempo real** vía TCP sockets## 📋 Tabla de Contenidos

- **Persistencia de datos** con SQLite

- [Descripción](#-descripción)

## Tipos de Combustible- [Arquitectura](#-arquitectura)

- [Características](#-características)

- Gasolina 93- [Tecnologías](#-tecnologías)

- Gasolina 95- [Requisitos Previos](#-requisitos-previos)

- Gasolina 97- [Instalación](#-instalación)

- Diesel- [Uso](#-uso)

- Kerosene- [Estructura del Proyecto](#-estructura-del-proyecto)

- [Persistencia de Datos](#-persistencia-de-datos)

## Requisitos- [API](#-api)

- [Troubleshooting](#-troubleshooting)

- Docker- [Contribución](#-contribución)

- Docker Compose

## 🎯 Descripción

## Instalación y Uso

Sistema distribuido de **tres niveles jerárquicos** para la gestión completa de una cadena de estaciones de servicio. Maneja **5 tipos de combustible** con sincronización automática de precios, registro de transacciones y persistencia de datos.

```bash

# Iniciar el sistema### Tipos de Combustible

docker-compose up -d --build- 🔴 Gasolina 93

- 🟡 Gasolina 95  

# Detener el sistema- 🟢 Gasolina 97

docker-compose down- 🔵 Diesel

```- ⚪ Kerosene



## Acceso a Interfaces## 🏗️ Arquitectura



- **Casa Matriz**: http://localhost:5000```

- **Distribuidor 1**: http://localhost:8001┌─────────────────────────────────────────────────────────────┐

- **Distribuidor 2**: http://localhost:8002│                    🏢 CASA MATRIZ (Nivel 1)                 │

- **Distribuidor 3**: http://localhost:8003│                  Puerto Web: 5000 | TCP: 5001               │

│                                                              │

Desde cada distribuidor puedes acceder a sus 4 surtidores.│  • Gestión centralizada de precios                          │

│  • Reportes consolidados de ventas                          │

## Estructura del Proyecto│  • Monitoreo de distribuidores                              │

└──────────────────┬──────────────────┬───────────────────────┘

```                   │                  │

Proyecto2SD/         ┌─────────┴─────────┬────────┴─────────┐

├── casa_matriz/         │                   │                  │

│   ├── app.py┌────────▼────────┐ ┌────────▼────────┐ ┌──────▼──────────┐

│   └── templates/│ 🏪 DISTRIBUIDOR 1│ │ 🏪 DISTRIBUIDOR 2│ │ 🏪 DISTRIBUIDOR 3│

│       └── casa_matriz.html│ Web: 8001       │ │ Web: 8002       │ │ Web: 8003        │

├── distribuidor/│ TCP: 6001       │ │ TCP: 6002       │ │ TCP: 6003        │

│   ├── app.py│                 │ │                 │ │                  │

│   └── templates/│ • SQLite local  │ │ • SQLite local  │ │ • SQLite local   │

│       ├── distribuidor.html│ • 4 surtidores  │ │ • 4 surtidores  │ │ • 4 surtidores   │

│       └── surtidor.html└──┬───┬───┬───┬──┘ └──┬───┬───┬───┬──┘ └──┬───┬───┬───┬───┘

├── docker-compose.yml   │   │   │   │       │   │   │   │       │   │   │   │

└── README.md   ▼   ▼   ▼   ▼       ▼   ▼   ▼   ▼       ▼   ▼   ▼   ▼

```  ⛽  ⛽  ⛽  ⛽       ⛽  ⛽  ⛽  ⛽       ⛽  ⛽  ⛽  ⛽

 1.1 1.2 1.3 1.4    2.1 2.2 2.3 2.4    3.1 3.2 3.3 3.4

## Arquitectura9101 9102 9103 9104 9201 9202 9203 9204 9301 9302 9303 9304



- **Casa Matriz** (Puerto 5000): Servidor TCP en puerto 9999 para distribuidoresTotal: 16 Contenedores Docker | 12 Surtidores | 60 Tipos de Combustible

- **Distribuidores** (Puertos 8001-8003): Servidores TCP locales (puertos 7771-7773)```

- **Comunicación**: Sockets TCP con mensajes JSON

- **Base de datos**: SQLite independiente por componente### Flujo de Datos



## Funcionalidades```

┌──────────────┐    Actualización    ┌──────────────┐

### Casa Matriz│ Casa Matriz  │ ──────Precios──────>│ Distribuidor │

- Actualizar precios globales│              │<────Transacciones───│              │

- Ver distribuidores conectados└──────────────┘                     └───────┬──────┘

- Estadísticas en tiempo real                                             │

- Control de simulación                                      Sincronización

- Borrado de datos del sistema                                             │

                                     ┌───────▼──────┐

### Distribuidores                                     │   Surtidor   │

- Modo autónomo (sin Casa Matriz)                                     │              │

- Sincronización de precios                                     └──────────────┘

- Registro de transacciones```

- Gestión de 4 surtidores

## ✨ Características

### Surtidores

- Dispensado de combustible### 🔄 Sincronización

- Contadores acumulativos por tipo- ✅ Actualización automática de precios en cascada

- Estados: LIBRE / EN_OPERACION- ✅ Sincronización de transacciones con reintentos

- ✅ Recuperación automática ante desconexiones

## Tecnologías- ✅ Modo autónomo para distribuidores



- Python 3.11### 💾 Persistencia

- Flask- ✅ Base de datos SQLite en cada distribuidor

- SQLite- ✅ Volúmenes Docker para persistencia entre reinicios

- Docker- ✅ Sistema de backups automáticos cada 5 minutos

- TCP Sockets- ✅ Logs de transacciones en formato JSON


### 🖥️ Interfaces
- ✅ Interfaz web responsive para cada componente
- ✅ Navegación integrada entre niveles
- ✅ Actualización en tiempo real con polling
- ✅ Visualización de estadísticas y reportes

### 🔐 Validación
- ✅ Validación de integridad de transacciones
- ✅ Corrección automática de inconsistencias
- ✅ Tolerancia a fallos de 1 peso en totales

## 🛠️ Tecnologías

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| **Lenguaje** | Python | 3.11-slim |
| **Framework Web** | Flask | 3.0.0 |
| **Base de Datos** | SQLite | 3.x |
| **Servidor WSGI** | Werkzeug | 3.0.1 |
| **Comunicación** | TCP Sockets + HTTP/REST | - |
| **Contenedores** | Docker + Docker Compose | 20.10+ |
| **Formato de Datos** | JSON | - |

## 📦 Requisitos Previos

- **Docker Desktop** 20.10 o superior
- **Docker Compose** v2.0 o superior
- **Git** (para clonar el repositorio)
- **4GB RAM mínimo** (recomendado 8GB)
- **Puertos disponibles**: 5000-5001, 6001-6003, 8001-8003, 9101-9304

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/1Bnja/SistemaGasolinera.git
cd SistemaGasolinera
```

### 2. Construir e iniciar el sistema

```bash
# Construcción e inicio
docker-compose up -d --build

# Ver logs en tiempo real
docker-compose logs -f

# Verificar contenedores
docker-compose ps
```

### 3. Verificar funcionamiento

```bash
# Debería mostrar 16 contenedores corriendo
docker ps | findstr "proyecto2sd"
```

## 💻 Uso

### Inicio Rápido

1. **Abrir página principal**: `INDEX.html` en tu navegador
2. **Acceder a Casa Matriz**: http://localhost:5000
3. **Actualizar precios**:
   - Ingresar nuevos precios en la sección "Gestión de Precios"
   - Click en "Actualizar Precios"
   - Los cambios se propagan automáticamente

4. **Dispensar combustible**:
   - Acceder a cualquier surtidor (ej: http://localhost:9101)
   - Seleccionar tipo de combustible y cantidad
   - Click en "Dispensar"
   - La transacción se registra y sincroniza

### URLs de Acceso

#### Casa Matriz
- **Web**: http://localhost:5000
- **TCP**: localhost:5001

#### Distribuidores
| ID | Web | TCP |
|----|-----|-----|
| 1 | http://localhost:8001 | localhost:6001 |
| 2 | http://localhost:8002 | localhost:6002 |
| 3 | http://localhost:8003 | localhost:6003 |

#### Surtidores
| Distribuidor | Surtidores | Puertos |
|-------------|-----------|---------|
| 1 | 1.1 - 1.4 | 9101-9104 |
| 2 | 2.1 - 2.4 | 9201-9204 |
| 3 | 3.1 - 3.4 | 9301-9304 |

### Comandos Útiles

```bash
# Detener sistema (mantiene datos)
docker-compose down

# Detener y eliminar datos
docker-compose down -v

# Reiniciar un componente específico
docker-compose restart casa-matriz

# Ver logs de un componente
docker logs casa-matriz --tail 50 -f

# Acceder a la base de datos
docker exec distribuidor-1 sqlite3 /data/distribuidor_1.db "SELECT * FROM transacciones LIMIT 10"
```

## 📁 Estructura del Proyecto

```
SistemaGasolinera/
├── casa_matriz/
│   ├── Dockerfile
│   ├── app.py                 # Servidor principal
│   └── templates/
│       └── casa_matriz.html   # Interfaz web
├── distribuidor/
│   ├── Dockerfile
│   ├── app.py                 # Lógica del distribuidor
│   └── templates/
│       └── distribuidor.html  # Interfaz web
├── surtidor/
│   ├── Dockerfile
│   ├── app.py                 # Lógica del surtidor
│   └── templates/
│       └── surtidor.html      # Interfaz web
├── docker-compose.yml         # Orquestación de contenedores
├── requirements.txt           # Dependencias Python
├── INDEX.html                 # Página de navegación
├── .gitignore
└── README.md
```

## 💾 Persistencia de Datos

### Volúmenes Docker

```yaml
volumes:
  dist1-data:  # /data en distribuidor-1
  dist2-data:  # /data en distribuidor-2
  dist3-data:  # /data en distribuidor-3
```

### Bases de Datos

Cada distribuidor mantiene:

```
/data/
├── distribuidor_1.db          # Base de datos principal
├── distribuidor_1.db.backup   # Backup automático
└── transacciones_1.log        # Log de transacciones JSON
```

### Esquema de Tablas

**transacciones**
```sql
CREATE TABLE transacciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    surtidor_id TEXT,
    tipo_combustible TEXT,
    timestamp TEXT,
    litros REAL,
    precio_por_litro REAL,
    total REAL,
    sincronizado INTEGER DEFAULT 0
);
```

**surtidores**
```sql
CREATE TABLE surtidores (
    id TEXT PRIMARY KEY,
    estado TEXT DEFAULT 'LIBRE',
    litros_93 REAL DEFAULT 0,
    litros_95 REAL DEFAULT 0,
    -- ... (otros tipos)
    cargas_93 INTEGER DEFAULT 0,
    -- ... (contadores)
);
```

## 🔌 API

### Casa Matriz

#### Actualizar Precios
```http
POST /api/precios
Content-Type: application/json

{
  "93": 1500,
  "95": 1600,
  "97": 1700,
  "diesel": 1400,
  "kerosene": 1300
}
```

#### Obtener Reportes
```http
GET /api/reporte
Response: {
  "total_transacciones": 150,
  "ventas_por_combustible": {...},
  "total_ventas": 5000000
}
```

### Distribuidor

#### Registrar Transacción
```http
POST /api/transacciones
Content-Type: application/json

{
  "surtidor_id": "1.1",
  "tipo_combustible": "95",
  "litros": 40,
  "precio_por_litro": 1600,
  "total": 64000,
  "timestamp": "2025-10-26T12:00:00"
}
```

#### Limpiar Base de Datos
```http
POST /api/transacciones/limpiar
Response: { "message": "Base de datos limpiada", "registros_eliminados": 100 }
```

## 🐛 Troubleshooting

### Problema: Contenedores no inician

```bash
# Verificar logs
docker-compose logs casa-matriz

# Verificar puertos ocupados
netstat -ano | findstr "5000"

# Limpiar y reiniciar
docker-compose down -v
docker-compose up -d --build
```

### Problema: Distribuidores no conectan

```bash
# Verificar red Docker
docker network inspect proyecto2sd_fuel-network

# Reiniciar en orden
docker-compose restart casa-matriz
sleep 5
docker-compose restart distribuidor-1 distribuidor-2 distribuidor-3
```

### Problema: Datos no persisten

```bash
# Verificar volúmenes
docker volume ls | findstr "dist"

# NO usar -v al detener si quieres mantener datos
docker-compose down  # ✅ Mantiene datos
docker-compose down -v  # ❌ Borra datos
```

## 📊 Monitoreo

### Verificar Estado del Sistema

```bash
# Ver todos los contenedores
docker-compose ps

# Estadísticas de recursos
docker stats

# Ver transacciones en tiempo real
docker logs -f distribuidor-1 | findstr "Transacción"
```

### Consultar Base de Datos

```bash
# Total de transacciones
docker exec distribuidor-1 sqlite3 /data/distribuidor_1.db \
  "SELECT COUNT(*) FROM transacciones"

# Transacciones pendientes de sincronización
docker exec distribuidor-1 sqlite3 /data/distribuidor_1.db \
  "SELECT COUNT(*) FROM transacciones WHERE sincronizado = 0"

# Ventas por combustible
docker exec distribuidor-1 sqlite3 /data/distribuidor_1.db \
  "SELECT tipo_combustible, SUM(litros), SUM(total) FROM transacciones GROUP BY tipo_combustible"
```


