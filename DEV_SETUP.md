# Predictly Markets - Entorno de Desarrollo

## Infraestructura Docker Compose

Este proyecto utiliza Docker Compose para orquestar todos los servicios necesarios en desarrollo:
- **PostgreSQL 16**: Base de datos principal
- **Redis 7**: Cache y sesiones
- **Backend FastAPI**: API REST en Python
- **Frontend Next.js**: Interfaz de usuario en React/TypeScript

## Requisitos Previos

- Docker >= 20.x
- Docker Compose >= 2.x
- Node.js >= 20.x (para instalar dependencias del frontend localmente)

## Instalación y Uso

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd Predictlymarkets
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Las variables por defecto funcionan para desarrollo local. Puedes modificar `.env` según necesites.

### 3. Instalar dependencias del frontend (requerido)

Debido a limitaciones con npm en contenedores, las dependencias del frontend deben instalarse localmente:

```bash
cd frontend
npm install
cd ..
```

### 4. Levantar todos los servicios

```bash
docker compose up -d
```

Este comando:
- Construye las imágenes de backend y frontend
- Levanta PostgreSQL y Redis con healthchecks
- Espera a que los servicios estén healthy antes de iniciar backend/frontend
- Monta el código fuente para hot-reload

### 5. Verificar que todo funcione

```bash
# Ver logs de todos los servicios
docker compose logs

# Ver logs específicos
docker compose logs backend
docker compose logs frontend

# Verificar estado de servicios
docker compose ps
```

Deberías ver:
```
✅ Successfully connected to PostgreSQL database
✅ Successfully connected to Redis
```

### 6. Acceder a los servicios

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432 (usuario: `predictly`, password: `predictly_dev_password`, db: `predictly_db`)
- **Redis**: localhost:6379

## Desarrollo

### Hot Reload

Ambos servicios soportan hot-reload:

- **Backend**: Uvicorn detecta cambios en `/app` y reinicia automáticamente
- **Frontend**: Next.js Turbopack detecta cambios y recarga en el navegador

Simplemente edita los archivos y guarda para ver los cambios.

### Ejecutar comandos dentro de los contenedores

```bash
# Backend - ejecutar migraciones, tests, etc
docker compose exec backend python -m pytest

# Frontend - ejecutar linters, builds, etc
docker compose exec frontend npm run lint

# PostgreSQL - acceder a la consola
docker compose exec postgres psql -U predictly -d predictly_db

# Redis - acceder a la CLI
docker compose exec redis redis-cli
```

### Ver logs en tiempo real

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f  # todos los servicios
```

## Detener los servicios

```bash
# Detener sin eliminar volúmenes
docker compose down

# Detener y eliminar volúmenes (limpia la DB)
docker compose down -v
```

## Reconstruir imágenes

Si cambias dependencias (pyproject.toml, package.json):

```bash
# Reconstruir todo
docker compose build

# Reconstruir solo un servicio
docker compose build backend
docker compose build frontend

# Forzar reconstrucción sin cache
docker compose build --no-cache
```

## Troubleshooting

### Error: "Cannot connect to PostgreSQL"

Verifica que el healthcheck esté OK:
```bash
docker compose ps
```

Si postgres no está "healthy", revisa los logs:
```bash
docker compose logs postgres
```

### Error: "Redis connection failed"

Similar al anterior, verifica:
```bash
docker compose logs redis
```

### Frontend no inicia correctamente

Asegúrate de haber instalado dependencias localmente:
```bash
cd frontend
npm install
cd ..
docker compose restart frontend
```

### Cambios en el código no se reflejan

1. Verifica que el volumen esté montado correctamente:
   ```bash
   docker compose exec backend ls -la /app
   ```

2. Reinicia el servicio:
   ```bash
   docker compose restart backend
   ```

### Limpiar todo y empezar de cero

```bash
docker compose down -v
docker system prune -a
cd frontend && rm -rf node_modules && npm install && cd ..
docker compose up -d --build
```

## Arquitectura de Volúmenes

- **postgres_data**: Persiste los datos de PostgreSQL entre reinicios
- **./backend**: Montado en `/app` del contenedor backend (hot-reload)
- **./frontend**: Montado en `/app` del contenedor frontend (hot-reload)

Los node_modules del frontend se montan desde el host (por eso la instalación local es necesaria).

## Networking

Todos los servicios están en la red `predictly_network`:

- Los contenedores se comunican entre sí usando nombres de servicio:
  - Backend → Postgres: `postgresql://predictly:password@postgres:5432/predictly_db`
  - Backend → Redis: `redis://redis:6379/0`

- Desde el host (tu máquina):
  - Frontend: `http://localhost:3000`
  - Backend: `http://localhost:8000`
  - Postgres: `localhost:5432`
  - Redis: `localhost:6379`

## Siguientes Pasos

1. ✅ Infraestructura de desarrollo funcionando
2. ⏳ Implementar modelos de datos (tablas PostgreSQL)
3. ⏳ Implementar endpoints de API
4. ⏳ Implementar pricing engine (LMSR)
5. ⏳ Implementar ledger contable
6. ⏳ Implementar UI básica

## Notas Técnicas

### Backend Dependencies

El backend requiere:
- FastAPI
- Uvicorn
- SQLAlchemy >= 2.0
- psycopg2-binary (driver PostgreSQL)
- redis >= 5.0

Todas están definidas en `backend/pyproject.toml` y se instalan automáticamente en el contenedor.

### Frontend Dependencies

El frontend usa:
- Next.js 16 (con Turbopack)
- React 19
- TypeScript
- Tailwind CSS 4

**Importante**: Las dependencias deben instalarse localmente con `npm install` antes de usar Docker Compose.

### Healthchecks

- **Postgres**: `pg_isready -U predictly` cada 5s
- **Redis**: `redis-cli ping` cada 5s

El backend espera a que ambos estén "healthy" antes de iniciar.

### Logs de Conexión

Al iniciar, el backend loguea las conexiones:

```
INFO:app.main:✅ Successfully connected to PostgreSQL database
INFO:app.main:✅ Successfully connected to Redis
```

Si no ves estos mensajes, revisa las variables de entorno en `docker-compose.yml`.
