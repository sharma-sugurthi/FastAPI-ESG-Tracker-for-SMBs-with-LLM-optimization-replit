#!/bin/bash

# Production Deployment Script for ESG Compliance Tracker

set -e

echo "🚀 ESG Compliance Tracker - Production Deployment"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN=""
EMAIL=""
ENVIRONMENT="production"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        --staging)
            ENVIRONMENT="staging"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -d, --domain DOMAIN    Domain name for the application"
            echo "  -e, --email EMAIL      Email for Let's Encrypt certificates"
            echo "  --staging              Deploy to staging environment"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Pre-deployment checks
pre_deployment_checks() {
    echo "🔍 Running pre-deployment checks..."
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ .env file not found${NC}"
        echo "Please create .env file with production configuration"
        exit 1
    fi
    
    # Check required environment variables
    required_vars=("SECRET_KEY" "MODEL_PROVIDER" "DATABASE_URL")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" .env; then
            echo -e "${RED}❌ Required environment variable $var not found in .env${NC}"
            exit 1
        fi
    done
    
    # Check if LLM API key is set
    model_provider=$(grep "^MODEL_PROVIDER=" .env | cut -d'=' -f2)
    case $model_provider in
        "groq")
            if ! grep -q "^GROQ_API_KEY=" .env; then
                echo -e "${RED}❌ GROQ_API_KEY not found in .env${NC}"
                exit 1
            fi
            ;;
        "gemini")
            if ! grep -q "^GEMINI_API_KEY=" .env; then
                echo -e "${RED}❌ GEMINI_API_KEY not found in .env${NC}"
                exit 1
            fi
            ;;
        "openai")
            if ! grep -q "^OPENAI_API_KEY=" .env; then
                echo -e "${RED}❌ OPENAI_API_KEY not found in .env${NC}"
                exit 1
            fi
            ;;
    esac
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Pre-deployment checks passed${NC}"
}

# Setup SSL certificates
setup_ssl() {
    echo "🔐 Setting up SSL certificates..."
    
    if [ -z "$DOMAIN" ]; then
        echo -e "${YELLOW}⚠️ No domain specified, using self-signed certificate${NC}"
        ./scripts/setup-ssl.sh
    else
        echo "🌐 Setting up Let's Encrypt certificate for $DOMAIN"
        
        if [ -z "$EMAIL" ]; then
            read -p "Enter email for Let's Encrypt: " EMAIL
        fi
        
        # Update nginx configuration with domain
        sed -i.bak "s/your-domain.com/$DOMAIN/g" nginx.conf
        
        # Setup Let's Encrypt
        ./scripts/setup-ssl.sh
    fi
}

# Update CORS configuration
update_cors() {
    echo "🌐 Updating CORS configuration..."
    
    if [ ! -z "$DOMAIN" ]; then
        # Update ALLOWED_ORIGINS in .env
        current_origins=$(grep "^ALLOWED_ORIGINS=" .env | cut -d'=' -f2-)
        new_origins=$(echo "$current_origins" | sed "s/your-frontend-domain.com/$DOMAIN/g")
        sed -i.bak "s|^ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=$new_origins|" .env
        
        echo -e "${GREEN}✅ CORS updated for domain: $DOMAIN${NC}"
    else
        echo -e "${YELLOW}⚠️ No domain specified, using default CORS configuration${NC}"
    fi
}

# Build and deploy
deploy_application() {
    echo "🏗️ Building and deploying application..."
    
    # Create necessary directories
    mkdir -p uploads logs ssl
    
    # Set proper permissions
    chmod 755 uploads logs
    chmod 700 ssl
    
    # Build and start services
    if [ "$ENVIRONMENT" = "staging" ]; then
        echo "🧪 Deploying to staging environment..."
        docker-compose -f docker-compose.yml up -d --build
    else
        echo "🚀 Deploying to production environment..."
        docker-compose -f docker-compose.prod.yml up -d --build
    fi
    
    # Wait for services to be ready
    echo "⏳ Waiting for services to be ready..."
    sleep 30
    
    # Run health checks
    ./scripts/smoke-test.sh
}

