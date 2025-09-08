import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Button, Modal, Form, Alert, Badge, Spinner, Table, Dropdown, Image } from 'react-bootstrap';
import { mediaService, MediaThumbnail, MediaUploadData, MediaStats } from '../services/mediaService';
import { interventionService, Intervention } from '../services/interventionService';

const Medias: React.FC = () => {
  const [medias, setMedias] = useState<MediaThumbnail[]>([]);
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedMedia, setSelectedMedia] = useState<MediaThumbnail | null>(null);
  const [stats, setStats] = useState<MediaStats | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  
  // Filtres
  const [filters, setFilters] = useState({
    intervention_id: '',
    type_media: '',
    statut: '',
    avec_gps: false,
    avec_annotations: false,
    search: ''
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadData, setUploadData] = useState<MediaUploadData>({
    intervention_id: '',
    type_media: 'photo',
    annotations: '',
    description: '',
    mode_capture: 'manual'
  });

  useEffect(() => {
    loadData();
  }, [currentPage, filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [mediasResponse, interventionsResponse, statsData] = await Promise.all([
        mediaService.getMedias(
          currentPage, 
          12, 
          filters.intervention_id || undefined,
          undefined,
          filters.type_media || undefined,
          filters.statut || undefined,
          filters.avec_gps || undefined,
          filters.avec_annotations || undefined,
          undefined,
          undefined,
          filters.search || undefined
        ),
        interventionService.getInterventions(1, 1000),
        mediaService.getStats()
      ]);
      
      setMedias(mediasResponse.medias);
      setTotalPages(mediasResponse.pages);
      setTotal(mediasResponse.total);
      setInterventions(interventionsResponse.interventions);
      setStats(statsData);
    } catch (err) {
      setError('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    
    // Déterminer le type de média
    const type = file.type.startsWith('image/') ? 'photo' :
                 file.type.startsWith('video/') ? 'video' :
                 file.type.startsWith('audio/') ? 'audio' :
                 file.type.startsWith('application/pdf') ? 'document' : 'autre';

    setUploadData({
      ...uploadData,
      type_media: type as any
    });

    setShowUploadModal(true);
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileInputRef.current?.files?.[0]) return;

    try {
      setUploading(true);
      const file = fileInputRef.current.files[0];
      
      await mediaService.uploadMedia(
        file,
        uploadData,
        (progress) => setUploadProgress(progress)
      );
      
      setShowUploadModal(false);
      setUploadProgress(0);
      resetUploadForm();
      await loadData();
    } catch (err) {
      setError('Erreur lors de l\'upload');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce média ?')) {
      try {
        await mediaService.deleteMedia(id);
        await loadData();
      } catch (err) {
        setError('Erreur lors de la suppression');
      }
    }
  };

  const handleDownload = async (media: MediaThumbnail) => {
    try {
      const blob = await mediaService.downloadMedia(media.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = media.nom_fichier;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Erreur lors du téléchargement');
    }
  };

  const handleView = (media: MediaThumbnail) => {
    setSelectedMedia(media);
    setShowViewModal(true);
  };

  const resetUploadForm = () => {
    setUploadData({
      intervention_id: '',
      type_media: 'photo',
      annotations: '',
      description: '',
      mode_capture: 'manual'
    });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getStatusBadge = (statut: string) => {
    const variants = {
      'uploading': 'warning',
      'uploaded': 'info',
      'processing': 'primary',
      'ready': 'success',
      'error': 'danger',
      'deleted': 'secondary'
    };
    return <Badge bg={variants[statut as keyof typeof variants] || 'secondary'}>{statut}</Badge>;
  };

  const getTypeBadge = (type: string) => {
    const variants = {
      'photo': 'primary',
      'video': 'success',
      'audio': 'info',
      'document': 'warning',
      'autre': 'secondary'
    };
    return <Badge bg={variants[type as keyof typeof variants] || 'secondary'}>{type}</Badge>;
  };

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="d-flex justify-content-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Chargement...</span>
          </Spinner>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid>
      <Row>
        <Col>
          <h1 className="mb-4">
            <i className="fas fa-images me-2"></i>
            Médias & Collecte Terrain
          </h1>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Statistiques */}
      {stats && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-images stats-icon"></i>
                <div className="stats-number">{stats.total_medias}</div>
                <div className="stats-label">Total Médias</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-calendar-month stats-icon"></i>
                <div className="stats-number">{stats.medias_ce_mois}</div>
                <div className="stats-label">Ce Mois</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-map-marker-alt stats-icon"></i>
                <div className="stats-number">{stats.medias_avec_gps}</div>
                <div className="stats-label">Avec GPS</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-comment stats-icon"></i>
                <div className="stats-number">{stats.medias_avec_annotations}</div>
                <div className="stats-label">Annotés</div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Filtres et actions */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <Row className="align-items-center">
                <Col md={2}>
                  <Form.Control
                    type="text"
                    placeholder="Rechercher..."
                    value={filters.search}
                    onChange={(e) => setFilters({...filters, search: e.target.value})}
                  />
                </Col>
                <Col md={2}>
                  <Form.Select
                    value={filters.intervention_id}
                    onChange={(e) => setFilters({...filters, intervention_id: e.target.value})}
                  >
                    <option value="">Toutes les interventions</option>
                    {interventions.map(intervention => (
                      <option key={intervention.id} value={intervention.id}>
                        {intervention.type_intervention} - {intervention.client?.nom}
                      </option>
                    ))}
                  </Form.Select>
                </Col>
                <Col md={2}>
                  <Form.Select
                    value={filters.type_media}
                    onChange={(e) => setFilters({...filters, type_media: e.target.value})}
                  >
                    <option value="">Tous les types</option>
                    <option value="photo">Photos</option>
                    <option value="video">Vidéos</option>
                    <option value="audio">Audios</option>
                    <option value="document">Documents</option>
                  </Form.Select>
                </Col>
                <Col md={2}>
                  <Form.Check
                    type="checkbox"
                    label="Avec GPS"
                    checked={filters.avec_gps}
                    onChange={(e) => setFilters({...filters, avec_gps: e.target.checked})}
                  />
                </Col>
                <Col md={2}>
                  <Form.Check
                    type="checkbox"
                    label="Annotés"
                    checked={filters.avec_annotations}
                    onChange={(e) => setFilters({...filters, avec_annotations: e.target.checked})}
                  />
                </Col>
                <Col md={2} className="text-end">
                  <Button variant="success" onClick={() => fileInputRef.current?.click()}>
                    <i className="fas fa-upload me-1"></i>
                    Uploader
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    style={{ display: 'none' }}
                    onChange={handleFileUpload}
                    accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
                  />
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Grille des médias */}
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Médias ({total})</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                {medias.map((media) => (
                  <Col md={3} lg={2} key={media.id} className="mb-3">
                    <Card className="media-card">
                      <div className="media-thumbnail" onClick={() => handleView(media)}>
                        {media.type_media === 'photo' ? (
                          <Image
                            src={mediaService.getThumbnailUrl(media)}
                            fluid
                            className="media-image"
                            onError={(e) => {
                              (e.target as HTMLImageElement).src = '/placeholder-image.png';
                            }}
                          />
                        ) : (
                          <div className="media-placeholder">
                            <i className={`${mediaService.getMediaIcon(media.type_media)} fa-3x`}></i>
                          </div>
                        )}
                        <div className="media-overlay">
                          <Badge bg="dark" className="media-type-badge">
                            {getTypeBadge(media.type_media)}
                          </Badge>
                          {media.statut === 'ready' && (
                            <Badge bg="success" className="media-status-badge">
                              <i className="fas fa-check"></i>
                            </Badge>
                          )}
                        </div>
                      </div>
                      <Card.Body className="p-2">
                        <div className="media-info">
                          <div className="media-name" title={media.nom_fichier}>
                            {media.nom_fichier.length > 20 
                              ? `${media.nom_fichier.substring(0, 20)}...` 
                              : media.nom_fichier
                            }
                          </div>
                          <div className="media-details">
                            <small className="text-muted">
                              {mediaService.formatFileSize(media.taille_fichier)}
                            </small>
                            {media.resolution_x && media.resolution_y && (
                              <small className="text-muted d-block">
                                {media.resolution_x}x{media.resolution_y}
                              </small>
                            )}
                            {media.duree && (
                              <small className="text-muted d-block">
                                {mediaService.formatDuration(media.duree)}
                              </small>
                            )}
                          </div>
                        </div>
                        <div className="media-actions mt-2">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleView(media)}
                            className="me-1"
                          >
                            <i className="fas fa-eye"></i>
                          </Button>
                          <Button
                            variant="outline-success"
                            size="sm"
                            onClick={() => handleDownload(media)}
                            className="me-1"
                          >
                            <i className="fas fa-download"></i>
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleDelete(media.id)}
                          >
                            <i className="fas fa-trash"></i>
                          </Button>
                        </div>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="d-flex justify-content-center mt-3">
                  <nav>
                    <ul className="pagination">
                      <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                        <button 
                          className="page-link" 
                          onClick={() => setCurrentPage(currentPage - 1)}
                          disabled={currentPage === 1}
                        >
                          Précédent
                        </button>
                      </li>
                      {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                        <li key={page} className={`page-item ${currentPage === page ? 'active' : ''}`}>
                          <button 
                            className="page-link" 
                            onClick={() => setCurrentPage(page)}
                          >
                            {page}
                          </button>
                        </li>
                      ))}
                      <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                        <button 
                          className="page-link" 
                          onClick={() => setCurrentPage(currentPage + 1)}
                          disabled={currentPage === totalPages}
                        >
                          Suivant
                        </button>
                      </li>
                    </ul>
                  </nav>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modal d'upload */}
      <Modal show={showUploadModal} onHide={() => setShowUploadModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Uploader un Média</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleUpload}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Intervention *</Form.Label>
                  <Form.Select
                    value={uploadData.intervention_id}
                    onChange={(e) => setUploadData({...uploadData, intervention_id: e.target.value})}
                    required
                  >
                    <option value="">Sélectionner une intervention</option>
                    {interventions.map(intervention => (
                      <option key={intervention.id} value={intervention.id}>
                        {intervention.type_intervention} - {intervention.client?.nom}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Type de média *</Form.Label>
                  <Form.Select
                    value={uploadData.type_media}
                    onChange={(e) => setUploadData({...uploadData, type_media: e.target.value as any})}
                    required
                  >
                    <option value="photo">Photo</option>
                    <option value="video">Vidéo</option>
                    <option value="audio">Audio</option>
                    <option value="document">Document</option>
                    <option value="autre">Autre</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Latitude GPS</Form.Label>
                  <Form.Control
                    type="text"
                    value={uploadData.latitude || ''}
                    onChange={(e) => setUploadData({...uploadData, latitude: e.target.value})}
                    placeholder="48.8566"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Longitude GPS</Form.Label>
                  <Form.Control
                    type="text"
                    value={uploadData.longitude || ''}
                    onChange={(e) => setUploadData({...uploadData, longitude: e.target.value})}
                    placeholder="2.3522"
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Annotations</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={uploadData.annotations || ''}
                onChange={(e) => setUploadData({...uploadData, annotations: e.target.value})}
                placeholder="Notes sur le média..."
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={uploadData.description || ''}
                onChange={(e) => setUploadData({...uploadData, description: e.target.value})}
                placeholder="Description détaillée..."
              />
            </Form.Group>
            {uploading && (
              <div className="mb-3">
                <div className="progress">
                  <div 
                    className="progress-bar" 
                    role="progressbar" 
                    style={{ width: `${uploadProgress}%` }}
                  >
                    {uploadProgress}%
                  </div>
                </div>
              </div>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowUploadModal(false)}>
              Annuler
            </Button>
            <Button variant="primary" type="submit" disabled={uploading}>
              {uploading ? 'Upload en cours...' : 'Uploader'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Modal de visualisation */}
      <Modal show={showViewModal} onHide={() => setShowViewModal(false)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>
            {selectedMedia?.nom_fichier}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedMedia && (
            <Row>
              <Col md={8}>
                {selectedMedia.type_media === 'photo' ? (
                  <Image
                    src={mediaService.getMediaUrl(selectedMedia)}
                    fluid
                    className="img-fluid"
                  />
                ) : (
                  <div className="text-center p-5">
                    <i className={`${mediaService.getMediaIcon(selectedMedia.type_media)} fa-5x text-muted`}></i>
                    <p className="mt-3">Prévisualisation non disponible pour ce type de fichier</p>
                  </div>
                )}
              </Col>
              <Col md={4}>
                <h6>Informations</h6>
                <Table size="sm">
                  <tbody>
                    <tr>
                      <td><strong>Type:</strong></td>
                      <td>{getTypeBadge(selectedMedia.type_media)}</td>
                    </tr>
                    <tr>
                      <td><strong>Taille:</strong></td>
                      <td>{mediaService.formatFileSize(selectedMedia.taille_fichier)}</td>
                    </tr>
                    {selectedMedia.resolution_x && selectedMedia.resolution_y && (
                      <tr>
                        <td><strong>Résolution:</strong></td>
                        <td>{selectedMedia.resolution_x}x{selectedMedia.resolution_y}</td>
                      </tr>
                    )}
                    {selectedMedia.duree && (
                      <tr>
                        <td><strong>Durée:</strong></td>
                        <td>{mediaService.formatDuration(selectedMedia.duree)}</td>
                      </tr>
                    )}
                    {selectedMedia.latitude && selectedMedia.longitude && (
                      <tr>
                        <td><strong>GPS:</strong></td>
                        <td>{selectedMedia.latitude}, {selectedMedia.longitude}</td>
                      </tr>
                    )}
                    {selectedMedia.date_prise && (
                      <tr>
                        <td><strong>Date de prise:</strong></td>
                        <td>{new Date(selectedMedia.date_prise).toLocaleString('fr-FR')}</td>
                      </tr>
                    )}
                  </tbody>
                </Table>
                
                {selectedMedia.annotations && (
                  <div className="mt-3">
                    <h6>Annotations</h6>
                    <p className="text-muted">{selectedMedia.annotations}</p>
                  </div>
                )}
                
                {selectedMedia.description && (
                  <div className="mt-3">
                    <h6>Description</h6>
                    <p className="text-muted">{selectedMedia.description}</p>
                  </div>
                )}
                
                <div className="mt-3">
                  <Button 
                    variant="success" 
                    onClick={() => handleDownload(selectedMedia)}
                    className="w-100"
                  >
                    <i className="fas fa-download me-2"></i>
                    Télécharger
                  </Button>
                </div>
              </Col>
            </Row>
          )}
        </Modal.Body>
      </Modal>
    </Container>
  );
};

export default Medias;
