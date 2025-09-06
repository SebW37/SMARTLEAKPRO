import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './pages/Auth/Login';
import Dashboard from './pages/Dashboard/Dashboard';
import Clients from './pages/Clients/Clients';
import ClientDetail from './pages/Clients/ClientDetail';
import Interventions from './pages/Interventions/Interventions';
import InterventionDetail from './pages/Interventions/InterventionDetail';
import Inspections from './pages/Inspections/Inspections';
import InspectionDetail from './pages/Inspections/InspectionDetail';
import Reports from './pages/Reports/Reports';
import Profile from './pages/Profile/Profile';
import { GeolocationOffline } from './pages/Settings/GeolocationOffline';
import LoadingSpinner from './components/UI/LoadingSpinner';

const App: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <>
      <Helmet>
        <title>SmartLeakPro - Gestion d'Inspections de Fuites d'Eau</title>
        <meta name="description" content="Application de gestion centralisée des inspections de fuites d'eau" />
      </Helmet>
      
      <Routes>
        <Route
          path="/login"
          element={user ? <Navigate to="/" replace /> : <Login />}
        />
        
        {user ? (
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="clients" element={<Clients />} />
            <Route path="clients/:id" element={<ClientDetail />} />
            <Route path="interventions" element={<Interventions />} />
            <Route path="interventions/:id" element={<InterventionDetail />} />
            <Route path="inspections" element={<Inspections />} />
            <Route path="inspections/:id" element={<InspectionDetail />} />
            <Route path="reports" element={<Reports />} />
            <Route path="profile" element={<Profile />} />
            <Route path="settings/geolocation-offline" element={<GeolocationOffline />} />
          </Route>
        ) : (
          <Route path="*" element={<Navigate to="/login" replace />} />
        )}
      </Routes>
    </>
  );
};

export default App;
