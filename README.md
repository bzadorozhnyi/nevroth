# 😊 Nervoth Backend API

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.16-FF1709?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-✓-2496ED?logo=docker)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql)](https://www.postgresql.org/)
[![Celery](https://img.shields.io/badge/Celery-5.x-%2300B57F?logo=celery&logoColor=white)](https://docs.celeryq.dev/en/stable/)
[![Flower](https://img.shields.io/badge/Flower-%20for%20Celery-FF6B00?logo=flower&logoColor=white)](https://flower.readthedocs.io/)


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

### ⏳ Background Tasks with Celery

To ensure fast API response times and a smooth user experience, Nevroth offloads time-consuming tasks to Celery workers.

Implemented asynchronous tasks:

- 📧 `send_mail_task` — used to send password recovery emails.

- 🧠 `follow_up_no_habits_selected_task` — reminds users to select habits if they forgot to.

- 🧹 `cleanup_old_messages_task` — regularly purges outdated chat messages to keep the database clean.

All tasks are run asynchronously via Celery and can be monitored using tools like Flower or logs inside Docker.

### 🔌 Real-Time Communication

Nevroth supports real-time features via Django Channels and WebSockets:

- 🔁 `ws/chats/<chat_id>/` — new messages inside a selected chat.

- 📥 `ws/chat-list/` — receive real-time updates from other chats.

This allows seamless user experience for chat interactions and live updates without page reloads.

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
