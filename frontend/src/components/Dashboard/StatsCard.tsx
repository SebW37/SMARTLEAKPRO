import React from 'react';

interface StatsCardProps {
  title: string;
  value: number;
  total?: number;
  icon: string;
  color: 'blue' | 'green' | 'yellow' | 'red';
}

const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  total,
  icon,
  color,
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    red: 'bg-red-50 text-red-600',
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`w-8 h-8 rounded-md flex items-center justify-center ${colorClasses[color]}`}>
              <span className="text-lg">{icon}</span>
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {title}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-gray-900">
                  {value}
                </div>
                {total !== undefined && (
                  <div className="ml-2 text-sm text-gray-500">
                    / {total}
                  </div>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsCard;
