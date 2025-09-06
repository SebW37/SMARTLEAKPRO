# SmartLeakPro API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
L'API utilise JWT (JSON Web Tokens) pour l'authentification. Incluez le token dans l'en-tête Authorization :

```
Authorization: Bearer <your-token>
```

## Endpoints

### Authentication

#### POST /auth/login/
Connexion utilisateur
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "role": "admin|manager|technician|client"
  }
}
```

#### POST /auth/logout/
Déconnexion utilisateur
```json
{
  "refresh": "string"
}
```

#### GET /auth/profile/
Récupérer le profil utilisateur

#### PATCH /auth/profile/update/
Mettre à jour le profil utilisateur

### Clients

#### GET /clients/
Liste des clients avec filtres et pagination

**Query Parameters:**
- `page`: Numéro de page (défaut: 1)
- `client_type`: Type de client (individual, company, public)
- `is_active`: Statut actif (true/false)
- `city`: Ville
- `search`: Recherche textuelle

**Response:**
```json
{
  "count": 100,
  "next": "http://api/clients/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "string",
      "client_type": "individual",
      "email": "string",
      "phone": "string",
      "address": "string",
      "city": "string",
      "postal_code": "string",
      "country": "string",
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /clients/{id}/
Détails d'un client

#### POST /clients/
Créer un nouveau client

#### PATCH /clients/{id}/
Modifier un client

#### DELETE /clients/{id}/
Supprimer un client

#### GET /clients/stats/
Statistiques des clients

### Interventions

#### GET /interventions/
Liste des interventions

**Query Parameters:**
- `page`: Numéro de page
- `status`: Statut (scheduled, in_progress, completed, cancelled, postponed)
- `priority`: Priorité (low, medium, high, urgent)
- `intervention_type`: Type d'intervention
- `client`: ID du client
- `assigned_technician`: ID du technicien assigné
- `search`: Recherche textuelle

#### GET /interventions/{id}/
Détails d'une intervention

#### POST /interventions/
Créer une nouvelle intervention

#### PATCH /interventions/{id}/
Modifier une intervention

#### DELETE /interventions/{id}/
Supprimer une intervention

#### POST /interventions/{id}/start/
Démarrer une intervention

#### POST /interventions/{id}/complete/
Terminer une intervention

#### GET /interventions/calendar/
Vue calendrier des interventions

#### GET /interventions/stats/
Statistiques des interventions

### Inspections

#### GET /inspections/
Liste des inspections

**Query Parameters:**
- `page`: Numéro de page
- `status`: Statut (draft, in_progress, completed, validated, rejected)
- `client`: ID du client
- `site`: ID du site
- `inspector`: ID de l'inspecteur
- `template`: ID du template
- `search`: Recherche textuelle

#### GET /inspections/{id}/
Détails d'une inspection

#### POST /inspections/
Créer une nouvelle inspection

#### PATCH /inspections/{id}/
Modifier une inspection

#### DELETE /inspections/{id}/
Supprimer une inspection

#### POST /inspections/{id}/start/
Démarrer une inspection

#### POST /inspections/{id}/complete/
Terminer une inspection

#### POST /inspections/{id}/validate/
Valider une inspection

#### GET /inspections/stats/
Statistiques des inspections

### Rapports

#### GET /reports/
Liste des rapports

#### GET /reports/{id}/
Détails d'un rapport

#### POST /reports/generate/
Générer un nouveau rapport

**Request Body:**
```json
{
  "template": 1,
  "title": "string",
  "description": "string",
  "format": "pdf|docx|html|xlsx",
  "client": 1,
  "intervention": 1,
  "inspection": 1,
  "content_config": {}
}
```

#### GET /reports/{id}/download/
Télécharger un rapport

#### GET /reports/{id}/view/
Consulter un rapport

#### GET /reports/stats/
Statistiques des rapports

### Notifications

#### GET /notifications/
Liste des notifications

#### GET /notifications/{id}/
Détails d'une notification

#### POST /notifications/send/
Envoyer une notification

#### POST /notifications/mark-read/
Marquer des notifications comme lues

#### GET /notifications/unread/
Notifications non lues

#### GET /notifications/stats/
Statistiques des notifications

## Codes de statut HTTP

- `200` - Succès
- `201` - Créé
- `400` - Requête invalide
- `401` - Non authentifié
- `403` - Accès refusé
- `404` - Non trouvé
- `500` - Erreur serveur

## Gestion des erreurs

Les erreurs sont retournées au format JSON :

```json
{
  "detail": "Message d'erreur",
  "errors": {
    "field_name": ["Message d'erreur spécifique"]
  }
}
```

## Pagination

Tous les endpoints de liste supportent la pagination :

```json
{
  "count": 100,
  "next": "http://api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtrage et recherche

La plupart des endpoints supportent :
- Filtrage par champs spécifiques
- Recherche textuelle avec le paramètre `search`
- Tri avec le paramètre `ordering`

## Limites de taux

- API générale : 10 requêtes/seconde
- Connexion : 5 tentatives/minute

## Exemples d'utilisation

### Créer un client
```bash
curl -X POST http://localhost:8000/api/clients/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Client Test",
    "client_type": "individual",
    "email": "client@test.com",
    "address": "123 Rue Test",
    "city": "Paris",
    "postal_code": "75001",
    "country": "France"
  }'
```

### Créer une intervention
```bash
curl -X POST http://localhost:8000/api/interventions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Inspection urgente",
    "description": "Inspection de fuite d'eau",
    "intervention_type": "inspection",
    "priority": "urgent",
    "client": 1,
    "scheduled_date": "2023-12-01T10:00:00Z"
  }'
```

### Générer un rapport
```bash
curl -X POST http://localhost:8000/api/reports/generate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "template": 1,
    "title": "Rapport d'inspection",
    "format": "pdf",
    "client": 1,
    "intervention": 1
  }'
```
