#!/bin/bash

# Secret Rotation Script for ESG Compliance Tracker

set -e

echo "🔄 ESG Compliance Tracker - Secret Rotation"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Backup current .env
backup_env() {
    if [ -f ".env" ]; then
        timestamp=$(date +%Y%m%d_%H%M%S)
        cp .env ".env.backup.$timestamp"
        echo -e "${GREEN}✅ Backed up current .env to .env.backup.$timestamp${NC}"
    fi
}

# Generate secure random string
generate_secret() {
    local length=${1:-64}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Update secret in .env file
update_secret() {
    local key=$1
    local new_value=$2
    local env_file=${3:-.env}
    
    if [ -f "$env_file" ]; then
        # Use sed to replace the value
        if grep -q "^$key=" "$env_file"; then
            sed -i.bak "s|^$key=.*|$key=$new_value|" "$env_file"
            echo -e "${GREEN}✅ Updated $key${NC}"
        else
            echo "$key=$new_value" >> "$env_file"
            echo -e "${GREEN}✅ Added $key${NC}"
        fi
    else
        echo -e "${RED}❌ .env file not found${NC}"
        exit 1
    fi
}

# Rotate JWT secret
rotate_jwt_secret() {
    echo "🔑 Rotating JWT secret key..."
    new_secret=$(generate_secret 64)
    update_secret "SECRET_KEY" "$new_secret"
    echo -e "${YELLOW}⚠️ All users will need to re-authenticate after this change${NC}"
}

# Rotate database password
rotate_db_password() {
    echo "🗄️ Rotating database password..."
    new_password=$(generate_secret 32)
    
    # Update .env
    current_db_url=$(grep "^DATABASE_URL=" .env | cut -d'=' -f2-)
    new_db_url=$(echo "$current_db_url" | sed "s/:.*@/:$new_password@/")
    update_secret "DATABASE_URL" "$new_db_url"
    
    # Update docker-compose
    if [ -f "docker-compose.yml" ]; then
        sed -i.bak "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$new_password/" docker-compose.yml
    fi
    if [ -f "docker-compose.prod.yml" ]; then
        sed -i.bak "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$new_password/" docker-compose.prod.yml
    fi
    
    echo -e "${YELLOW}⚠️ Database will need to be restarted with new password${NC}"
}

# Rotate Redis password
rotate_redis_password() {
    echo "🔴 Rotating Redis password..."
    new_password=$(generate_secret 32)
    
    # Update Redis URL in .env
    update_secret "REDIS_PASSWORD" "$new_password"
    
    # Update Redis URL if it exists
    if grep -q "^REDIS_URL=" .env; then
        new_redis_url="redis://:$new_password@redis:6379/0"
        update_secret "REDIS_URL" "$new_redis_url"
    fi
    
    echo -e "${YELLOW}⚠️ Redis will need to be restarted with new password${NC}"
}

# Generate new API keys reminder
rotate_api_keys() {
    echo "🔌 API Keys Rotation Reminder:"
    echo "Please manually rotate the following API keys:"
    echo "1. GROQ_API_KEY - Visit https://console.groq.com/"
    echo "2. GEMINI_API_KEY - Visit https://makersuite.google.com/"
    echo "3. OPENAI_API_KEY - Visit https://platform.openai.com/"
    echo "4. FIREBASE credentials - Visit Firebase Console"
    echo "5. SUPABASE_KEY - Visit Supabase Dashboard"
    echo ""
    echo "After obtaining new keys, update them in .env file"
}

# SSL certificate renewal
renew_ssl_certificates() {
    echo "🔐 SSL Certificate Renewal..."
    
    if [ -f "ssl/cert.pem" ]; then
        # Check certificate expiry
        expiry_date=$(openssl x509 -enddate -noout -in ssl/cert.pem | cut -d= -f2)
        expiry_timestamp=$(date -d "$expiry_date" +%s)
        current_timestamp=$(date +%s)
        days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
        
        echo "Certificate expires in $days_until_expiry days"
        
        if [ $days_until_expiry -lt 30 ]; then
            echo -e "${YELLOW}⚠️ Certificate expires soon. Consider renewal.${NC}"
            
            # If using Let's Encrypt
            if command -v certbot &> /dev/null; then
                echo "Run: sudo certbot renew"
            else
                echo "Generate new certificate or run: ./scripts/setup-ssl.sh"
            fi
        else
            echo -e "${GREEN}✅ Certificate is valid for $days_until_expiry more days${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ No SSL certificate found${NC}"
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "Select secrets to rotate:"
    echo "1. JWT Secret Key (requires user re-authentication)"
    echo "2. Database Password (requires DB restart)"
    echo "3. Redis Password (requires Redis restart)"
    echo "4. All Application Secrets (1-3)"
    echo "5. API Keys Reminder"
    echo "6. SSL Certificate Check/Renewal"
    echo "7. Full Security Rotation (All)"
    echo "8. Exit"
    echo ""
}

# Restart services
restart_services() {
    echo "🔄 Restarting services..."
    
    if [ -f "docker-compose.yml" ]; then
        echo "Restarting Docker services..."
        docker-compose down
        docker-compose up -d --build
        echo -e "${GREEN}✅ Services restarted${NC}"
    else
        echo -e "${YELLOW}⚠️ Manual service restart required${NC}"
    fi
}

# Main execution
main() {
    echo "🔒 Starting secret rotation process..."
    
    # Backup current configuration
    backup_env
    
    while true; do
        show_menu
        read -p "Enter your choice (1-8): " choice
        
        case $choice in
            1)
                rotate_jwt_secret
                ;;
            2)
                rotate_db_password
                ;;
            3)
                rotate_redis_password
                ;;
            4)
                rotate_jwt_secret
                rotate_db_password
                rotate_redis_password
                ;;
            5)
                rotate_api_keys
                ;;
            6)
                renew_ssl_certificates
                ;;
            7)
                rotate_jwt_secret
                rotate_db_password
                rotate_redis_password
                rotate_api_keys
                renew_ssl_certificates
                ;;
            8)
                echo "👋 Exiting secret rotation"
                break
                ;;
            *)
                echo -e "${RED}❌ Invalid choice${NC}"
                ;;
        esac
        
        if [ $choice -ge 1 ] && [ $choice -le 4 ]; then
            echo ""
            read -p "Restart services now? (y/n): " restart_choice
            if [ "$restart_choice" = "y" ] || [ "$restart_choice" = "Y" ]; then
                restart_services
            else
                echo -e "${YELLOW}⚠️ Remember to restart services manually${NC}"
            fi
        fi
        
        echo ""
        read -p "Continue with more rotations? (y/n): " continue_choice
        if [ "$continue_choice" != "y" ] && [ "$continue_choice" != "Y" ]; then
            break
        fi
    done
    
    echo ""
    echo -e "${GREEN}🎉 Secret rotation completed!${NC}"
    echo "📝 Summary of changes:"
    echo "- Backup created with timestamp"
    echo "- Selected secrets have been rotated"
    echo "- Services may need restart"
    echo ""
    echo "🔍 Next steps:"
    echo "1. Test the application: ./scripts/smoke-test.sh"
    echo "2. Update any external configurations"
    echo "3. Notify team members of changes"
    echo "4. Update monitoring/alerting systems"
}

# Check dependencies
check_dependencies() {
    if ! command -v openssl &> /dev/null; then
        echo -e "${RED}❌ openssl is required but not installed${NC}"
        exit 1
    fi
}

# Run main function
check_dependencies
main