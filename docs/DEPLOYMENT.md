# Guide de Déploiement - SmartLeakPro

## 🚀 Déploiement en Production

### Prérequis
- Docker et Docker Compose installés
- Accès à un serveur Linux (Ubuntu 20.04+ recommandé)
- Domaine configuré avec certificats SSL
- Base de données PostgreSQL (optionnel, peut utiliser le conteneur)

### 1. Préparation du serveur

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Installer Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Installer Git
sudo apt install git -y
```

### 2. Configuration de l'application

```bash
# Cloner le repository
git clone https://github.com/votre-username/smartleakpro.git
cd smartleakpro

# Copier et configurer les variables d'environnement
cp .env.example .env
nano .env
```

Variables d'environnement importantes :
```env
# Base de données
DATABASE_URL=postgresql://smartleakpro:password@db:5432/smartleakpro

# Sécurité
SECRET_KEY=your-very-secure-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://redis:6379

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### 3. Configuration SSL (Nginx)

```bash
# Créer le répertoire pour les certificats
sudo mkdir -p /etc/nginx/ssl

# Copier vos certificats SSL
sudo cp your-cert.pem /etc/nginx/ssl/
sudo cp your-key.pem /etc/nginx/ssl/

# Configurer Nginx
sudo nano /etc/nginx/sites-available/smartleakpro
```

Configuration Nginx :
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/your-cert.pem;
    ssl_certificate_key /etc/nginx/ssl/your-key.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4. Déploiement avec Docker

```bash
# Construire et lancer l'application
docker-compose up --build -d

# Vérifier le statut
docker-compose ps

# Vérifier les logs
docker-compose logs -f
```

### 5. Initialisation de la base de données

```bash
# Exécuter les migrations
docker-compose exec backend python -m alembic upgrade head

# Créer un utilisateur administrateur
docker-compose exec backend python -c "
from backend.database import get_db
from backend.models import Utilisateur
from backend.services.security_service import security_service
import asyncio

async def create_admin():
    db = next(get_db())
    admin = Utilisateur(
        nom_utilisateur='admin',
        email='admin@smartleakpro.com',
        nom='Administrateur',
        prenom='Admin',
        mot_de_passe_hash=security_service.get_password_hash('admin123'),
        role='admin',
        statut='actif',
        consentement_rgpd=True
    )
    db.add(admin)
    db.commit()
    print('Utilisateur admin créé')

asyncio.run(create_admin())
"
```

### 6. Configuration du monitoring

```bash
# Accéder à Grafana
# URL: https://your-domain.com:3000
# Login: admin / admin

# Configurer les dashboards
# Les dashboards sont automatiquement provisionnés
```

### 7. Sauvegarde automatique

Créer un script de sauvegarde :

```bash
sudo nano /usr/local/bin/backup-smartleakpro.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backups/smartleakpro"
DATE=$(date +%Y%m%d_%H%M%S)

# Créer le répertoire de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarder la base de données
docker-compose exec -T db pg_dump -U smartleakpro smartleakpro > $BACKUP_DIR/db_$DATE.sql

# Sauvegarder les uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /var/lib/docker/volumes/smartleakpro_uploads/_data .

# Nettoyer les anciennes sauvegardes (garder 30 jours)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
# Rendre le script exécutable
sudo chmod +x /usr/local/bin/backup-smartleakpro.sh

# Programmer la sauvegarde quotidienne
sudo crontab -e
# Ajouter : 0 2 * * * /usr/local/bin/backup-smartleakpro.sh
```

## 🔄 Mise à jour de l'application

```bash
# Arrêter l'application
docker-compose down

# Mettre à jour le code
git pull origin main

# Reconstruire et relancer
docker-compose up --build -d

# Vérifier les migrations
docker-compose exec backend python -m alembic upgrade head
```

## 🚨 Gestion des incidents

### Vérification du statut
```bash
# Statut des conteneurs
docker-compose ps

# Logs en temps réel
docker-compose logs -f

# Utilisation des ressources
docker stats
```

### Redémarrage des services
```bash
# Redémarrer un service spécifique
docker-compose restart backend

# Redémarrer tous les services
docker-compose restart

# Redémarrer avec reconstruction
docker-compose up --build -d
```

### Restauration depuis sauvegarde
```bash
# Arrêter l'application
docker-compose down

# Restaurer la base de données
docker-compose exec -T db psql -U smartleakpro smartleakpro < /backups/smartleakpro/db_YYYYMMDD_HHMMSS.sql

# Restaurer les uploads
tar -xzf /backups/smartleakpro/uploads_YYYYMMDD_HHMMSS.tar.gz -C /var/lib/docker/volumes/smartleakpro_uploads/_data

# Relancer l'application
docker-compose up -d
```

## 📊 Monitoring et alertes

### Métriques surveillées
- Temps de réponse des API
- Utilisation CPU/Mémoire
- Erreurs et exceptions
- Requêtes base de données
- Logs d'audit

### Alertes configurées
- Temps de réponse > 2s
- Taux d'erreur > 5%
- Utilisation mémoire > 80%
- Espace disque < 20%

### Accès aux outils
- **Grafana** : https://your-domain.com:3000
- **Prometheus** : https://your-domain.com:9090
- **Kibana** : https://your-domain.com:5601

## 🔧 Maintenance

### Tâches quotidiennes
- Vérification des logs d'erreur
- Surveillance des métriques
- Vérification des sauvegardes

### Tâches hebdomadaires
- Mise à jour des dépendances
- Nettoyage des logs anciens
- Vérification de la sécurité

### Tâches mensuelles
- Mise à jour du système
- Révision des permissions
- Test de restauration

## 📞 Support

En cas de problème :
1. Vérifier les logs : `docker-compose logs -f`
2. Consulter les métriques dans Grafana
3. Vérifier l'espace disque : `df -h`
4. Contacter l'équipe de support
