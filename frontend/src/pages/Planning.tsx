import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Button, Modal, Form, Alert, Badge, Spinner } from 'react-bootstrap';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';
import { planningService, RendezVous, RendezVousCreate, CalendarEvent, PlanningStats } from '../services/planningService';
import { clientService, Client } from '../services/clientService';
import { interventionService, Intervention } from '../services/interventionService';

const Planning: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingRdv, setEditingRdv] = useState<RendezVous | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [stats, setStats] = useState<PlanningStats | null>(null);
  const [view, setView] = useState('dayGridMonth');
  const [technicienFilter, setTechnicienFilter] = useState('');
  
  const calendarRef = useRef<FullCalendar>(null);
  
  const [formData, setFormData] = useState<RendezVousCreate>({
    client_id: '',
    date_heure_debut: '',
    date_heure_fin: '',
    utilisateur_responsable: '',
    notes: '',
    couleur: '#007bff',
    rappel_avant: 24
  });

  useEffect(() => {
    loadData();
  }, [technicienFilter]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [clientsResponse, interventionsResponse, statsData] = await Promise.all([
        clientService.getClients(1, 1000),
        interventionService.getInterventions(1, 1000),
        planningService.getStats()
      ]);
      
      setClients(clientsResponse.clients);
      setInterventions(interventionsResponse.interventions);
      setStats(statsData);
      
      await loadCalendarEvents();
    } catch (err) {
      setError('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const loadCalendarEvents = async () => {
    try {
      const response = await planningService.getCalendarEvents(undefined, undefined, technicienFilter);
      setEvents(response.events);
    } catch (err) {
      console.error('Erreur lors du chargement des événements:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingRdv) {
        await planningService.updateRendezVous(editingRdv.id, formData);
      } else {
        await planningService.createRendezVous(formData);
      }
      setShowModal(false);
      setEditingRdv(null);
      resetForm();
      await loadCalendarEvents();
      await loadData(); // Recharger les stats
    } catch (err) {
      setError('Erreur lors de la sauvegarde');
    }
  };

  const handleEdit = (rdv: RendezVous) => {
    setEditingRdv(rdv);
    setFormData({
      client_id: rdv.client_id,
      intervention_id: rdv.intervention_id || '',
      date_heure_debut: rdv.date_heure_debut.slice(0, 16),
      date_heure_fin: rdv.date_heure_fin.slice(0, 16),
      utilisateur_responsable: rdv.utilisateur_responsable || '',
      notes: rdv.notes || '',
      couleur: rdv.couleur || '#007bff',
      rappel_avant: rdv.rappel_avant
    });
    setShowModal(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce rendez-vous ?')) {
      try {
        await planningService.deleteRendezVous(id);
        await loadCalendarEvents();
        await loadData();
      } catch (err) {
        setError('Erreur lors de la suppression');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      client_id: '',
      date_heure_debut: '',
      date_heure_fin: '',
      utilisateur_responsable: '',
      notes: '',
      couleur: '#007bff',
      rappel_avant: 24
    });
  };

  const handleDateSelect = (selectInfo: any) => {
    setSelectedDate(selectInfo.start);
    setFormData({
      ...formData,
      date_heure_debut: selectInfo.start.toISOString().slice(0, 16),
      date_heure_fin: selectInfo.end.toISOString().slice(0, 16)
    });
    setShowModal(true);
  };

  const handleEventClick = (clickInfo: any) => {
    const event = clickInfo.event;
    const rdv: RendezVous = {
      id: event.id,
      client_id: event.extendedProps.client_id || '',
      intervention_id: event.extendedProps.intervention_id,
      date_heure_debut: event.start.toISOString(),
      date_heure_fin: event.end.toISOString(),
      statut: event.extendedProps.statut,
      utilisateur_responsable: event.extendedProps.technicien,
      notes: event.extendedProps.notes,
      couleur: event.backgroundColor,
      rappel_avant: event.extendedProps.rappel_avant,
      date_creation: '',
      client: { id: '', nom: event.extendedProps.client }
    };
    handleEdit(rdv);
  };

  const handleEventDrop = async (eventDropInfo: any) => {
    try {
      const event = eventDropInfo.event;
      await planningService.updateRendezVous(event.id, {
        date_heure_debut: event.start.toISOString(),
        date_heure_fin: event.end.toISOString()
      });
    } catch (err) {
      setError('Erreur lors du déplacement du rendez-vous');
      eventDropInfo.revert();
    }
  };

  const getStatusBadge = (statut: string) => {
    const variants = {
      'planifié': 'secondary',
      'confirmé': 'primary',
      'annulé': 'danger',
      'terminé': 'success'
    };
    return <Badge bg={variants[statut as keyof typeof variants] || 'secondary'}>{statut}</Badge>;
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
            <i className="fas fa-calendar-alt me-2"></i>
            Planning & Calendrier
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
                <i className="fas fa-calendar-check stats-icon"></i>
                <div className="stats-number">{stats.total_rdv}</div>
                <div className="stats-label">Total RDV</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-calendar-day stats-icon"></i>
                <div className="stats-number">{stats.rdv_aujourd_hui}</div>
                <div className="stats-label">Aujourd'hui</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-calendar-week stats-icon"></i>
                <div className="stats-number">{stats.rdv_cette_semaine}</div>
                <div className="stats-label">Cette semaine</div>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stats-card text-center">
              <Card.Body>
                <i className="fas fa-exclamation-triangle stats-icon"></i>
                <div className="stats-number">{stats.rdv_en_retard}</div>
                <div className="stats-label">En retard</div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Contrôles */}
      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <Row className="align-items-center">
                <Col md={3}>
                  <Form.Select
                    value={view}
                    onChange={(e) => {
                      setView(e.target.value);
                      if (calendarRef.current) {
                        calendarRef.current.getApi().changeView(e.target.value);
                      }
                    }}
                  >
                    <option value="dayGridMonth">Mois</option>
                    <option value="timeGridWeek">Semaine</option>
                    <option value="timeGridDay">Jour</option>
                    <option value="listWeek">Liste</option>
                  </Form.Select>
                </Col>
                <Col md={3}>
                  <Form.Control
                    type="text"
                    placeholder="Filtrer par technicien..."
                    value={technicienFilter}
                    onChange={(e) => setTechnicienFilter(e.target.value)}
                  />
                </Col>
                <Col md={6} className="text-end">
                  <Button variant="success" onClick={() => setShowModal(true)}>
                    <i className="fas fa-plus me-1"></i>
                    Nouveau RDV
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Calendrier */}
      <Row>
        <Col>
          <Card>
            <Card.Body>
              <FullCalendar
                ref={calendarRef}
                plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
                initialView={view}
                headerToolbar={{
                  left: 'prev,next today',
                  center: 'title',
                  right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
                }}
                events={events}
                selectable={true}
                selectMirror={true}
                dayMaxEvents={true}
                weekends={true}
                select={handleDateSelect}
                eventClick={handleEventClick}
                eventDrop={handleEventDrop}
                eventResize={handleEventDrop}
                height="auto"
                locale="fr"
                buttonText={{
                  today: "Aujourd'hui",
                  month: "Mois",
                  week: "Semaine",
                  day: "Jour",
                  list: "Liste"
                }}
                eventDisplay="block"
                eventTextColor="#ffffff"
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modal de création/édition */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {editingRdv ? 'Modifier le Rendez-vous' : 'Nouveau Rendez-vous'}
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
                  <Form.Label>Intervention (optionnel)</Form.Label>
                  <Form.Select
                    value={formData.intervention_id || ''}
                    onChange={(e) => setFormData({...formData, intervention_id: e.target.value})}
                  >
                    <option value="">Aucune intervention</option>
                    {interventions.map(intervention => (
                      <option key={intervention.id} value={intervention.id}>
                        {intervention.type_intervention} - {intervention.client?.nom}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Date et heure de début *</Form.Label>
                  <Form.Control
                    type="datetime-local"
                    value={formData.date_heure_debut}
                    onChange={(e) => setFormData({...formData, date_heure_debut: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Date et heure de fin *</Form.Label>
                  <Form.Control
                    type="datetime-local"
                    value={formData.date_heure_fin}
                    onChange={(e) => setFormData({...formData, date_heure_fin: e.target.value})}
                    required
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Technicien responsable</Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.utilisateur_responsable || ''}
                    onChange={(e) => setFormData({...formData, utilisateur_responsable: e.target.value})}
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Couleur</Form.Label>
                  <Form.Control
                    type="color"
                    value={formData.couleur || '#007bff'}
                    onChange={(e) => setFormData({...formData, couleur: e.target.value})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Rappel (heures avant)</Form.Label>
                  <Form.Control
                    type="number"
                    min="0"
                    max="168"
                    value={formData.rappel_avant || 24}
                    onChange={(e) => setFormData({...formData, rappel_avant: parseInt(e.target.value) || 24})}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Form.Group className="mb-3">
              <Form.Label>Notes</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={formData.notes || ''}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
              />
            </Form.Group>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Annuler
            </Button>
            <Button variant="primary" type="submit">
              {editingRdv ? 'Modifier' : 'Créer'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default Planning;
