"""
Modèles de données SQLAlchemy
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from .database import Base


# Enums pour les statuts et types
class StatutIntervention(str, enum.Enum):
    PLANIFIE = "planifié"
    EN_COURS = "en_cours"
    VALIDE = "validé"
    ARCHIVE = "archivé"


class TypeIntervention(str, enum.Enum):
    INSPECTION = "inspection"
    DETECTION = "détection"
    REPARATION = "réparation"
    MAINTENANCE = "maintenance"
    AUTRE = "autre"


class StatutInspection(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    TERMINEE = "terminée"
    ANNULEE = "annulée"


class StatutRendezVous(str, enum.Enum):
    PLANIFIE = "planifié"
    CONFIRME = "confirmé"
    ANNULE = "annulé"
    TERMINE = "terminé"


class TypeRapport(str, enum.Enum):
    INSPECTION = "inspection"
    VALIDATION = "validation"
    INTERVENTION = "intervention"
    MAINTENANCE = "maintenance"
    AUTRE = "autre"


class StatutRapport(str, enum.Enum):
    BROUILLON = "brouillon"
    VALIDE = "validé"
    ARCHIVE = "archivé"


class TypeMedia(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    AUTRE = "autre"


class StatutMedia(str, enum.Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"


class RoleUtilisateur(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TECHNICIEN = "technicien"
    CONSULTANT = "consultant"
    LECTEUR = "lecteur"


class StatutUtilisateur(str, enum.Enum):
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    INACTIF = "inactif"
    EN_ATTENTE = "en_attente"


class TypeAction(str, enum.Enum):
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


class NiveauLog(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class StatutAPIKey(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class TypeWebhook(str, enum.Enum):
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


class StatutWebhook(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    DISABLED = "disabled"


class TypeIntegration(str, enum.Enum):
    ZAPIER = "zapier"
    N8N = "n8n"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    MAILCHIMP = "mailchimp"
    MQTT = "mqtt"
    CUSTOM = "custom"


class Client(Base):
    """Modèle Client pour la Phase 1"""
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False, index=True)
    raison_sociale = Column(String(255), nullable=True)
    adresse = Column(Text, nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    statut = Column(String(20), default="actif", nullable=False)  # actif, inactif
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Champs additionnels pour Phase 1
    notes = Column(Text, nullable=True)
    contact_principal = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<Client(id={self.id}, nom='{self.nom}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "nom": self.nom,
            "raison_sociale": self.raison_sociale,
            "adresse": self.adresse,
            "telephone": self.telephone,
            "email": self.email,
            "statut": self.statut,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "notes": self.notes,
            "contact_principal": self.contact_principal
        }


class Intervention(Base):
    """Modèle Intervention pour la Phase 2"""
    __tablename__ = "interventions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    date_intervention = Column(DateTime(timezone=True), nullable=False, index=True)
    type_intervention = Column(Enum(TypeIntervention), nullable=False, default=TypeIntervention.INSPECTION)
    statut = Column(Enum(StatutIntervention), nullable=False, default=StatutIntervention.PLANIFIE, index=True)
    lieu = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    technicien_assigné = Column(String(255), nullable=True)  # Pour Phase 2, on utilise un string
    priorite = Column(String(20), default="normale", nullable=False)  # basse, normale, haute, urgente
    duree_estimee = Column(Integer, nullable=True)  # en minutes
    
    # Coordonnées GPS (optionnel)
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    
    # Dates système
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    client = relationship("Client", back_populates="interventions")
    inspections = relationship("Inspection", back_populates="intervention", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Intervention(id={self.id}, type='{self.type_intervention}', statut='{self.statut}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "date_intervention": self.date_intervention.isoformat() if self.date_intervention else None,
            "type_intervention": self.type_intervention.value if self.type_intervention else None,
            "statut": self.statut.value if self.statut else None,
            "lieu": self.lieu,
            "description": self.description,
            "technicien_assigné": self.technicien_assigné,
            "priorite": self.priorite,
            "duree_estimee": self.duree_estimee,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "date_debut": self.date_debut.isoformat() if self.date_debut else None,
            "date_fin": self.date_fin.isoformat() if self.date_fin else None,
            "client": self.client.to_dict() if self.client else None
        }


class Inspection(Base):
    """Modèle Inspection lié aux interventions"""
    __tablename__ = "inspections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intervention_id = Column(UUID(as_uuid=True), ForeignKey("interventions.id"), nullable=False, index=True)
    statut = Column(Enum(StatutInspection), nullable=False, default=StatutInspection.EN_ATTENTE)
    type_inspection = Column(String(100), nullable=False)  # visuelle, sonore, thermique, etc.
    resultat = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    photos = Column(JSON, nullable=True)  # Liste des URLs des photos
    coordonnees_gps = Column(JSON, nullable=True)  # {"lat": 48.8566, "lng": 2.3522}
    
    # Dates
    date_inspection = Column(DateTime(timezone=True), nullable=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    intervention = relationship("Intervention", back_populates="inspections")
    
    def __repr__(self):
        return f"<Inspection(id={self.id}, type='{self.type_inspection}', statut='{self.statut}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "intervention_id": str(self.intervention_id),
            "statut": self.statut.value if self.statut else None,
            "type_inspection": self.type_inspection,
            "resultat": self.resultat,
            "observations": self.observations,
            "photos": self.photos,
            "coordonnees_gps": self.coordonnees_gps,
            "date_inspection": self.date_inspection.isoformat() if self.date_inspection else None,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None
        }


# Mise à jour de la relation Client
Client.interventions = relationship("Intervention", back_populates="client", cascade="all, delete-orphan")


class RendezVous(Base):
    """Modèle RendezVous pour la Phase 3 - Planning"""
    __tablename__ = "rendez_vous"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intervention_id = Column(UUID(as_uuid=True), ForeignKey("interventions.id"), nullable=True, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    date_heure_debut = Column(DateTime(timezone=True), nullable=False, index=True)
    date_heure_fin = Column(DateTime(timezone=True), nullable=False, index=True)
    statut = Column(Enum(StatutRendezVous), nullable=False, default=StatutRendezVous.PLANIFIE, index=True)
    utilisateur_responsable = Column(String(255), nullable=True)  # Technicien responsable
    notes = Column(Text, nullable=True)
    couleur = Column(String(7), nullable=True)  # Code couleur hex pour le calendrier
    rappel_avant = Column(Integer, default=24, nullable=False)  # Rappel en heures avant le RDV
    
    # Dates système
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    intervention = relationship("Intervention", back_populates="rendez_vous")
    client = relationship("Client", back_populates="rendez_vous")
    
    def __repr__(self):
        return f"<RendezVous(id={self.id}, debut='{self.date_heure_debut}', statut='{self.statut}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "intervention_id": str(self.intervention_id) if self.intervention_id else None,
            "client_id": str(self.client_id),
            "date_heure_debut": self.date_heure_debut.isoformat() if self.date_heure_debut else None,
            "date_heure_fin": self.date_heure_fin.isoformat() if self.date_heure_fin else None,
            "statut": self.statut.value if self.statut else None,
            "utilisateur_responsable": self.utilisateur_responsable,
            "notes": self.notes,
            "couleur": self.couleur,
            "rappel_avant": self.rappel_avant,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "intervention": self.intervention.to_dict() if self.intervention else None,
            "client": self.client.to_dict() if self.client else None
        }
    
    def to_calendar_event(self):
        """Conversion en événement calendrier (FullCalendar)"""
        return {
            "id": str(self.id),
            "title": f"{self.client.nom if self.client else 'N/A'} - {self.intervention.type_intervention.value if self.intervention else 'RDV'}",
            "start": self.date_heure_debut.isoformat() if self.date_heure_debut else None,
            "end": self.date_heure_fin.isoformat() if self.date_heure_fin else None,
            "backgroundColor": self.couleur or self.get_default_color(),
            "borderColor": self.couleur or self.get_default_color(),
            "textColor": "#ffffff",
            "extendedProps": {
                "statut": self.statut.value if self.statut else None,
                "client": self.client.nom if self.client else None,
                "intervention": self.intervention.type_intervention.value if self.intervention else None,
                "technicien": self.utilisateur_responsable,
                "notes": self.notes,
                "rappel_avant": self.rappel_avant
            }
        }
    
    def get_default_color(self):
        """Couleur par défaut selon le statut"""
        colors = {
            StatutRendezVous.PLANIFIE: "#6c757d",  # Gris
            StatutRendezVous.CONFIRME: "#007bff",  # Bleu
            StatutRendezVous.ANNULE: "#dc3545",    # Rouge
            StatutRendezVous.TERMINE: "#28a745"    # Vert
        }
        return colors.get(self.statut, "#6c757d")


# Mise à jour des relations existantes
Client.rendez_vous = relationship("RendezVous", back_populates="client", cascade="all, delete-orphan")
Intervention.rendez_vous = relationship("RendezVous", back_populates="intervention", cascade="all, delete-orphan")


class Rapport(Base):
    """Modèle Rapport pour la Phase 4 - Reporting"""
    __tablename__ = "rapports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intervention_id = Column(UUID(as_uuid=True), ForeignKey("interventions.id"), nullable=False, index=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    type_rapport = Column(Enum(TypeRapport), nullable=False, default=TypeRapport.INSPECTION)
    contenu = Column(JSON, nullable=True)  # Contenu structuré du rapport
    auteur_rapport = Column(String(255), nullable=True)  # Utilisateur qui a créé le rapport
    statut = Column(Enum(StatutRapport), nullable=False, default=StatutRapport.BROUILLON, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Métadonnées
    taille_fichier = Column(Integer, nullable=True)  # Taille en octets
    type_fichier = Column(String(50), nullable=True)  # PDF, DOCX, etc.
    version = Column(String(20), default="1.0", nullable=False)
    chemin_fichier = Column(String(500), nullable=True)  # Chemin vers le fichier stocké
    
    # Dates système
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    date_validation = Column(DateTime(timezone=True), nullable=True)
    date_archivage = Column(DateTime(timezone=True), nullable=True)
    
    # Relations
    intervention = relationship("Intervention", back_populates="rapports")
    fichiers = relationship("FichierRapport", back_populates="rapport", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Rapport(id={self.id}, titre='{self.titre}', statut='{self.statut}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "intervention_id": str(self.intervention_id),
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "type_rapport": self.type_rapport.value if self.type_rapport else None,
            "contenu": self.contenu,
            "auteur_rapport": self.auteur_rapport,
            "statut": self.statut.value if self.statut else None,
            "titre": self.titre,
            "description": self.description,
            "taille_fichier": self.taille_fichier,
            "type_fichier": self.type_fichier,
            "version": self.version,
            "chemin_fichier": self.chemin_fichier,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "date_validation": self.date_validation.isoformat() if self.date_validation else None,
            "date_archivage": self.date_archivage.isoformat() if self.date_archivage else None,
            "intervention": self.intervention.to_dict() if self.intervention else None
        }


class FichierRapport(Base):
    """Modèle FichierRapport pour stocker les médias et fichiers associés"""
    __tablename__ = "fichiers_rapport"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rapport_id = Column(UUID(as_uuid=True), ForeignKey("rapports.id"), nullable=False, index=True)
    nom_fichier = Column(String(255), nullable=False)
    chemin_fichier = Column(String(500), nullable=False)
    type_fichier = Column(String(50), nullable=False)  # image, video, document, etc.
    taille_fichier = Column(Integer, nullable=False)  # Taille en octets
    mime_type = Column(String(100), nullable=True)
    
    # Métadonnées pour les médias
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    date_prise = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    
    # Dates système
    date_upload = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    rapport = relationship("Rapport", back_populates="fichiers")
    
    def __repr__(self):
        return f"<FichierRapport(id={self.id}, nom='{self.nom_fichier}', type='{self.type_fichier}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "rapport_id": str(self.rapport_id),
            "nom_fichier": self.nom_fichier,
            "chemin_fichier": self.chemin_fichier,
            "type_fichier": self.type_fichier,
            "taille_fichier": self.taille_fichier,
            "mime_type": self.mime_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "date_prise": self.date_prise.isoformat() if self.date_prise else None,
            "description": self.description,
            "date_upload": self.date_upload.isoformat() if self.date_upload else None
        }


# Mise à jour des relations existantes
Intervention.rapports = relationship("Rapport", back_populates="intervention", cascade="all, delete-orphan")


class Media(Base):
    """Modèle Media pour la Phase 5 - Multimédia & Collecte Terrain"""
    __tablename__ = "medias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intervention_id = Column(UUID(as_uuid=True), ForeignKey("interventions.id"), nullable=False, index=True)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=True, index=True)
    
    # Informations de base
    nom_fichier = Column(String(255), nullable=False)
    nom_original = Column(String(255), nullable=False)
    type_media = Column(Enum(TypeMedia), nullable=False, index=True)
    statut = Column(Enum(StatutMedia), nullable=False, default=StatutMedia.UPLOADING, index=True)
    
    # Stockage
    url_fichier = Column(String(500), nullable=False)  # Chemin vers le fichier stocké
    chemin_local = Column(String(500), nullable=True)  # Chemin local temporaire
    taille_fichier = Column(Integer, nullable=False)  # Taille en octets
    mime_type = Column(String(100), nullable=True)
    hash_fichier = Column(String(64), nullable=True)  # Hash pour vérification intégrité
    
    # Géolocalisation
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)
    precision_gps = Column(String(20), nullable=True)  # Précision GPS en mètres
    altitude = Column(String(20), nullable=True)
    
    # Métadonnées temporelles
    date_prise = Column(DateTime(timezone=True), nullable=True, index=True)
    date_upload = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Métadonnées EXIF/techniques
    meta_exif = Column(JSON, nullable=True)  # Données EXIF complètes
    resolution_x = Column(Integer, nullable=True)  # Largeur en pixels
    resolution_y = Column(Integer, nullable=True)  # Hauteur en pixels
    duree = Column(Integer, nullable=True)  # Durée en secondes pour vidéos/audio
    
    # Annotations et descriptions
    annotations = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Tags libres
    
    # Gestion des versions
    version = Column(String(20), default="1.0", nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("medias.id"), nullable=True)  # Pour les versions
    est_version = Column(Boolean, default=False, nullable=False)
    
    # Utilisateur et contexte
    utilisateur_upload = Column(String(255), nullable=True)
    appareil_info = Column(String(255), nullable=True)  # Info sur l'appareil utilisé
    mode_capture = Column(String(50), nullable=True)  # mode_capture, mode_upload, etc.
    
    # Relations
    intervention = relationship("Intervention", back_populates="medias")
    inspection = relationship("Inspection", back_populates="medias")
    parent = relationship("Media", remote_side=[id], back_populates="versions")
    versions = relationship("Media", back_populates="parent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Media(id={self.id}, nom='{self.nom_fichier}', type='{self.type_media}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "intervention_id": str(self.intervention_id),
            "inspection_id": str(self.inspection_id) if self.inspection_id else None,
            "nom_fichier": self.nom_fichier,
            "nom_original": self.nom_original,
            "type_media": self.type_media.value if self.type_media else None,
            "statut": self.statut.value if self.statut else None,
            "url_fichier": self.url_fichier,
            "chemin_local": self.chemin_local,
            "taille_fichier": self.taille_fichier,
            "mime_type": self.mime_type,
            "hash_fichier": self.hash_fichier,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "precision_gps": self.precision_gps,
            "altitude": self.altitude,
            "date_prise": self.date_prise.isoformat() if self.date_prise else None,
            "date_upload": self.date_upload.isoformat() if self.date_upload else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "meta_exif": self.meta_exif,
            "resolution_x": self.resolution_x,
            "resolution_y": self.resolution_y,
            "duree": self.duree,
            "annotations": self.annotations,
            "description": self.description,
            "tags": self.tags,
            "version": self.version,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "est_version": self.est_version,
            "utilisateur_upload": self.utilisateur_upload,
            "appareil_info": self.appareil_info,
            "mode_capture": self.mode_capture
        }
    
    def to_thumbnail_dict(self):
        """Conversion pour affichage en miniature"""
        return {
            "id": str(self.id),
            "nom_fichier": self.nom_fichier,
            "type_media": self.type_media.value if self.type_media else None,
            "statut": self.statut.value if self.statut else None,
            "url_fichier": self.url_fichier,
            "taille_fichier": self.taille_fichier,
            "date_prise": self.date_prise.isoformat() if self.date_prise else None,
            "annotations": self.annotations,
            "description": self.description,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "resolution_x": self.resolution_x,
            "resolution_y": self.resolution_y,
            "duree": self.duree
        }
    
    def get_thumbnail_url(self):
        """URL pour la miniature (à implémenter selon le stockage)"""
        if self.type_media == TypeMedia.PHOTO:
            return f"{self.url_fichier}?thumbnail=true"
        return self.url_fichier
    
    def get_download_url(self):
        """URL pour le téléchargement"""
        return f"/api/medias/{self.id}/download"
    
    def is_image(self):
        """Vérifier si c'est une image"""
        return self.type_media == TypeMedia.PHOTO
    
    def is_video(self):
        """Vérifier si c'est une vidéo"""
        return self.type_media == TypeMedia.VIDEO
    
    def is_audio(self):
        """Vérifier si c'est un audio"""
        return self.type_media == TypeMedia.AUDIO


