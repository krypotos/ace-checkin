# Deployment Guide 🚀

Complete guide for deploying Ace Check-in on DigitalOcean.

## Prerequisites

- DigitalOcean account
- Domain name (optional but recommended)
- SSH access to your local machine
- Basic Linux command-line knowledge

## Step 1: Create a DigitalOcean Droplet

1. **Log in to DigitalOcean Console**
   - Go to https://cloud.digitalocean.com

2. **Create a New Droplet**
   - Click "Create" → "Droplets"
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Recommended 2GB RAM, 50GB SSD
   - **Region**: Choose closest to your location
   - **Authentication**: SSH key (recommended over password)
   - **Hostname**: ace-checkin-app
   - Click "Create Droplet"

3. **Note Your IP Address**
   - After creation, copy the IPv4 address (e.g., 192.168.1.1)

## Step 2: Configure DNS (Optional)

If you have a domain name:

1. **Add A Record**
   - Go to your domain registrar
   - Add A record: `@` → your Droplet IP
   - Add CNAME record: `www` → `@`

2. **Wait for DNS Propagation**
   - Can take 1-24 hours
   - Check: `nslookup yourdomain.com`

## Step 3: Connect to Your Droplet

```bash
# Connect via SSH
ssh -i ~/.ssh/your-key.pem root@YOUR_DROPLET_IP

# Or if using password authentication
ssh root@YOUR_DROPLET_IP
```

## Step 4: Install Docker and Docker Compose

```bash
# Update system packages
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add docker to sudo group
usermod -aG docker root

# Verify installation
docker --version
docker-compose --version
```

## Step 5: Clone and Set Up the Application

```bash
# Create application directory
mkdir -p /opt/ace-checkin
cd /opt/ace-checkin

# Clone repository
git clone <your-repo-url> .
# Or if no git: download and extract the files

# Create .env file with secure values
cat > .env << 'EOF'
DB_USER=ace_user
DB_PASSWORD=$(openssl rand -base64 32)
DB_NAME=ace_checkin
DB_HOST=db
DB_PORT=5432
ENVIRONMENT=production
EOF

# Verify .env was created
cat .env
```

## Step 6: Configure Nginx with SSL

### Option A: Using Let's Encrypt (Recommended)

```bash
# Install Certbot
apt-get install -y certbot python3-certbot-nginx

# Generate certificate (replace with your domain)
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Note: You may need to temporarily stop Docker for this

# Create SSL directory
mkdir -p /opt/ace-checkin/nginx/ssl

# Copy certificates
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/ace-checkin/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/ace-checkin/nginx/ssl/key.pem
```

### Option B: Self-Signed Certificate (Testing Only)

```bash
# Generate self-signed certificate
mkdir -p /opt/ace-checkin/nginx/ssl
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout /opt/ace-checkin/nginx/ssl/key.pem \
  -out /opt/ace-checkin/nginx/ssl/cert.pem \
  -days 365 -subj "/CN=yourdomain.com"
```

## Step 7: Update Nginx Configuration

Edit `nginx/conf.d/default.conf`:

```bash
nano /opt/ace-checkin/nginx/conf.d/default.conf
```

Uncomment and update the HTTPS section:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # ... rest of configuration
}
```

## Step 8: Start the Application

```bash
cd /opt/ace-checkin

# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Check app specifically
docker-compose logs app
```

## Step 9: Run Initial Setup

```bash
# Create database tables and run migrations
docker-compose exec app alembic upgrade head

# Verify database connection
docker-compose exec app python3 -c "from app.database import engine; engine.connect(); print('Database connected!')"

# Create a test member
docker-compose exec app python3 << 'EOF'
from app.database import SessionLocal
from app.models import Member
from datetime import datetime

db = SessionLocal()
test_member = Member(
    member_id="TEST001",
    name="Test Member",
    email="test@example.com"
)
db.add(test_member)
db.commit()
print("Test member created!")
EOF
```

## Step 10: Set Up Automatic Backups

```bash
# Create backup script
cat > /opt/ace-checkin/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/ace-checkin/backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup database
docker-compose exec -T db pg_dump -U ace_user ace_checkin > \
  $BACKUP_DIR/ace_checkin_$TIMESTAMP.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

echo "Backup completed: ace_checkin_$TIMESTAMP.sql"
EOF

chmod +x /opt/ace-checkin/backup.sh

# Add to crontab for daily backups at 2 AM
crontab -e
# Add line: 0 2 * * * cd /opt/ace-checkin && ./backup.sh
```

## Step 11: Set Up Monitoring and Logs

```bash
# View real-time logs
docker-compose logs -f app

# View specific container
docker-compose logs app --tail=100

