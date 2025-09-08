import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Modal, Form, Alert, Badge, Spinner, Table, Dropdown } from 'react-bootstrap';
import { rapportService, Rapport, RapportCreate, GenerationRapport, RapportStats } from '../services/rapportService';
import { interventionService, Intervention } from '../services/interventionService';

const Rapports: React.FC = () => {
  const [rapports, setRapports] = useState<Rapport[]>([]);
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [editingRapport, setEditingRapport] = useState<Rapport | null>(null);
  const [stats, setStats] = useState<RapportStats | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  
  // Filtres
  const [filters, setFilters] = useState({
    type_rapport: '',
    statut: '',
    search: ''
  });

  const [formData, setFormData] = useState<RapportCreate>({
    intervention_id: '',
    type_rapport: 'inspection',
    titre: '',
    description: '',
    auteur_rapport: ''
  });

  const [generateData, setGenerateData] = useState<GenerationRapport>({
    intervention_id: '',
    type_rapport: 'inspection',
    format_export: 'pdf',
    inclure_medias: true,
    inclure_gps: true
  });

  useEffect(() => {
    loadData();
  }, [currentPage, filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [rapportsResponse, interventionsResponse, statsData] = await Promise.all([
        rapportService.getRapports(
          currentPage, 
          10, 
          undefined, 
          filters.type_rapport || undefined,
          filters.statut || undefined,
          undefined,
          undefined,
          undefined,
          filters.search || undefined
        ),
        interventionService.getInterventions(1, 1000),
        rapportService.getStats()
      ]);
      
      setRapports(rapportsResponse.rapports);
      setTotalPages(rapportsResponse.pages);
      setTotal(rapportsResponse.total);
      setInterventions(interventionsResponse.interventions);
      setStats(statsData);
    } catch (err) {
      setError('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingRapport) {
        await rapportService.updateRapport(editingRapport.id, formData);
      } else {
        await rapportService.createRapport(formData);
      }
      setShowModal(false);
      setEditingRapport(null);
      resetForm();
      await loadData();
    } catch (err) {
      setError('Erreur lors de la sauvegarde');
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await rapportService.generateRapport(generateData);
      setShowGenerateModal(false);
      resetGenerateForm();
      await loadData();
    } catch (err) {
      setError('Erreur lors de la génération du rapport');
    }
  };

  const handleEdit = (rapport: Rapport) => {
    setEditingRapport(rapport);
    setFormData({
      intervention_id: rapport.intervention_id,
      type_rapport: rapport.type_rapport,
      titre: rapport.titre,
      description: rapport.description || '',
      auteur_rapport: rapport.auteur_rapport || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce rapport ?')) {
      try {
        await rapportService.deleteRapport(id);
        await loadData();
      } catch (err) {
        setError('Erreur lors de la suppression');
      }
    }
  };

  const handleDownload = async (id: string) => {
    try {
      const blob = await rapportService.downloadRapport(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `rapport_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Erreur lors du téléchargement');
    }
  };

  const resetForm = () => {
    setFormData({
      intervention_id: '',
      type_rapport: 'inspection',
      titre: '',
      description: '',
      auteur_rapport: ''
    });
  };

  const resetGenerateForm = () => {
    setGenerateData({
      intervention_id: '',
      type_rapport: 'inspection',
      format_export: 'pdf',
      inclure_medias: true,
      inclure_gps: true
    });
  };

  const getStatusBadge = (statut: string) => {
    const variants = {
      'brouillon': 'secondary',
      'validé': 'success',
      'archivé': 'info'
    };
    return <Badge bg={variants[statut as keyof typeof variants] || 'secondary'}>{statut}</Badge>;
  };

  const getTypeBadge = (type: string) => {
    const variants = {
      'inspection': 'primary',
      'validation': 'success',
      'intervention': 'warning',
      'maintenance': 'info',
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
            <i className="fas fa-file-alt me-2"></i>
            Rapports & Documentation
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
                <i className="fas fa-file-alt stats-icon"></i>
                <div className="stats-number">{stats.total_rapports}</div>
                <div className="stats-label">Total Rapports</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-calendar-month stats-icon"></i>
                <div className="stats-number">{stats.rapports_ce_mois}</div>
                <div className="stats-label">Ce Mois</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-clock stats-icon"></i>
                <div className="stats-number">{stats.rapports_en_attente}</div>
                <div className="stats-label">En Attente</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-check-circle stats-icon"></i>
                <div className="stats-number">{stats.rapports_valides}</div>
                <div className="stats-label">Validés</div>
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
                <Col md={3}>
                  <Form.Control
                    type="text"
                    placeholder="Rechercher..."
                    value={filters.search}
                    onChange={(e) => setFilters({...filters, search: e.target.value})}
                  />
                </Col>
                <Col md={2}>
                  <Form.Select
                    value={filters.type_rapport}
                    onChange={(e) => setFilters({...filters, type_rapport: e.target.value})}
                  >
                    <option value="">Tous les types</option>
                    <option value="inspection">Inspection</option>
                    <option value="validation">Validation</option>
                    <option value="intervention">Intervention</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="autre">Autre</option>
                  </Form.Select>
                </Col>
                <Col md={2}>
                  <Form.Select
                    value={filters.statut}
                    onChange={(e) => setFilters({...filters, statut: e.target.value})}
                  >
                    <option value="">Tous les statuts</option>
                    <option value="brouillon">Brouillon</option>
                    <option value="validé">Validé</option>
                    <option value="archivé">Archivé</option>
                  </Form.Select>
                </Col>
                <Col md={5} className="text-end">
                  <Button variant="success" onClick={() => setShowModal(true)} className="me-2">
                    <i className="fas fa-plus me-1"></i>
                    Nouveau Rapport
                  </Button>
                  <Button variant="primary" onClick={() => setShowGenerateModal(true)}>
                    <i className="fas fa-magic me-1"></i>
                    Générer Rapport
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Liste des rapports */}
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Liste des Rapports ({total})</h5>
            </Card.Header>
            <Card.Body>
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>Titre</th>
                    <th>Type</th>
                    <th>Statut</th>
                    <th>Intervention</th>
                    <th>Auteur</th>
                    <th>Date</th>
                    <th>Taille</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {rapports.map((rapport) => (
                    <tr key={rapport.id}>
                      <td>
                        <strong>{rapport.titre}</strong>
                        {rapport.description && (
                          <div className="text-muted small">{rapport.description}</div>
                        )}
                      </td>
                      <td>{getTypeBadge(rapport.type_rapport)}</td>
                      <td>{getStatusBadge(rapport.statut)}</td>
                      <td>
                        {rapport.intervention?.type_intervention || 'N/A'}
                        {rapport.intervention?.client && (
                          <div className="text-muted small">{rapport.intervention.client.nom}</div>
                        )}
                      </td>
                      <td>{rapport.auteur_rapport || 'N/A'}</td>
                      <td>{new Date(rapport.date_creation).toLocaleDateString('fr-FR')}</td>
                      <td>
                        {rapport.taille_fichier ? 
                          `${(rapport.taille_fichier / 1024).toFixed(1)} KB` : 
                          'N/A'
                        }
                      </td>
                      <td>
                        <Dropdown>
                          <Dropdown.Toggle variant="outline-secondary" size="sm">
                            <i className="fas fa-ellipsis-v"></i>
                          </Dropdown.Toggle>
                          <Dropdown.Menu>
                            <Dropdown.Item onClick={() => handleEdit(rapport)}>
                              <i className="fas fa-edit me-2"></i>Modifier
                            </Dropdown.Item>
                            {rapport.chemin_fichier && (
                              <Dropdown.Item onClick={() => handleDownload(rapport.id)}>
                                <i className="fas fa-download me-2"></i>Télécharger
                              </Dropdown.Item>
                            )}
                            <Dropdown.Divider />
                            <Dropdown.Item 
                              onClick={() => handleDelete(rapport.id)}
                              className="text-danger"
                            >
                              <i className="fas fa-trash me-2"></i>Supprimer
                            </Dropdown.Item>
                          </Dropdown.Menu>
                        </Dropdown>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>

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

      {/* Modal de création/édition */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {editingRapport ? 'Modifier le Rapport' : 'Nouveau Rapport'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Intervention *</Form.Label>
                  <Form.Select
                    value={formData.intervention_id}
                    onChange={(e) => setFormData({...formData, intervention_id: e.target.value})}
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
                  <Form.Label>Type de rapport *</Form.Label>
                  <Form.Select
                    value={formData.type_rapport}
                    onChange={(e) => setFormData({...formData, type_rapport: e.target.value as any})}
                    required
                  >
                    <option value="inspection">Inspection</option>
                    <option value="validation">Validation</option>
                    <option value="intervention">Intervention</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="autre">Autre</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Titre *</Form.Label>
              <Form.Control
                type="text"
                value={formData.titre}
                onChange={(e) => setFormData({...formData, titre: e.target.value})}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.description || ''}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Auteur</Form.Label>
              <Form.Control
                type="text"
                value={formData.auteur_rapport || ''}
                onChange={(e) => setFormData({...formData, auteur_rapport: e.target.value})}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              {editingRapport ? 'Modifier' : 'Créer'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Modal de génération */}
      <Modal show={showGenerateModal} onHide={() => setShowGenerateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Générer un Rapport Automatique</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleGenerate}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Intervention *</Form.Label>
                  <Form.Select
                    value={generateData.intervention_id}
                    onChange={(e) => setGenerateData({...generateData, intervention_id: e.target.value})}
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
                  <Form.Label>Type de rapport *</Form.Label>
                  <Form.Select
                    value={generateData.type_rapport}
                    onChange={(e) => setGenerateData({...generateData, type_rapport: e.target.value as any})}
                    required
                  >
                    <option value="inspection">Inspection</option>
                    <option value="validation">Validation</option>
                    <option value="intervention">Intervention</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="autre">Autre</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Format d'export *</Form.Label>
                  <Form.Select
                    value={generateData.format_export}
                    onChange={(e) => setGenerateData({...generateData, format_export: e.target.value as any})}
                    required
                  >
                    <option value="pdf">PDF</option>
                    <option value="docx">Word (DOCX)</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Check
                  type="checkbox"
                  label="Inclure les médias"
                  checked={generateData.inclure_medias}
                  onChange={(e) => setGenerateData({...generateData, inclure_medias: e.target.checked})}
                />
              </Col>
              <Col md={6}>
                <Form.Check
                  type="checkbox"
                  label="Inclure les coordonnées GPS"
                  checked={generateData.inclure_gps}
                  onChange={(e) => setGenerateData({...generateData, inclure_gps: e.target.checked})}
                />
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowGenerateModal(false)}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              <i className="fas fa-magic me-1"></i>
              Générer
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default Rapports;
