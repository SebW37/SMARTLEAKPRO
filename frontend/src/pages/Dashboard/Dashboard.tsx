import React from 'react';
import { useQuery } from 'react-query';
import { clientService, interventionService, inspectionService, notificationService } from '../../services';
import StatsCard from '../../components/Dashboard/StatsCard';
import RecentInterventions from '../../components/Dashboard/RecentInterventions';
import RecentInspections from '../../components/Dashboard/RecentInspections';
import Notifications from '../../components/Dashboard/Notifications';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Dashboard: React.FC = () => {
  const { data: clientStats, isLoading: clientStatsLoading } = useQuery(
    'clientStats',
    clientService.getClientStats
  );
  
  const { data: interventionStats, isLoading: interventionStatsLoading } = useQuery(
    'interventionStats',
    interventionService.getInterventionStats
  );
  
  const { data: inspectionStats, isLoading: inspectionStatsLoading } = useQuery(
    'inspectionStats',
    inspectionService.getInspectionStats
  );
  
  const { data: notifications, isLoading: notificationsLoading } = useQuery(
    'unreadNotifications',
    notificationService.getUnreadNotifications
  );

  const isLoading = clientStatsLoading || interventionStatsLoading || inspectionStatsLoading;

  if (isLoading) {
    return <LoadingSpinner className="h-64" />;
  }

  const stats = [
    {
      title: 'Clients actifs',
      value: clientStats?.active_clients || 0,
      total: clientStats?.total_clients || 0,
      icon: '👥',
      color: 'blue',
    },
    {
      title: 'Interventions en cours',
      value: interventionStats?.in_progress_interventions || 0,
      total: interventionStats?.total_interventions || 0,
      icon: '🔧',
      color: 'yellow',
    },
    {
      title: 'Inspections terminées',
      value: inspectionStats?.completed_inspections || 0,
      total: inspectionStats?.total_inspections || 0,
      icon: '🔍',
      color: 'green',
    },
    {
      title: 'Notifications non lues',
      value: notifications?.length || 0,
      icon: '🔔',
      color: 'red',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Tableau de bord</h1>
        <p className="mt-1 text-sm text-gray-500">
          Vue d'ensemble de votre activité
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <StatsCard
            key={index}
            title={stat.title}
            value={stat.value}
            total={stat.total}
            icon={stat.icon}
            color={stat.color as 'blue' | 'green' | 'yellow' | 'red'}
          />
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Interventions */}
        <RecentInterventions />
        
        {/* Recent Inspections */}
        <RecentInspections />
      </div>

      {/* Notifications */}
      {notifications && notifications.length > 0 && (
        <div className="lg:col-span-2">
          <Notifications notifications={notifications} />
        </div>
      )}
    </div>
  );
};

export default Dashboard;