# Save logs to file
docker-compose logs > app_logs.txt
```

## Step 12: Configure Firewall (UFW)

```bash
# Install UFW (if not already installed)
apt-get install -y ufw

# Enable firewall
ufw enable

# Allow SSH (IMPORTANT: do this before enabling firewall!)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Check status
ufw status
```

## Step 13: Set Up Auto-Renewal for SSL Certificate

```bash
# Add cron job for Let's Encrypt renewal
cat > /etc/cron.d/letsencrypt << 'EOF'
0 3 * * * root certbot renew --quiet && cd /opt/ace-checkin && docker-compose restart nginx
EOF

# Verify
cat /etc/cron.d/letsencrypt
```

## Step 14: Test the Deployment

```bash
# Test health endpoint
curl https://yourdomain.com/health

# Test API documentation
# Visit: https://yourdomain.com/docs

# Create a test member
curl -X POST https://yourdomain.com/api/members \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "MEMBER001",
    "name": "John Doe",
    "email": "john@example.com"
  }'

# Test entry check-in
curl -X POST https://yourdomain.com/api/entry \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "MEMBER001",
    "notes": "Court A"
  }'
```

## Maintenance

### Update Application

```bash
cd /opt/ace-checkin

# Pull latest code
git pull

# Rebuild and restart
docker-compose build
docker-compose up -d

# Run migrations if needed
docker-compose exec app alembic upgrade head

# Check status
docker-compose ps
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose exec db psql -U ace_user -d ace_checkin

# Useful SQL commands:
# \dt                    - List tables
# \d members             - Describe table
# SELECT * FROM members; - Query data
# \q                     - Exit
```

### Monitor System Resources

```bash
# Check Docker stats
docker stats

# Check disk space
df -h

# Check memory
free -h

# Check running processes
ps aux | grep docker
```

## Troubleshooting

### Issue: SSL Certificate Errors

```bash
# Check certificate validity
openssl s_client -connect yourdomain.com:443

# Renew certificate manually
certbot renew --force-renewal

# Copy to Docker volume
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /opt/ace-checkin/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /opt/ace-checkin/nginx/ssl/key.pem

# Restart Nginx
docker-compose restart nginx
```

### Issue: Database Connection Issues

```bash
# Check database logs
docker-compose logs db

# Test connection
docker-compose exec app python3 << 'EOF'
from sqlalchemy import create_engine
engine = create_engine('postgresql://ace_user:ace_password@db:5432/ace_checkin')
connection = engine.connect()
print("Connected successfully!")
connection.close()
EOF
```

### Issue: Out of Disk Space

```bash
# Check disk usage
du -sh *

# Clean Docker images and containers
docker system prune -a

# Check PostgreSQL data size
docker-compose exec db du -sh /var/lib/postgresql/data
```

### Issue: High Memory Usage

```bash
# Check Docker stats
docker stats

# Adjust Docker Compose resources
# Edit docker-compose.yml and add:
# services:
#   app:
#     deploy:
#       resources:
#         limits:
#           memory: 512M
```

## Scaling Considerations

As your tennis club grows:

1. **Load Balancing**
   - Use DigitalOcean Load Balancer
   - Multiple app instances behind proxy

2. **Database Scaling**
   - Move to managed database service
   - Implement read replicas

3. **Caching**
   - Add Redis for session/cache
   - Reduce database load

4. **CDN**
   - Use DigitalOcean Spaces + CDN
   - Faster content delivery

## Security Checklist

- [ ] SSL/HTTPS enabled
- [ ] Firewall configured (UFW)
- [ ] Strong database password
- [ ] Regular backups scheduled
- [ ] SSH key authentication only
- [ ] Fail2ban installed (optional)
- [ ] Monitoring and logging enabled
- [ ] Environment variables secured
- [ ] Regular updates scheduled
- [ ] CORS configured appropriately

## Support and Monitoring

### Set Up Monitoring Alerts (Optional)

```bash
# Install monitoring tools
apt-get install -y htop iotop

# Monitor in real-time
htop

# Check log files
tail -f /var/log/syslog
```

### Log Rotation

```bash
# Docker automatically rotates logs, but you can configure it
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Restart Docker
systemctl restart docker
```

## Rollback Procedure

If something goes wrong:

```bash
# Stop services
docker-compose down

# Restore from backup
docker-compose exec -T db psql -U ace_user ace_checkin < backups/ace_checkin_TIMESTAMP.sql

# Restart
docker-compose up -d

# Verify
docker-compose ps
```

---

**Deployment Complete! Your Ace Check-in system is now live. 🎉**

For questions or issues, refer to the main README.md or check the logs with:
```bash
docker-compose logs -f
```
