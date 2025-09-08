# 🚀 Déploiement SmartLeakPro sur Railway

## 📋 Étapes de déploiement

### 1. **Préparation du repository GitHub**
- ✅ Code pushé sur GitHub
- ✅ Fichiers de configuration Railway créés
- ✅ Settings de production configurés

### 2. **Déploiement sur Railway**

#### **Option A : Via l'interface Railway**
1. Aller sur [railway.app](https://railway.app)
2. Se connecter avec GitHub
3. Cliquer sur "New Project"
4. Sélectionner "Deploy from GitHub repo"
5. Choisir le repository `SebW37/SMARTLEAKPRO`
6. Railway détectera automatiquement Django

#### **Option B : Via Railway CLI**
```bash
# Installer Railway CLI
npm install -g @railway/cli

# Se connecter
railway login

# Initialiser le projet
railway init

# Déployer
railway up
```

### 3. **Configuration de la base de données**

#### **Ajouter PostgreSQL :**
1. Dans le dashboard Railway
2. Cliquer sur "New Service"
3. Sélectionner "Database" → "PostgreSQL"
4. Railway créera automatiquement les variables d'environnement

#### **Variables d'environnement :**
```
SECRET_KEY=your-secret-key-here
DEBUG=False
RAILWAY_ENVIRONMENT=production
```

### 4. **Migration de la base de données**
```bash
# Via Railway CLI
railway run python manage.py migrate

# Ou via le dashboard Railway
# Terminal → python manage.py migrate
```

### 5. **Création du superutilisateur**
```bash
# Via Railway CLI
railway run python manage.py createsuperuser

# Ou via le dashboard Railway
# Terminal → python manage.py createsuperuser
```

### 6. **Création des données de test**
```bash
# Via Railway CLI
railway run python manage.py create_sample_data
railway run python manage.py create_intervention_data
```

## 🔧 **Configuration automatique**

Railway détectera automatiquement :
- ✅ `requirements.txt` - Dépendances Python
- ✅ `Procfile` - Commande de démarrage
- ✅ `railway.json` - Configuration Railway
- ✅ `runtime.txt` - Version Python

## 🌐 **URL de déploiement**

Une fois déployé, Railway fournira une URL comme :
`https://smartleakpro-production.up.railway.app`

## 📊 **Monitoring**

- **Logs** : Disponibles dans le dashboard Railway
- **Métriques** : CPU, RAM, requêtes
- **Base de données** : PostgreSQL managé

## 🔄 **Mise à jour**

Pour mettre à jour l'application :
```bash
# Push sur GitHub
git add .
git commit -m "Update application"
git push origin main

# Railway redéploiera automatiquement
```

## 🛠️ **Dépannage**

### **Problèmes courants :**
1. **Erreur de base de données** : Vérifier les variables d'environnement PostgreSQL
2. **Erreur de statiques** : Vérifier WhiteNoise configuration
3. **Erreur de migration** : Exécuter `python manage.py migrate`

### **Logs utiles :**
```bash
# Voir les logs
railway logs

# Accéder au terminal
railway shell
```

## ✅ **Vérification du déploiement**

1. **Page d'accueil** : `https://votre-app.railway.app/`
2. **Administration** : `https://votre-app.railway.app/admin/`
3. **Interventions** : `https://votre-app.railway.app/interventions/`
4. **Clients** : `https://votre-app.railway.app/clients/`

## 🎯 **Prochaines étapes**

1. **Configurer un domaine personnalisé** (optionnel)
2. **Activer HTTPS** (automatique sur Railway)
3. **Configurer les sauvegardes** de la base de données
4. **Monitorer les performances**

---

**SmartLeakPro** est maintenant prêt pour la production ! 🚀
