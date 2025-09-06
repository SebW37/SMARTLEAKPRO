# SmartLeakPro

Application web de gestion centralisée des clients, interventions et rapports d'inspection pour la détection de fuites.

## 🌊 Fonctionnalités

- **Gestion des clients** - Gestion complète des clients et de leurs sites
- **Interface d'administration** - Interface Django Admin simplifiée
- **Géolocalisation** - Support des coordonnées GPS (latitude/longitude)
- **Interface web moderne** - Interface responsive avec Bootstrap
- **Gestion des utilisateurs** - Création et gestion des utilisateurs simplifiée

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Installation locale

1. **Cloner le repository**
```bash
git clone https://github.com/votre-username/SmartLeakPro.git
cd SmartLeakPro
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer la base de données**
```bash
python manage_simple.py makemigrations
python manage_simple.py migrate
```

5. **Créer un superutilisateur**
```bash
python manage_simple.py createsuperuser
```

6. **Créer des données de test**
```bash
python manage_simple.py create_sample_data
```

7. **Lancer le serveur**
```bash
python manage_simple.py runserver
```

## 📱 Utilisation

### Accès à l'application
- **Interface utilisateur** : http://localhost:8000/
- **Administration** : http://localhost:8000/admin/
- **API REST** : http://localhost:8000/api/ (à venir)

### Identifiants par défaut
- **Nom d'utilisateur** : admin
- **Mot de passe** : admin123

### Création d'utilisateurs
```bash
python manage_simple.py create_user --username technicien1 --email tech1@example.com
```

## 🏗️ Architecture

### Backend
- **Framework** : Django 4.2
- **Base de données** : SQLite (développement)
- **API** : Django REST Framework (à venir)

### Frontend
- **Framework** : HTML/CSS/JavaScript
- **UI** : Bootstrap 5
- **Templates** : Django Templates

### Applications Django
- `clients` - Gestion des clients et sites
- `interventions` - Gestion des interventions (à venir)
- `inspections` - Rapports d'inspection (à venir)

## 📋 Fonctionnalités à venir

- [ ] Module interventions
- [ ] Module inspections
- [ ] API REST complète
- [ ] Frontend React
- [ ] Application mobile
- [ ] Géolocalisation avancée
- [ ] Rapports PDF
- [ ] Notifications

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.

---

**SmartLeakPro** - Solution professionnelle pour la gestion des fuites