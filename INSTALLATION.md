# Guide d'Installation - SmartLeakPro

## Prérequis

### 1. Python 3.8+
```bash
python --version
```

### 2. PostgreSQL avec PostGIS
- Installer PostgreSQL 12+
- Installer l'extension PostGIS

#### Sur Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis postgresql-12-postgis-3
```

#### Sur Windows:
- Télécharger PostgreSQL depuis https://www.postgresql.org/download/windows/
- Installer PostGIS via Stack Builder

#### Sur macOS:
```bash
brew install postgresql postgis
```

### 3. Redis (pour le cache et les tâches asynchrones)
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows
# Télécharger depuis https://github.com/microsoftarchive/redis/releases
```

## Installation

### 1. Cloner le projet
```bash
git clone <repository-url>
cd SmartLeakPro1
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

#### Activer PostGIS sur PostgreSQL:
```sql
-- Se connecter à PostgreSQL en tant que superutilisateur
psql -U postgres

-- Créer la base de données
CREATE DATABASE smartleakpro;

-- Se connecter à la base de données
\c smartleakpro

-- Activer PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

#### Ou utiliser le script fourni:
```bash
# Configurer les variables d'environnement
export DB_NAME=smartleakpro
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432

# Exécuter le script (Linux/macOS)
chmod +x scripts/setup_postgis.sh
./scripts/setup_postgis.sh
```

### 5. Configuration des variables d'environnement
```bash
# Copier le fichier d'exemple
cp env.example .env

# Éditer le fichier .env avec vos paramètres
nano .env
```

Variables importantes dans `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=smartleakpro
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
```

### 6. Migrations de la base de données
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

### 8. Collecter les fichiers statiques
```bash
python manage.py collectstatic
```

## Installation Frontend

### 1. Installer Node.js et npm
- Télécharger depuis https://nodejs.org/

### 2. Installer les dépendances
```bash
cd frontend
npm install
```

### 3. Configuration
```bash
# Copier le fichier d'exemple
cp env.example .env

# Éditer avec vos paramètres
nano .env
```

Variables importantes dans `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## Démarrage

### 1. Démarrer Redis
```bash
# Linux/macOS
redis-server

# Windows
redis-server.exe
```

### 2. Démarrer le serveur Django
```bash
python manage.py runserver
```

### 3. Démarrer le serveur de développement React
```bash
cd frontend
npm start
```

### 4. Démarrer Celery (optionnel, pour les tâches asynchrones)
```bash
# Terminal séparé
celery -A smartleakpro worker -l info
celery -A smartleakpro beat -l info
```

## Accès

- **Application web**: http://localhost:3000
- **API**: http://localhost:8000/api
- **Admin Django**: http://localhost:8000/admin
- **Documentation API**: http://localhost:8000/swagger/

## Fonctionnalités Géolocalisation et Hors-ligne

### Géolocalisation
- **Geocoding**: Conversion d'adresses en coordonnées GPS
- **Reverse Geocoding**: Conversion de coordonnées en adresses
- **Tracking**: Suivi de position en temps réel pendant les inspections
- **Recherche de proximité**: Trouver des clients/interventions à proximité

### Mode Hors-ligne
- **Cache de données**: Stockage local des données pour utilisation hors-ligne
- **Synchronisation**: Synchronisation automatique des modifications
- **Gestion des conflits**: Résolution des conflits de synchronisation
- **Queue de synchronisation**: File d'attente des actions à synchroniser

## Dépannage

### Erreur PostGIS
```bash
# Vérifier que PostGIS est installé
psql -d smartleakpro -c "SELECT PostGIS_Version();"
```

### Erreur Redis
```bash
# Vérifier que Redis fonctionne
redis-cli ping
```

### Erreur de migration
```bash
# Réinitialiser les migrations (ATTENTION: supprime les données)
python manage.py migrate --fake-initial
```

### Problèmes de permissions
```bash
# Linux/macOS
sudo chown -R $USER:$USER .
chmod -R 755 .
```

## Support

Pour toute question ou problème, consultez la documentation ou contactez l'équipe de développement.
