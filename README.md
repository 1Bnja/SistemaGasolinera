# Sistema de Gestión de Combustibles

Sistema distribuido de tres niveles para la gestión de estaciones de servicio con sincronización en tiempo real.

## 🚀 Inicio Rápido

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/sistema-combustibles.git
cd sistema-combustibles

# Iniciar el sistema
docker-compose up --build

# Acceder a la interfaz
# Abrir INDEX.html en tu navegador
```

## 📋 Requisitos

- Docker Desktop
- Docker Compose
- Puertos disponibles: 5000-5001, 6001-6003, 8001-8003

## 🏗️ Arquitectura

```
Casa Matriz (localhost:5000)
    ├── Distribuidor 1 (localhost:8001)
    │   ├── Surtidor 1.1
    │   ├── Surtidor 1.2
    │   ├── Surtidor 1.3
    │   └── Surtidor 1.4
    ├── Distribuidor 2 (localhost:8002)
    │   └── ... 4 surtidores
    └── Distribuidor 3 (localhost:8003)
        └── ... 4 surtidores
```

## 🎯 Características

- **Casa Matriz**: Control centralizado de precios
- **3 Distribuidores**: Gestión local con modo autónomo
- **12 Surtidores**: 5 tipos de combustible cada uno
- **Sincronización TCP/IP** en tiempo real
- **Persistencia SQLite** con backups automáticos

## 🌐 Acceso

| Componente | URL |
|-----------|-----|
| Página Principal | `INDEX.html` |
| Casa Matriz | http://localhost:5000 |
| Distribuidor 1 | http://localhost:8001 |
| Distribuidor 2 | http://localhost:8002 |
| Distribuidor 3 | http://localhost:8003 |

## 🛠️ Comandos Útiles

```bash
# Detener el sistema
docker-compose down

# Ver logs
docker-compose logs -f

# Reiniciar un componente
docker-compose restart casa-matriz

# Borrar datos (incluye volúmenes)
docker-compose down -v
```

## 📁 Estructura

```
.
├── casa_matriz/          # Servidor central
│   ├── app.py
│   └── templates/
├── distribuidor/         # Servidores locales
│   ├── app.py
│   └── templates/
├── docker-compose.yml    # Configuración Docker
└── INDEX.html           # Página de navegación
```

## 🎨 Tecnologías

- Python 3.11
- Flask
- SQLite
- Docker
- TCP Sockets

## 👥 Equipo

Universidad de Talca - Proyecto 2 Sistemas Distribuidos

