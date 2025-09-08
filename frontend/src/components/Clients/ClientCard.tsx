import React from 'react';
import { Link } from 'react-router-dom';
import { Client } from '../../types';

interface ClientCardProps {
  client: Client;
}

const ClientCard: React.FC<ClientCardProps> = ({ client }) => {
  const getClientTypeIcon = (type: string) => {
    switch (type) {
      case 'individual':
        return '👤';
      case 'company':
        return '🏢';
      case 'public':
        return '🏛️';
      default:
        return '👤';
    }
  };

  const getClientTypeText = (type: string) => {
    switch (type) {
      case 'individual':
        return 'Particulier';
      case 'company':
        return 'Entreprise';
      case 'public':
        return 'Public';
      default:
        return type;
    }
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow duration-200">
      <div className="p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-lg">{getClientTypeIcon(client.client_type)}</span>
            </div>
          </div>
          <div className="ml-4 flex-1 min-w-0">
            <Link
              to={`/clients/${client.id}`}
              className="text-lg font-medium text-gray-900 hover:text-blue-600 truncate block"
            >
              {client.name}
            </Link>
            <p className="text-sm text-gray-500">
              {getClientTypeText(client.client_type)}
            </p>
          </div>
          <div className="flex-shrink-0">
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              client.is_active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {client.is_active ? 'Actif' : 'Inactif'}
            </span>
          </div>
        </div>
        
        <div className="mt-4">
          <div className="text-sm text-gray-600">
            <p className="truncate">{client.address}</p>
            <p className="truncate">{client.postal_code} {client.city}</p>
          </div>
          
          {client.email && (
            <p className="mt-2 text-sm text-gray-500 truncate">
              📧 {client.email}
            </p>
          )}
          
          {client.phone && (
            <p className="text-sm text-gray-500 truncate">
              📞 {client.phone}
            </p>
          )}
        </div>
        
        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {client.sites_count || 0} site{(client.sites_count || 0) !== 1 ? 's' : ''}
          </div>
          
          <div className="flex space-x-2">
            <Link
              to={`/clients/${client.id}`}
              className="text-blue-600 hover:text-blue-500 text-sm font-medium"
            >
              Voir
            </Link>
            <Link
              to={`/clients/${client.id}/edit`}
              className="text-gray-600 hover:text-gray-500 text-sm font-medium"
            >
              Modifier
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClientCard;
