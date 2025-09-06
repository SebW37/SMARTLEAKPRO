# Fonctionnalités de Géolocalisation et Mode Hors-ligne

## Vue d'ensemble

SmartLeakPro intègre des fonctionnalités avancées de géolocalisation et de gestion hors-ligne pour permettre aux techniciens de travailler efficacement sur le terrain, même sans connexion internet.

## 🌍 Fonctionnalités de Géolocalisation

### 1. Geocoding et Reverse Geocoding

#### Geocoding (Adresse → Coordonnées)
- **API Endpoint**: `POST /api/core/geolocation/geocode/`
- **Fonctionnalité**: Convertit une adresse en coordonnées GPS
- **Utilisation**: Recherche automatique de localisation lors de la création d'interventions

```javascript
// Exemple d'utilisation
const result = await geocodeAddress("123 Rue de la Paix, 75001 Paris");
if (result.success) {
  console.log(result.location); // { latitude: 48.8566, longitude: 2.3522 }
}
```

#### Reverse Geocoding (Coordonnées → Adresse)
- **API Endpoint**: `POST /api/core/geolocation/reverse/`
- **Fonctionnalité**: Convertit des coordonnées GPS en adresse lisible
- **Utilisation**: Affichage d'adresses lors du suivi de position

```javascript
// Exemple d'utilisation
const result = await reverseGeocode(48.8566, 2.3522);
if (result.success) {
  console.log(result.address.display_name);
}
```

### 2. Calcul de Distance

- **API Endpoint**: `POST /api/core/geolocation/distance/`
- **Fonctionnalité**: Calcule la distance entre deux points
- **Utilisation**: Optimisation des trajets, calcul de proximité

```javascript
// Exemple d'utilisation
const distance = await calculateDistance(
  { latitude: 48.8566, longitude: 2.3522 },
  { latitude: 48.8606, longitude: 2.3376 }
);
console.log(distance.distance.kilometers); // Distance en kilomètres
```

### 3. Recherche de Proximité

- **API Endpoint**: `POST /api/core/geolocation/nearby/`
- **Fonctionnalité**: Trouve des éléments à proximité d'un point donné
- **Types supportés**: Clients, Interventions, Inspections
- **Utilisation**: Découverte d'éléments proches lors des inspections

```javascript
// Exemple d'utilisation
const nearby = await findNearby(48.8566, 2.3522, 1000, 'clients');
console.log(nearby.results); // Liste des clients dans un rayon de 1km
```

### 4. Suivi de Position en Temps Réel

#### Démarrage du Suivi
- **API Endpoint**: `POST /api/core/geolocation/tracking/start/`
- **Fonctionnalité**: Démarre le suivi de position pour une inspection
- **Utilisation**: Enregistrement automatique du parcours du technicien

#### Enregistrement de Position
- **API Endpoint**: `POST /api/core/geolocation/tracking/record/`
- **Fonctionnalité**: Enregistre un point de position
- **Utilisation**: Tracking automatique ou manuel

#### Arrêt du Suivi
- **API Endpoint**: `POST /api/core/geolocation/tracking/stop/`
- **Fonctionnalité**: Arrête le suivi et retourne les données collectées

## 📱 Mode Hors-ligne

### 1. Préparation des Données Hors-ligne

#### Préparation des Données
- **API Endpoint**: `POST /api/core/offline/prepare/`
- **Fonctionnalité**: Prépare les données nécessaires pour le mode hors-ligne
- **Types de données**: Clients, Interventions, Inspections

```javascript
// Exemple d'utilisation
const offlineData = await prepareOfflineData(['clients', 'interventions', 'inspections']);
```

### 2. Stockage Local

#### Stockage de Données
- **API Endpoint**: `POST /api/core/offline/store/`
- **Fonctionnalité**: Stocke des données pour utilisation hors-ligne
- **Utilisation**: Cache des données critiques

#### Récupération de Données
- **API Endpoint**: `GET /api/core/offline/data/`
- **Fonctionnalité**: Récupère les données stockées localement

### 3. Queue de Synchronisation

#### Ajout à la Queue
- **API Endpoint**: `POST /api/core/offline/queue/`
- **Fonctionnalité**: Ajoute une action à la queue de synchronisation
- **Actions supportées**: create, update, delete

```javascript
// Exemple d'utilisation
await queueSyncAction('create', 'inspection', 'temp_123', inspectionData);
```

#### Traitement de la Queue
- **API Endpoint**: `POST /api/core/offline/sync/`
- **Fonctionnalité**: Traite les actions en attente de synchronisation
- **Utilisation**: Synchronisation automatique ou manuelle

### 4. Gestion des Conflits

#### Détection de Conflits
- **API Endpoint**: `GET /api/core/offline/conflicts/`
- **Fonctionnalité**: Liste les conflits de synchronisation
- **Utilisation**: Résolution manuelle des conflits

