import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Clients from './pages/Clients';
import ClientDetail from './pages/ClientDetail';
import Interventions from './pages/Interventions';
import Planning from './pages/Planning';
import Rapports from './pages/Rapports';
import Medias from './pages/Medias';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar';
import 'bootstrap/dist/css/bootstrap.min.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Navbar />
          <div className="container-fluid mt-4">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/clients" 
                element={
                  <ProtectedRoute>
                    <Clients />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/clients/:id" 
                element={
                  <ProtectedRoute>
                    <ClientDetail />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/interventions" 
                element={
                  <ProtectedRoute>
                    <Interventions />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/planning" 
                element={
                  <ProtectedRoute>
                    <Planning />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/rapports" 
                element={
                  <ProtectedRoute>
                    <Rapports />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/medias" 
                element={
                  <ProtectedRoute>
                    <Medias />
                  </ProtectedRoute>
                } 
              />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
