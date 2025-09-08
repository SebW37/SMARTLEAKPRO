# 🚀 Déploiement SmartLeakPro sur Hostinger KVM2

## 🎯 **Avantages Hostinger KVM2**

### ✅ **Parfait pour SmartLeakPro :**
- **VPS complet** : Contrôle total du serveur
- **PostgreSQL** : Base de données native
- **Performance** : Ressources dédiées
- **Coût** : Plus économique que Railway
- **Flexibilité** : Configuration personnalisée
- **SSL gratuit** : Let's Encrypt

## 📋 **Spécifications recommandées**

### **Configuration serveur :**
- **RAM** : 2-4 GB minimum
- **CPU** : 2-4 vCPU
- **Stockage** : 50-100 GB SSD
- **OS** : Ubuntu 20.04/22.04 LTS
- **Bande passante** : Illimitée

## 🔧 **Étapes de déploiement**

### **1. Préparation du serveur**

#### **Connexion SSH :**
```bash
ssh root@your-server-ip
```

#### **Mise à jour du système :**
```bash
apt update && apt upgrade -y
```

### **2. Installation des dépendances**

#### **Python et PostgreSQL :**
```bash
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git
```

#### **Node.js (pour le frontend) :**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt install -y nodejs
```

### **3. Configuration PostgreSQL**

#### **Créer la base de données :**
```bash
sudo -u postgres psql
CREATE DATABASE smartleakpro;
CREATE USER smartleakpro WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE smartleakpro TO smartleakpro;
\q
```

### **4. Déploiement de l'application**

#### **Cloner le repository :**
```bash
cd /home
git clone https://github.com/SebW37/SMARTLEAKPRO.git
cd SMARTLEAKPRO
```

#### **Créer l'environnement virtuel :**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### **Installer les dépendances :**
```bash
pip install -r requirements.txt
pip install dj-database-url
```

### **5. Configuration de l'application**

#### **Variables d'environnement :**
```bash
cp env.example .env
nano .env
```

#### **Contenu du fichier .env :**
```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost
DATABASE_URL=postgresql://smartleakpro:your_secure_password@localhost:5432/smartleakpro
```

#### **Migrations :**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py create_sample_data
python manage.py collectstatic --noinput
```

### **6. Configuration Gunicorn**

#### **Créer le fichier de configuration :**
```bash
cat > gunicorn.conf.py << EOF
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
```

#### **Service systemd :**
```bash
cat > /etc/systemd/system/smartleakpro.service << EOF
[Unit]
Description=SmartLeakPro Django App
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/home/SMARTLEAKPRO
Environment=PATH=/home/SMARTLEAKPRO/venv/bin
ExecStart=/home/SMARTLEAKPRO/venv/bin/gunicorn --config gunicorn.conf.py smartleakpro.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

### **7. Configuration Nginx**

#### **Fichier de configuration :**
```bash
cat > /etc/nginx/sites-available/smartleakpro << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/SMARTLEAKPRO;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /home/SMARTLEAKPRO;
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
```

#### **Activer le site :**
```bash
ln -s /etc/nginx/sites-available/smartleakpro /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### **8. SSL avec Let's Encrypt**

#### **Installation :**
```bash
apt install -y certbot python3-certbot-nginx
```

#### **Configuration SSL :**
```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

### **9. Démarrage des services**

```bash
systemctl enable smartleakpro
systemctl start smartleakpro
systemctl enable nginx
systemctl start nginx
```

## 🔄 **Mise à jour de l'application**

### **Script de mise à jour :**
```bash
#!/bin/bash
cd /home/SMARTLEAKPRO
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
systemctl restart smartleakpro
```

## 📊 **Monitoring et maintenance**

### **Logs :**
```bash
# Logs de l'application
journalctl -u smartleakpro -f

# Logs Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### **Sauvegarde de la base de données :**
```bash
# Sauvegarde
pg_dump -h localhost -U smartleakpro smartleakpro > backup_$(date +%Y%m%d).sql

# Restauration
psql -h localhost -U smartleakpro smartleakpro < backup_20240101.sql
```

## 💰 **Coûts estimés**

### **Hostinger KVM2 :**
- **VPS Business** : ~15-25€/mois
- **VPS Premium** : ~25-40€/mois
- **Domaine** : ~10€/an
- **SSL** : Gratuit (Let's Encrypt)

### **Total mensuel :** ~15-40€/mois

## ✅ **Vérification du déploiement**

1. **Page d'accueil** : `https://your-domain.com/`
2. **Administration** : `https://your-domain.com/admin/`
3. **Interventions** : `https://your-domain.com/interventions/`
4. **Clients** : `https://your-domain.com/clients/`

## 🎯 **Avantages vs Railway**

| Critère | Hostinger KVM2 | Railway |
|---------|----------------|---------|
| **Coût** | 15-40€/mois | 5-50€/mois |
| **Contrôle** | Total | Limité |
| **Performance** | Dédiée | Partagée |
| **Base de données** | PostgreSQL natif | PostgreSQL managé |
| **SSL** | Let's Encrypt gratuit | Automatique |
| **Maintenance** | Manuelle | Automatique |

---

**Hostinger KVM2 est parfait pour SmartLeakPro !** 🚀
