import React from 'react';
import { Navbar as BootstrapNavbar, Nav, Container, Button } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <BootstrapNavbar bg="primary" variant="dark" expand="lg">
      <Container>
        <BootstrapNavbar.Brand href="/">
          <i className="fas fa-tint me-2"></i>
          SmartLeakPro
        </BootstrapNavbar.Brand>
        
        <BootstrapNavbar.Toggle aria-controls="basic-navbar-nav" />
        
        <BootstrapNavbar.Collapse id="basic-navbar-nav">
          {user && (
            <Nav className="me-auto">
              <Nav.Link 
                href="/dashboard" 
                className={isActive('/dashboard') ? 'active' : ''}
              >
                <i className="fas fa-tachometer-alt me-1"></i>
                Dashboard
              </Nav.Link>
              <Nav.Link 
                href="/clients" 
                className={isActive('/clients') ? 'active' : ''}
              >
                <i className="fas fa-users me-1"></i>
                Clients
              </Nav.Link>
              <Nav.Link 
                href="/interventions" 
                className={isActive('/interventions') ? 'active' : ''}
              >
                <i className="fas fa-tools me-1"></i>
                Interventions
              </Nav.Link>
              <Nav.Link 
                href="/planning" 
                className={isActive('/planning') ? 'active' : ''}
              >
                <i className="fas fa-calendar-alt me-1"></i>
                Planning
              </Nav.Link>
              <Nav.Link 
                href="/rapports" 
                className={isActive('/rapports') ? 'active' : ''}
              >
                <i className="fas fa-file-alt me-1"></i>
                Rapports
              </Nav.Link>
              <Nav.Link 
                href="/medias" 
                className={isActive('/medias') ? 'active' : ''}
              >
                <i className="fas fa-images me-1"></i>
                Médias
              </Nav.Link>
            </Nav>
          )}
          
          <Nav>
            {user ? (
              <>
                <Nav.Link disabled>
                  <i className="fas fa-user me-1"></i>
                  {user.username}
                </Nav.Link>
                <Button 
                  variant="outline-light" 
                  size="sm" 
                  onClick={handleLogout}
                >
                  <i className="fas fa-sign-out-alt me-1"></i>
                  Déconnexion
                </Button>
              </>
            ) : (
              <Nav.Link href="/login">
                <i className="fas fa-sign-in-alt me-1"></i>
                Connexion
              </Nav.Link>
            )}
          </Nav>
        </BootstrapNavbar.Collapse>
      </Container>
    </BootstrapNavbar>
  );
};

export default Navbar;
