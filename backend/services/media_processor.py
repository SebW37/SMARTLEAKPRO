"""
Service de traitement des médias
"""

import os
import uuid
import hashlib
import mimetypes
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json

from PIL import Image, ExifTags
import cv2
import exifread
from moviepy.editor import VideoFileClip
import magic

from ..models import Media, TypeMedia, StatutMedia


class MediaProcessor:
    """Processeur de médias pour extraction de métadonnées et traitement"""
    
    def __init__(self):
        self.upload_dir = Path("backend/static/uploads")
        self.thumbnails_dir = Path("backend/static/thumbnails")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        
        # Types MIME supportés
        self.supported_types = {
            'image/jpeg': TypeMedia.PHOTO,
            'image/png': TypeMedia.PHOTO,
            'image/gif': TypeMedia.PHOTO,
            'image/webp': TypeMedia.PHOTO,
            'video/mp4': TypeMedia.VIDEO,
            'video/avi': TypeMedia.VIDEO,
            'video/mov': TypeMedia.VIDEO,
            'video/webm': TypeMedia.VIDEO,
            'audio/mp3': TypeMedia.AUDIO,
            'audio/wav': TypeMedia.AUDIO,
            'audio/m4a': TypeMedia.AUDIO,
            'application/pdf': TypeMedia.DOCUMENT,
            'application/msword': TypeMedia.DOCUMENT,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': TypeMedia.DOCUMENT
        }
    
    async def process_uploaded_file(
        self, 
        file_path: str, 
        original_filename: str,
        intervention_id: str,
        inspection_id: Optional[str] = None,
        user_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Traiter un fichier uploadé"""
        
        try:
            # Vérifier le type de fichier
            mime_type = magic.from_file(file_path, mime=True)
            if mime_type not in self.supported_types:
                raise ValueError(f"Type de fichier non supporté: {mime_type}")
            
            type_media = self.supported_types[mime_type]
            
            # Générer un nom de fichier unique
            file_extension = Path(original_filename).suffix
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            final_path = self.upload_dir / unique_filename
            
            # Déplacer le fichier vers le répertoire final
            os.rename(file_path, str(final_path))
            
            # Calculer le hash du fichier
            file_hash = await self._calculate_file_hash(final_path)
            
            # Extraire les métadonnées
            metadata = await self._extract_metadata(final_path, type_media)
            
            # Créer la miniature si c'est une image
            thumbnail_path = None
            if type_media == TypeMedia.PHOTO:
                thumbnail_path = await self._create_thumbnail(final_path)
            
            # Créer l'enregistrement en base
            media_data = {
                "intervention_id": intervention_id,
                "inspection_id": inspection_id,
                "nom_fichier": unique_filename,
                "nom_original": original_filename,
                "type_media": type_media,
                "statut": StatutMedia.READY,
                "url_fichier": f"/static/uploads/{unique_filename}",
                "taille_fichier": os.path.getsize(final_path),
                "mime_type": mime_type,
                "hash_fichier": file_hash,
                "meta_exif": metadata.get("exif", {}),
                "resolution_x": metadata.get("width"),
                "resolution_y": metadata.get("height"),
                "duree": metadata.get("duration"),
                "date_prise": metadata.get("date_prise"),
                "utilisateur_upload": user_data.get("username") if user_data else None,
                "appareil_info": metadata.get("camera_info"),
                "mode_capture": user_data.get("mode_capture") if user_data else None
            }
            
            # Ajouter les données GPS si disponibles
            if metadata.get("gps"):
                gps = metadata["gps"]
                media_data.update({
                    "latitude": gps.get("latitude"),
                    "longitude": gps.get("longitude"),
                    "precision_gps": gps.get("precision"),
                    "altitude": gps.get("altitude")
                })
            
            return {
                "media_data": media_data,
                "thumbnail_path": thumbnail_path,
                "success": True
            }
            
        except Exception as e:
            # Nettoyer le fichier en cas d'erreur
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculer le hash SHA-256 du fichier"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def _extract_metadata(self, file_path: Path, type_media: TypeMedia) -> Dict[str, Any]:
        """Extraire les métadonnées du fichier"""
        metadata = {}
        
        try:
            if type_media == TypeMedia.PHOTO:
                metadata = await self._extract_image_metadata(file_path)
            elif type_media == TypeMedia.VIDEO:
                metadata = await self._extract_video_metadata(file_path)
            elif type_media == TypeMedia.AUDIO:
                metadata = await self._extract_audio_metadata(file_path)
            else:
                metadata = await self._extract_basic_metadata(file_path)
                
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées: {e}")
            metadata = await self._extract_basic_metadata(file_path)
        
        return metadata
    
    async def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extraire les métadonnées d'une image"""
        metadata = {}
        
        try:
            # Utiliser PIL pour les métadonnées de base
            with Image.open(file_path) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["format"] = img.format
                metadata["mode"] = img.mode
                
                # Extraire les données EXIF
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                
                metadata["exif"] = exif_data
                
                # Extraire les données GPS depuis EXIF
                gps_data = self._extract_gps_from_exif(exif_data)
                if gps_data:
                    metadata["gps"] = gps_data
                
                # Extraire la date de prise
                date_prise = self._extract_date_from_exif(exif_data)
                if date_prise:
                    metadata["date_prise"] = date_prise
                
                # Informations sur l'appareil
                camera_info = self._extract_camera_info(exif_data)
                if camera_info:
                    metadata["camera_info"] = camera_info
                    
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées d'image: {e}")
        
        return metadata
    
    async def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extraire les métadonnées d'une vidéo"""
        metadata = {}
        
        try:
            # Utiliser moviepy pour les métadonnées vidéo
            with VideoFileClip(str(file_path)) as clip:
                metadata["width"] = clip.w
                metadata["height"] = clip.h
                metadata["duration"] = int(clip.duration)
                metadata["fps"] = clip.fps
                
                # Utiliser OpenCV pour plus de détails
                cap = cv2.VideoCapture(str(file_path))
                if cap.isOpened():
                    metadata["frame_count"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    metadata["codec"] = cap.get(cv2.CAP_PROP_FOURCC)
                    cap.release()
                    
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées vidéo: {e}")
        
        return metadata
    
    async def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extraire les métadonnées d'un audio"""
        metadata = {}
        
        try:
            # Utiliser moviepy pour les métadonnées audio
            with VideoFileClip(str(file_path)) as clip:
                metadata["duration"] = int(clip.duration)
                metadata["fps"] = clip.fps
                
        except Exception as e:
            print(f"Erreur lors de l'extraction des métadonnées audio: {e}")
        
        return metadata
    
    async def _extract_basic_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extraire les métadonnées de base"""
        return {
            "size": os.path.getsize(file_path),
            "modified": datetime.fromtimestamp(os.path.getmtime(file_path))
        }
    
    def _extract_gps_from_exif(self, exif_data: Dict) -> Optional[Dict[str, Any]]:
        """Extraire les données GPS depuis les données EXIF"""
        try:
            gps_info = exif_data.get('GPSInfo')
            if not gps_info:
                return None
            
            # Conversion des coordonnées GPS
            lat = self._convert_gps_coordinate(gps_info.get(2), gps_info.get(1))
            lon = self._convert_gps_coordinate(gps_info.get(4), gps_info.get(3))
            
            if lat is None or lon is None:
                return None
            
            return {
                "latitude": str(lat),
                "longitude": str(lon),
                "altitude": str(gps_info.get(6, 0)) if gps_info.get(6) else None,
                "precision": "10"  # Précision par défaut
            }
            
        except Exception as e:
            print(f"Erreur lors de l'extraction GPS: {e}")
            return None
    
    def _convert_gps_coordinate(self, coord, ref):
        """Convertir les coordonnées GPS EXIF en décimales"""
        try:
            if not coord or not ref:
                return None
            
            degrees = float(coord[0])
            minutes = float(coord[1])
            seconds = float(coord[2])
            
            result = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            if ref in ['S', 'W']:
                result = -result
                
            return result
            
        except Exception:
            return None
    
    def _extract_date_from_exif(self, exif_data: Dict) -> Optional[datetime]:
        """Extraire la date de prise depuis les données EXIF"""
        try:
            date_str = exif_data.get('DateTime') or exif_data.get('DateTimeOriginal')
            if date_str:
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except Exception:
            pass
        return None
    
    def _extract_camera_info(self, exif_data: Dict) -> Optional[str]:
        """Extraire les informations sur l'appareil photo"""
        try:
            make = exif_data.get('Make', '')
            model = exif_data.get('Model', '')
            if make and model:
                return f"{make} {model}"
        except Exception:
            pass
        return None
    
    async def _create_thumbnail(self, file_path: Path) -> Optional[str]:
        """Créer une miniature pour une image"""
        try:
            with Image.open(file_path) as img:
                # Redimensionner en gardant les proportions
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Sauvegarder la miniature
                thumbnail_filename = f"thumb_{file_path.stem}.jpg"
                thumbnail_path = self.thumbnails_dir / thumbnail_filename
                img.save(thumbnail_path, "JPEG", quality=85)
                
                return f"/static/thumbnails/{thumbnail_filename}"
                
        except Exception as e:
            print(f"Erreur lors de la création de la miniature: {e}")
            return None
    
    async def delete_media_files(self, media: Media) -> bool:
        """Supprimer les fichiers associés à un média"""
        try:
            # Supprimer le fichier principal
            main_file = self.upload_dir / media.nom_fichier
            if main_file.exists():
                os.remove(main_file)
            
            # Supprimer la miniature si elle existe
            if media.type_media == TypeMedia.PHOTO:
                thumbnail_file = self.thumbnails_dir / f"thumb_{media.nom_fichier.split('.')[0]}.jpg"
                if thumbnail_file.exists():
                    os.remove(thumbnail_file)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la suppression des fichiers: {e}")
            return False
    
    def get_media_file_path(self, media: Media) -> Path:
        """Obtenir le chemin vers le fichier d'un média"""
        return self.upload_dir / media.nom_fichier
    
    def get_thumbnail_path(self, media: Media) -> Optional[Path]:
        """Obtenir le chemin vers la miniature d'un média"""
        if media.type_media == TypeMedia.PHOTO:
            return self.thumbnails_dir / f"thumb_{media.nom_fichier.split('.')[0]}.jpg"
        return None
