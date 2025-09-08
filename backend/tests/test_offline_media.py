"""
Tests hors-ligne pour module multimédia - Phase Test & Debug
"""

import pytest
import asyncio
import tempfile
import os
import json
from unittest.mock import patch, Mock, AsyncMock
from datetime import datetime
import uuid

from ..services.media_processor import MediaProcessor
from ..models import Media, Intervention
from ..services.offline_sync import OfflineSyncService


class TestOfflineMediaCapture:
    """Tests de capture multimédia hors-ligne"""
    
    def test_offline_media_storage(self):
        """Test stockage hors-ligne des médias"""
        processor = MediaProcessor()
        
        # Créer un fichier temporaire pour simuler un média
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(b"fake image content")
            temp_file_path = temp_file.name
        
        try:
            # Simuler la capture hors-ligne
            media_data = {
                "intervention_id": str(uuid.uuid4()),
                "type_media": "photo",
                "nom_fichier": "offline_test.jpg",
                "description": "Test hors-ligne",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Stocker le média hors-ligne
            offline_path = processor.store_offline_media(temp_file_path, media_data)
            
            assert os.path.exists(offline_path)
            assert os.path.getsize(offline_path) > 0
            
            # Vérifier que les métadonnées sont sauvegardées
            metadata_path = offline_path + ".metadata"
            assert os.path.exists(metadata_path)
            
            with open(metadata_path, 'r') as f:
                saved_metadata = json.load(f)
            
            assert saved_metadata["intervention_id"] == media_data["intervention_id"]
            assert saved_metadata["type_media"] == media_data["type_media"]
            assert saved_metadata["latitude"] == media_data["latitude"]
            assert saved_metadata["longitude"] == media_data["longitude"]
            
        finally:
            # Nettoyer
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(offline_path):
                os.unlink(offline_path)
            if os.path.exists(metadata_path):
                os.unlink(metadata_path)
    
    def test_offline_media_metadata_extraction(self):
        """Test extraction de métadonnées hors-ligne"""
        processor = MediaProcessor()
        
        # Mock des métadonnées EXIF
        mock_exif = {
            "DateTime": "2024:01:01 12:00:00",
            "GPSInfo": {1: "N", 2: (48, 51, 0), 3: "E", 4: (2, 20, 0)},
            "Make": "Test Camera",
            "Model": "Test Model"
        }
        
        with patch('PIL.ExifTags.TAGS', {271: "Make", 272: "Model", 306: "DateTime"}):
            with patch('PIL.Image.open') as mock_open:
                mock_image = Mock()
                mock_image._getexif.return_value = mock_exif
                mock_image.size = (1920, 1080)
                mock_image.format = "JPEG"
                mock_open.return_value = mock_image
                
                # Créer un fichier temporaire
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_file.write(b"fake image content")
                    temp_file_path = temp_file.name
                
                try:
                    # Extraire les métadonnées hors-ligne
                    metadata = processor.extract_offline_metadata(temp_file_path)
                    
                    assert metadata["make"] == "Test Camera"
                    assert metadata["model"] == "Test Model"
                    assert metadata["datetime"] == "2024:01:01 12:00:00"
                    assert metadata["width"] == 1920
                    assert metadata["height"] == 1080
                    assert metadata["format"] == "JPEG"
                    
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
    
    def test_offline_thumbnail_generation(self):
        """Test génération de miniatures hors-ligne"""
        processor = MediaProcessor()
        
        # Mock d'une image
        mock_image = Mock()
        mock_image.size = (1920, 1080)
        mock_image.format = "JPEG"
        
        with patch('PIL.Image.open', return_value=mock_image):
            with patch('PIL.Image.thumbnail') as mock_thumbnail:
                # Créer un fichier temporaire
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_file.write(b"fake image content")
                    temp_file_path = temp_file.name
                
                try:
                    # Générer une miniature hors-ligne
                    thumbnail_path = processor.generate_offline_thumbnail(temp_file_path, (200, 200))
                    
                    assert os.path.exists(thumbnail_path)
                    mock_thumbnail.assert_called_once()
                    
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                    if os.path.exists(thumbnail_path):
                        os.unlink(thumbnail_path)
    
    def test_offline_media_compression(self):
        """Test compression de médias hors-ligne"""
        processor = MediaProcessor()
        
        # Mock d'une image
        mock_image = Mock()
        mock_image.size = (1920, 1080)
        mock_image.format = "JPEG"
        
        with patch('PIL.Image.open', return_value=mock_image):
            with patch('PIL.Image.save') as mock_save:
                # Créer un fichier temporaire
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_file.write(b"fake image content")
                    temp_file_path = temp_file.name
                
                try:
                    # Compresser l'image hors-ligne
                    compressed_path = processor.compress_offline_media(temp_file_path, quality=80)
                    
                    assert os.path.exists(compressed_path)
                    mock_save.assert_called_once()
                    
                    # Vérifier que la compression a été appliquée
                    call_args = mock_save.call_args
                    assert call_args[1]["quality"] == 80
                    assert call_args[1]["optimize"] is True
                    
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                    if os.path.exists(compressed_path):
                        os.unlink(compressed_path)


class TestOfflineSyncService:
    """Tests du service de synchronisation hors-ligne"""
    
    def test_offline_queue_management(self):
        """Test gestion de la file d'attente hors-ligne"""
        sync_service = OfflineSyncService()
        
        # Ajouter des médias à la file d'attente
        media_items = [
            {
                "id": str(uuid.uuid4()),
                "intervention_id": str(uuid.uuid4()),
                "type_media": "photo",
                "file_path": "/offline/photo1.jpg",
                "metadata": {"description": "Photo 1"}
            },
            {
                "id": str(uuid.uuid4()),
                "intervention_id": str(uuid.uuid4()),
                "type_media": "video",
                "file_path": "/offline/video1.mp4",
                "metadata": {"description": "Video 1"}
            }
        ]
        
        for media_item in media_items:
            sync_service.add_to_offline_queue(media_item)
        
        # Vérifier que les éléments sont dans la file
        queue = sync_service.get_offline_queue()
        assert len(queue) == 2
        
        # Vérifier le contenu
        assert any(item["type_media"] == "photo" for item in queue)
        assert any(item["type_media"] == "video" for item in queue)
    
    def test_offline_sync_priority(self):
        """Test priorité de synchronisation hors-ligne"""
        sync_service = OfflineSyncService()
        
        # Ajouter des médias avec différentes priorités
        high_priority_media = {
            "id": str(uuid.uuid4()),
            "intervention_id": str(uuid.uuid4()),
            "type_media": "photo",
            "file_path": "/offline/urgent.jpg",
            "priority": "high",
            "metadata": {"description": "Urgent"}
        }
        
        low_priority_media = {
            "id": str(uuid.uuid4()),
            "intervention_id": str(uuid.uuid4()),
            "type_media": "photo",
            "file_path": "/offline/normal.jpg",
            "priority": "low",
            "metadata": {"description": "Normal"}
        }
        
        sync_service.add_to_offline_queue(low_priority_media)
        sync_service.add_to_offline_queue(high_priority_media)
        
        # Vérifier que l'élément haute priorité est en premier
        queue = sync_service.get_offline_queue()
        assert queue[0]["priority"] == "high"
        assert queue[1]["priority"] == "low"
    
    def test_offline_sync_retry_mechanism(self):
        """Test mécanisme de retry pour la synchronisation"""
        sync_service = OfflineSyncService()
        
        # Ajouter un média à la file
        media_item = {
            "id": str(uuid.uuid4()),
            "intervention_id": str(uuid.uuid4()),
            "type_media": "photo",
            "file_path": "/offline/retry_test.jpg",
            "retry_count": 0,
            "max_retries": 3
        }
        
        sync_service.add_to_offline_queue(media_item)
        
        # Simuler des échecs de synchronisation
        for attempt in range(3):
            success = sync_service.sync_offline_media(media_item["id"])
            assert success is False  # Simuler l'échec
            
            # Vérifier que le retry_count a été incrémenté
            queue = sync_service.get_offline_queue()
            media = next(item for item in queue if item["id"] == media_item["id"])
            assert media["retry_count"] == attempt + 1
        
        # Après 3 tentatives, l'élément devrait être marqué comme échoué
        queue = sync_service.get_offline_queue()
        media = next(item for item in queue if item["id"] == media_item["id"])
        assert media["retry_count"] == 3
        assert media["status"] == "failed"
    
    def test_offline_sync_batch_processing(self):
        """Test traitement par lots de la synchronisation"""
        sync_service = OfflineSyncService()
        
        # Ajouter plusieurs médias à la file
        media_items = []
        for i in range(10):
            media_item = {
                "id": str(uuid.uuid4()),
                "intervention_id": str(uuid.uuid4()),
                "type_media": "photo",
                "file_path": f"/offline/batch_{i}.jpg",
                "metadata": {"description": f"Batch {i}"}
            }
            media_items.append(media_item)
            sync_service.add_to_offline_queue(media_item)
        
        # Traiter par lots
        batch_size = 5
        processed_count = 0
        
        for batch in sync_service.process_offline_batch(batch_size):
            processed_count += len(batch)
            assert len(batch) <= batch_size
        
        assert processed_count == 10
    
    def test_offline_sync_conflict_resolution(self):
        """Test résolution de conflits de synchronisation"""
        sync_service = OfflineSyncService()
        
        # Ajouter un média avec des métadonnées conflictuelles
        media_item = {
            "id": str(uuid.uuid4()),
            "intervention_id": str(uuid.uuid4()),
            "type_media": "photo",
            "file_path": "/offline/conflict.jpg",
            "metadata": {"description": "Original"},
            "server_version": 1,
            "local_version": 2
        }
        
        sync_service.add_to_offline_queue(media_item)
        
        # Simuler un conflit de version
        conflict_resolution = sync_service.resolve_sync_conflict(media_item["id"])
        
        assert conflict_resolution is not None
        assert conflict_resolution["action"] in ["keep_local", "keep_server", "merge"]
        
        if conflict_resolution["action"] == "merge":
            assert "merged_metadata" in conflict_resolution


class TestOfflineMediaValidation:
    """Tests de validation des médias hors-ligne"""
    
    def test_offline_media_integrity_check(self):
        """Test vérification d'intégrité des médias hors-ligne"""
        processor = MediaProcessor()
        
        # Créer un fichier temporaire avec un hash connu
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            content = b"test content for integrity check"
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Calculer le hash du fichier
            file_hash = processor.calculate_file_hash(temp_file_path)
            
            # Vérifier l'intégrité
            is_valid = processor.verify_file_integrity(temp_file_path, file_hash)
            assert is_valid is True
            
            # Modifier le fichier et vérifier que l'intégrité échoue
            with open(temp_file_path, 'ab') as f:
                f.write(b"corrupted")
            
            is_valid = processor.verify_file_integrity(temp_file_path, file_hash)
            assert is_valid is False
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_offline_media_format_validation(self):
        """Test validation du format des médias hors-ligne"""
        processor = MediaProcessor()
        
        # Test avec différents formats de fichiers
        test_cases = [
            ("test.jpg", "image/jpeg", True),
            ("test.png", "image/png", True),
            ("test.mp4", "video/mp4", True),
            ("test.txt", "text/plain", False),
            ("test.exe", "application/x-msdownload", False)
        ]
        
        for filename, mime_type, should_be_valid in test_cases:
            with tempfile.NamedTemporaryFile(suffix=f".{filename.split('.')[-1]}", delete=False) as temp_file:
                temp_file.write(b"fake content")
                temp_file_path = temp_file.name
            
            try:
                is_valid = processor.validate_media_format(temp_file_path, mime_type)
                assert is_valid == should_be_valid
                
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
    
    def test_offline_media_size_validation(self):
        """Test validation de la taille des médias hors-ligne"""
        processor = MediaProcessor()
        
        # Test avec différentes tailles de fichiers
        test_cases = [
            (1024, True),  # 1KB - valide
            (1024 * 1024, True),  # 1MB - valide
            (10 * 1024 * 1024, True),  # 10MB - valide
            (100 * 1024 * 1024, False),  # 100MB - trop volumineux
        ]
        
        for file_size, should_be_valid in test_cases:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(b"x" * file_size)
                temp_file_path = temp_file.name
            
            try:
                is_valid = processor.validate_media_size(temp_file_path, max_size=50 * 1024 * 1024)  # 50MB max
                assert is_valid == should_be_valid
                
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)


