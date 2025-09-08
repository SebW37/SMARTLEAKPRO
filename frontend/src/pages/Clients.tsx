import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Form, Modal, Alert, Spinner } from 'react-bootstrap';
import { clientService, Client, ClientCreate } from '../services/clientService';

const Clients: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState<ClientCreate>({
    nom: '',
    raison_sociale: '',
    adresse: '',
    telephone: '',
    email: '',
    notes: '',
    contact_principal: ''
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      setLoading(true);
      const response = await clientService.getClients(1, 100, searchTerm, statusFilter);
      setClients(response.clients);
    } catch (err) {
      setError('Erreur lors du chargement des clients');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingClient) {
        await clientService.updateClient(editingClient.id, formData);
      } else {
        await clientService.createClient(formData);
      }
      setShowModal(false);
      setEditingClient(null);
      setFormData({
        nom: '',
        raison_sociale: '',
        adresse: '',
        telephone: '',
        email: '',
        notes: '',
        contact_principal: ''
      });
      loadClients();
    } catch (err) {
      setError('Erreur lors de la sauvegarde');
    }
  };

  const handleEdit = (client: Client) => {
    setEditingClient(client);
    setFormData({
      nom: client.nom,
      raison_sociale: client.raison_sociale || '',
      adresse: client.adresse || '',
      telephone: client.telephone || '',
      email: client.email || '',
      notes: client.notes || '',
      contact_principal: client.contact_principal || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce client ?')) {
      try {
        await clientService.deleteClient(id);
        loadClients();
      } catch (err) {
        setError('Erreur lors de la suppression');
      }
    }
  };

  const handleSearch = () => {
    loadClients();
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
            <i className="fas fa-users me-2"></i>
            Gestion des Clients
          </h1>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Row className="mb-4">
        <Col md={6}>
          <Form.Control
            type="text"
            placeholder="Rechercher par nom ou email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </Col>
        <Col md={3}>
          <Form.Select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Tous les statuts</option>
            <option value="actif">Actif</option>
            <option value="inactif">Inactif</option>
          </Form.Select>
        </Col>
        <Col md={3}>
          <Button variant="primary" onClick={handleSearch} className="me-2">
            <i className="fas fa-search me-1"></i>
            Rechercher
          </Button>
          <Button variant="success" onClick={() => setShowModal(true)}>
            <i className="fas fa-plus me-1"></i>
            Nouveau Client
          </Button>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Liste des Clients ({clients.length})</h5>
            </Card.Header>
            <Card.Body className="p-0">
              <Table responsive hover>
                <thead>
                  <tr>
                    <th>Nom</th>
                    <th>Email</th>
                    <th>Téléphone</th>
                    <th>Statut</th>
                    <th>Date Création</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {clients.map((client) => (
                    <tr key={client.id}>
                      <td>
                        <strong>{client.nom}</strong>
                        {client.raison_sociale && (
                          <div className="text-muted small">{client.raison_sociale}</div>
                        )}
                      </td>
                      <td>{client.email || '-'}</td>
                      <td>{client.telephone || '-'}</td>
                      <td>
                        <span className={`badge ${client.statut === 'actif' ? 'bg-success' : 'bg-secondary'}`}>
                          {client.statut}
                        </span>
                      </td>
                      <td>{new Date(client.date_creation).toLocaleDateString('fr-FR')}</td>
                      <td>
                        <Button
                          variant="outline-primary"
                          size="sm"
                          onClick={() => handleEdit(client)}
                          className="me-1"
                        >
                          <i className="fas fa-edit"></i>
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleDelete(client.id)}
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
            {editingClient ? 'Modifier le Client' : 'Nouveau Client'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Nom *</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.nom}
                    onChange={(e) => setFormData({...formData, nom: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Raison Sociale</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.raison_sociale}
                    onChange={(e) => setFormData({...formData, raison_sociale: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Email</Form.Label>
                  <Form.Control
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Téléphone</Form.Label>
                  <Form.Control
                    type="tel"
                    value={formData.telephone}
                    onChange={(e) => setFormData({...formData, telephone: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Adresse</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={formData.adresse}
                onChange={(e) => setFormData({...formData, adresse: e.target.value})}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Contact Principal</Form.Label>
              <Form.Control
                type="text"
                value={formData.contact_principal}
                onChange={(e) => setFormData({...formData, contact_principal: e.target.value})}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Notes</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              {editingClient ? 'Modifier' : 'Créer'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default Clients;
