import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { clientService } from '../../services';
import { Client } from '../../types';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import Button from '../../components/UI/Button';

const ClientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const clientId = parseInt(id || '0');

  const { data: client, isLoading, error } = useQuery(
    ['client', clientId],
    () => clientService.getClient(clientId),
    { enabled: !!clientId }
  );

  if (isLoading) {
    return <LoadingSpinner className="h-64" />;
  }

  if (error || !client) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Client non trouvé</p>
        <Link to="/clients">
          <Button variant="primary" className="mt-4">
            Retour aux clients
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <nav className="flex" aria-label="Breadcrumb">
            <ol className="flex items-center space-x-4">
              <li>
                <Link to="/clients" className="text-gray-400 hover:text-gray-500">
                  Clients
                </Link>
              </li>
              <li>
                <div className="flex items-center">
                  <svg className="flex-shrink-0 h-5 w-5 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="ml-4 text-sm font-medium text-gray-500">{client.name}</span>
                </div>
              </li>
            </ol>
          </nav>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{client.name}</h1>
        </div>
        
        <div className="mt-4 sm:mt-0">
          <Link to={`/clients/${client.id}/edit`}>
            <Button variant="primary">
              Modifier
            </Button>
          </Link>
        </div>
      </div>

      {/* Client Info */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Informations générales</h3>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Type</dt>
                  <dd className="text-sm text-gray-900 capitalize">{client.client_type}</dd>
                </div>
                {client.email && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Email</dt>
                    <dd className="text-sm text-gray-900">{client.email}</dd>
                  </div>
                )}
                {client.phone && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Téléphone</dt>
                    <dd className="text-sm text-gray-900">{client.phone}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-sm font-medium text-gray-500">Statut</dt>
                  <dd className="text-sm">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      client.is_active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {client.is_active ? 'Actif' : 'Inactif'}
                    </span>
                  </dd>
                </div>
              </dl>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Adresse</h3>
              <div className="text-sm text-gray-900">
                <p>{client.address}</p>
                <p>{client.postal_code} {client.city}</p>
                <p>{client.country}</p>
              </div>
            </div>
          </div>
          
          {client.notes && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Notes</h3>
              <p className="text-sm text-gray-900">{client.notes}</p>
            </div>
          )}
        </div>
      </div>

      {/* Sites */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Sites</h3>
            <Button variant="secondary" size="sm">
              Ajouter un site
            </Button>
          </div>
          
          {client.sites_count === 0 ? (
            <p className="text-sm text-gray-500">Aucun site enregistré</p>
          ) : (
            <p className="text-sm text-gray-500">
              {client.sites_count} site{client.sites_count !== 1 ? 's' : ''} enregistré{client.sites_count !== 1 ? 's' : ''}
            </p>
          )}
        </div>
      </div>

      {/* Recent Interventions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Interventions récentes</h3>
            <Link to={`/interventions?client=${client.id}`}>
              <Button variant="secondary" size="sm">
                Voir toutes
              </Button>
            </Link>
          </div>
          
          <p className="text-sm text-gray-500">Aucune intervention récente</p>
        </div>
      </div>
    </div>
  );
};

export default ClientDetail;
