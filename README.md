# Pasted.IR 🚀

A modern, secure, and privacy-focused pastebin service, built with Django.

![Pasted.IR](https://img.shields.io/badge/Pasted.IR-Web%20%7C%20API%20%7C%20Bot-blue)
![Django](https://img.shields.io/badge/Django-5.1.4-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-GPL%20v3.0-red)

## 🌟 Features

### Web Application
- **Modern UI**: Clean, responsive design with dark/light mode support
- **Syntax Highlighting**: Automatic language detection and highlighting
- **Password Protection**: Secure paste encryption with optional passwords
- **Expiration Control**: Configurable paste expiration (1 day to 1 year)
- **One-time Links**: Self-destructing pastes after first view
- **History Management**: View and manage your paste history
- **Raw View**: View pastes without formatting

### API
- **RESTful API**: Full CRUD operations for pastes
- **Language Support**: Get available programming languages
- **Bot Authentication**: Secure API access with bot tokens
- **Rate Limiting**: Built-in protection against abuse
- **OpenAPI Documentation**: Auto-generated API docs with drf-spectacular


## 🏗️ Architecture

```
PastedIR/
├── 📁 pastebinir/          # Django project settings
├── 📁 api/                 # REST API endpoints
├── 📁 website/             # Web application views
├── 📁 templates/           # HTML templates
├── 📁 static/              # CSS, JS, images
├── 📁 compose/             # Docker configurations
├── 📁 nginx-configs/       # Nginx configuration templates
├── 🐳 docker-compose.yml   # Container orchestration
└── 📄 pyproject.toml       # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- uv
- Docker & Docker Compose
- Redis (for caching and task scheduling)

### 1. Clone the Repository
```bash
git clone https://github.com/BuddySirJava/PasteIR.git
cd PastedIR
```

### 2. Environment Setup
```bash
# Copy environment file
cp example.env .env

# Edit environment variables
nano .env
```

### 3. Docker Deployment (Recommended)
```bash
# Start all services (includes PostgreSQL and Redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Manual Setup (Development)
```bash
# sync dependencies
uv sync 
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Start scheduler worker (in another terminal)
python manage.py scheduler_worker default
```

## 🌐 Nginx Configuration

The project includes pre-configured Nginx templates for production deployment:

### Configuration Files
- `nginx-configs/example.nginx.conf` - Main Nginx configuration
- `nginx-configs/example.default.conf` - Server block configuration with:
  - Rate limiting zones
  - SSL/TLS configuration
  - Security headers (CSP, HSTS, etc.)
  - Bot server IP whitelisting
  - Static file serving optimization

### Setup Instructions
1. Copy the example configurations to your Nginx directory:
```bash
sudo cp nginx-configs/example.nginx.conf /etc/nginx/nginx.conf
sudo cp nginx-configs/example.default.conf /etc/nginx/sites-available/pasted.ir
```

2. Update the configuration files:
   - Replace `example.com` with your domain
   - Update SSL certificate paths
   - Configure your bot server IP in the whitelist
   - Adjust rate limiting settings as needed

3. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/pasted.ir /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Features
- **Rate Limiting**: Separate zones for API, create endpoints, and general traffic
- **Bot Whitelisting**: IP-based and token-based bot authentication
- **Security Headers**: Comprehensive CSP, HSTS, and other security headers
- **Static File Optimization**: Efficient serving of CSS, JS, and media files
- **SSL/TLS**: Production-ready HTTPS configuration

## ⚙️ Configuration

### Environment Variables

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost

# Database (PostgreSQL)
POSTGRES_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost

# Static Files
STATIC_URL=/static/
STATIC_ROOT=/static

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com
BOT_TOKEN=your-bot-token-for-api-calls

# Redis (for caching and task scheduling)
REDIS_HOST=localhost
REDIS_PORT=6379
```


## 🔧 API Documentation

### Endpoints

#### Pastes
- `GET /api/pastes/` - List pastes
- `POST /api/pastes/` - Create new paste
- `GET /api/pastes/{id}/` - Get specific paste
- `DELETE /api/pastes/{id}/` - Delete paste

#### Languages
- `GET /api/languages/` - Get available languages

### Authentication
Include bot token in headers:
```
X-Bot-Token: your-bot-token
```

### Example Usage
```bash
# Create a paste
curl -X POST https://pasted.ir/api/pastes/ \
  -H "Content-Type: application/json" \
  -H "X-Bot-Token: your-bot-token" \
  -d '{
    "content": "print(\"Hello, World!\")",
    "language": 1,
    "expiration": 7,
    "one_time": false
  }'
```

## 🎨 Customization

### Themes
The application supports dark/light mode with automatic theme switching. Customize colors in `templates/base.html`:

```css
:root {
    --bg-primary: #ffffff;
    --text-primary: #1f2937;
    /* ... more variables */
}

.dark {
    --bg-primary: #1e293b;
    --text-primary: #f8fafc;
    /* ... more variables */
}
```


## 🔒 Security Features

- **Password Protection**: Optional encryption for sensitive pastes
- **Rate Limiting**: API and bot rate limiting to prevent abuse
- **CSRF Protection**: Built-in Django CSRF protection
- **Input Validation**: Comprehensive input sanitization
- **Bot Authentication**: Secure API access with tokens
- **Expiration Control**: Automatic paste cleanup

## 📊 Monitoring

### Logs
```bash
# View application logs
docker-compose logs -f web

# View scheduler logs
docker-compose logs -f scheduler
```

### Health Checks
- API health: `GET /api/health/`
- Bot status: `/status` command in private chat

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](gnu-gpl-v3.0.md) file for details.

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) - Web framework
- [Django REST Framework](https://www.django-rest-framework.org/) - API framework
- [highlight.js](https://highlightjs.org/) - Syntax highlighting
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework

## 📞 Support

- **Website**: [pasted.ir](https://pasted.ir)
- **Issues**: [GitHub Issues](https://github.com/BuddySirJava/PastedIR/issues)
- **Telegram**: [Send Private Message](https://telegram.me/Buddy_R)
---

Made with ❤️ for the Persian development community 
