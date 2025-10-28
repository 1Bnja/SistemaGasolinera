# Sistema de Gestión de Gasolineras# Sistema de Gestión de Combustibles



Sistema distribuido para gestión de precios y transacciones de combustible.Sistema distribuido de tres niveles para la gestión de estaciones de servicio con sincronización en tiempo real.



## Inicio Rápido## 🚀 Inicio Rápido



```bash```bash

docker-compose up -d --build# Clonar el repositorio

```git clone https://github.com/tu-usuario/sistema-combustibles.git

cd sistema-combustibles

Abrir `INDEX.html` en el navegador.

# Iniciar el sistema

## Requisitosdocker-compose up --build



- Docker# Acceder a la interfaz

- Docker Compose# Abrir INDEX.html en tu navegador

```

## Arquitectura

## 📋 Requisitos

```

Casa Matriz (Puerto 5000)- Docker Desktop

├── Distribuidor 1 (Puerto 8001) → 4 surtidores- Docker Compose

├── Distribuidor 2 (Puerto 8002) → 4 surtidores  - Puertos disponibles: 5000-5001, 6001-6003, 8001-8003

└── Distribuidor 3 (Puerto 8003) → 4 surtidores

```## 🏗️ Arquitectura



**Comunicación:** TCP Sockets (Puerto 9999 Casa Matriz, 7771-7773 Distribuidores)```

Casa Matriz (localhost:5000)

## Tipos de Combustible    ├── Distribuidor 1 (localhost:8001)

    │   ├── Surtidor 1.1

- Gasolina 93, 95, 97    │   ├── Surtidor 1.2

- Diesel    │   ├── Surtidor 1.3

- Kerosene    │   └── Surtidor 1.4

    ├── Distribuidor 2 (localhost:8002)

## Funcionalidades    │   └── ... 4 surtidores

    └── Distribuidor 3 (localhost:8003)

**Casa Matriz**        └── ... 4 surtidores

- Actualizar precios globalmente```

- Ver distribuidores conectados

- Estadísticas en tiempo real## 🎯 Características

- Control de simulación

- **Casa Matriz**: Control centralizado de precios

**Distribuidores**- **3 Distribuidores**: Gestión local con modo autónomo

- Modo autónomo- **12 Surtidores**: 5 tipos de combustible cada uno

- Sincronizar precios- **Sincronización TCP/IP** en tiempo real

- Registrar transacciones- **Persistencia SQLite** con backups automáticos

- Gestionar 4 surtidores

## 🌐 Acceso

**Surtidores**

- Dispensar combustible| Componente | URL |

- Contadores acumulativos|-----------|-----|

- Estados: LIBRE / EN_OPERACION| Página Principal | `INDEX.html` |

| Casa Matriz | http://localhost:5000 |

## Acceso| Distribuidor 1 | http://localhost:8001 |

| Distribuidor 2 | http://localhost:8002 |

- Casa Matriz: http://localhost:5000| Distribuidor 3 | http://localhost:8003 |

- Distribuidor 1: http://localhost:8001

- Distribuidor 2: http://localhost:8002## 🛠️ Comandos Útiles

- Distribuidor 3: http://localhost:8003

```bash

## Comandos# Detener el sistema

docker-compose down

```bash

# Detener# Ver logs

docker-compose downdocker-compose logs -f



# Ver logs# Reiniciar un componente

docker-compose logs -fdocker-compose restart casa-matriz



# Borrar datos# Borrar datos (incluye volúmenes)

docker-compose down -vdocker-compose down -v

``````



## Estructura## 📁 Estructura



``````

Proyecto2SD/.

├── casa_matriz/├── casa_matriz/          # Servidor central

│   ├── app.py│   ├── app.py

│   ├── static/│   └── templates/

│   │   ├── css/├── distribuidor/         # Servidores locales

│   │   └── js/│   ├── app.py

│   └── templates/│   └── templates/

├── distribuidor/├── docker-compose.yml    # Configuración Docker

│   ├── app.py└── INDEX.html           # Página de navegación

│   ├── static/```

│   │   ├── css/

│   │   └── js/## 🎨 Tecnologías

│   └── templates/

├── docker-compose.yml- Python 3.11

└── INDEX.html- Flask

```- SQLite

- Docker

## Tecnologías- TCP Sockets



- Python 3.11## 👥 Equipo

- Flask

- SQLiteUniversidad de Talca - Proyecto 2 Sistemas Distribuidos

- Docker

- TCP Sockets
