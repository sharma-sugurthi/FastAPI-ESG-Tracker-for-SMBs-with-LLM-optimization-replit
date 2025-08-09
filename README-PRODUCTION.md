# ESG Compliance Tracker - Production Setup Guide

## 🚀 Quick Production Deployment

### 1. Environment Setup

```bash
# Clone repository
git clone <your-repo>
cd esg-compliance-tracker

# Copy and configure environment
cp .env.example .env
# Edit .env with your production values
```

### 2. Get LLM API Keys

#### Groq (Recommended - Free Tier)
1. Visit https://console.groq.com/
2. Sign up and get API key
3. Add to .env: `GROQ_API_KEY=gsk_your_key_here`

#### Google Gemini (Alternative)
1. Visit https://makersuite.google.com/
2. Get API key
3. Add to .env: `GEMINI_API_KEY=your_key_here`

### 3. Deploy with Docker

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Setup SSL certificates
./scripts/setup-ssl.sh

# Deploy application
docker-compose -f docker-compose.prod.yml up -d --build

# Run smoke tests
./scripts/smoke-test.sh
```

### 4. Production Checklist

- [ ] Update `SECRET_KEY` in .env
- [ ] Configure LLM API key
- [ ] Set production database password
- [ ] Update `ALLOWED_ORIGINS` with your frontend domains
- [ ] Setup SSL certificates
- [ ] Configure monitoring
- [ ] Setup backups
- [ ] Test all endpoints

## 🔧 Configuration Details

### Required Environment Variables

```env
# Security
SECRET_KEY=your-super-secure-secret-key-here
DEBUG=false

# LLM Provider
MODEL_PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_api_key_here

# Database
DATABASE_URL=postgresql://postgres:secure_password@db:5432/esg_tracker

# CORS (update with your domains)
ALLOWED_ORIGINS=["https://your-frontend.com","https://your-app.com"]
```

### CORS Configuration

Update the `ALLOWED_ORIGINS` in your .env file:

```env
ALLOWED_ORIGINS=["https://your-frontend-domain.com","https://your-app-domain.com","https://admin.your-domain.com"]
```

For development, you can use:
```env
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080","http://127.0.0.1:3000"]
```

## 🔐 Security Features

### HTTPS Setup
```bash
# Automatic SSL with Let's Encrypt
./scripts/setup-ssl.sh

# Or use existing certificates
# Place cert.pem and key.pem in ssl/ directory
```

### Secret Rotation
```bash
# Rotate all secrets
./scripts/secret-rotation.sh

# This will rotate:
# - JWT secret key
# - Database passwords
# - Redis passwords
# - SSL certificates
```

### Security Headers
The nginx configuration includes:
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection
- Referrer-Policy

## 📊 Monitoring & Testing

### Smoke Tests
```bash
# Test all endpoints
./scripts/smoke-test.sh

# Test specific URL
./scripts/smoke-test.sh https://your-domain.com
```

### Health Monitoring
```bash
# Check application health
curl https://your-domain.com/health

# Check predictive service
curl https://your-domain.com/predictive/health

# Check API documentation
curl https://your-domain.com/docs
```

### Key Endpoints to Test

1. **Core Endpoints**
   - `GET /health` - Application health
   - `GET /docs` - API documentation
   - `GET /` - Root endpoint

2. **Authentication**
   - `POST /auth/register` - User registration
   - `POST /auth/login` - User login
   - `GET /auth/providers` - Available auth providers

3. **ESG Assessment**
   - `GET /esg/questions` - ESG questionnaire
   - `POST /esg/questionnaire` - Submit assessment

4. **Predictive Compliance**
   - `GET /predictive/health` - Service health
   - `POST /predictive/alerts/generate` - Generate alerts
   - `POST /predictive/analytics/benchmarking` - Industry benchmarking

## 🗄️ Database Setup

The database is automatically initialized with:
- User management tables
- ESG questionnaire storage
- Task tracking
- Predictive alerts
- Score history

### Manual Database Operations
```bash
# Connect to database
docker-compose exec db psql -U postgres -d esg_tracker

# Backup database
docker-compose exec db pg_dump -U postgres esg_tracker > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres esg_tracker < backup.sql
```

## 🔄 Deployment Automation

### Full Production Deploy
```bash
# Deploy with domain and SSL
./scripts/production-deploy.sh -d your-domain.com -e admin@your-domain.com

# Deploy to staging
./scripts/production-deploy.sh --staging
```

### CI/CD Integration

For GitHub Actions, create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        run: |
          # Add your deployment commands here
          ./scripts/production-deploy.sh
```

## 📈 Scaling Considerations

### Load Balancing
```yaml
# docker-compose.prod.yml
services:
  app:
    deploy:
      replicas: 3
    ports:
      - "8000-8002:8000"
```

### Database Scaling
- Use read replicas for heavy read workloads
- Implement connection pooling
- Consider database sharding for large datasets

### Caching
- Redis is included for caching LLM responses
- Configure cache TTL based on your needs
- Monitor cache hit rates

## 🚨 Troubleshooting

### Common Issues

1. **LLM API Errors**
   ```bash
   # Check API key
   echo $GROQ_API_KEY
   
   # Test API connectivity
   curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Test connection
   docker-compose exec db psql -U postgres -d esg_tracker -c "SELECT 1;"
   ```

3. **CORS Errors**
   - Verify `ALLOWED_ORIGINS` in .env
   - Check nginx configuration
   - Test with browser developer tools

4. **SSL Certificate Issues**
   ```bash
   # Check certificate validity
   openssl x509 -in ssl/cert.pem -text -noout
   
   # Renew Let's Encrypt certificate
   sudo certbot renew
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Add indexes for frequently queried columns
   CREATE INDEX idx_users_email ON users(email);
   CREATE INDEX idx_questionnaires_user_id ON esg_questionnaires(user_id);
   ```

2. **Application Optimization**
   - Enable Redis caching
   - Use connection pooling
   - Optimize LLM API calls

3. **Infrastructure Optimization**
   - Use CDN for static assets
   - Implement horizontal scaling
   - Monitor resource usage

## 📞 Support

### Logs and Debugging
```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f db

# Nginx logs
docker-compose logs -f nginx

# System logs
sudo journalctl -u docker -f
```

### Backup and Recovery
```bash
# Create backup
./scripts/backup.sh

# Restore from backup
docker-compose exec -T db psql -U postgres esg_tracker < backup.sql
```

### Security Monitoring
```bash
# Check for security updates
./scripts/security-check.sh

# Rotate secrets
./scripts/secret-rotation.sh

# Update SSL certificates
./scripts/setup-ssl.sh
```

---

**🎉 Your ESG Compliance Tracker is now ready for production!**

For additional support, check the main README.md or create an issue in the repository.