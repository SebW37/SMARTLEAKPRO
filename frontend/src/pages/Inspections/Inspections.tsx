import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { inspectionService } from '../../services';
import { Inspection, InspectionFilters } from '../../types';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Inspections: React.FC = () => {
  const [filters, setFilters] = useState<InspectionFilters>({});
  const [searchTerm, setSearchTerm] = useState('');

  const { data, isLoading, error } = useQuery(
    ['inspections', filters, searchTerm],
    () => inspectionService.getInspections({ ...filters, search: searchTerm || undefined })
  );

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

  if (isLoading) {
    return <LoadingSpinner className="h-64" />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erreur lors du chargement des inspections</p>
      </div>
    );
  }

  const inspections = data?.results || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inspections</h1>
          <p className="mt-1 text-sm text-gray-500">
            {data?.count || 0} inspection{data?.count !== 1 ? 's' : ''} au total
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0">
          <Link to="/inspections/new">
            <Button variant="primary">
              Nouvelle inspection
            </Button>
          </Link>
        </div>
      </div>

      {/* Search */}
      <div className="flex-1">
        <Input
          placeholder="Rechercher une inspection..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          leftIcon={
            <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          }
        />
      </div>

      {/* Inspections List */}
      {inspections.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Aucune inspection trouvée
          </h3>
          <p className="text-gray-500">
            {searchTerm
              ? 'Aucune inspection ne correspond à votre recherche.'
              : 'Commencez par créer votre première inspection.'
            }
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {inspections.map((inspection: Inspection) => (
              <li key={inspection.id}>
                <Link
                  to={`/inspections/${inspection.id}`}
                  className="block hover:bg-gray-50 px-4 py-4 sm:px-6"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-blue-600 truncate">
                          {inspection.title}
                        </p>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(inspection.status)}`}>
                            {getStatusText(inspection.status)}
                          </span>
                          {inspection.score_percentage !== null && (
                            <span className="text-xs text-gray-500">
                              {inspection.score_percentage.toFixed(1)}%
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <p className="truncate">
                          {inspection.client_name}
                          {inspection.site_name && ` - ${inspection.site_name}`}
                        </p>
                      </div>
                      <div className="mt-1 flex items-center text-sm text-gray-500">
                        <p>
                          📅 {new Date(inspection.inspection_date).toLocaleDateString('fr-FR', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                        {inspection.inspector_name && (
                          <p className="ml-4">
                            👤 {inspection.inspector_name}
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
            Affichage de {inspections.length} sur {data.count} inspections
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

export default Inspections;