# Mise à jour des relations existantes
Intervention.medias = relationship("Media", back_populates="intervention", cascade="all, delete-orphan")
Inspection.medias = relationship("Media", back_populates="inspection", cascade="all, delete-orphan")


class Utilisateur(Base):
    """Modèle Utilisateur pour la Phase 6 - Sécurité & Administration"""
    __tablename__ = "utilisateurs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Informations de base
    nom_utilisateur = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    
    # Authentification
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleUtilisateur), nullable=False, default=RoleUtilisateur.LECTEUR, index=True)
    statut = Column(Enum(StatutUtilisateur), nullable=False, default=StatutUtilisateur.ACTIF, index=True)
    
    # Sécurité
    deux_facteurs_actif = Column(Boolean, default=False, nullable=False)
    secret_2fa = Column(String(32), nullable=True)  # Secret pour 2FA
    derniere_connexion = Column(DateTime(timezone=True), nullable=True, index=True)
    derniere_activite = Column(DateTime(timezone=True), nullable=True, index=True)
    nombre_tentatives_echec = Column(Integer, default=0, nullable=False)
    compte_verrouille_jusqu_a = Column(DateTime(timezone=True), nullable=True)
    
    # Tokens de rafraîchissement
    refresh_token = Column(String(500), nullable=True)
    refresh_token_expire = Column(DateTime(timezone=True), nullable=True)
    
    # Données personnelles (RGPD)
    telephone = Column(String(20), nullable=True)
    adresse = Column(Text, nullable=True)
    date_naissance = Column(Date, nullable=True)
    consentement_rgpd = Column(Boolean, default=False, nullable=False)
    date_consentement = Column(DateTime(timezone=True), nullable=True)
    date_anonymisation = Column(DateTime(timezone=True), nullable=True)
    
    # Métadonnées
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    cree_par = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=True)
    modifie_par = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=True)
    
    # Préférences
    langue = Column(String(5), default="fr", nullable=False)
    fuseau_horaire = Column(String(50), default="Europe/Paris", nullable=False)
    notifications_email = Column(Boolean, default=True, nullable=False)
    notifications_push = Column(Boolean, default=True, nullable=False)
    
    # Relations
    cree_par_utilisateur = relationship("Utilisateur", remote_side=[id], foreign_keys=[cree_par])
    modifie_par_utilisateur = relationship("Utilisateur", remote_side=[id], foreign_keys=[modifie_par])
    logs_audit = relationship("LogAudit", back_populates="utilisateur", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Utilisateur(id={self.id}, nom_utilisateur='{self.nom_utilisateur}', role='{self.role}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API (sans données sensibles)"""
        return {
            "id": str(self.id),
            "nom_utilisateur": self.nom_utilisateur,
            "email": self.email,
            "nom": self.nom,
            "prenom": self.prenom,
            "role": self.role.value if self.role else None,
            "statut": self.statut.value if self.statut else None,
            "deux_facteurs_actif": self.deux_facteurs_actif,
            "derniere_connexion": self.derniere_connexion.isoformat() if self.derniere_connexion else None,
            "derniere_activite": self.derniere_activite.isoformat() if self.derniere_activite else None,
            "telephone": self.telephone,
            "adresse": self.adresse,
            "date_naissance": self.date_naissance.isoformat() if self.date_naissance else None,
            "consentement_rgpd": self.consentement_rgpd,
            "date_consentement": self.date_consentement.isoformat() if self.date_consentement else None,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "langue": self.langue,
            "fuseau_horaire": self.fuseau_horaire,
            "notifications_email": self.notifications_email,
            "notifications_push": self.notifications_push
        }
    
    def to_public_dict(self):
        """Conversion publique (pour affichage dans les listes)"""
        return {
            "id": str(self.id),
            "nom_utilisateur": self.nom_utilisateur,
            "nom": self.nom,
            "prenom": self.prenom,
            "role": self.role.value if self.role else None,
            "statut": self.statut.value if self.statut else None,
            "derniere_connexion": self.derniere_connexion.isoformat() if self.derniere_connexion else None,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None
        }
    
    def is_active(self):
        """Vérifier si l'utilisateur est actif"""
        return self.statut == StatutUtilisateur.ACTIF
    
    def is_locked(self):
        """Vérifier si le compte est verrouillé"""
        if self.compte_verrouille_jusqu_a:
            return datetime.utcnow() < self.compte_verrouille_jusqu_a
        return False
    
    def can_access(self, resource: str, action: str) -> bool:
        """Vérifier les permissions d'accès"""
        # Définir les permissions par rôle
        permissions = {
            RoleUtilisateur.ADMIN: ["*"],  # Accès total
            RoleUtilisateur.MANAGER: [
                "clients:read", "clients:write", "clients:delete",
                "interventions:read", "interventions:write", "interventions:delete",
                "planning:read", "planning:write", "planning:delete",
                "rapports:read", "rapports:write", "rapports:delete",
                "medias:read", "medias:write", "medias:delete",
                "utilisateurs:read", "utilisateurs:write"
            ],
            RoleUtilisateur.TECHNICIEN: [
                "clients:read",
                "interventions:read", "interventions:write",
                "planning:read", "planning:write",
                "rapports:read", "rapports:write",
                "medias:read", "medias:write", "medias:upload"
            ],
            RoleUtilisateur.CONSULTANT: [
                "clients:read",
                "interventions:read",
                "planning:read",
                "rapports:read", "rapports:export",
                "medias:read", "medias:download"
            ],
            RoleUtilisateur.LECTEUR: [
                "clients:read",
                "interventions:read",
                "planning:read",
                "rapports:read",
                "medias:read"
            ]
        }
        
        user_permissions = permissions.get(self.role, [])
        required_permission = f"{resource}:{action}"
        
        return "*" in user_permissions or required_permission in user_permissions


class LogAudit(Base):
    """Modèle LogAudit pour la Phase 6 - Audit Trail"""
    __tablename__ = "logs_audit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Utilisateur et session
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=True, index=True)
    nom_utilisateur = Column(String(50), nullable=True, index=True)  # Pour les cas où l'utilisateur est supprimé
    session_id = Column(String(100), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(Text, nullable=True)
    
    # Action
    type_action = Column(Enum(TypeAction), nullable=False, index=True)
    ressource = Column(String(100), nullable=False, index=True)  # clients, interventions, etc.
    ressource_id = Column(String(100), nullable=True, index=True)  # ID de la ressource concernée
    action = Column(String(50), nullable=False)  # create, read, update, delete, etc.
    
    # Détails
    description = Column(Text, nullable=True)
    anciennes_valeurs = Column(JSON, nullable=True)  # Valeurs avant modification
    nouvelles_valeurs = Column(JSON, nullable=True)  # Valeurs après modification
    niveau_log = Column(Enum(NiveauLog), nullable=False, default=NiveauLog.INFO, index=True)
    
    # Contexte
    module = Column(String(50), nullable=True)  # auth, clients, interventions, etc.
    fonction = Column(String(100), nullable=True)  # Nom de la fonction/méthode
    ligne_code = Column(Integer, nullable=True)  # Numéro de ligne (optionnel)
    
    # Métadonnées
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    duree_ms = Column(Integer, nullable=True)  # Durée de l'action en millisecondes
    succes = Column(Boolean, default=True, nullable=False, index=True)
    message_erreur = Column(Text, nullable=True)
    
    # Relations
    utilisateur = relationship("Utilisateur", back_populates="logs_audit")
    
    def __repr__(self):
        return f"<LogAudit(id={self.id}, utilisateur='{self.nom_utilisateur}', action='{self.action}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "utilisateur_id": str(self.utilisateur_id) if self.utilisateur_id else None,
            "nom_utilisateur": self.nom_utilisateur,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "type_action": self.type_action.value if self.type_action else None,
            "ressource": self.ressource,
            "ressource_id": self.ressource_id,
            "action": self.action,
            "description": self.description,
            "anciennes_valeurs": self.anciennes_valeurs,
            "nouvelles_valeurs": self.nouvelles_valeurs,
            "niveau_log": self.niveau_log.value if self.niveau_log else None,
            "module": self.module,
            "fonction": self.fonction,
            "ligne_code": self.ligne_code,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "duree_ms": self.duree_ms,
            "succes": self.succes,
            "message_erreur": self.message_erreur
        }


class ConsentementRGPD(Base):
    """Modèle ConsentementRGPD pour la Phase 6 - Gestion RGPD"""
    __tablename__ = "consentements_rgpd"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Utilisateur
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False, index=True)
    
    # Type de consentement
    type_consentement = Column(String(50), nullable=False, index=True)  # cookies, marketing, analytics, etc.
    version_consentement = Column(String(20), default="1.0", nullable=False)
    
    # Consentement
    consentement_donne = Column(Boolean, nullable=False, index=True)
    date_consentement = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_expiration = Column(DateTime(timezone=True), nullable=True)
    
    # Contexte
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    source = Column(String(50), nullable=True)  # web, mobile, api, etc.
    
    # Révocation
    date_revocation = Column(DateTime(timezone=True), nullable=True)
    raison_revocation = Column(Text, nullable=True)
    
    # Métadonnées
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relations
    utilisateur = relationship("Utilisateur")
    
    def __repr__(self):
        return f"<ConsentementRGPD(id={self.id}, utilisateur_id={self.utilisateur_id}, type='{self.type_consentement}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "utilisateur_id": str(self.utilisateur_id),
            "type_consentement": self.type_consentement,
            "version_consentement": self.version_consentement,
            "consentement_donne": self.consentement_donne,
            "date_consentement": self.date_consentement.isoformat() if self.date_consentement else None,
            "date_expiration": self.date_expiration.isoformat() if self.date_expiration else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "source": self.source,
            "date_revocation": self.date_revocation.isoformat() if self.date_revocation else None,
            "raison_revocation": self.raison_revocation,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None
        }
    
    def is_valid(self):
        """Vérifier si le consentement est valide"""
        if not self.consentement_donne:
            return False
        if self.date_revocation:
            return False
        if self.date_expiration and datetime.utcnow() > self.date_expiration:
            return False
        return True


