"""
Schémas Pydantic pour validation des données API
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from enum import Enum


class ClientBase(BaseModel):
    """Schéma de base pour Client"""
    nom: str = Field(..., min_length=1, max_length=255, description="Nom du client")
    raison_sociale: Optional[str] = Field(None, max_length=255, description="Raison sociale")
    adresse: Optional[str] = Field(None, description="Adresse complète")
    telephone: Optional[str] = Field(None, max_length=20, description="Téléphone principal")
    email: Optional[EmailStr] = Field(None, description="Email principal")
    notes: Optional[str] = Field(None, description="Notes additionnelles")
    contact_principal: Optional[str] = Field(None, max_length=255, description="Contact principal")


class ClientCreate(ClientBase):
    """Schéma pour création de client"""
    statut: str = Field(default="actif", description="Statut du client")


class ClientUpdate(BaseModel):
    """Schéma pour mise à jour de client"""
    nom: Optional[str] = Field(None, min_length=1, max_length=255)
    raison_sociale: Optional[str] = Field(None, max_length=255)
    adresse: Optional[str] = None
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    statut: Optional[str] = Field(None, description="Statut: actif ou inactif")
    notes: Optional[str] = None
    contact_principal: Optional[str] = Field(None, max_length=255)


class ClientResponse(ClientBase):
    """Schéma de réponse pour Client"""
    id: UUID
    statut: str
    date_creation: datetime
    date_modification: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    """Schéma pour liste paginée de clients"""
    clients: list[ClientResponse]
    total: int
    page: int
    size: int
    pages: int


# Schémas d'authentification
class UserLogin(BaseModel):
    """Schéma pour connexion utilisateur"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class Token(BaseModel):
    """Schéma pour token JWT"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Données du token"""
    username: Optional[str] = None


# Enums pour les interventions
class StatutInterventionEnum(str, Enum):
    PLANIFIE = "planifié"
    EN_COURS = "en_cours"
    VALIDE = "validé"
    ARCHIVE = "archivé"


class TypeInterventionEnum(str, Enum):
    INSPECTION = "inspection"
    DETECTION = "détection"
    REPARATION = "réparation"
    MAINTENANCE = "maintenance"
    AUTRE = "autre"


class StatutInspectionEnum(str, Enum):
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    TERMINEE = "terminée"
    ANNULEE = "annulée"


class StatutRendezVousEnum(str, Enum):
    PLANIFIE = "planifié"
    CONFIRME = "confirmé"
    ANNULE = "annulé"
    TERMINE = "terminé"


class TypeRapportEnum(str, Enum):
    INSPECTION = "inspection"
    VALIDATION = "validation"
    INTERVENTION = "intervention"
    MAINTENANCE = "maintenance"
    AUTRE = "autre"


class StatutRapportEnum(str, Enum):
    BROUILLON = "brouillon"
    VALIDE = "validé"
    ARCHIVE = "archivé"


