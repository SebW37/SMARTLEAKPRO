import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import { interventionService, InterventionStats } from '../services/interventionService';
import { planningService, PlanningStats } from '../services/planningService';
import { rapportService, RapportStats } from '../services/rapportService';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<InterventionStats | null>(null);
  const [planningStats, setPlanningStats] = useState<PlanningStats | null>(null);
  const [rapportStats, setRapportStats] = useState<RapportStats | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [interventionStats, planningStatsData, rapportStatsData] = await Promise.all([
        interventionService.getStats(),
        planningService.getStats(),
        rapportService.getStats()
      ]);
      setStats(interventionStats);
      setPlanningStats(planningStatsData);
      setRapportStats(rapportStatsData);
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error);
    }
  };

  return (
    <Container>
      <Row>
        <Col>
          <h1 className="mb-4">
            <i className="fas fa-tachometer-alt me-2"></i>
            Dashboard
          </h1>
        </Col>
      </Row>
      
      <Row>
        <Col md={4}>
          <Card className="stats-card text-center">
            <Card.Body>
              <i className="fas fa-users stats-icon"></i>
              <div className="stats-number">0</div>
              <div className="stats-label">Clients</div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4}>
          <Card className="stats-card text-center">
            <Card.Body>
              <i className="fas fa-tools stats-icon"></i>
              <div className="stats-number">{stats?.total || 0}</div>
              <div className="stats-label">Interventions</div>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4}>
          <Card className="stats-card text-center">
            <Card.Body>
              <i className="fas fa-file-alt stats-icon"></i>
              <div className="stats-number">{rapportStats?.total_rapports || 0}</div>
              <div className="stats-label">Rapports</div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">
                <i className="fas fa-info-circle me-2"></i>
                Bienvenue dans SmartLeakPro
              </h5>
            </Card.Header>
            <Card.Body>
              <p>Bonjour <strong>{user?.username}</strong> !</p>
              <p>SmartLeakPro est votre solution de gestion des détections de fuite d'eau.</p>
              <p>Phase 4 : Module Rapports opérationnel</p>
              <ul>
                <li>Gestion des clients</li>
                <li>Gestion des interventions et workflows</li>
                <li>Planning et calendrier interactif</li>
                <li>Génération automatique de rapports</li>
                <li>Authentification sécurisée</li>
                <li>Interface moderne et responsive</li>
              </ul>
              
              {(stats || planningStats || rapportStats) && (
                <div className="mt-3">
                  <h6>Statistiques :</h6>
                  <Row>
                    {stats && (
                      <Col md={3}>
                        <strong>Interventions par statut :</strong>
                        <ul className="list-unstyled">
                          {Object.entries(stats.par_statut).map(([statut, count]) => (
                            <li key={statut}>
                              <span className="badge bg-secondary me-2">{count}</span>
                              {statut}
                            </li>
                          ))}
                        </ul>
                      </Col>
                    )}
                    {planningStats && (
                      <Col md={3}>
                        <strong>RDV par statut :</strong>
                        <ul className="list-unstyled">
                          {Object.entries(planningStats.par_statut).map(([statut, count]) => (
                            <li key={statut}>
                              <span className="badge bg-primary me-2">{count}</span>
                              {statut}
                            </li>
                          ))}
                        </ul>
                      </Col>
                    )}
                    {rapportStats && (
                      <Col md={3}>
                        <strong>Rapports par type :</strong>
                        <ul className="list-unstyled">
                          {Object.entries(rapportStats.par_type).map(([type, count]) => (
                            <li key={type}>
                              <span className="badge bg-success me-2">{count}</span>
                              {type}
                            </li>
                          ))}
                        </ul>
                      </Col>
                    )}
                    {rapportStats && (
                      <Col md={3}>
                        <strong>Rapports par auteur :</strong>
                        <ul className="list-unstyled">
                          {Object.entries(rapportStats.par_auteur).map(([auteur, count]) => (
                            <li key={auteur}>
                              <span className="badge bg-warning me-2">{count}</span>
                              {auteur}
                            </li>
                          ))}
                        </ul>
                      </Col>
                    )}
                  </Row>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;
