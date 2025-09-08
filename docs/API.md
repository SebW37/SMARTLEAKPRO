# Documentation API - SmartLeakPro

## 🔗 Base URL
```
https://api.smartleakpro.com/api
```

## 🔐 Authentification

### JWT Token
L'API utilise l'authentification JWT. Inclure le token dans l'en-tête Authorization :

```http
Authorization: Bearer <your-jwt-token>
```

### Clé API
Alternative à JWT pour les intégrations :

```http
X-API-Key: <your-api-key>
```

## 📋 Endpoints

### Authentification

#### POST /auth/login
Connexion utilisateur

**Body:**
```json
{
  "nom_utilisateur": "string",
  "mot_de_passe": "string",
  "code_2fa": "string" // optionnel
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 1800,
  "utilisateur": {
    "id": "uuid",
    "nom_utilisateur": "string",
    "email": "string",
    "role": "string"
  }
}
```

#### POST /auth/refresh
Rafraîchir le token

**Body:**
```json
{
  "refresh_token": "string"
}
```

#### POST /auth/logout
Déconnexion

### Clients

#### GET /clients/
Liste des clients avec pagination

**Query Parameters:**
- `page` (int): Numéro de page (défaut: 1)
- `size` (int): Taille de page (défaut: 10)
- `search` (string): Recherche textuelle
- `statut` (string): Filtrer par statut

**Response:**
```json
{
  "clients": [
    {
      "id": "uuid",
      "nom": "string",
      "email": "string",
      "telephone": "string",
      "adresse": "string",
      "statut": "string",
      "date_creation": "datetime"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

#### POST /clients/
Créer un client

**Body:**
```json
{
  "nom": "string",
  "email": "string",
  "telephone": "string",
  "adresse": "string",
  "statut": "actif"
}
```

#### GET /clients/{id}
Récupérer un client par ID

#### PUT /clients/{id}
Mettre à jour un client

#### DELETE /clients/{id}
Supprimer un client

### Interventions

#### GET /interventions/
Liste des interventions

**Query Parameters:**
- `page`, `size`, `search`
- `client_id` (uuid): Filtrer par client
- `statut` (string): Filtrer par statut
- `type_intervention` (string): Filtrer par type
- `date_debut` (date): Date de début
- `date_fin` (date): Date de fin

**Response:**
```json
{
  "interventions": [
    {
      "id": "uuid",
      "client_id": "uuid",
      "date_intervention": "datetime",
      "type_intervention": "string",
      "statut": "string",
      "lieu": "string",
      "description": "string",
      "technicien_assigné": "string"
    }
  ],
  "total": 50,
  "page": 1,
  "size": 10,
  "pages": 5
}
```

#### POST /interventions/
Créer une intervention

**Body:**
```json
{
  "client_id": "uuid",
  "date_intervention": "datetime",
  "type_intervention": "inspection",
  "statut": "planifie",
  "lieu": "string",
  "description": "string",
  "technicien_assigné": "string"
}
```

#### POST /interventions/{id}/change-status
Changer le statut d'une intervention

**Body:**
```json
{
  "nouveau_statut": "en_cours",
  "commentaire": "string" // optionnel
}
```

### Planning

#### GET /planning/
Liste des rendez-vous

**Query Parameters:**
- `date_debut` (date): Date de début
- `date_fin` (date): Date de fin
- `client_id` (uuid): Filtrer par client
- `statut` (string): Filtrer par statut

#### GET /planning/calendar
Événements du calendrier

**Query Parameters:**
- `start` (date): Date de début
- `end` (date): Date de fin

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "string",
    "start": "datetime",
    "end": "datetime",
    "color": "string",
    "client": "string",
    "intervention_id": "uuid"
  }
]
```

### Rapports

#### GET /rapports/
Liste des rapports

#### POST /rapports/generate
Générer un rapport

**Body:**
```json
{
  "intervention_id": "uuid",
  "type_rapport": "inspection",
  "format": "pdf",
  "template": "default"
}
```

#### GET /rapports/{id}/download
Télécharger un rapport

### Médias

#### GET /medias/
Liste des médias

**Query Parameters:**
- `intervention_id` (uuid): Filtrer par intervention
- `type_media` (string): Filtrer par type
- `search` (string): Recherche textuelle

#### POST /medias/upload
Upload de média

**Body:** (multipart/form-data)
- `file`: Fichier à uploader
- `intervention_id`: ID de l'intervention
- `description`: Description du média
- `tags`: Tags (JSON array)

