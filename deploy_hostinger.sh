#!/bin/bash
# Script de déploiement SmartLeakPro sur Hostinger KVM2

echo "🚀 Déploiement SmartLeakPro sur Hostinger KVM2"

# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances système
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# Installation de Node.js (pour le frontend React)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Création de l'utilisateur application
sudo useradd -m -s /bin/bash smartleakpro
sudo usermod -aG sudo smartleakpro

# Configuration PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE smartleakpro;"
sudo -u postgres psql -c "CREATE USER smartleakpro WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE smartleakpro TO smartleakpro;"

# Cloner le repository
cd /home/smartleakpro
sudo -u smartleakpro git clone https://github.com/SebW37/SMARTLEAKPRO.git
cd SMARTLEAKPRO

# Créer l'environnement virtuel
sudo -u smartleakpro python3 -m venv venv
sudo -u smartleakpro source venv/bin/activate

# Installer les dépendances
sudo -u smartleakpro venv/bin/pip install -r requirements.txt

# Configuration des variables d'environnement
sudo -u smartleakpro cp .env.example .env
sudo -u smartleakpro nano .env

# Migrations de la base de données
sudo -u smartleakpro venv/bin/python manage.py migrate
sudo -u smartleakpro venv/bin/python manage.py createsuperuser
sudo -u smartleakpro venv/bin/python manage.py create_sample_data

# Collecter les fichiers statiques
sudo -u smartleakpro venv/bin/python manage.py collectstatic --noinput

# Configuration Gunicorn
sudo -u smartleakpro cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF

# Service systemd pour Gunicorn
sudo tee /etc/systemd/system/smartleakpro.service > /dev/null << EOF
[Unit]
Description=SmartLeakPro Django App
After=network.target

[Service]
Type=notify
User=smartleakpro
Group=smartleakpro
WorkingDirectory=/home/smartleakpro/SMARTLEAKPRO
Environment=PATH=/home/smartleakpro/SMARTLEAKPRO/venv/bin
ExecStart=/home/smartleakpro/SMARTLEAKPRO/venv/bin/gunicorn --config gunicorn.conf.py smartleakpro.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Configuration Nginx
sudo tee /etc/nginx/sites-available/smartleakpro > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/smartleakpro/SMARTLEAKPRO;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /home/smartleakpro/SMARTLEAKPRO;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Activer le site
sudo ln -s /etc/nginx/sites-available/smartleakpro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Démarrer les services
sudo systemctl enable smartleakpro
sudo systemctl start smartleakpro
sudo systemctl enable nginx
sudo systemctl start nginx

# Configuration SSL avec Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

echo "✅ Déploiement terminé !"
echo "🌐 Votre application est disponible sur : https://your-domain.com"
echo "🔧 Administration : https://your-domain.com/admin/"
