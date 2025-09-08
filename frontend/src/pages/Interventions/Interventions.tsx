import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { interventionService } from '../../services';
import { Intervention, InterventionFilters } from '../../types';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Interventions: React.FC = () => {
  const [filters, setFilters] = useState<InterventionFilters>({});
  const [searchTerm, setSearchTerm] = useState('');

  const { data, isLoading, error } = useQuery(
    ['interventions', filters, searchTerm],
    () => interventionService.getInterventions({ ...filters, search: searchTerm || undefined })
  );

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

  if (isLoading) {
    return <LoadingSpinner className="h-64" />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erreur lors du chargement des interventions</p>
      </div>
    );
  }

  const interventions = data?.results || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Interventions</h1>
          <p className="mt-1 text-sm text-gray-500">
            {data?.count || 0} intervention{data?.count !== 1 ? 's' : ''} au total
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0">
          <Link to="/interventions/new">
            <Button variant="primary">
              Nouvelle intervention
            </Button>
          </Link>
        </div>
      </div>

      {/* Search */}
      <div className="flex-1">
        <Input
          placeholder="Rechercher une intervention..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          leftIcon={
            <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          }
        />
      </div>

      {/* Interventions List */}
      {interventions.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">🔧</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Aucune intervention trouvée
          </h3>
          <p className="text-gray-500">
            {searchTerm
              ? 'Aucune intervention ne correspond à votre recherche.'
              : 'Commencez par créer votre première intervention.'
            }
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {interventions.map((intervention: Intervention) => (
              <li key={intervention.id}>
                <Link
                  to={`/interventions/${intervention.id}`}
                  className="block hover:bg-gray-50 px-4 py-4 sm:px-6"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-blue-600 truncate">
                          {intervention.title}
                        </p>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPriorityColor(intervention.priority)}`}>
                            {getPriorityText(intervention.priority)}
                          </span>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(intervention.status)}`}>
                            {getStatusText(intervention.status)}
                          </span>
                        </div>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <p className="truncate">
                          {intervention.client_name}
                          {intervention.site_name && ` - ${intervention.site_name}`}
                        </p>
                      </div>
                      <div className="mt-1 flex items-center text-sm text-gray-500">
                        <p>
                          📅 {new Date(intervention.scheduled_date).toLocaleDateString('fr-FR', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                        {intervention.assigned_technician_name && (
                          <p className="ml-4">
                            👤 {intervention.assigned_technician_name}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Pagination */}
      {data && data.count > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-700">
            Affichage de {interventions.length} sur {data.count} interventions
          </p>
          
          <div className="flex gap-2">
            {data.previous && (
              <Button variant="secondary" size="sm">
                Précédent
              </Button>
            )}
            {data.next && (
              <Button variant="secondary" size="sm">
                Suivant
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Interventions;