#### GET /medias/{id}/download
Télécharger un média

### Utilisateurs

#### GET /utilisateurs/
Liste des utilisateurs (Admin uniquement)

#### POST /utilisateurs/
Créer un utilisateur (Admin uniquement)

**Body:**
```json
{
  "nom_utilisateur": "string",
  "email": "string",
  "nom": "string",
  "prenom": "string",
  "mot_de_passe": "string",
  "confirmer_mot_de_passe": "string",
  "role": "admin",
  "consentement_rgpd": true
}
```

### Clés API

#### GET /api-keys/
Liste des clés API

#### POST /api-keys/
Créer une clé API

**Body:**
```json
{
  "nom": "string",
  "description": "string",
  "scopes": ["read", "write"],
  "limite_requetes_par_minute": 100,
  "limite_requetes_par_jour": 1000,
  "limite_requetes_par_mois": 30000
}
```

### Webhooks

#### GET /webhooks/
Liste des webhooks

#### POST /webhooks/
Créer un webhook

**Body:**
```json
{
  "nom": "string",
  "description": "string",
  "url": "https://webhook.site/test",
  "type_webhook": "intervention_created",
  "secret": "string",
  "conditions": [
    {
      "field": "data.statut",
      "operator": "equals",
      "value": "en_cours"
    }
  ]
}
```

#### POST /webhooks/{id}/test
Tester un webhook

### Intégrations

#### GET /integrations/
Liste des intégrations

#### POST /integrations/
Créer une intégration

**Body:**
```json
{
  "nom": "string",
  "description": "string",
  "type_integration": "zapier",
  "configuration": {
    "webhook_url": "https://hooks.zapier.com/test",
    "api_key": "string"
  }
}
```

## 📊 Codes de statut HTTP

- `200` - Succès
- `201` - Créé
- `204` - Pas de contenu
- `400` - Requête invalide
- `401` - Non authentifié
- `403` - Accès interdit
- `404` - Non trouvé
- `422` - Erreur de validation
- `429` - Trop de requêtes
- `500` - Erreur serveur

## 🔒 Rate Limiting

L'API implémente un rate limiting :
- **Par défaut** : 100 requêtes/minute
- **Avec clé API** : Selon la configuration de la clé
- **Headers de réponse** :
  - `X-RateLimit-Limit` : Limite par minute
  - `X-RateLimit-Remaining` : Requêtes restantes
  - `X-RateLimit-Reset` : Timestamp de reset

## 📝 Exemples d'utilisation

### JavaScript (Fetch)
```javascript
const response = await fetch('https://api.smartleakpro.com/api/clients/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
```

### Python (Requests)
```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.smartleakpro.com/api/clients/',
    headers=headers
)

data = response.json()
```

### cURL
```bash
curl -X GET "https://api.smartleakpro.com/api/clients/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

## 🔄 Webhooks

### Types d'événements
- `intervention_created` - Nouvelle intervention
- `intervention_updated` - Intervention mise à jour
- `intervention_status_changed` - Statut changé
- `rapport_generated` - Rapport généré
- `media_uploaded` - Média uploadé
- `user_created` - Utilisateur créé
- `client_created` - Client créé

### Format des événements
```json
{
  "type": "intervention_created",
  "timestamp": "2024-01-01T10:00:00Z",
  "data": {
    "id": "uuid",
    "client_id": "uuid",
    "statut": "planifie"
  },
  "resource_id": "uuid"
}
```

### Signature HMAC
Les webhooks incluent une signature HMAC dans l'en-tête `X-Webhook-Signature` :
```
X-Webhook-Signature: sha256=<signature>
```

## 🐛 Gestion d'erreurs

### Format des erreurs
```json
{
  "detail": "Message d'erreur",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "email": ["Email invalide"]
  }
}
```

### Codes d'erreur
- `VALIDATION_ERROR` - Erreur de validation
- `AUTHENTICATION_ERROR` - Erreur d'authentification
- `AUTHORIZATION_ERROR` - Erreur d'autorisation
- `NOT_FOUND` - Ressource non trouvée
- `RATE_LIMIT_EXCEEDED` - Limite de taux dépassée
- `INTERNAL_ERROR` - Erreur interne

## 📈 Monitoring

### Métriques disponibles
- Temps de réponse des endpoints
- Nombre de requêtes par endpoint
- Taux d'erreur par endpoint
- Utilisation des clés API
- Exécution des webhooks

### Alertes
- Temps de réponse > 2s
- Taux d'erreur > 5%
- Échec de webhook > 3 tentatives
