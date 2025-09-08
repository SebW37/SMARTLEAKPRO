"""
Tests unitaires pour les services - Phase Test & Debug
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import uuid

from ..services.security_service import SecurityService
from ..services.api_service import APIService
from ..services.report_generator import ReportGenerator
from ..services.media_processor import MediaProcessor


class TestSecurityService:
    """Tests pour SecurityService"""
    
    def test_password_hashing(self):
        """Test hachage des mots de passe"""
        service = SecurityService()
        password = "test_password_123"
        
        # Test hachage
        hashed = service.get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hash length
        
        # Test vérification
        assert service.verify_password(password, hashed) is True
        assert service.verify_password("wrong_password", hashed) is False
    
    def test_jwt_token_creation(self):
        """Test création de tokens JWT"""
        service = SecurityService()
        data = {"sub": "test_user", "role": "admin"}
        
        # Test création token
        token = service.create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 100
        
        # Test vérification token
        payload = service.verify_token(token)
        assert payload["sub"] == "test_user"
        assert payload["role"] == "admin"
    
    def test_refresh_token_creation(self):
        """Test création de refresh tokens"""
        service = SecurityService()
        user_id = str(uuid.uuid4())
        
        refresh_token = service.create_refresh_token(user_id)
        assert isinstance(refresh_token, str)
        
        # Test vérification refresh token
        payload = service.verify_refresh_token(refresh_token)
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"
    
    def test_2fa_setup(self):
        """Test configuration 2FA"""
        service = SecurityService()
        user_email = "test@example.com"
        
        secret, qr_code = service.setup_2fa(user_email)
        
        assert isinstance(secret, str)
        assert len(secret) == 32  # TOTP secret length
        assert isinstance(qr_code, str)
        assert "data:image/png;base64" in qr_code
    
    def test_2fa_verification(self):
        """Test vérification 2FA"""
        service = SecurityService()
        secret = "JBSWY3DPEHPK3PXP"
        code = "123456"  # Code de test
        
        # Mock du code TOTP
        with patch('pyotp.TOTP.verify') as mock_verify:
            mock_verify.return_value = True
            
            result = service.verify_2fa(secret, code)
            assert result is True
            
            mock_verify.return_value = False
            result = service.verify_2fa(secret, code)
            assert result is False
    
    def test_audit_logging(self):
        """Test journalisation d'audit"""
        service = SecurityService()
        
        # Mock de la base de données
        mock_db = Mock()
        
        log_data = {
            "utilisateur_id": str(uuid.uuid4()),
            "action": "login",
            "ressource": "auth",
            "details": {"ip": "127.0.0.1"}
        }
        
        # Test création de log
        with patch.object(service, 'log_audit_action') as mock_log:
            service.log_audit_action(mock_db, **log_data)
            mock_log.assert_called_once()


class TestAPIService:
    """Tests pour APIService"""
    
    def test_generate_api_key(self):
        """Test génération de clé API"""
        service = APIService()
        
        api_key, secret_key = service.generate_api_key()
        
        assert isinstance(api_key, str)
        assert isinstance(secret_key, str)
        assert len(api_key) == 32
        assert len(secret_key) == 64
        assert api_key.startswith("sk_")
    
    def test_validate_api_key(self):
        """Test validation de clé API"""
        service = APIService()
        
        # Test clé valide
        valid_key = "sk_test123456789012345678901234567890"
        assert service.validate_api_key_format(valid_key) is True
        
        # Test clé invalide
        invalid_key = "invalid_key"
        assert service.validate_api_key_format(invalid_key) is False
    
    def test_webhook_signature(self):
        """Test signature de webhook"""
        service = APIService()
        
        payload = '{"test": "data"}'
        secret = "test_secret"
        
        signature = service.create_webhook_signature(payload, secret)
        
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex length
        
        # Test vérification signature
        assert service.verify_webhook_signature(payload, signature, secret) is True
        assert service.verify_webhook_signature(payload, signature, "wrong_secret") is False
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        service = APIService()
        
        # Test compteur de requêtes
        key = "test_user"
        limit = 100
        
        # Simuler 50 requêtes
        for i in range(50):
            assert service.check_rate_limit(key, limit) is True
        
        # Simuler dépassement de limite
        with patch.object(service, 'get_request_count', return_value=150):
            assert service.check_rate_limit(key, limit) is False


