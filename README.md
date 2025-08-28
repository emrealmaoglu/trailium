# 🚀 Trailium - Social Platform (Development Version)

**A social media platform built with Vue.js and Django - Currently in active development, NOT production-ready.**

[![Vue.js](https://img.shields.io/badge/Vue.js-3.5.18-4FC08D?style=for-the-badge&logo=vue.js)](https://vuejs.org/)
[![Django](https://img.shields.io/badge/Django-5.2.5-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-3.8-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

## ⚠️ **IMPORTANT DISCLAIMER**

**This project is currently in active development and is NOT production-ready.** The following features are still being implemented:

- [ ] Complete security hardening
- [ ] Comprehensive testing suite
- [ ] Production deployment configuration
- [ ] Performance optimization
- [ ] Monitoring and alerting
- [ ] Backup and disaster recovery

**Do not deploy this to production without completing the security and testing requirements.**

## ✨ **Current Features**

### 🔒 **Basic Security** (In Progress)
- JWT authentication with httpOnly cookies
- Basic CORS configuration
- Input validation
- Rate limiting (basic implementation)

### 📱 **UI/UX** (Basic Implementation)
- Responsive design (needs improvement)
- Basic component structure
- Form validation
- Notification system

### 🏗️ **Architecture** (Foundation Only)
- Django REST API backend
- Vue.js 3 frontend
- PostgreSQL database
- Docker containerization

## 🚀 **Development Setup**

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 16+
- Docker & Docker Compose

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/trailium.git
cd trailium
```

2. **Backend Setup**
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. **Frontend Setup**
```bash
cd apps/frontend
npm install
npm run dev
```

4. **Docker Setup (Recommended)**
```bash
cd infra/compose
docker-compose up -d
```

## 🔧 **Configuration**

### Environment Variables

Create a `.env` file in the `infra/compose` directory:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-development-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
POSTGRES_DB=trailium_dev
POSTGRES_USER=trailium
POSTGRES_PASSWORD=trailium

# CORS Settings
CORS_ALLOW_ALL_ORIGINS=True  # Only for development!
```

### Removed/Quarantined Deployment Items
- Dockerfiles and compose moved under `infra/`
- Production-only settings removed or quarantined
- Monitoring/observability configs quarantined
- Build artifacts, logs, heavy media removed
(This list will be finalized after the audit clean-up PR is merged.)

## 🧪 **Testing**

### Backend Testing
```bash
cd apps/backend
pytest
pytest --cov=. --cov-report=html
```

### Frontend Testing
```bash
cd apps/frontend
npm test
npm run test:coverage
```

**Note: Test coverage is currently incomplete and needs significant improvement.**

## 🧰 Local Run (PostgreSQL)

Backend

```bash
cd apps/backend
python -m venv .venv && source .venv/bin/activate
cp .env.example .env
# ensure a local Postgres is running and matches .env
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Frontend

```bash
cd apps/frontend
cp .env.example .env  # contains VITE_API_BASE_URL=http://127.0.0.1:8000
npm install
npm run dev
```

3-minute demo

1) Open FE → /register → create user
2) /login → sign in (remember me optional)
3) Redirected to /users stub → open AvatarMenu → Logout

## 🗂️ Documentation & i18n Updates

- All backend modules, modeller, serializer ve view'ler Türkçe NumPy tarzı docstring ile açıklandı.
- Frontend bileşenleri ve Pinia store'ları için JSDoc yorumları eklendi (asgari düzeyde).
- UI, Türkçe/İngilizce çift dil desteğine sahiptir. Varsayılan dil Türkçe'dir.
- Dili değiştirmek için sağ üstteki kullanıcı menüsünden Dil bölümünden (🇹🇷/🇺🇸) seçim yapın.

### i18n

- vue-i18n kuruldu (Vue 3 uyumlu v9).
- Arayüz Türkçe/İngilizce destekler; dil değişimi için Kullanıcı Menüsü → Dil.

## 🚧 **Known Issues & Limitations**

### Security Issues (CRITICAL)
- [ ] Hardcoded secret keys in development
- [ ] CORS configuration too permissive
- [ ] Missing input sanitization
- [ ] No audit logging
- [ ] Weak password policies

### Performance Issues
- [ ] No caching strategy
- [ ] N+1 database queries
- [ ] No CDN configuration
- [ ] Missing database indexes
- [ ] No lazy loading

### Architecture Issues
- [ ] Monolithic structure
- [ ] No microservices separation
- [ ] Missing health checks
- [ ] No monitoring
- [ ] No backup strategy

## 📋 **Development Roadmap**

### Phase 1: Security Hardening (URGENT)
- [ ] Implement proper environment variable management
- [ ] Add comprehensive input validation
- [ ] Implement audit logging
- [ ] Add security headers
- [ ] Complete CORS configuration

### Phase 2: Testing & Quality
- [ ] Achieve 80%+ test coverage
- [ ] Add integration tests
- [ ] Implement CI/CD pipeline
- [ ] Add code quality checks

### Phase 3: Production Readiness
- [ ] Performance optimization
- [ ] Monitoring and alerting
- [ ] Backup and recovery
- [ ] Documentation completion

### Phase 4: Feature Enhancement
- [ ] Real-time updates
- [ ] Advanced content types
- [ ] User engagement features
- [ ] Mobile app

## 🆘 **Getting Help**

### Common Issues

#### Backend Won't Start
```bash
# Check environment variables
python manage.py check --deploy

# Verify database connection
python manage.py check --database default
```

#### Frontend Build Issues
```bash
# Clear dependencies
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+
```

#### Docker Issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🤝 **Contributing**

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. **Add tests for new functionality**
5. **Ensure all tests pass**
6. Submit a pull request

### Code Standards
- **Frontend**: ESLint + Prettier
- **Backend**: Black + isort + flake8
- **Testing**: 80%+ coverage required
- **Documentation**: Update README and inline docs

## 📚 **API Documentation**

### Authentication Endpoints
```
POST /api/auth/login/          # User login
POST /api/auth/register/       # User registration
POST /api/auth/refresh/        # Token refresh
POST /api/auth/logout/         # User logout
```

### Core Endpoints
```
GET    /health/                # Health check
GET    /api/users/             # List users
GET    /api/posts/             # List posts
POST   /api/posts/             # Create post
```

**Note: API documentation is incomplete. Use the health endpoint to verify service status.**


## 🙏 **Acknowledgments**

- **Vue.js Team** for the amazing framework
- **Django Team** for the robust backend framework
- **Open Source Community** for inspiration and tools

---

**⚠️ REMEMBER: This is a development version. Do not deploy to production without completing the security and testing requirements.**

**Made with ❤️ by the Trailium Team**
