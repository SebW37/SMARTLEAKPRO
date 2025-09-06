import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { reportService } from '../../services';
import { Report } from '../../types';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Reports: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const { data, isLoading, error } = useQuery(
    ['reports', searchTerm],
    () => reportService.getReports(1)
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'generating':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'archived':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'generating':
        return 'En cours de génération';
      case 'completed':
        return 'Terminé';
      case 'failed':
        return 'Échec';
      case 'archived':
        return 'Archivé';
      default:
        return status;
    }
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'pdf':
        return '📄';
      case 'docx':
        return '📝';
      case 'html':
        return '🌐';
      case 'xlsx':
        return '📊';
      default:
        return '📄';
    }
  };

  const handleDownload = async (report: Report) => {
    try {
      await reportService.downloadReport(report.id, `${report.title}.${report.format}`);
    } catch (error) {
      console.error('Download error:', error);
    }
  };

  if (isLoading) {
    return <LoadingSpinner className="h-64" />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Erreur lors du chargement des rapports</p>
      </div>
    );
  }

  const reports = data?.results || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Rapports</h1>
          <p className="mt-1 text-sm text-gray-500">
            {data?.count || 0} rapport{data?.count !== 1 ? 's' : ''} au total
          </p>
        </div>
        
        <div className="mt-4 sm:mt-0">
          <Button variant="primary">
            Générer un rapport
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="flex-1">
        <Input
          placeholder="Rechercher un rapport..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          leftIcon={
            <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          }
        />
      </div>

      {/* Reports List */}
      {reports.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">📄</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Aucun rapport trouvé
          </h3>
          <p className="text-gray-500">
            {searchTerm
              ? 'Aucun rapport ne correspond à votre recherche.'
              : 'Commencez par générer votre premier rapport.'
            }
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {reports.map((report: Report) => (
              <li key={report.id}>
                <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {report.title}
                        </p>
                        <div className="flex items-center space-x-2">
                          <span className="text-lg">{getFormatIcon(report.format)}</span>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(report.status)}`}>
                            {getStatusText(report.status)}
                          </span>
                        </div>
                      </div>
                      <div className="mt-2 flex items-center text-sm text-gray-500">
                        <p className="truncate">
                          {report.client_name || report.intervention_title || report.inspection_title || 'Rapport général'}
                        </p>
                      </div>
                      <div className="mt-1 flex items-center text-sm text-gray-500">
                        <p>
                          📅 {new Date(report.created_at).toLocaleDateString('fr-FR', {
                            weekday: 'long',
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                        {report.file_size && (
                          <p className="ml-4">
                            💾 {(report.file_size / 1024).toFixed(1)} KB
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0 flex items-center space-x-2">
                      {report.status === 'completed' && report.file_url && (
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleDownload(report)}
                        >
                          Télécharger
                        </Button>
                      )}
                      <Link to={`/reports/${report.id}`}>
                        <Button variant="secondary" size="sm">
                          Voir
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Pagination */}
      {data && data.count > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-700">
            Affichage de {reports.length} sur {data.count} rapports
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

export default Reports;