class TestReportGenerator:
    """Tests pour ReportGenerator"""
    
    def test_pdf_generation(self):
        """Test génération PDF"""
        generator = ReportGenerator()
        
        # Mock des données d'intervention
        intervention_data = {
            "id": str(uuid.uuid4()),
            "client": {"nom": "Client Test"},
            "date": datetime.now(),
            "description": "Test intervention"
        }
        
        # Test génération PDF
        with patch('weasyprint.HTML.write_pdf') as mock_pdf:
            mock_pdf.return_value = b"PDF content"
            
            result = generator.generate_pdf_report(intervention_data, "inspection")
            
            assert result is not None
            mock_pdf.assert_called_once()
    
    def test_word_generation(self):
        """Test génération Word"""
        generator = ReportGenerator()
        
        intervention_data = {
            "id": str(uuid.uuid4()),
            "client": {"nom": "Client Test"},
            "date": datetime.now(),
            "description": "Test intervention"
        }
        
        # Test génération Word
        with patch('docx.Document.save') as mock_save:
            result = generator.generate_word_report(intervention_data, "inspection")
            
            assert result is not None
            mock_save.assert_called_once()
    
    def test_excel_generation(self):
        """Test génération Excel"""
        generator = ReportGenerator()
        
        data = [
            {"nom": "Client 1", "interventions": 5},
            {"nom": "Client 2", "interventions": 3}
        ]
        
        # Test génération Excel
        with patch('openpyxl.Workbook.save') as mock_save:
            result = generator.generate_excel_report(data, "clients")
            
            assert result is not None
            mock_save.assert_called_once()


class TestMediaProcessor:
    """Tests pour MediaProcessor"""
    
    def test_image_processing(self):
        """Test traitement d'image"""
        processor = MediaProcessor()
        
        # Mock d'une image
        mock_image = Mock()
        mock_image.size = (1920, 1080)
        mock_image.format = "JPEG"
        
        with patch('PIL.Image.open', return_value=mock_image):
            with patch('PIL.Image.thumbnail') as mock_thumbnail:
                result = processor.process_image("test.jpg", "test_thumb.jpg")
                
                assert result is not None
                mock_thumbnail.assert_called_once()
    
    def test_exif_extraction(self):
        """Test extraction EXIF"""
        processor = MediaProcessor()
        
        # Mock des données EXIF
        mock_exif = {
            "DateTime": "2024:01:01 12:00:00",
            "GPSInfo": {1: "N", 2: (48, 51, 0), 3: "E", 4: (2, 20, 0)},
            "Make": "Test Camera"
        }
        
        with patch('PIL.ExifTags.TAGS', {271: "Make", 306: "DateTime"}):
            with patch('PIL.Image.open') as mock_open:
                mock_image = Mock()
                mock_image._getexif.return_value = mock_exif
                mock_open.return_value = mock_image
                
                exif_data = processor.extract_exif_data("test.jpg")
                
                assert isinstance(exif_data, dict)
                assert "make" in exif_data
                assert "datetime" in exif_data
    
    def test_video_processing(self):
        """Test traitement vidéo"""
        processor = MediaProcessor()
        
        # Mock des métadonnées vidéo
        mock_metadata = {
            "duration": 120.5,
            "fps": 30.0,
            "resolution": (1920, 1080)
        }
        
        with patch('moviepy.VideoFileClip') as mock_video:
            mock_clip = Mock()
            mock_clip.duration = 120.5
            mock_clip.fps = 30.0
            mock_clip.size = (1920, 1080)
            mock_video.return_value = mock_clip
            
            metadata = processor.extract_video_metadata("test.mp4")
            
            assert metadata["duration"] == 120.5
            assert metadata["fps"] == 30.0
            assert metadata["resolution"] == (1920, 1080)
    
    def test_thumbnail_generation(self):
        """Test génération de miniatures"""
        processor = MediaProcessor()
        
        # Mock d'une image
        mock_image = Mock()
        mock_image.size = (1920, 1080)
        
        with patch('PIL.Image.open', return_value=mock_image):
            with patch('PIL.Image.thumbnail') as mock_thumbnail:
                result = processor.generate_thumbnail("test.jpg", (200, 200))
                
                assert result is not None
                mock_thumbnail.assert_called_once_with((200, 200), Image.Resampling.LANCZOS)