#### Résolution de Conflits
- **API Endpoint**: `POST /api/core/offline/conflicts/resolve/`
- **Fonctionnalité**: Résout un conflit de synchronisation
- **Options**: use_server, use_client, merge

## 🔧 Composants React

### 1. LocationPicker
Composant pour la sélection et la saisie de localisation.

```jsx
<LocationPicker
  initialLocation={location}
  onLocationChange={handleLocationChange}
  showAddressInput={true}
/>
```

### 2. LocationTracker
Composant pour le suivi de position en temps réel.

```jsx
<LocationTracker
  inspectionId={inspectionId}
  onTrackingStart={handleTrackingStart}
  onTrackingStop={handleTrackingStop}
  autoRecord={true}
  recordInterval={30}
/>
```

### 3. OfflineManager
Composant pour la gestion du mode hors-ligne.

```jsx
<OfflineManager />
```

### 4. OfflineIndicator
Indicateur de statut de connexion et de synchronisation.

```jsx
<OfflineIndicator />
```

## 🎯 Hooks React

### useOfflineMode
Hook pour gérer l'état du mode hors-ligne.

```javascript
const {
  isOnline,
  isOfflineMode,
  pendingChanges,
  isSyncing,
  performSync,
  enableAutoSync
} = useOfflineMode();
```

## 📊 Services JavaScript

### GeolocationService
Service pour les opérations de géolocalisation.

```javascript
import { 
  geocodeAddress, 
  reverseGeocode, 
  calculateDistance, 
  findNearby 
} from './services/geolocationService';
```

### OfflineService
Service pour la gestion hors-ligne.

```javascript
import { 
  prepareOfflineData, 
  queueSyncAction, 
  processSync 
} from './services/offlineService';
```

## 🗄️ Configuration Base de Données

### Extensions PostGIS
La base de données utilise PostGIS pour les fonctionnalités géospatiales :

```sql
-- Activer PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
```

### Champs Géospatiaux
Les modèles incluent des champs `PointField` pour stocker les coordonnées :

```python
# Exemple dans un modèle Django
location = gis_models.PointField(blank=True, null=True, verbose_name="Localisation")
```

## ⚙️ Configuration

### Settings Django
```python
# Configuration géolocalisation
GEOLOCATION_SETTINGS = {
    'DEFAULT_SRID': 4326,  # WGS84
    'CACHE_TIMEOUT': 86400,  # 24 heures
    'NOMINATIM_USER_AGENT': 'SmartLeakPro/1.0',
    'NOMINATIM_TIMEOUT': 10,
}

# Configuration mode hors-ligne
OFFLINE_SETTINGS = {
    'CACHE_TIMEOUT': 604800,  # 7 jours
    'SYNC_QUEUE_TIMEOUT': 604800,  # 7 jours
    'CONFLICT_TIMEOUT': 2592000,  # 30 jours
    'AUTO_SYNC_INTERVAL': 30000,  # 30 secondes
}
```

## 🚀 Utilisation Pratique

### 1. Inspection avec Géolocalisation
1. Le technicien ouvre une inspection
2. Le système récupère automatiquement sa position GPS
3. Le technicien peut rechercher des éléments à proximité
4. Le suivi de position est activé automatiquement
5. Les données sont synchronisées en temps réel ou en mode hors-ligne

### 2. Mode Hors-ligne
1. Le technicien prépare ses données avant de partir sur le terrain
2. En cas de perte de connexion, l'application passe en mode hors-ligne
3. Les modifications sont stockées localement
4. Lors de la reconnexion, la synchronisation se fait automatiquement
5. Les conflits sont détectés et peuvent être résolus manuellement

## 🔒 Sécurité et Confidentialité

### Données de Géolocalisation
- Les coordonnées GPS sont stockées de manière sécurisée
- Le suivi de position nécessite l'autorisation de l'utilisateur
- Les données peuvent être supprimées à la demande

### Mode Hors-ligne
- Les données sensibles sont chiffrées localement
- La synchronisation utilise des tokens d'authentification
- Les conflits sont résolus de manière sécurisée

## 📈 Performance

### Optimisations
- Cache des résultats de geocoding (24h)
- Synchronisation par lots
- Compression des données hors-ligne
- Mise en cache intelligente

### Monitoring
- Logs détaillés des opérations de géolocalisation
- Métriques de synchronisation
- Alertes en cas de problème

## 🛠️ Maintenance

### Nettoyage des Données
- Suppression automatique des données de tracking anciennes
- Nettoyage des caches expirés
- Archivage des conflits résolus

### Sauvegarde
- Sauvegarde régulière des données géospatiales
- Export des données de tracking
- Restauration en cas de problème
