# 😊 Nervoth Backend API

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.16-FF1709?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://www.postgresql.org/)

API for Nevroth – an app to help users track and improve their progress in overcoming harmful habits.

## 🌟 Features

### **Core API**
- **Modern REST Architecture**: JWT authentication, OpenAPI 3.0 docs, and DRF-powered endpoints.
- **Django ORM**: PostgreSQL-optimized queries with atomic transactions.
- **Admin Dashboard**: Pre-configured Django Admin.

### **Developer Experience**
- **Dockerized**: [![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker)](https://www.docker.com/)  
  - Local development with `docker-compose` (API + PostgreSQL).  
- **Ruff for code quality**: [![Ruff](https://img.shields.io/badge/Ruff-FCC21B?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
 
## 💻 Local Development
Use Docker Compose for easy local setup. It starts the API and PostgreSQL database automatically.

### ✅ Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/)

### 🏁 Getting Started

1. Clone the repository.
2. Start the services:
   ```bash
   docker compose up -d
   ```

3. The API will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

4. Database connection details:
   - **Host**: `localhost`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: `password`
   - **Database**: `nevroth_db`
  
Access the admin panel at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

### 🔧 Useful Commands

- Check management commands:
  ```bash
  docker compose exec api python manage.py help
  ```

- View logs:
  ```bash
  docker compose logs -f api
  ```

- Run tests inside container:
  ```bash
  docker compose exec api python manage.py test
  ```

### 🎨 For Frontend Developers

- API Docs URL: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- Admin panel: Use to view and edit test data during development.