class TypeMediaEnum(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    AUTRE = "autre"


class StatutMediaEnum(str, Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"


# Schémas pour les Interventions
class InterventionBase(BaseModel):
    """Schéma de base pour Intervention"""
    client_id: UUID = Field(..., description="ID du client")
    date_intervention: datetime = Field(..., description="Date de l'intervention")
    type_intervention: TypeInterventionEnum = Field(..., description="Type d'intervention")
    lieu: Optional[str] = Field(None, description="Lieu de l'intervention")
    description: Optional[str] = Field(None, description="Description de l'intervention")
    technicien_assigné: Optional[str] = Field(None, max_length=255, description="Technicien assigné")
    priorite: str = Field(default="normale", description="Priorité: basse, normale, haute, urgente")
    duree_estimee: Optional[int] = Field(None, ge=0, description="Durée estimée en minutes")
    latitude: Optional[str] = Field(None, max_length=20, description="Latitude GPS")
    longitude: Optional[str] = Field(None, max_length=20, description="Longitude GPS")


class InterventionCreate(InterventionBase):
    """Schéma pour création d'intervention"""
    pass


class InterventionUpdate(BaseModel):
    """Schéma pour mise à jour d'intervention"""
    date_intervention: Optional[datetime] = None
    type_intervention: Optional[TypeInterventionEnum] = None
    statut: Optional[StatutInterventionEnum] = None
    lieu: Optional[str] = None
    description: Optional[str] = None
    technicien_assigné: Optional[str] = Field(None, max_length=255)
    priorite: Optional[str] = None
    duree_estimee: Optional[int] = Field(None, ge=0)
    latitude: Optional[str] = Field(None, max_length=20)
    longitude: Optional[str] = Field(None, max_length=20)
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None


class InterventionResponse(InterventionBase):
    """Schéma de réponse pour Intervention"""
    id: UUID
    statut: StatutInterventionEnum
    date_creation: datetime
    date_modification: Optional[datetime] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    client: Optional[ClientResponse] = None

    class Config:
        from_attributes = True


class InterventionListResponse(BaseModel):
    """Schéma pour liste paginée d'interventions"""
    interventions: List[InterventionResponse]
    total: int
    page: int
    size: int
    pages: int


# Schémas pour les Inspections
class InspectionBase(BaseModel):
    """Schéma de base pour Inspection"""
    intervention_id: UUID = Field(..., description="ID de l'intervention")
    type_inspection: str = Field(..., min_length=1, max_length=100, description="Type d'inspection")
    resultat: Optional[str] = Field(None, description="Résultat de l'inspection")
    observations: Optional[str] = Field(None, description="Observations")
    photos: Optional[List[str]] = Field(None, description="Liste des URLs des photos")
    coordonnees_gps: Optional[dict] = Field(None, description="Coordonnées GPS")
    date_inspection: Optional[datetime] = Field(None, description="Date de l'inspection")


class InspectionCreate(InspectionBase):
    """Schéma pour création d'inspection"""
    pass


class InspectionUpdate(BaseModel):
    """Schéma pour mise à jour d'inspection"""
    statut: Optional[StatutInspectionEnum] = None
    type_inspection: Optional[str] = Field(None, min_length=1, max_length=100)
    resultat: Optional[str] = None
    observations: Optional[str] = None
    photos: Optional[List[str]] = None
    coordonnees_gps: Optional[dict] = None
    date_inspection: Optional[datetime] = None


class InspectionResponse(InspectionBase):
    """Schéma de réponse pour Inspection"""
    id: UUID
    statut: StatutInspectionEnum
    date_creation: datetime
    date_modification: Optional[datetime] = None

    class Config:
        from_attributes = True


# Schémas pour les workflows
class WorkflowAction(BaseModel):
    """Schéma pour action de workflow"""
    action: str = Field(..., description="Action à effectuer")
    commentaire: Optional[str] = Field(None, description="Commentaire sur l'action")
    technicien: Optional[str] = Field(None, description="Technicien assigné")


class StatutChange(BaseModel):
    """Schéma pour changement de statut"""
    nouveau_statut: StatutInterventionEnum = Field(..., description="Nouveau statut")
    commentaire: Optional[str] = Field(None, description="Commentaire sur le changement")
    date_debut: Optional[datetime] = Field(None, description="Date de début (si passage en cours)")
    date_fin: Optional[datetime] = Field(None, description="Date de fin (si passage en validé)")


# Schémas pour les RendezVous (Planning)
class RendezVousBase(BaseModel):
    """Schéma de base pour RendezVous"""
    client_id: UUID = Field(..., description="ID du client")
    intervention_id: Optional[UUID] = Field(None, description="ID de l'intervention (optionnel)")
    date_heure_debut: datetime = Field(..., description="Date et heure de début")
    date_heure_fin: datetime = Field(..., description="Date et heure de fin")
    utilisateur_responsable: Optional[str] = Field(None, max_length=255, description="Technicien responsable")
    notes: Optional[str] = Field(None, description="Notes du rendez-vous")
    couleur: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Couleur hexadécimale")
    rappel_avant: int = Field(default=24, ge=0, le=168, description="Rappel en heures avant le RDV")


class RendezVousCreate(RendezVousBase):
    """Schéma pour création de rendez-vous"""
    pass


class RendezVousUpdate(BaseModel):
    """Schéma pour mise à jour de rendez-vous"""
    date_heure_debut: Optional[datetime] = None
    date_heure_fin: Optional[datetime] = None
    statut: Optional[StatutRendezVousEnum] = None
    utilisateur_responsable: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    couleur: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    rappel_avant: Optional[int] = Field(None, ge=0, le=168)


class RendezVousResponse(RendezVousBase):
    """Schéma de réponse pour RendezVous"""
    id: UUID
    statut: StatutRendezVousEnum
    date_creation: datetime
    date_modification: Optional[datetime] = None
    client: Optional[ClientResponse] = None
    intervention: Optional[InterventionResponse] = None

    class Config:
        from_attributes = True


class RendezVousListResponse(BaseModel):
    """Schéma pour liste paginée de rendez-vous"""
    rendez_vous: List[RendezVousResponse]
    total: int
    page: int
    size: int
    pages: int


class CalendarEvent(BaseModel):
    """Schéma pour événement calendrier (FullCalendar)"""
    id: str
    title: str
    start: str
    end: str
    backgroundColor: str
    borderColor: str
    textColor: str
    extendedProps: dict


class RendezVousCalendarResponse(BaseModel):
    """Schéma pour réponse calendrier"""
    events: List[CalendarEvent]
    total: int


class PlanningStats(BaseModel):
    """Schéma pour statistiques du planning"""
    total_rdv: int
    rdv_aujourd_hui: int
    rdv_cette_semaine: int
    rdv_en_retard: int
    par_statut: dict
    par_technicien: dict


class CreneauDisponible(BaseModel):
    """Schéma pour créneau disponible"""
    debut: datetime
    fin: datetime
    duree_minutes: int
    technicien: Optional[str] = None


class ValidationCreneau(BaseModel):
    """Schéma pour validation de créneau"""
    technicien: Optional[str] = None
    date_debut: datetime
    date_fin: datetime
    rdv_id_exclu: Optional[UUID] = None  # Pour exclure un RDV lors de la modification


# Schémas pour les Rapports
class RapportBase(BaseModel):
    """Schéma de base pour Rapport"""
    intervention_id: UUID = Field(..., description="ID de l'intervention")
    type_rapport: TypeRapportEnum = Field(..., description="Type de rapport")
    titre: str = Field(..., min_length=1, max_length=255, description="Titre du rapport")
    description: Optional[str] = Field(None, description="Description du rapport")
    auteur_rapport: Optional[str] = Field(None, max_length=255, description="Auteur du rapport")
    contenu: Optional[dict] = Field(None, description="Contenu structuré du rapport")


class RapportCreate(RapportBase):
    """Schéma pour création de rapport"""
    pass


class RapportUpdate(BaseModel):
    """Schéma pour mise à jour de rapport"""
    titre: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    statut: Optional[StatutRapportEnum] = None
    contenu: Optional[dict] = None
    auteur_rapport: Optional[str] = Field(None, max_length=255)


class RapportResponse(RapportBase):
    """Schéma de réponse pour Rapport"""
    id: UUID
    statut: StatutRapportEnum
    date_creation: datetime
    date_modification: Optional[datetime] = None
    date_validation: Optional[datetime] = None
    date_archivage: Optional[datetime] = None
    taille_fichier: Optional[int] = None
    type_fichier: Optional[str] = None
    version: str
    chemin_fichier: Optional[str] = None
    intervention: Optional[InterventionResponse] = None

    class Config:
        from_attributes = True


class RapportListResponse(BaseModel):
    """Schéma pour liste paginée de rapports"""
    rapports: List[RapportResponse]
    total: int
    page: int
    size: int
    pages: int


# Schémas pour les Fichiers de Rapport
class FichierRapportBase(BaseModel):
    """Schéma de base pour FichierRapport"""
    rapport_id: UUID = Field(..., description="ID du rapport")
    nom_fichier: str = Field(..., min_length=1, max_length=255, description="Nom du fichier")
    type_fichier: str = Field(..., min_length=1, max_length=50, description="Type de fichier")
    description: Optional[str] = Field(None, description="Description du fichier")
    latitude: Optional[str] = Field(None, max_length=20, description="Latitude GPS")
    longitude: Optional[str] = Field(None, max_length=20, description="Longitude GPS")
    date_prise: Optional[datetime] = Field(None, description="Date de prise du média")


class FichierRapportCreate(FichierRapportBase):
    """Schéma pour création de fichier rapport"""
    pass


class FichierRapportResponse(FichierRapportBase):
    """Schéma de réponse pour FichierRapport"""
    id: UUID
    chemin_fichier: str
    taille_fichier: int
    mime_type: Optional[str] = None
    date_upload: datetime

    class Config:
        from_attributes = True


# Schémas pour la génération de rapports
class GenerationRapport(BaseModel):
    """Schéma pour génération de rapport"""
    intervention_id: UUID = Field(..., description="ID de l'intervention")
    type_rapport: TypeRapportEnum = Field(..., description="Type de rapport")
    template: Optional[str] = Field(None, description="Template à utiliser")
    format_export: str = Field(default="pdf", description="Format d'export (pdf, docx)")
    inclure_medias: bool = Field(default=True, description="Inclure les médias")
    inclure_gps: bool = Field(default=True, description="Inclure les coordonnées GPS")
    options: Optional[dict] = Field(None, description="Options personnalisées")


class RapportStats(BaseModel):
    """Schéma pour statistiques des rapports"""
    total_rapports: int
    rapports_ce_mois: int
    rapports_en_attente: int
    rapports_valides: int
    par_type: dict
    par_auteur: dict
    taille_totale: int  # En octets


class ExportRapport(BaseModel):
    """Schéma pour export de rapports"""
    format: str = Field(..., description="Format d'export (csv, xlsx, pdf)")
    filtres: Optional[dict] = Field(None, description="Filtres à appliquer")
    colonnes: Optional[List[str]] = Field(None, description="Colonnes à inclure")


# Schémas pour les Médias
class MediaBase(BaseModel):
    """Schéma de base pour Media"""
    intervention_id: UUID = Field(..., description="ID de l'intervention")
    inspection_id: Optional[UUID] = Field(None, description="ID de l'inspection (optionnel)")
    nom_fichier: str = Field(..., min_length=1, max_length=255, description="Nom du fichier")
    nom_original: str = Field(..., min_length=1, max_length=255, description="Nom original du fichier")
    type_media: TypeMediaEnum = Field(..., description="Type de média")
    annotations: Optional[str] = Field(None, description="Annotations du média")
    description: Optional[str] = Field(None, description="Description du média")
    tags: Optional[List[str]] = Field(None, description="Tags associés")
    latitude: Optional[str] = Field(None, max_length=20, description="Latitude GPS")
    longitude: Optional[str] = Field(None, max_length=20, description="Longitude GPS")
    precision_gps: Optional[str] = Field(None, max_length=20, description="Précision GPS en mètres")
    altitude: Optional[str] = Field(None, max_length=20, description="Altitude")
    date_prise: Optional[datetime] = Field(None, description="Date de prise du média")
    appareil_info: Optional[str] = Field(None, max_length=255, description="Information sur l'appareil")
    mode_capture: Optional[str] = Field(None, max_length=50, description="Mode de capture")


class MediaCreate(MediaBase):
    """Schéma pour création de média"""
    pass


class MediaUpdate(BaseModel):
    """Schéma pour mise à jour de média"""
    annotations: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    statut: Optional[StatutMediaEnum] = None


class MediaResponse(MediaBase):
    """Schéma de réponse pour Media"""
    id: UUID
    statut: StatutMediaEnum
    url_fichier: str
    taille_fichier: int
    mime_type: Optional[str] = None
    hash_fichier: Optional[str] = None
    date_upload: datetime
    date_modification: Optional[datetime] = None
    meta_exif: Optional[dict] = None
    resolution_x: Optional[int] = None
    resolution_y: Optional[int] = None
    duree: Optional[int] = None
    version: str
    parent_id: Optional[UUID] = None
    est_version: bool
    utilisateur_upload: Optional[str] = None

    class Config:
        from_attributes = True


class MediaThumbnailResponse(BaseModel):
    """Schéma pour miniature de média"""
    id: UUID
    nom_fichier: str
    type_media: TypeMediaEnum
    statut: StatutMediaEnum
    url_fichier: str
    taille_fichier: int
    date_prise: Optional[datetime] = None
    annotations: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    resolution_x: Optional[int] = None
    resolution_y: Optional[int] = None
    duree: Optional[int] = None

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    """Schéma pour liste paginée de médias"""
    medias: List[MediaThumbnailResponse]
    total: int
    page: int
    size: int
    pages: int


# Schémas pour l'upload de médias
class MediaUpload(BaseModel):
    """Schéma pour upload de média"""
    intervention_id: UUID = Field(..., description="ID de l'intervention")
    inspection_id: Optional[UUID] = Field(None, description="ID de l'inspection")
    type_media: TypeMediaEnum = Field(..., description="Type de média")
    annotations: Optional[str] = Field(None, description="Annotations")
    description: Optional[str] = Field(None, description="Description")
    tags: Optional[List[str]] = Field(None, description="Tags")
    latitude: Optional[str] = Field(None, description="Latitude GPS")
    longitude: Optional[str] = Field(None, description="Longitude GPS")
    precision_gps: Optional[str] = Field(None, description="Précision GPS")
    altitude: Optional[str] = Field(None, description="Altitude")
    date_prise: Optional[datetime] = Field(None, description="Date de prise")
    appareil_info: Optional[str] = Field(None, description="Information appareil")
    mode_capture: Optional[str] = Field(None, description="Mode de capture")


class MediaUploadResponse(BaseModel):
    """Schéma de réponse pour upload de média"""
    media_id: UUID
    upload_url: Optional[str] = None
    status: str
    message: str


class MediaStats(BaseModel):
    """Schéma pour statistiques des médias"""
    total_medias: int
    medias_ce_mois: int
    medias_en_attente: int
    medias_ready: int
    par_type: dict
    par_intervention: dict
    taille_totale: int  # En octets
    medias_avec_gps: int
    medias_avec_annotations: int


class MediaSearch(BaseModel):
    """Schéma pour recherche de médias"""
    query: Optional[str] = Field(None, description="Recherche textuelle")
    type_media: Optional[TypeMediaEnum] = Field(None, description="Filtrer par type")
    intervention_id: Optional[UUID] = Field(None, description="Filtrer par intervention")
    date_debut: Optional[datetime] = Field(None, description="Date de début")
    date_fin: Optional[datetime] = Field(None, description="Date de fin")
    avec_gps: Optional[bool] = Field(None, description="Avec coordonnées GPS")
    avec_annotations: Optional[bool] = Field(None, description="Avec annotations")
    tags: Optional[List[str]] = Field(None, description="Filtrer par tags")


class MediaBatchOperation(BaseModel):
    """Schéma pour opérations en lot sur les médias"""
    media_ids: List[UUID] = Field(..., description="IDs des médias")
    operation: str = Field(..., description="Opération à effectuer")
    parameters: Optional[dict] = Field(None, description="Paramètres de l'opération")


# Schémas pour la Sécurité & Administration
class RoleUtilisateurEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TECHNICIEN = "technicien"
    CONSULTANT = "consultant"
    LECTEUR = "lecteur"


class StatutUtilisateurEnum(str, Enum):
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    INACTIF = "inactif"
    EN_ATTENTE = "en_attente"


class TypeActionEnum(str, Enum):
    CONNEXION = "connexion"
    DECONNEXION = "deconnexion"
    CREATION = "creation"
    MODIFICATION = "modification"
    SUPPRESSION = "suppression"
    LECTURE = "lecture"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    EXPORT = "export"
    IMPORT = "import"
    CHANGEMENT_ROLE = "changement_role"
    CHANGEMENT_PERMISSION = "changement_permission"
    RESET_PASSWORD = "reset_password"
    ACTIVATION_2FA = "activation_2fa"
    DESACTIVATION_2FA = "desactivation_2fa"


class NiveauLogEnum(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Schémas pour les Utilisateurs
class UtilisateurBase(BaseModel):
    """Schéma de base pour Utilisateur"""
    nom_utilisateur: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur")
    email: str = Field(..., description="Adresse email")
    nom: str = Field(..., min_length=1, max_length=100, description="Nom de famille")
    prenom: str = Field(..., min_length=1, max_length=100, description="Prénom")
    role: RoleUtilisateurEnum = Field(..., description="Rôle utilisateur")
    telephone: Optional[str] = Field(None, max_length=20, description="Numéro de téléphone")
    adresse: Optional[str] = Field(None, description="Adresse")
    date_naissance: Optional[date] = Field(None, description="Date de naissance")
    langue: str = Field("fr", description="Langue préférée")
    fuseau_horaire: str = Field("Europe/Paris", description="Fuseau horaire")
    notifications_email: bool = Field(True, description="Notifications par email")
    notifications_push: bool = Field(True, description="Notifications push")


class UtilisateurCreate(UtilisateurBase):
    """Schéma pour création d'utilisateur"""
    mot_de_passe: str = Field(..., min_length=8, description="Mot de passe")
    confirmer_mot_de_passe: str = Field(..., description="Confirmation du mot de passe")
    consentement_rgpd: bool = Field(..., description="Consentement RGPD")
    
    @validator('confirmer_mot_de_passe')
    def passwords_match(cls, v, values, **kwargs):
        if 'mot_de_passe' in values and v != values['mot_de_passe']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v


class UtilisateurUpdate(BaseModel):
    """Schéma pour mise à jour d'utilisateur"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, description="Adresse email")
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = None
    date_naissance: Optional[date] = None
    langue: Optional[str] = None
    fuseau_horaire: Optional[str] = None
    notifications_email: Optional[bool] = None
    notifications_push: Optional[bool] = None


class UtilisateurResponse(UtilisateurBase):
    """Schéma de réponse pour Utilisateur"""
    id: UUID
    statut: StatutUtilisateurEnum
    deux_facteurs_actif: bool
    derniere_connexion: Optional[datetime] = None
    derniere_activite: Optional[datetime] = None
    consentement_rgpd: bool
    date_consentement: Optional[datetime] = None
    date_creation: datetime
    date_modification: Optional[datetime] = None

    class Config:
        from_attributes = True


class UtilisateurPublicResponse(BaseModel):
    """Schéma de réponse publique pour Utilisateur"""
    id: UUID
    nom_utilisateur: str
    nom: str
    prenom: str
    role: RoleUtilisateurEnum
    statut: StatutUtilisateurEnum
    derniere_connexion: Optional[datetime] = None
    date_creation: datetime

    class Config:
        from_attributes = True


class UtilisateurListResponse(BaseModel):
    """Schéma pour liste paginée d'utilisateurs"""
    utilisateurs: List[UtilisateurPublicResponse]
    total: int
    page: int
    size: int
    pages: int


# Schémas pour l'authentification
class LoginRequest(BaseModel):
    """Schéma pour demande de connexion"""
    nom_utilisateur: str = Field(..., description="Nom d'utilisateur ou email")
    mot_de_passe: str = Field(..., description="Mot de passe")
    code_2fa: Optional[str] = Field(None, description="Code 2FA (si activé)")


class LoginResponse(BaseModel):
    """Schéma de réponse pour connexion"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    utilisateur: UtilisateurResponse


class RefreshTokenRequest(BaseModel):
    """Schéma pour rafraîchissement de token"""
    refresh_token: str = Field(..., description="Token de rafraîchissement")


class ChangePasswordRequest(BaseModel):
    """Schéma pour changement de mot de passe"""
    mot_de_passe_actuel: str = Field(..., description="Mot de passe actuel")
    nouveau_mot_de_passe: str = Field(..., min_length=8, description="Nouveau mot de passe")
    confirmer_nouveau_mot_de_passe: str = Field(..., description="Confirmation du nouveau mot de passe")
    
    @validator('confirmer_nouveau_mot_de_passe')
    def passwords_match(cls, v, values, **kwargs):
        if 'nouveau_mot_de_passe' in values and v != values['nouveau_mot_de_passe']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v


class ResetPasswordRequest(BaseModel):
    """Schéma pour demande de réinitialisation de mot de passe"""
    email: str = Field(..., description="Adresse email")


class ResetPasswordConfirm(BaseModel):
    """Schéma pour confirmation de réinitialisation de mot de passe"""
    token: str = Field(..., description="Token de réinitialisation")
    nouveau_mot_de_passe: str = Field(..., min_length=8, description="Nouveau mot de passe")
    confirmer_nouveau_mot_de_passe: str = Field(..., description="Confirmation du nouveau mot de passe")
    
    @validator('confirmer_nouveau_mot_de_passe')
    def passwords_match(cls, v, values, **kwargs):
        if 'nouveau_mot_de_passe' in values and v != values['nouveau_mot_de_passe']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v


# Schémas pour 2FA
class TwoFactorSetupResponse(BaseModel):
    """Schéma de réponse pour configuration 2FA"""
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class TwoFactorVerifyRequest(BaseModel):
    """Schéma pour vérification 2FA"""
    code: str = Field(..., description="Code 2FA")


# Schémas pour les logs d'audit
class LogAuditResponse(BaseModel):
    """Schéma de réponse pour LogAudit"""
    id: UUID
    utilisateur_id: Optional[UUID] = None
    nom_utilisateur: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    type_action: TypeActionEnum
    ressource: str
    ressource_id: Optional[str] = None
    action: str
    description: Optional[str] = None
    anciennes_valeurs: Optional[dict] = None
    nouvelles_valeurs: Optional[dict] = None
    niveau_log: NiveauLogEnum
    module: Optional[str] = None
    fonction: Optional[str] = None
    ligne_code: Optional[int] = None
    timestamp: datetime
    duree_ms: Optional[int] = None
    succes: bool
    message_erreur: Optional[str] = None

    class Config:
        from_attributes = True


class LogAuditListResponse(BaseModel):
    """Schéma pour liste paginée de logs d'audit"""
    logs: List[LogAuditResponse]
    total: int
    page: int
    size: int
    pages: int


class LogAuditSearch(BaseModel):
    """Schéma pour recherche dans les logs d'audit"""
    utilisateur_id: Optional[UUID] = None
    type_action: Optional[TypeActionEnum] = None
    ressource: Optional[str] = None
    niveau_log: Optional[NiveauLogEnum] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    succes: Optional[bool] = None
    ip_address: Optional[str] = None


# Schémas pour RGPD
class ConsentementRGPDBase(BaseModel):
    """Schéma de base pour ConsentementRGPD"""
    type_consentement: str = Field(..., description="Type de consentement")
    consentement_donne: bool = Field(..., description="Consentement donné")
    date_expiration: Optional[datetime] = Field(None, description="Date d'expiration")


class ConsentementRGPDCreate(ConsentementRGPDBase):
    """Schéma pour création de consentement RGPD"""
    pass


class ConsentementRGPDResponse(ConsentementRGPDBase):
    """Schéma de réponse pour ConsentementRGPD"""
    id: UUID
    utilisateur_id: UUID
    version_consentement: str
    date_consentement: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    source: Optional[str] = None
    date_revocation: Optional[datetime] = None
    raison_revocation: Optional[str] = None
    date_creation: datetime

    class Config:
        from_attributes = True


class RGPDExportRequest(BaseModel):
    """Schéma pour demande d'export RGPD"""
    utilisateur_id: UUID = Field(..., description="ID de l'utilisateur")
    format: str = Field("json", description="Format d'export (json, csv, pdf)")


class RGPDAnonymizeRequest(BaseModel):
    """Schéma pour demande d'anonymisation RGPD"""
    utilisateur_id: UUID = Field(..., description="ID de l'utilisateur")
    raison: str = Field(..., description="Raison de l'anonymisation")


# Schémas pour les statistiques de sécurité
class SecurityStats(BaseModel):
    """Schéma pour statistiques de sécurité"""
    total_utilisateurs: int
    utilisateurs_actifs: int
    utilisateurs_avec_2fa: int
    connexions_ce_mois: int
    echecs_connexion_ce_mois: int
    logs_audit_ce_mois: int
    par_role: dict
    par_statut: dict
    activite_recente: List[dict]
    alertes_securite: List[dict]


# Schémas pour les permissions
class PermissionCheck(BaseModel):
    """Schéma pour vérification de permissions"""
    resource: str = Field(..., description="Ressource")
    action: str = Field(..., description="Action")
    utilisateur_id: Optional[UUID] = Field(None, description="ID utilisateur (optionnel)")


class PermissionResponse(BaseModel):
    """Schéma de réponse pour permissions"""
    autorise: bool
    raison: Optional[str] = None


# Schémas pour les API & Intégrations
class StatutAPIKeyEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class TypeWebhookEnum(str, Enum):
    INTERVENTION_CREATED = "intervention_created"
    INTERVENTION_UPDATED = "intervention_updated"
    INTERVENTION_STATUS_CHANGED = "intervention_status_changed"
    RAPPORT_GENERATED = "rapport_generated"
    MEDIA_UPLOADED = "media_uploaded"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    CLIENT_CREATED = "client_created"
    CLIENT_UPDATED = "client_updated"
    PLANNING_CREATED = "planning_created"
    PLANNING_UPDATED = "planning_updated"


class StatutWebhookEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    DISABLED = "disabled"


class TypeIntegrationEnum(str, Enum):
    ZAPIER = "zapier"
    N8N = "n8n"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    MAILCHIMP = "mailchimp"
    MQTT = "mqtt"
    CUSTOM = "custom"


# Schémas pour les clés API
class APIKeyBase(BaseModel):
    """Schéma de base pour APIKey"""
    nom: str = Field(..., min_length=1, max_length=100, description="Nom de la clé API")
    description: Optional[str] = Field(None, description="Description de la clé API")
    scopes: List[str] = Field(..., description="Liste des permissions")
    limite_requetes_par_minute: int = Field(100, ge=1, le=10000, description="Limite par minute")
    limite_requetes_par_jour: int = Field(10000, ge=1, le=1000000, description="Limite par jour")
    limite_requetes_par_mois: int = Field(300000, ge=1, le=10000000, description="Limite par mois")
    date_expiration: Optional[datetime] = Field(None, description="Date d'expiration")
    ips_autorisees: Optional[List[str]] = Field(None, description="IPs autorisées")
    user_agents_autorises: Optional[List[str]] = Field(None, description="User-Agents autorisés")


class APIKeyCreate(APIKeyBase):
    """Schéma pour création de clé API"""
    pass


class APIKeyUpdate(BaseModel):
    """Schéma pour mise à jour de clé API"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    scopes: Optional[List[str]] = None
    limite_requetes_par_minute: Optional[int] = Field(None, ge=1, le=10000)
    limite_requetes_par_jour: Optional[int] = Field(None, ge=1, le=1000000)
    limite_requetes_par_mois: Optional[int] = Field(None, ge=1, le=10000000)
    date_expiration: Optional[datetime] = None
    ips_autorisees: Optional[List[str]] = None
    user_agents_autorises: Optional[List[str]] = None


class APIKeyResponse(APIKeyBase):
    """Schéma de réponse pour APIKey"""
    id: UUID
    cle_api: str
    utilisateur_id: UUID
    statut: StatutAPIKeyEnum
    date_creation: datetime
    derniere_utilisation: Optional[datetime] = None
    nombre_requetes_total: int
    nombre_requetes_ce_mois: int

    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    """Schéma pour liste paginée de clés API"""
    api_keys: List[APIKeyResponse]
    total: int
    page: int
    size: int
    pages: int


# Schémas pour les webhooks
class WebhookBase(BaseModel):
    """Schéma de base pour Webhook"""
    nom: str = Field(..., min_length=1, max_length=100, description="Nom du webhook")
    description: Optional[str] = Field(None, description="Description du webhook")
    url: str = Field(..., description="URL de destination")
    type_webhook: TypeWebhookEnum = Field(..., description="Type d'événement")
    secret: Optional[str] = Field(None, description="Secret pour signature HMAC")
    headers_customises: Optional[dict] = Field(None, description="Headers personnalisés")
    conditions: Optional[List[dict]] = Field(None, description="Conditions de déclenchement")
    ressources_filtrees: Optional[List[str]] = Field(None, description="Ressources à surveiller")
    nombre_tentatives_max: int = Field(3, ge=1, le=10, description="Nombre max de tentatives")
    delai_entre_tentatives: int = Field(60, ge=1, le=3600, description="Délai entre tentatives (s)")
    timeout: int = Field(30, ge=1, le=300, description="Timeout (s)")


class WebhookCreate(WebhookBase):
    """Schéma pour création de webhook"""
    pass


class WebhookUpdate(BaseModel):
    """Schéma pour mise à jour de webhook"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    url: Optional[str] = None
    secret: Optional[str] = None
    headers_customises: Optional[dict] = None
    conditions: Optional[List[dict]] = None
    ressources_filtrees: Optional[List[str]] = None
    nombre_tentatives_max: Optional[int] = Field(None, ge=1, le=10)
    delai_entre_tentatives: Optional[int] = Field(None, ge=1, le=3600)
    timeout: Optional[int] = Field(None, ge=1, le=300)


class WebhookResponse(WebhookBase):
    """Schéma de réponse pour Webhook"""
    id: UUID
    utilisateur_id: UUID
    statut: StatutWebhookEnum
    date_creation: datetime
    date_modification: Optional[datetime] = None
    derniere_execution: Optional[datetime] = None
    nombre_executions_total: int
    nombre_executions_reussies: int
    nombre_executions_echec: int

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    """Schéma pour liste paginée de webhooks"""
    webhooks: List[WebhookResponse]
    total: int
    page: int
    size: int
    pages: int


# Schémas pour les exécutions de webhooks
class WebhookExecutionResponse(BaseModel):
    """Schéma de réponse pour WebhookExecution"""
    id: UUID
    webhook_id: UUID
    type_evenement: str
    ressource_id: Optional[str] = None
    donnees_evenement: Optional[dict] = None
    statut: StatutWebhookEnum
    numero_tentative: int
    code_reponse_http: Optional[int] = None
    temps_reponse_ms: Optional[int] = None
    message_erreur: Optional[str] = None
    date_debut: datetime
    date_fin: Optional[datetime] = None
    ip_destination: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


# Schémas pour les logs API
class LogAPIResponse(BaseModel):
    """Schéma de réponse pour LogAPI"""
    id: UUID
    api_key_id: Optional[UUID] = None
    method: str
    endpoint: str
    query_params: Optional[dict] = None
    request_headers: Optional[dict] = None
    request_body: Optional[str] = None
    status_code: int
    response_headers: Optional[dict] = None
    response_body: Optional[str] = None
    temps_reponse_ms: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    utilisateur_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class LogAPIListResponse(BaseModel):
    """Schéma pour liste paginée de logs API"""
    logs: List[LogAPIResponse]
    total: int
    page: int
    size: int
    pages: int


# Schémas pour les intégrations
class IntegrationBase(BaseModel):
    """Schéma de base pour Integration"""
    nom: str = Field(..., min_length=1, max_length=100, description="Nom de l'intégration")
    description: Optional[str] = Field(None, description="Description de l'intégration")
    type_integration: TypeIntegrationEnum = Field(..., description="Type d'intégration")
    configuration: dict = Field(..., description="Configuration spécifique")


class IntegrationCreate(IntegrationBase):
    """Schéma pour création d'intégration"""
    pass


class IntegrationUpdate(BaseModel):
    """Schéma pour mise à jour d'intégration"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    configuration: Optional[dict] = None
    statut: Optional[str] = None


class IntegrationResponse(IntegrationBase):
    """Schéma de réponse pour Integration"""
    id: UUID
    utilisateur_id: UUID
    statut: str
    date_creation: datetime
    date_modification: Optional[datetime] = None
    derniere_synchronisation: Optional[datetime] = None
    nombre_synchronisations: int

    class Config:
        from_attributes = True


class IntegrationListResponse(BaseModel):
    """Schéma pour liste paginée d'intégrations"""
    integrations: List[IntegrationResponse]
    total: int
    page: int
    size: int
    pages: int


# Schémas pour les événements webhook
class WebhookEvent(BaseModel):
    """Schéma pour événement webhook"""
    type: str = Field(..., description="Type d'événement")
    timestamp: datetime = Field(..., description="Timestamp de l'événement")
    data: dict = Field(..., description="Données de l'événement")
    resource_id: Optional[str] = Field(None, description="ID de la ressource")
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur")


# Schémas pour les statistiques API
class APIStats(BaseModel):
    """Schéma pour statistiques API"""
    total_requetes: int
    requetes_ce_mois: int
    requetes_aujourd_hui: int
    taux_erreur: float
    temps_reponse_moyen: float
    par_endpoint: dict
    par_status_code: dict
    par_utilisateur: dict
    top_ips: List[dict]
    activite_recente: List[dict]


# Schémas pour les tests d'API
class APITestRequest(BaseModel):
    """Schéma pour test d'API"""
    endpoint: str = Field(..., description="Endpoint à tester")
    method: str = Field(..., description="Méthode HTTP")
    headers: Optional[dict] = Field(None, description="Headers de la requête")
    body: Optional[dict] = Field(None, description="Corps de la requête")
    query_params: Optional[dict] = Field(None, description="Paramètres de requête")


class APITestResponse(BaseModel):
    """Schéma de réponse pour test d'API"""
    success: bool
    status_code: int
    response_time_ms: int
    response_headers: dict
    response_body: dict
    error_message: Optional[str] = None
