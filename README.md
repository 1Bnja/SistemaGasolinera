# Sistema de Gestión de Combustibles

Sistema distribuido de 2 niveles para la gestión integral de estaciones de servicio con sincronización en tiempo real.

## 🚀 Inicio Rápido

```bash
# 1. Levantar el sistema con Docker
docker-compose up --build

# 2. Abrir INDEX.html en tu navegador
# O acceder directamente a: http://localhost:5000
```

El sistema estará disponible en segundos. La página INDEX.html te permite navegar fácilmente entre todos los componentes.

## 📋 Requisitos

- Docker Desktop instalado
- Docker Compose
- Puertos disponibles: 5000-5001, 6001-6003, 8001-8003

## 🏗️ Arquitectura del Sistema

```
Casa Matriz (localhost:5000)
    ├── Distribuidor 1 (localhost:8001)
    │   ├── Surtidor 1.1, 1.2, 1.3, 1.4
    ├── Distribuidor 2 (localhost:8002)
    │   ├── Surtidor 2.1, 2.2, 2.3, 2.4
    └── Distribuidor 3 (localhost:8003)
        └── Surtidor 3.1, 3.2, 3.3, 3.4
```

**Comunicación:**
- Casa Matriz: Puerto TCP 5001
- Distribuidores: Puertos TCP 6001-6003
- Sincronización en tiempo real vía TCP Sockets

## ⛽ Tipos de Combustible

Cada surtidor maneja 5 tipos de combustible:
- **Gasolina 93, 95, 97**
- **Diesel**
- **Kerosene**

## 🎯 Características Principales

### Casa Matriz
- ✅ Actualización centralizada de precios
- ✅ Monitoreo de distribuidores conectados
- ✅ Estadísticas consolidadas en tiempo real
- ✅ Control global de simulación
- ✅ Reportes por tipo de combustible

### Distribuidores
- ✅ Modo autónomo (funciona sin conexión a Casa Matriz)
- ✅ Sincronización automática de precios
- ✅ Gestión de 4 surtidores cada uno
- ✅ Registro local de transacciones
- ✅ Base de datos SQLite con backups automáticos

### Surtidores
- ✅ Dispensado manual y automático
- ✅ Contadores acumulativos por combustible
- ✅ Estados: LIBRE / EN_OPERACIÓN
- ✅ Interfaz individual por surtidor

## 🌐 Acceso a las Interfaces

| Componente | URL | Descripción |
|------------|-----|-------------|
| **Página Principal** | `INDEX.html` | Panel de navegación completo |
| **Casa Matriz** | http://localhost:5000 | Control centralizado |
| **Distribuidor 1** | http://localhost:8001 | Gestión local + 4 surtidores |
| **Distribuidor 2** | http://localhost:8002 | Gestión local + 4 surtidores |
| **Distribuidor 3** | http://localhost:8003 | Gestión local + 4 surtidores |
| **Surtidores** | `/surtidor/1` hasta `/surtidor/4` | En cada distribuidor |

## 🛠️ Comandos Útiles

```bash
# Iniciar el sistema
docker-compose up --build

# Detener el sistema
docker-compose down

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar un componente específico
docker-compose restart casa-matriz
docker-compose restart distribuidor-1

# Limpiar todo (incluyendo datos)
docker-compose down -v
```

## 📁 Estructura del Proyecto

```
sistema-combustibles/
├── INDEX.html              # Página de navegación principal
├── docker-compose.yml      # Configuración de contenedores
├── requirements.txt        # Dependencias Python
├── casa_matriz/           # Aplicación central
│   ├── app.py            # Servidor Flask + TCP
│   ├── Dockerfile
│   ├── templates/        # Interfaz web
│   └── static/          # CSS y JavaScript
├── distribuidor/          # Aplicación distribuidor
│   ├── app.py            # Servidor Flask + TCP
│   ├── Dockerfile
│   ├── templates/        # Interfaces (distribuidor + surtidores)
│   └── static/          # CSS y JavaScript
└── README.md
```

## 🎨 Tecnologías

- **Backend:** Python 3.11 + Flask
- **Base de Datos:** SQLite
- **Comunicación:** TCP Sockets
- **Contenedores:** Docker + Docker Compose
- **Frontend:** HTML5 + CSS3 + JavaScript (Vanilla)
- **Iconos:** Lucide Icons

## 💡 Funcionalidades Especiales

### Simulación Automática
La Casa Matriz puede controlar la simulación automática de transacciones en todos los distribuidores:
- **Iniciar/Detener** simulación global
- **Monitoreo** del estado de cada distribuidor
- Transacciones aleatorias en surtidores disponibles

### Modo Autónomo
Los distribuidores continúan funcionando si pierden conexión con Casa Matriz:
- Mantienen últimos precios recibidos
- Registran transacciones localmente
- Sincronizan automáticamente al reconectar

### Persistencia de Datos
- Bases de datos SQLite independientes por nivel
- Backups automáticos cada 5 minutos
- Logs de transacciones en archivos `.log`

## 🐛 Solución de Problemas

**Si un puerto está ocupado:**
```bash
# Verificar puertos en uso
netstat -ano | findstr "5000"  # Windows
lsof -i :5000                   # Mac/Linux
```

**Si los contenedores no inician:**
```bash
# Reconstruir desde cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

**Si no hay conexión entre componentes:**
- Verificar que la red `fuel-network` esté activa
- Revisar logs: `docker-compose logs casa-matriz`

## 👥 Desarrollo

**Universidad de Talca**  
Proyecto 2 - Sistemas Distribuidos

---

**Nota:** Para la mejor experiencia, abre `INDEX.html` en tu navegador después de iniciar el sistema con Docker Compose. Desde ahí podrás navegar fácilmente entre todos los componentes.