# 🏢 Sistema Distribuido de Gestión de Combustibles

[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)](https://www.sqlite.org/)

> Sistema distribuido de tres capas para la gestión integral de estaciones de servicio con arquitectura de microservicios

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Persistencia de Datos](#-persistencia-de-datos)
- [API](#-api)
- [Troubleshooting](#-troubleshooting)
- [Contribución](#-contribución)

## 🎯 Descripción

Sistema distribuido de **tres niveles jerárquicos** para la gestión completa de una cadena de estaciones de servicio. Maneja **5 tipos de combustible** con sincronización automática de precios, registro de transacciones y persistencia de datos.

### Tipos de Combustible
- 🔴 Gasolina 93
- 🟡 Gasolina 95  
- 🟢 Gasolina 97
- 🔵 Diesel
- ⚪ Kerosene

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    🏢 CASA MATRIZ (Nivel 1)                 │
│                  Puerto Web: 5000 | TCP: 5001               │
│                                                              │
│  • Gestión centralizada de precios                          │
│  • Reportes consolidados de ventas                          │
│  • Monitoreo de distribuidores                              │
└──────────────────┬──────────────────┬───────────────────────┘
                   │                  │
         ┌─────────┴─────────┬────────┴─────────┐
         │                   │                  │
┌────────▼────────┐ ┌────────▼────────┐ ┌──────▼──────────┐
│ 🏪 DISTRIBUIDOR 1│ │ 🏪 DISTRIBUIDOR 2│ │ 🏪 DISTRIBUIDOR 3│
│ Web: 8001       │ │ Web: 8002       │ │ Web: 8003        │
│ TCP: 6001       │ │ TCP: 6002       │ │ TCP: 6003        │
│                 │ │                 │ │                  │
│ • SQLite local  │ │ • SQLite local  │ │ • SQLite local   │
│ • 4 surtidores  │ │ • 4 surtidores  │ │ • 4 surtidores   │
└──┬───┬───┬───┬──┘ └──┬───┬───┬───┬──┘ └──┬───┬───┬───┬───┘
   │   │   │   │       │   │   │   │       │   │   │   │
   ▼   ▼   ▼   ▼       ▼   ▼   ▼   ▼       ▼   ▼   ▼   ▼
  ⛽  ⛽  ⛽  ⛽       ⛽  ⛽  ⛽  ⛽       ⛽  ⛽  ⛽  ⛽
 1.1 1.2 1.3 1.4    2.1 2.2 2.3 2.4    3.1 3.2 3.3 3.4
9101 9102 9103 9104 9201 9202 9203 9204 9301 9302 9303 9304

Total: 16 Contenedores Docker | 12 Surtidores | 60 Tipos de Combustible
```

### Flujo de Datos

```
┌──────────────┐    Actualización    ┌──────────────┐
│ Casa Matriz  │ ──────Precios──────>│ Distribuidor │
│              │<────Transacciones───│              │
└──────────────┘                     └───────┬──────┘
                                             │
                                      Sincronización
                                             │
                                     ┌───────▼──────┐
                                     │   Surtidor   │
                                     │              │
                                     └──────────────┘
```

## ✨ Características

### 🔄 Sincronización
- ✅ Actualización automática de precios en cascada
- ✅ Sincronización de transacciones con reintentos
- ✅ Recuperación automática ante desconexiones
- ✅ Modo autónomo para distribuidores

### 💾 Persistencia
- ✅ Base de datos SQLite en cada distribuidor
- ✅ Volúmenes Docker para persistencia entre reinicios
- ✅ Sistema de backups automáticos cada 5 minutos
- ✅ Logs de transacciones en formato JSON

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

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es parte del curso de Sistemas Distribuidos de la Universidad de Talca.

## 👥 Autores

- **Desarrollador Principal**: [@1Bnja](https://github.com/1Bnja)

## 🙏 Agradecimientos

- Universidad de Talca - Facultad de Ingeniería
- Curso de Sistemas Distribuidos
- Comunidad de Docker y Flask

---

**⭐ Si este proyecto te fue útil, considera darle una estrella en GitHub**
