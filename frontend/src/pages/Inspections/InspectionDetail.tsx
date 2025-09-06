import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { inspectionService } from '../../services';
import { Inspection } from '../../types';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import Button from '../../components/UI/Button';
import { LocationPicker } from '../../components/Geolocation/LocationPicker';
import { LocationTracker } from '../../components/Geolocation/LocationTracker';
import { Modal } from '../../components/UI/Modal';

const InspectionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const inspectionId = parseInt(id || '0');
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [showTrackingModal, setShowTrackingModal] = useState(false);

  const { data: inspection, isLoading, error } = useQuery(
    ['inspection', inspectionId],
    () => inspectionService.getInspection(inspectionId),
    { enabled: !!inspectionId }
  );

  if (isLoading) {
    return <LoadingSpinner className="h-64" />;
  }

  if (error || !inspection) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Inspection non trouvée</p>
        <Link to="/inspections">
          <Button variant="primary" className="mt-4">
            Retour aux inspections
          </Button>
        </Link>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'validated':
        return 'bg-blue-100 text-blue-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'draft':
        return 'Brouillon';
      case 'in_progress':
        return 'En cours';
      case 'completed':
        return 'Terminée';
      case 'validated':
        return 'Validée';
      case 'rejected':
        return 'Rejetée';
      default:
        return status;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <nav className="flex" aria-label="Breadcrumb">
            <ol className="flex items-center space-x-4">
              <li>
                <Link to="/inspections" className="text-gray-400 hover:text-gray-500">
                  Inspections
                </Link>
              </li>
              <li>
                <div className="flex items-center">
                  <svg className="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="ml-4 text-sm font-medium text-gray-500">{inspection.title}</span>
                </div>
              </li>
            </ol>
          </nav>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{inspection.title}</h1>
        </div>
        
        <div className="mt-4 sm:mt-0 flex space-x-3">
          {inspection.status === 'draft' && (
            <Button
              variant="success"
              onClick={() => {
                // Handle start inspection
                console.log('Start inspection');
              }}
            >
              Démarrer
            </Button>
          )}
          {inspection.status === 'in_progress' && (
            <Button
              variant="success"
              onClick={() => {
                // Handle complete inspection
                console.log('Complete inspection');
              }}
            >
              Terminer
            </Button>
          )}
          {inspection.status === 'completed' && (
            <Button
              variant="primary"
              onClick={() => {
                // Handle validate inspection
                console.log('Validate inspection');
              }}
            >
              Valider
            </Button>
          )}
          <Link to={`/inspections/${inspection.id}/edit`}>
            <Button variant="secondary">
              Modifier
            </Button>
          </Link>
        </div>
      </div>

      {/* Status */}
      <div className="flex flex-wrap gap-4">
        <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(inspection.status)}`}>
          {getStatusText(inspection.status)}
        </span>
        {inspection.compliance_status && (
          <span className="inline-flex px-3 py-1 text-sm font-semibold rounded-full bg-blue-100 text-blue-800">
            {inspection.compliance_status}
          </span>
        )}
        {inspection.score_percentage !== null && (
          <span className="inline-flex px-3 py-1 text-sm font-semibold rounded-full bg-green-100 text-green-800">
            Score: {inspection.score_percentage.toFixed(1)}%
          </span>
        )}
      </div>

      {/* Inspection Info */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Informations générales</h3>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Client</dt>
                  <dd className="text-sm text-gray-900">
                    <Link to={`/clients/${inspection.client}`} className="text-blue-600 hover:text-blue-500">
                      {inspection.client_name}
                    </Link>
                  </dd>
                </div>
                {inspection.site_name && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Site</dt>
                    <dd className="text-sm text-gray-900">{inspection.site_name}</dd>
                  </div>
                )}
                {inspection.inspector_name && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Inspecteur</dt>
                    <dd className="text-sm text-gray-900">{inspection.inspector_name}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-sm font-medium text-gray-500">Date d'inspection</dt>
                  <dd className="text-sm text-gray-900">
                    {new Date(inspection.inspection_date).toLocaleString('fr-FR')}
                  </dd>
                </div>
              </dl>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Résultats</h3>
              <dl className="space-y-3">
                {inspection.score !== null && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Score</dt>
                    <dd className="text-sm text-gray-900">
                      {inspection.score} / {inspection.max_score || 'N/A'}
                    </dd>
                  </div>
                )}
                {inspection.score_percentage !== null && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Pourcentage</dt>
                    <dd className="text-sm text-gray-900">
                      {inspection.score_percentage.toFixed(1)}%
                    </dd>
                  </div>
                )}
                {inspection.duration && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Durée</dt>
                    <dd className="text-sm text-gray-900">{inspection.duration}</dd>
                  </div>
                )}
                {inspection.started_at && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Débuté à</dt>
                    <dd className="text-sm text-gray-900">
                      {new Date(inspection.started_at).toLocaleString('fr-FR')}
                    </dd>
                  </div>
                )}
                {inspection.completed_at && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Terminé à</dt>
                    <dd className="text-sm text-gray-900">
                      {new Date(inspection.completed_at).toLocaleString('fr-FR')}
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
          
          {inspection.description && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Description</h3>
              <p className="text-sm text-gray-900">{inspection.description}</p>
            </div>
          )}
          
          {inspection.notes && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Notes</h3>
              <p className="text-sm text-gray-900">{inspection.notes}</p>
            </div>
          )}
          
          {inspection.recommendations && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Recommandations</h3>
              <p className="text-sm text-gray-900">{inspection.recommendations}</p>
            </div>
          )}
        </div>
      </div>

      {/* Form Data */}
      {inspection.form_data && Object.keys(inspection.form_data).length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Données du formulaire</h3>
            <div className="space-y-3">
              {Object.entries(inspection.form_data).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <dt className="text-sm font-medium text-gray-500">{key}</dt>
                  <dd className="text-sm text-gray-900">{String(value)}</dd>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InspectionDetail;
