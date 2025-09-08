import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { clientService } from '../../services';
import { Client, ClientFilters } from '../../types';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import ClientCard from '../../components/Clients/ClientCard';
import ClientFiltersModal from '../../components/Clients/ClientFiltersModal';

const Clients: React.FC = () => {
  const [filters, setFilters] = useState<ClientFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const { data, isLoading, error } = useQuery(
    ['clients', filters, searchTerm],
    () => clientService.getClients({ ...filters, search: searchTerm || undefined })
  );

  const handleFilterChange = (newFilters: ClientFilters) => {
    setFilters(newFilters);
    setShowFilters(false);
  };

  const clearFilters = () => {
    setFilters({});
    setSearchTerm('');
  };

  if (isLoading) {
    return <LoadingSpinner className="h-64" />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erreur lors du chargement des clients</p>
      </div>
    );
  }

  const clients = data?.results || [];
  const hasActiveFilters = Object.values(filters).some(value => value !== undefined && value !== '') || searchTerm;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clients</h1>
          <p className="mt-1 text-sm text-gray-500">
            {data?.count || 0} client{data?.count !== 1 ? 's' : ''} au total
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0">
          <Link to="/clients/new">
            <Button variant="primary">
              Nouveau client
            </Button>
          </Link>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            placeholder="Rechercher un client..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            leftIcon={
              <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />
        </div>
        
        <div className="flex gap-2">
          <Button
            variant="secondary"
            onClick={() => setShowFilters(true)}
          >
            Filtres
          </Button>
          
          {hasActiveFilters && (
            <Button
              variant="secondary"
              onClick={clearFilters}
            >
              Effacer
            </Button>
          )}
        </div>
      </div>

      {/* Active Filters */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(filters).map(([key, value]) => {
            if (value === undefined || value === '') return null;
            return (
              <span
                key={key}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
              >
                {key}: {value}
                <button
                  onClick={() => setFilters({ ...filters, [key]: undefined })}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            );
          })}
          {searchTerm && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
              Recherche: {searchTerm}
              <button
                onClick={() => setSearchTerm('')}
                className="ml-2 text-blue-600 hover:text-blue-800"
              >
                ×
              </button>
            </span>
          )}
        </div>
      )}

      {/* Clients Grid */}
      {clients.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">👥</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Aucun client trouvé
          </h3>
          <p className="text-gray-500">
            {hasActiveFilters
              ? 'Aucun client ne correspond à vos critères de recherche.'
              : 'Commencez par ajouter votre premier client.'
            }
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {clients.map((client) => (
            <ClientCard key={client.id} client={client} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.count > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-700">
            Affichage de {clients.length} sur {data.count} clients
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

      {/* Filters Modal */}
      <ClientFiltersModal
        isOpen={showFilters}
        onClose={() => setShowFilters(false)}
        filters={filters}
        onApply={handleFilterChange}
      />
    </div>
  );
};

export default Clients;