class APIKey(Base):
    """Modèle APIKey pour la Phase 7 - API & Intégrations"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Informations de base
    nom = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    cle_api = Column(String(64), unique=True, nullable=False, index=True)
    secret_key = Column(String(128), nullable=False)
    
    # Propriétaire
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False, index=True)
    
    # Permissions et scopes
    scopes = Column(JSON, nullable=False)  # Liste des permissions
    statut = Column(Enum(StatutAPIKey), nullable=False, default=StatutAPIKey.ACTIVE, index=True)
    
    # Limites et quotas
    limite_requetes_par_minute = Column(Integer, default=100, nullable=False)
    limite_requetes_par_jour = Column(Integer, default=10000, nullable=False)
    limite_requetes_par_mois = Column(Integer, default=300000, nullable=False)
    
    # Métadonnées
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_expiration = Column(DateTime(timezone=True), nullable=True)
    derniere_utilisation = Column(DateTime(timezone=True), nullable=True)
    nombre_requetes_total = Column(Integer, default=0, nullable=False)
    nombre_requetes_ce_mois = Column(Integer, default=0, nullable=False)
    
    # IP et restrictions
    ips_autorisees = Column(JSON, nullable=True)  # Liste des IPs autorisées
    user_agents_autorises = Column(JSON, nullable=True)  # Liste des User-Agents autorisés
    
    # Relations
    utilisateur = relationship("Utilisateur")
    logs_api = relationship("LogAPI", back_populates="api_key", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, nom='{self.nom}', statut='{self.statut}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "nom": self.nom,
            "description": self.description,
            "cle_api": self.cle_api,
            "utilisateur_id": str(self.utilisateur_id),
            "scopes": self.scopes,
            "statut": self.statut.value if self.statut else None,
            "limite_requetes_par_minute": self.limite_requetes_par_minute,
            "limite_requetes_par_jour": self.limite_requetes_par_jour,
            "limite_requetes_par_mois": self.limite_requetes_par_mois,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_expiration": self.date_expiration.isoformat() if self.date_expiration else None,
            "derniere_utilisation": self.derniere_utilisation.isoformat() if self.derniere_utilisation else None,
            "nombre_requetes_total": self.nombre_requetes_total,
            "nombre_requetes_ce_mois": self.nombre_requetes_ce_mois,
            "ips_autorisees": self.ips_autorisees,
            "user_agents_autorises": self.user_agents_autorises
        }
    
    def is_active(self):
        """Vérifier si la clé API est active"""
        if self.statut != StatutAPIKey.ACTIVE:
            return False
        if self.date_expiration and datetime.utcnow() > self.date_expiration:
            return False
        return True
    
    def has_scope(self, scope: str) -> bool:
        """Vérifier si la clé API a un scope spécifique"""
        return scope in self.scopes or "admin" in self.scopes
    
    def can_make_request(self) -> bool:
        """Vérifier si la clé API peut faire une requête (quotas)"""
        # Vérifier les quotas (simplifié)
        return self.nombre_requetes_ce_mois < self.limite_requetes_par_mois


class Webhook(Base):
    """Modèle Webhook pour la Phase 7 - API & Intégrations"""
    __tablename__ = "webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Informations de base
    nom = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=False)
    type_webhook = Column(Enum(TypeWebhook), nullable=False, index=True)
    
    # Propriétaire
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False, index=True)
    
    # Configuration
    statut = Column(Enum(StatutWebhook), nullable=False, default=StatutWebhook.ACTIVE, index=True)
    secret = Column(String(128), nullable=True)  # Secret pour signature HMAC
    headers_customises = Column(JSON, nullable=True)  # Headers personnalisés
    
    # Filtres et conditions
    conditions = Column(JSON, nullable=True)  # Conditions pour déclencher le webhook
    ressources_filtrees = Column(JSON, nullable=True)  # Ressources spécifiques à surveiller
    
    # Retry et timeout
    nombre_tentatives_max = Column(Integer, default=3, nullable=False)
    delai_entre_tentatives = Column(Integer, default=60, nullable=False)  # en secondes
    timeout = Column(Integer, default=30, nullable=False)  # en secondes
    
    # Métadonnées
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    derniere_execution = Column(DateTime(timezone=True), nullable=True)
    nombre_executions_total = Column(Integer, default=0, nullable=False)
    nombre_executions_reussies = Column(Integer, default=0, nullable=False)
    nombre_executions_echec = Column(Integer, default=0, nullable=False)
    
    # Relations
    utilisateur = relationship("Utilisateur")
    executions = relationship("WebhookExecution", back_populates="webhook", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Webhook(id={self.id}, nom='{self.nom}', type='{self.type_webhook}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "nom": self.nom,
            "description": self.description,
            "url": self.url,
            "type_webhook": self.type_webhook.value if self.type_webhook else None,
            "utilisateur_id": str(self.utilisateur_id),
            "statut": self.statut.value if self.statut else None,
            "secret": self.secret,
            "headers_customises": self.headers_customises,
            "conditions": self.conditions,
            "ressources_filtrees": self.ressources_filtrees,
            "nombre_tentatives_max": self.nombre_tentatives_max,
            "delai_entre_tentatives": self.delai_entre_tentatives,
            "timeout": self.timeout,
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "derniere_execution": self.derniere_execution.isoformat() if self.derniere_execution else None,
            "nombre_executions_total": self.nombre_executions_total,
            "nombre_executions_reussies": self.nombre_executions_reussies,
            "nombre_executions_echec": self.nombre_executions_echec
        }
    
    def is_active(self):
        """Vérifier si le webhook est actif"""
        return self.statut == StatutWebhook.ACTIVE
    
    def should_trigger(self, event_data: dict) -> bool:
        """Vérifier si le webhook doit être déclenché pour cet événement"""
        if not self.is_active():
            return False
        
        # Vérifier les conditions
        if self.conditions:
            for condition in self.conditions:
                if not self._evaluate_condition(condition, event_data):
                    return False
        
        return True
    
    def _evaluate_condition(self, condition: dict, event_data: dict) -> bool:
        """Évaluer une condition de webhook"""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        if field not in event_data:
            return False
        
        event_value = event_data[field]
        
        if operator == "equals":
            return event_value == value
        elif operator == "not_equals":
            return event_value != value
        elif operator == "contains":
            return value in str(event_value)
        elif operator == "not_contains":
            return value not in str(event_value)
        elif operator == "greater_than":
            return event_value > value
        elif operator == "less_than":
            return event_value < value
        
        return False


class WebhookExecution(Base):
    """Modèle WebhookExecution pour la Phase 7 - Exécutions de webhooks"""
    __tablename__ = "webhook_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Webhook
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id"), nullable=False, index=True)
    
    # Événement déclencheur
    type_evenement = Column(String(50), nullable=False, index=True)
    ressource_id = Column(String(100), nullable=True, index=True)
    donnees_evenement = Column(JSON, nullable=True)
    
    # Exécution
    statut = Column(Enum(StatutWebhook), nullable=False, index=True)
    numero_tentative = Column(Integer, default=1, nullable=False)
    code_reponse_http = Column(Integer, nullable=True)
    temps_reponse_ms = Column(Integer, nullable=True)
    message_erreur = Column(Text, nullable=True)
    
    # Métadonnées
    date_debut = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    ip_destination = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    
    # Relations
    webhook = relationship("Webhook", back_populates="executions")
    
    def __repr__(self):
        return f"<WebhookExecution(id={self.id}, webhook_id={self.webhook_id}, statut='{self.statut}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "webhook_id": str(self.webhook_id),
            "type_evenement": self.type_evenement,
            "ressource_id": self.ressource_id,
            "donnees_evenement": self.donnees_evenement,
            "statut": self.statut.value if self.statut else None,
            "numero_tentative": self.numero_tentative,
            "code_reponse_http": self.code_reponse_http,
            "temps_reponse_ms": self.temps_reponse_ms,
            "message_erreur": self.message_erreur,
            "date_debut": self.date_debut.isoformat() if self.date_debut else None,
            "date_fin": self.date_fin.isoformat() if self.date_fin else None,
            "ip_destination": self.ip_destination,
            "user_agent": self.user_agent
        }


class LogAPI(Base):
    """Modèle LogAPI pour la Phase 7 - Logs des appels API"""
    __tablename__ = "logs_api"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # API Key
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=True, index=True)
    
    # Requête
    method = Column(String(10), nullable=False, index=True)  # GET, POST, PUT, DELETE
    endpoint = Column(String(500), nullable=False, index=True)
    query_params = Column(JSON, nullable=True)
    request_headers = Column(JSON, nullable=True)
    request_body = Column(Text, nullable=True)
    
    # Réponse
    status_code = Column(Integer, nullable=False, index=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(Text, nullable=True)
    temps_reponse_ms = Column(Integer, nullable=False)
    
    # Client
    ip_address = Column(String(45), nullable=True, index=True)
    user_agent = Column(String(500), nullable=True)
    
    # Métadonnées
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=True, index=True)
    
    # Relations
    api_key = relationship("APIKey", back_populates="logs_api")
    utilisateur = relationship("Utilisateur")
    
    def __repr__(self):
        return f"<LogAPI(id={self.id}, method='{self.method}', endpoint='{self.endpoint}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "api_key_id": str(self.api_key_id) if self.api_key_id else None,
            "method": self.method,
            "endpoint": self.endpoint,
            "query_params": self.query_params,
            "request_headers": self.request_headers,
            "request_body": self.request_body,
            "status_code": self.status_code,
            "response_headers": self.response_headers,
            "response_body": self.response_body,
            "temps_reponse_ms": self.temps_reponse_ms,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "utilisateur_id": str(self.utilisateur_id) if self.utilisateur_id else None
        }


class Integration(Base):
    """Modèle Integration pour la Phase 7 - Intégrations externes"""
    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Informations de base
    nom = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type_integration = Column(Enum(TypeIntegration), nullable=False, index=True)
    
    # Configuration
    configuration = Column(JSON, nullable=False)  # Configuration spécifique à l'intégration
    statut = Column(String(20), default="active", nullable=False, index=True)
    
    # Propriétaire
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateurs.id"), nullable=False, index=True)
    
    # Métadonnées
    date_creation = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    derniere_synchronisation = Column(DateTime(timezone=True), nullable=True)
    nombre_synchronisations = Column(Integer, default=0, nullable=False)
    
    # Relations
    utilisateur = relationship("Utilisateur")
    
    def __repr__(self):
        return f"<Integration(id={self.id}, nom='{self.nom}', type='{self.type_integration}')>"
    
    def to_dict(self):
        """Conversion en dictionnaire pour l'API"""
        return {
            "id": str(self.id),
            "nom": self.nom,
            "description": self.description,
            "type_integration": self.type_integration.value if self.type_integration else None,
            "configuration": self.configuration,
            "statut": self.statut,
            "utilisateur_id": str(self.utilisateur_id),
            "date_creation": self.date_creation.isoformat() if self.date_creation else None,
            "date_modification": self.date_modification.isoformat() if self.date_modification else None,
            "derniere_synchronisation": self.derniere_synchronisation.isoformat() if self.derniere_synchronisation else None,
            "nombre_synchronisations": self.nombre_synchronisations
        }
