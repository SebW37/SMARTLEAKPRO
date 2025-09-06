import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { interventionService } from '../../services';
import { Intervention } from '../../types';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import Button from '../../components/UI/Button';

const InterventionDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const interventionId = parseInt(id || '0');

  const { data: intervention, isLoading, error } = useQuery(
    ['intervention', interventionId],
    () => interventionService.getIntervention(interventionId),
    { enabled: !!interventionId }
  );

  if (isLoading) {
    return <LoadingSpinner className="h-64" />;
  }

  if (error || !intervention) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Intervention non trouvée</p>
        <Link to="/interventions">
          <Button variant="primary" className="mt-4">
            Retour aux interventions
          </Button>
        </Link>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'postponed':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'Planifiée';
      case 'in_progress':
        return 'En cours';
      case 'completed':
        return 'Terminée';
      case 'cancelled':
        return 'Annulée';
      case 'postponed':
        return 'Reportée';
      default:
        return status;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'urgent':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'low':
        return 'Faible';
      case 'medium':
        return 'Moyenne';
      case 'high':
        return 'Haute';
      case 'urgent':
        return 'Urgente';
      default:
        return priority;
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
                <Link to="/interventions" className="text-gray-400 hover:text-gray-500">
                  Interventions
                </Link>
              </li>
              <li>
                <div className="flex items-center">
                  <svg className="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="ml-4 text-sm font-medium text-gray-500">{intervention.title}</span>
                </div>
              </li>
            </ol>
          </nav>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{intervention.title}</h1>
        </div>
        
        <div className="mt-4 sm:mt-0 flex space-x-3">
          {intervention.status === 'scheduled' && (
            <Button
              variant="success"
              onClick={() => {
                // Handle start intervention
                console.log('Start intervention');
              }}
            >
              Démarrer
            </Button>
          )}
          {intervention.status === 'in_progress' && (
            <Button
              variant="success"
              onClick={() => {
                // Handle complete intervention
                console.log('Complete intervention');
              }}
            >
              Terminer
            </Button>
          )}
          <Link to={`/interventions/${intervention.id}/edit`}>
            <Button variant="secondary">
              Modifier
            </Button>
          </Link>
        </div>
      </div>

      {/* Status and Priority */}
      <div className="flex flex-wrap gap-4">
        <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStatusColor(intervention.status)}`}>
          {getStatusText(intervention.status)}
        </span>
        <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getPriorityColor(intervention.priority)}`}>
          {getPriorityText(intervention.priority)}
        </span>
        {intervention.is_overdue && (
          <span className="inline-flex px-3 py-1 text-sm font-semibold rounded-full bg-red-100 text-red-800">
            En retard
          </span>
        )}
      </div>

      {/* Intervention Info */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Informations générales</h3>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Type</dt>
                  <dd className="text-sm text-gray-900 capitalize">{intervention.intervention_type}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Client</dt>
                  <dd className="text-sm text-gray-900">
                    <Link to={`/clients/${intervention.client}`} className="text-blue-600 hover:text-blue-500">
                      {intervention.client_name}
                    </Link>
                  </dd>
                </div>
                {intervention.site_name && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Site</dt>
                    <dd className="text-sm text-gray-900">{intervention.site_name}</dd>
                  </div>
                )}
                {intervention.assigned_technician_name && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Technicien assigné</dt>
                    <dd className="text-sm text-gray-900">{intervention.assigned_technician_name}</dd>
                  </div>
                )}
              </dl>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Planification</h3>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Date planifiée</dt>
                  <dd className="text-sm text-gray-900">
                    {new Date(intervention.scheduled_date).toLocaleString('fr-FR')}
                  </dd>
                </div>
                {intervention.estimated_duration && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Durée estimée</dt>
                    <dd className="text-sm text-gray-900">{intervention.estimated_duration}</dd>
                  </div>
                )}
                {intervention.actual_start_date && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Début réel</dt>
                    <dd className="text-sm text-gray-900">
                      {new Date(intervention.actual_start_date).toLocaleString('fr-FR')}
                    </dd>
                  </div>
                )}
                {intervention.actual_end_date && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Fin réelle</dt>
                    <dd className="text-sm text-gray-900">
                      {new Date(intervention.actual_end_date).toLocaleString('fr-FR')}
                    </dd>
                  </div>
                )}
                {intervention.duration && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Durée réelle</dt>
                    <dd className="text-sm text-gray-900">{intervention.duration}</dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
          
          {intervention.description && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Description</h3>
              <p className="text-sm text-gray-900">{intervention.description}</p>
            </div>
          )}
          
          {intervention.notes && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Notes</h3>
              <p className="text-sm text-gray-900">{intervention.notes}</p>
            </div>
          )}
          
          {intervention.materials_needed && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Matériel nécessaire</h3>
              <p className="text-sm text-gray-900">{intervention.materials_needed}</p>
            </div>
          )}
          
          {intervention.special_instructions && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Instructions spéciales</h3>
              <p className="text-sm text-gray-900">{intervention.special_instructions}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterventionDetail;