class TestOfflineMediaRecovery:
    """Tests de récupération des médias hors-ligne"""
    
    def test_offline_media_recovery_from_corruption(self):
        """Test récupération après corruption de médias hors-ligne"""
        processor = MediaProcessor()
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            temp_file.write(b"original content")
            temp_file_path = temp_file.name
        
        try:
            # Calculer le hash original
            original_hash = processor.calculate_file_hash(temp_file_path)
            
            # Corrompre le fichier
            with open(temp_file_path, 'ab') as f:
                f.write(b"corruption")
            
            # Vérifier que le fichier est corrompu
            corrupted_hash = processor.calculate_file_hash(temp_file_path)
            assert corrupted_hash != original_hash
            
            # Tenter la récupération
            recovery_success = processor.recover_corrupted_media(temp_file_path, original_hash)
            
            if recovery_success:
                # Vérifier que le fichier a été récupéré
                recovered_hash = processor.calculate_file_hash(temp_file_path)
                assert recovered_hash == original_hash
            else:
                # Si la récupération échoue, vérifier que le fichier est marqué comme corrompu
                assert processor.is_media_corrupted(temp_file_path)
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_offline_media_backup_and_restore(self):
        """Test sauvegarde et restauration des médias hors-ligne"""
        processor = MediaProcessor()
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            content = b"backup test content"
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Créer une sauvegarde
            backup_path = processor.create_media_backup(temp_file_path)
            assert os.path.exists(backup_path)
            
            # Vérifier que la sauvegarde est identique
            with open(temp_file_path, 'rb') as original:
                with open(backup_path, 'rb') as backup:
                    assert original.read() == backup.read()
            
            # Modifier le fichier original
            with open(temp_file_path, 'ab') as f:
                f.write(b"modified")
            
            # Restaurer depuis la sauvegarde
            restore_success = processor.restore_media_from_backup(temp_file_path, backup_path)
            assert restore_success is True
            
            # Vérifier que le fichier a été restauré
            with open(temp_file_path, 'rb') as f:
                restored_content = f.read()
            assert restored_content == content
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(backup_path):
                os.unlink(backup_path)
    
    def test_offline_media_cleanup(self):
        """Test nettoyage des médias hors-ligne"""
        processor = MediaProcessor()
        
        # Créer plusieurs fichiers temporaires
        temp_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_file.write(f"content {i}".encode())
                temp_files.append(temp_file.name)
        
        try:
            # Marquer certains fichiers comme obsolètes
            obsolete_files = temp_files[:2]
            for file_path in obsolete_files:
                processor.mark_media_as_obsolete(file_path)
            
            # Nettoyer les fichiers obsolètes
            cleaned_count = processor.cleanup_obsolete_media(temp_files)
            assert cleaned_count == 2
            
            # Vérifier que les fichiers obsolètes ont été supprimés
            for file_path in obsolete_files:
                assert not os.path.exists(file_path)
            
            # Vérifier que les fichiers non obsolètes sont toujours là
            for file_path in temp_files[2:]:
                assert os.path.exists(file_path)
            
        finally:
            # Nettoyer les fichiers restants
            for file_path in temp_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)
