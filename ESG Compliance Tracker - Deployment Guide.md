# ESG Compliance Tracker - Deployment Guide

This guide covers multiple deployment options for the ESG Compliance Tracker, from local development to production deployment on cloud platforms.

## 📋 Prerequisites

### Required
- Python 3.11+
- Git
- At least one LLM API key (Groq recommended for free tier)

### Optional
- Docker & Docker Compose
- PostgreSQL (for production)
- Redis (for caching)

## 🔧 Environment Configuration

### 1. Clone Repository
```bash
git clone <repository-url>
cd esg-compliance-tracker
```

### 2. Environment Setup
```bash
cp .env.example .env
```

### 3. Configure Environment Variables

#### Essential Configuration
```env
# Application
APP_NAME=ESG Compliance Tracker
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production

# LLM Provider (choose one)
MODEL_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key

# Alternative providers
# MODEL_PROVIDER=gemini
# GEMINI_API_KEY=your-gemini-api-key
# MODEL_PROVIDER=openai
# OPENAI_API_KEY=your-openai-api-key
```

#### Authentication (choose one)
```env
# Firebase Auth
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com

# OR Supabase Auth
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

#### Database (production)
```env
DATABASE_URL=postgresql://username:password@host:port/database
```

## 🚀 Deployment Options

## Option 1: Local Development

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### With Virtual Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## Option 2: Docker Development

### Using Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Services Included
- **app**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

### Using Docker Only
```bash
# Build image
docker build -t esg-tracker .

# Run container
docker run -p 8000:8000 --env-file .env esg-tracker
```

---

## Option 3: Render.com Deployment

### Automatic Deployment

1. **Fork/Clone Repository**
   - Fork this repository to your GitHub account
   - Or upload your code to a new repository

2. **Connect to Render**
   - Go to [Render.com](https://render.com)
   - Sign up/login with GitHub
   - Click "New +" → "Web Service"
   - Connect your repository

3. **Configure Service**
   - **Name**: `esg-compliance-tracker`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   ```
   PYTHON_VERSION=3.11.0
   DEBUG=false
   SECRET_KEY=your-production-secret-key
   MODEL_PROVIDER=groq
   GROQ_API_KEY=your-groq-api-key
   ALLOWED_ORIGINS=["*"]
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy on every git push

### Using render.yaml (Advanced)
```bash
# Use the provided render.yaml for infrastructure as code
# Just connect your repo and Render will read the configuration
```

### Database Setup on Render
1. Create PostgreSQL database service
2. Copy connection string to `DATABASE_URL` environment variable
3. Database will be automatically initialized

---

## Option 4: Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Heroku account

### Deployment Steps
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set MODEL_PROVIDER=groq
heroku config:set GROQ_API_KEY=your-groq-api-key
heroku config:set DEBUG=false

# Deploy
git push heroku main

# Open app
heroku open
```

### Procfile
Create a `Procfile` in the root directory:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Option 5: DigitalOcean App Platform

### Using App Spec
Create `.do/app.yaml`:
```yaml
name: esg-compliance-tracker
services:
- name: api
  source_dir: /
  github:
    repo: your-username/esg-compliance-tracker
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: MODEL_PROVIDER
    value: groq
  - key: GROQ_API_KEY
    value: your-groq-api-key
    type: SECRET
databases:
- name: esg-db
  engine: PG
  version: "13"
```

### Deploy
```bash
# Install doctl CLI
# Configure authentication
doctl apps create .do/app.yaml
```

---

## Option 6: AWS EC2 Deployment

### EC2 Setup
```bash
# Connect to EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Docker (optional)
sudo apt install docker.io docker-compose -y
sudo usermod -aG docker ubuntu
```

### Application Deployment
```bash
# Clone repository
git clone <your-repo-url>
cd esg-compliance-tracker

# Setup environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run with systemd (production)
sudo cp deployment/esg-tracker.service /etc/systemd/system/
sudo systemctl enable esg-tracker
sudo systemctl start esg-tracker
```

### Systemd Service File (`deployment/esg-tracker.service`)
```ini
[Unit]
Description=ESG Compliance Tracker
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/home/ubuntu/esg-compliance-tracker
Environment=PATH=/home/ubuntu/esg-compliance-tracker/venv/bin
ExecStart=/home/ubuntu/esg-compliance-tracker/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔐 Production Security Checklist

### Environment Variables
- [ ] Change default `SECRET_KEY`
- [ ] Set `DEBUG=false`
- [ ] Configure proper `ALLOWED_ORIGINS`
- [ ] Use strong database passwords
- [ ] Secure API keys

### Database Security
- [ ] Enable SSL connections
- [ ] Use connection pooling
- [ ] Regular backups
- [ ] Access restrictions

### Application Security
- [ ] Enable HTTPS
- [ ] Configure rate limiting
- [ ] Set up monitoring
- [ ] Log security events

### GDPR Compliance
- [ ] Configure data retention policies
- [ ] Set up user data deletion
- [ ] Privacy notice accessible
- [ ] Consent management working

---

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Application health
curl https://your-app.com/health

# Database connectivity
curl https://your-app.com/auth/providers
```

### Logging
```bash
# Docker logs
docker-compose logs -f app

# Systemd logs
sudo journalctl -u esg-tracker -f

# Application logs
tail -f logs/app.log
```

### Performance Monitoring
- Monitor response times
- Track LLM API usage
- Database query performance
- Memory and CPU usage

### Backup Strategy
```bash
# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d).tar.gz /path/to/app
```

---

## 🔧 Troubleshooting

### Common Issues

#### LLM Provider Errors
```bash
# Check API key configuration
echo $GROQ_API_KEY

# Test provider availability
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models
```

#### Database Connection Issues
```bash
# Test database connection
python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
print('Database connection successful')
"
```

#### Authentication Problems
```bash
# Verify JWT secret
python -c "
import os
print('Secret key length:', len(os.getenv('SECRET_KEY', '')))
"
```

#### CORS Issues
- Check `ALLOWED_ORIGINS` configuration
- Verify frontend domain is included
- Test with browser developer tools

### Performance Issues
- Enable Redis caching
- Optimize database queries
- Use connection pooling
- Monitor LLM API rate limits

### Scaling Considerations
- Use load balancer for multiple instances
- Implement database read replicas
- Cache frequently accessed data
- Monitor and optimize LLM usage

---

## 📈 Scaling & Optimization

### Horizontal Scaling
```yaml
# Docker Swarm
version: '3.8'
services:
  app:
    image: esg-tracker
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
```

### Caching Strategy
```python
# Redis caching for expensive operations
CACHE_TTL = 3600  # 1 hour
redis_client = redis.Redis(host='redis', port=6379)
```

### Database Optimization
- Index frequently queried columns
- Use database connection pooling
- Implement read replicas
- Regular VACUUM and ANALYZE

### LLM Cost Optimization
- Cache LLM responses
- Use cheaper models for simple tasks
- Implement request batching
- Monitor usage and costs

---

## 🆘 Support & Maintenance

### Regular Maintenance Tasks
- [ ] Update dependencies monthly
- [ ] Monitor security advisories
- [ ] Review and rotate API keys
- [ ] Clean up old data per GDPR
- [ ] Performance optimization
- [ ] Backup verification

### Monitoring Alerts
Set up alerts for:
- Application downtime
- High error rates
- Database connection issues
- LLM API failures
- High resource usage

### Update Process
```bash
# Backup before updates
./scripts/backup.sh

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests
pytest

# Deploy updates
./scripts/deploy.sh
```

---

**Need help?** Check the troubleshooting section or create an issue in the repository.