# Setup monitoring
setup_monitoring() {
    echo "📊 Setting up monitoring..."
    
    # Create monitoring script
    cat > scripts/monitor.sh << 'EOF'
#!/bin/bash

# Simple monitoring script
check_service() {
    local service=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service is down"
        # Add alerting logic here (email, Slack, etc.)
    fi
}

check_service "Application" "http://localhost:8000/health"
check_service "Database" "http://localhost:8000/auth/providers"

# Check disk space
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    echo "⚠️ Disk usage is ${disk_usage}%"
fi

# Check memory usage
memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $memory_usage -gt 80 ]; then
    echo "⚠️ Memory usage is ${memory_usage}%"
fi
EOF

    chmod +x scripts/monitor.sh
    
    # Setup cron job for monitoring
    (crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/esg-compliance-tracker/scripts/monitor.sh >> /var/log/esg-monitor.log 2>&1") | crontab -
    
    echo -e "${GREEN}✅ Monitoring setup complete${NC}"
}

# Setup backup
setup_backup() {
    echo "💾 Setting up backup system..."
    
    cat > scripts/backup.sh << 'EOF'
#!/bin/bash

# Backup script for ESG Compliance Tracker

BACKUP_DIR="/var/backups/esg-tracker"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T db pg_dump -U postgres esg_tracker > "$BACKUP_DIR/db_backup_$DATE.sql"

# Application data backup
tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" uploads logs .env

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

    chmod +x scripts/backup.sh
    
    # Setup daily backup cron job
    (crontab -l 2>/dev/null; echo "0 2 * * * /path/to/esg-compliance-tracker/scripts/backup.sh >> /var/log/esg-backup.log 2>&1") | crontab -
    
    echo -e "${GREEN}✅ Backup system setup complete${NC}"
}

# Post-deployment tasks
post_deployment() {
    echo "🎯 Running post-deployment tasks..."
    
    # Update firewall rules
    if command -v ufw &> /dev/null; then
        echo "🔥 Updating firewall rules..."
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw allow 22/tcp
        sudo ufw --force enable
    fi
    
    # Setup log rotation
    cat > /tmp/esg-tracker-logrotate << EOF
/path/to/esg-compliance-tracker/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart app
    endscript
}
EOF
    
    sudo mv /tmp/esg-tracker-logrotate /etc/logrotate.d/esg-tracker
    
    echo -e "${GREEN}✅ Post-deployment tasks completed${NC}"
}

# Main deployment function
main() {
    echo -e "${BLUE}🚀 Starting ESG Compliance Tracker Production Deployment${NC}"
    echo "Environment: $ENVIRONMENT"
    if [ ! -z "$DOMAIN" ]; then
        echo "Domain: $DOMAIN"
    fi
    echo ""
    
    # Confirm deployment
    read -p "Continue with deployment? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Deployment cancelled"
        exit 0
    fi
    
    # Run deployment steps
    pre_deployment_checks
    setup_ssl
    update_cors
    deploy_application
    setup_monitoring
    setup_backup
    post_deployment
    
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo "📋 Deployment Summary:"
    echo "- Application is running on ports 80 (HTTP) and 443 (HTTPS)"
    echo "- Database is initialized and running"
    echo "- SSL certificates are configured"
    echo "- Monitoring and backup systems are active"
    echo ""
    echo "🔗 Access Points:"
    if [ ! -z "$DOMAIN" ]; then
        echo "- Application: https://$DOMAIN"
        echo "- API Docs: https://$DOMAIN/docs"
        echo "- Health Check: https://$DOMAIN/health"
    else
        echo "- Application: https://your-server-ip"
        echo "- API Docs: https://your-server-ip/docs"
        echo "- Health Check: https://your-server-ip/health"
    fi
    echo ""
    echo "📝 Next Steps:"
    echo "1. Update DNS records to point to this server"
    echo "2. Test all functionality with ./scripts/smoke-test.sh"
    echo "3. Configure monitoring alerts"
    echo "4. Update team documentation"
    echo "5. Schedule regular security updates"
}

# Run main function
main