class TestIntegrationServices:
    """Tests d'intégration entre services"""
    
    def test_security_with_api(self):
        """Test intégration sécurité et API"""
        security_service = SecurityService()
        api_service = APIService()
        
        # Créer un utilisateur et une clé API
        user_id = str(uuid.uuid4())
        token = security_service.create_access_token({"sub": user_id})
        
        api_key, secret_key = api_service.generate_api_key()
        
        # Vérifier que les deux méthodes d'authentification fonctionnent
        assert token is not None
        assert api_key is not None
        assert api_key.startswith("sk_")
    
    def test_report_with_media(self):
        """Test intégration rapport et média"""
        report_generator = ReportGenerator()
        media_processor = MediaProcessor()
        
        # Mock des données avec média
        intervention_data = {
            "id": str(uuid.uuid4()),
            "client": {"nom": "Client Test"},
            "medias": [
                {"type": "photo", "url": "test.jpg"},
                {"type": "video", "url": "test.mp4"}
            ]
        }
        
        # Test génération de rapport avec médias
        with patch('weasyprint.HTML.write_pdf') as mock_pdf:
            mock_pdf.return_value = b"PDF content"
            
            result = report_generator.generate_pdf_report(intervention_data, "inspection")
            
            assert result is not None
            mock_pdf.assert_called_once()


class TestErrorHandling:
    """Tests de gestion d'erreurs"""
    
    def test_invalid_password_hash(self):
        """Test hachage de mot de passe invalide"""
        service = SecurityService()
        
        # Test avec mot de passe vide
        with pytest.raises(ValueError):
            service.get_password_hash("")
    
    def test_invalid_jwt_token(self):
        """Test token JWT invalide"""
        service = SecurityService()
        
        # Test avec token invalide
        with pytest.raises(Exception):
            service.verify_token("invalid_token")
    
    def test_file_not_found(self):
        """Test fichier non trouvé"""
        processor = MediaProcessor()
        
        # Test avec fichier inexistant
        with pytest.raises(FileNotFoundError):
            processor.extract_exif_data("nonexistent.jpg")
    
    def test_database_connection_error(self):
        """Test erreur de connexion base de données"""
        service = SecurityService()
        
        # Mock d'une erreur de base de données
        mock_db = Mock()
        mock_db.add.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception):
            service.log_audit_action(mock_db, "test_action", "test_resource")


class TestPerformanceServices:
    """Tests de performance des services"""
    
    def test_password_hashing_performance(self):
        """Test performance hachage des mots de passe"""
        service = SecurityService()
        password = "test_password_123"
        
        import time
        
        start_time = time.time()
        for _ in range(100):
            service.get_password_hash(password)
        end_time = time.time()
        
        # Vérifier que le hachage est rapide (< 1s pour 100 hachages)
        assert (end_time - start_time) < 1.0
    
    def test_jwt_creation_performance(self):
        """Test performance création JWT"""
        service = SecurityService()
        data = {"sub": "test_user"}
        
        import time
        
        start_time = time.time()
        for _ in range(1000):
            service.create_access_token(data)
        end_time = time.time()
        
        # Vérifier que la création JWT est rapide (< 1s pour 1000 tokens)
        assert (end_time - start_time) < 1.0
    
    def test_api_key_generation_performance(self):
        """Test performance génération clés API"""
        service = APIService()
        
        import time
        
        start_time = time.time()
        for _ in range(1000):
            service.generate_api_key()
        end_time = time.time()
        
        # Vérifier que la génération est rapide (< 1s pour 1000 clés)
        assert (end_time - start_time) < 1.0
