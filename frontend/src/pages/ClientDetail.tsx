import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Spinner, Alert } from 'react-bootstrap';
import { useParams, useNavigate } from 'react-router-dom';
import { clientService, Client } from '../services/clientService';

const ClientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [client, setClient] = useState<Client | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      loadClient(id);
    }
  }, [id]);

  const loadClient = async (clientId: string) => {
    try {
      setLoading(true);
      const clientData = await clientService.getClient(clientId);
      setClient(clientData);
    } catch (err) {
      setError('Erreur lors du chargement du client');
    } finally {
      setLoading(false);
    }
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

  if (error || !client) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">
          {error || 'Client non trouvé'}
        </Alert>
        <Button variant="primary" onClick={() => navigate('/clients')}>
          Retour à la liste
        </Button>
      </Container>
    );
  }

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <Button 
            variant="outline-secondary" 
            onClick={() => navigate('/clients')}
            className="me-2"
          >
            <i className="fas fa-arrow-left me-1"></i>
            Retour
          </Button>
          <h1 className="d-inline-block ms-2">
            <i className="fas fa-user me-2"></i>
            {client.nom}
          </h1>
        </Col>
      </Row>

      <Row>
        <Col md={8}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Informations Générales</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <p><strong>Nom :</strong> {client.nom}</p>
                  {client.raison_sociale && (
                    <p><strong>Raison Sociale :</strong> {client.raison_sociale}</p>
                  )}
                  <p><strong>Statut :</strong> 
                    <span className={`badge ${client.statut === 'actif' ? 'bg-success' : 'bg-secondary'} ms-2`}>
                      {client.statut}
                    </span>
                  </p>
                </Col>
                <Col md={6}>
                  {client.email && (
                    <p><strong>Email :</strong> {client.email}</p>
                  )}
                  {client.telephone && (
                    <p><strong>Téléphone :</strong> {client.telephone}</p>
                  )}
                  {client.contact_principal && (
                    <p><strong>Contact Principal :</strong> {client.contact_principal}</p>
                  )}
                </Col>
              </Row>
              
              {client.adresse && (
                <div className="mt-3">
                  <p><strong>Adresse :</strong></p>
                  <p className="text-muted">{client.adresse}</p>
                </div>
              )}
              
              {client.notes && (
                <div className="mt-3">
                  <p><strong>Notes :</strong></p>
                  <p className="text-muted">{client.notes}</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Informations Système</h5>
            </Card.Header>
            <Card.Body>
              <p><strong>ID :</strong> <code>{client.id}</code></p>
              <p><strong>Date de Création :</strong> 
                <br />
                <small className="text-muted">
                  {new Date(client.date_creation).toLocaleString('fr-FR')}
                </small>
              </p>
              {client.date_modification && (
                <p><strong>Dernière Modification :</strong>
                  <br />
                  <small className="text-muted">
                    {new Date(client.date_modification).toLocaleString('fr-FR')}
                  </small>
                </p>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default ClientDetail;
