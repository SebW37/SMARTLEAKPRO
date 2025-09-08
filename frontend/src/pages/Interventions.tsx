import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Form, Modal, Alert, Spinner, Badge } from 'react-bootstrap';
import { interventionService, Intervention, InterventionCreate, StatutChange } from '../services/interventionService';
import { clientService, Client } from '../services/clientService';

const Interventions: React.FC = () => {
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [editingIntervention, setEditingIntervention] = useState<Intervention | null>(null);
  const [selectedIntervention, setSelectedIntervention] = useState<Intervention | null>(null);
  const [formData, setFormData] = useState<InterventionCreate>({
    client_id: '',
    date_intervention: new Date().toISOString().slice(0, 16),
    type_intervention: 'inspection',
    priorite: 'normale'
  });
  const [statusChange, setStatusChange] = useState<StatutChange>({
    nouveau_statut: 'planifié',
    commentaire: ''
  });

  // Filtres
  const [filters, setFilters] = useState({
    client_id: '',
    statut: '',
    type_intervention: '',
    priorite: '',
    search: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [interventionsResponse, clientsResponse] = await Promise.all([
        interventionService.getInterventions(1, 100, filters.client_id, filters.statut, filters.type_intervention, filters.priorite, undefined, undefined, undefined, filters.search),
        clientService.getClients(1, 1000)
      ]);
      setInterventions(interventionsResponse.interventions);
      setClients(clientsResponse.clients);
    } catch (err) {
      setError('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingIntervention) {
        await interventionService.updateIntervention(editingIntervention.id, formData);
      } else {
        await interventionService.createIntervention(formData);
      }
      setShowModal(false);
      setEditingIntervention(null);
      resetForm();
      loadData();
    } catch (err) {
      setError('Erreur lors de la sauvegarde');
    }
  };

  const handleStatusChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIntervention) return;
    
    try {
      await interventionService.changeStatus(selectedIntervention.id, statusChange);
      setShowStatusModal(false);
      setSelectedIntervention(null);
      setStatusChange({ nouveau_statut: 'planifié', commentaire: '' });
      loadData();
    } catch (err) {
      setError('Erreur lors du changement de statut');
    }
  };

  const handleEdit = (intervention: Intervention) => {
    setEditingIntervention(intervention);
    setFormData({
      client_id: intervention.client_id,
      date_intervention: intervention.date_intervention.slice(0, 16),
      type_intervention: intervention.type_intervention,
      lieu: intervention.lieu || '',
      description: intervention.description || '',
      technicien_assigné: intervention.technicien_assigné || '',
      priorite: intervention.priorite,
      duree_estimee: intervention.duree_estimee,
      latitude: intervention.latitude || '',
      longitude: intervention.longitude || ''
    });
    setShowModal(true);
  };

  const handleStatusChangeClick = (intervention: Intervention) => {
    setSelectedIntervention(intervention);
    setStatusChange({
      nouveau_statut: intervention.statut,
      commentaire: ''
    });
    setShowStatusModal(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette intervention ?')) {
      try {
        await interventionService.deleteIntervention(id);
        loadData();
      } catch (err) {
        setError('Erreur lors de la suppression');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      client_id: '',
      date_intervention: new Date().toISOString().slice(0, 16),
      type_intervention: 'inspection',
      priorite: 'normale'
    });
  };

  const getStatusBadge = (statut: string) => {
    const variants = {
      'planifié': 'secondary',
      'en_cours': 'warning',
      'validé': 'success',
      'archivé': 'dark'
    };
    return <Badge bg={variants[statut as keyof typeof variants] || 'secondary'}>{statut}</Badge>;
  };

  const getPriorityBadge = (priorite: string) => {
    const variants = {
      'basse': 'success',
      'normale': 'primary',
      'haute': 'warning',
      'urgente': 'danger'
    };
    return <Badge bg={variants[priorite as keyof typeof variants] || 'primary'}>{priorite}</Badge>;
  };

  const getTypeIcon = (type: string) => {
    const icons = {
      'inspection': 'fas fa-search',
      'détection': 'fas fa-tint',
      'réparation': 'fas fa-tools',
      'maintenance': 'fas fa-wrench',
      'autre': 'fas fa-cog'
    };
    return <i className={`${icons[type as keyof typeof icons] || 'fas fa-cog'} me-1`}></i>;
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
    <Container>
      <Row>
        <Col>
          <h1 className="mb-4">
            <i className="fas fa-tools me-2"></i>
            Gestion des Interventions
          </h1>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Filtres */}
      <Row className="mb-4">
        <Card>
          <Card.Header>
            <h6 className="mb-0">Filtres</h6>
          </Card.Header>
          <Card.Body>
            <Row>
              <Col md={3}>
                <Form.Select
                  value={filters.client_id}
                  onChange={(e) => setFilters({...filters, client_id: e.target.value})}
                >
                  <option value="">Tous les clients</option>
                  {clients.map(client => (
                    <option key={client.id} value={client.id}>{client.nom}</option>
                  ))}
                </Form.Select>
              </Col>
              <Col md={2}>
                <Form.Select
                  value={filters.statut}
                  onChange={(e) => setFilters({...filters, statut: e.target.value})}
                >
                  <option value="">Tous les statuts</option>
                  <option value="planifié">Planifié</option>
                  <option value="en_cours">En cours</option>
                  <option value="validé">Validé</option>
                  <option value="archivé">Archivé</option>
                </Form.Select>
              </Col>
              <Col md={2}>
                <Form.Select
                  value={filters.type_intervention}
                  onChange={(e) => setFilters({...filters, type_intervention: e.target.value})}
                >
                  <option value="">Tous les types</option>
                  <option value="inspection">Inspection</option>
                  <option value="détection">Détection</option>
                  <option value="réparation">Réparation</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="autre">Autre</option>
                </Form.Select>
              </Col>
              <Col md={2}>
                <Form.Control
                  type="text"
                  placeholder="Rechercher..."
                  value={filters.search}
                  onChange={(e) => setFilters({...filters, search: e.target.value})}
                />
              </Col>
              <Col md={3}>
                <Button variant="primary" onClick={loadData} className="me-2">
                  <i className="fas fa-search me-1"></i>
                  Filtrer
                </Button>
                <Button variant="success" onClick={() => setShowModal(true)}>
                  <i className="fas fa-plus me-1"></i>
                  Nouvelle Intervention
                </Button>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      </Row>

      {/* Liste des interventions */}
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Liste des Interventions ({interventions.length})</h5>
            </Card.Header>
            <Card.Body className="p-0">
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Client</th>
                    <th>Date</th>
                    <th>Statut</th>
                    <th>Priorité</th>
                    <th>Technicien</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {interventions.map((intervention) => (
                    <tr key={intervention.id}>
                      <td>
                        {getTypeIcon(intervention.type_intervention)}
                        {intervention.type_intervention}
                      </td>
                      <td>
                        <strong>{intervention.client?.nom || 'N/A'}</strong>
                        {intervention.lieu && (
                          <div className="text-muted small">{intervention.lieu}</div>
                        )}
                      </td>
                      <td>
                        {new Date(intervention.date_intervention).toLocaleDateString('fr-FR')}
                        <div className="text-muted small">
                          {new Date(intervention.date_intervention).toLocaleTimeString('fr-FR', {hour: '2-digit', minute: '2-digit'})}
                        </div>
                      </td>
                      <td>{getStatusBadge(intervention.statut)}</td>
                      <td>{getPriorityBadge(intervention.priorite)}</td>
                      <td>{intervention.technicien_assigné || '-'}</td>
                      <td>
                        <Button
                          variant="outline-primary"
                          size="sm"
                          onClick={() => handleEdit(intervention)}
                          className="me-1"
                        >
                          <i className="fas fa-edit"></i>
                        </Button>
                        <Button
                          variant="outline-warning"
                          size="sm"
                          onClick={() => handleStatusChangeClick(intervention)}
                          className="me-1"
                        >
                          <i className="fas fa-exchange-alt"></i>
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleDelete(intervention.id)}
                        >
                          <i className="fas fa-trash"></i>
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modal de création/édition */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {editingIntervention ? 'Modifier l\'Intervention' : 'Nouvelle Intervention'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Client *</Form.Label>
                  <Form.Select
                    value={formData.client_id}
                    onChange={(e) => setFormData({...formData, client_id: e.target.value})}
                    required
                  >
                    <option value="">Sélectionner un client</option>
                    {clients.map(client => (
                      <option key={client.id} value={client.id}>{client.nom}</option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Date d'intervention *</Form.Label>
                  <Form.Control
                    type="datetime-local"
                    value={formData.date_intervention}
                    onChange={(e) => setFormData({...formData, date_intervention: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Type d'intervention *</Form.Label>
                  <Form.Select
                    value={formData.type_intervention}
                    onChange={(e) => setFormData({...formData, type_intervention: e.target.value as any})}
                    required
                  >
                    <option value="inspection">Inspection</option>
                    <option value="détection">Détection</option>
                    <option value="réparation">Réparation</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="autre">Autre</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Priorité</Form.Label>
                  <Form.Select
                    value={formData.priorite}
                    onChange={(e) => setFormData({...formData, priorite: e.target.value as any})}
                  >
                    <option value="basse">Basse</option>
                    <option value="normale">Normale</option>
                    <option value="haute">Haute</option>
                    <option value="urgente">Urgente</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Technicien assigné</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.technicien_assigné || ''}
                    onChange={(e) => setFormData({...formData, technicien_assigné: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Durée estimée (minutes)</Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.duree_estimee || ''}
                    onChange={(e) => setFormData({...formData, duree_estimee: parseInt(e.target.value) || undefined})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Lieu</Form.Label>
              <Form.Control
                type="text"
                value={formData.lieu || ''}
                onChange={(e) => setFormData({...formData, lieu: e.target.value})}
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
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Latitude GPS</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.latitude || ''}
                    onChange={(e) => setFormData({...formData, latitude: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Longitude GPS</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.longitude || ''}
                    onChange={(e) => setFormData({...formData, longitude: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              {editingIntervention ? 'Modifier' : 'Créer'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>

      {/* Modal de changement de statut */}
      <Modal show={showStatusModal} onHide={() => setShowStatusModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Changer le statut</Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleStatusChange}>
          <Modal.Body>
            <Form.Group className="mb-3">
              <Form.Label>Nouveau statut</Form.Label>
              <Form.Select
                value={statusChange.nouveau_statut}
                onChange={(e) => setStatusChange({...statusChange, nouveau_statut: e.target.value as any})}
                required
              >
                <option value="planifié">Planifié</option>
                <option value="en_cours">En cours</option>
                <option value="validé">Validé</option>
                <option value="archivé">Archivé</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Commentaire</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={statusChange.commentaire || ''}
                onChange={(e) => setStatusChange({...statusChange, commentaire: e.target.value})}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowStatusModal(false)}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              Changer le statut
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default Interventions;
