#!/bin/bash

# SSL Certificate Setup Script for ESG Compliance Tracker

set -e

echo "🔐 Setting up SSL certificates for ESG Compliance Tracker"

# Create SSL directory
mkdir -p ssl

# Check if certificates already exist
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    echo "✅ SSL certificates already exist"
    exit 0
fi

echo "📋 Choose SSL certificate option:"
echo "1. Generate self-signed certificate (development)"
echo "2. Use Let's Encrypt (production)"
echo "3. Use existing certificates"

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🔧 Generating self-signed certificate..."
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        echo "✅ Self-signed certificate generated"
        ;;
    2)
        echo "🌐 Setting up Let's Encrypt certificate..."
        read -p "Enter your domain name: " domain
        
        # Install certbot if not present
        if ! command -v certbot &> /dev/null; then
            echo "Installing certbot..."
            sudo apt-get update
            sudo apt-get install -y certbot python3-certbot-nginx
        fi
        
        # Generate certificate
        sudo certbot certonly --standalone -d $domain
        
        # Copy certificates
        sudo cp /etc/letsencrypt/live/$domain/fullchain.pem ssl/cert.pem
        sudo cp /etc/letsencrypt/live/$domain/privkey.pem ssl/key.pem
        sudo chown $USER:$USER ssl/*.pem
        
        echo "✅ Let's Encrypt certificate installed"
        ;;
    3)
        echo "📁 Place your certificate files in the ssl/ directory:"
        echo "  - ssl/cert.pem (certificate)"
        echo "  - ssl/key.pem (private key)"
        read -p "Press Enter when certificates are in place..."
        
        if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
            echo "❌ Certificate files not found"
            exit 1
        fi
        
        echo "✅ Using existing certificates"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Set proper permissions
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo "🎉 SSL setup complete!"
echo "📝 Update nginx.conf with your domain name before starting services"