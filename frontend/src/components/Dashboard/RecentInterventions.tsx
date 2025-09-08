import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { interventionService } from '../../services';
import { Intervention } from '../../types';
import LoadingSpinner from '../UI/LoadingSpinner';

const RecentInterventions: React.FC = () => {
  const { data, isLoading } = useQuery(
    'recentInterventions',
    () => interventionService.getInterventions({}, 1)
  );

  const interventions = data?.results?.slice(0, 5) || [];

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
      default:
        return status;
    }
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Interventions récentes</h3>
          <Link to="/interventions">
            <span className="text-sm text-blue-600 hover:text-blue-500">
              Voir toutes
            </span>
          </Link>
        </div>

        {isLoading ? (
          <LoadingSpinner className="h-32" />
        ) : interventions.length === 0 ? (
          <p className="text-sm text-gray-500">Aucune intervention récente</p>
        ) : (
          <div className="space-y-3">
            {interventions.map((intervention: Intervention) => (
              <div key={intervention.id} className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <Link
                    to={`/interventions/${intervention.id}`}
                    className="text-sm font-medium text-gray-900 hover:text-blue-600"
                  >
                    {intervention.title}
                  </Link>
                  <p className="text-sm text-gray-500 truncate">
                    {intervention.client_name}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(intervention.status)}`}>
                    {getStatusText(intervention.status)}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(intervention.scheduled_date).toLocaleDateString('fr-FR')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentInterventions;
