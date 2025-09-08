import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../contexts/AuthContext';
import { User } from '../../types';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Profile: React.FC = () => {
  const { user, updateProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Partial<User>>({
    defaultValues: user || {},
  });

  const onSubmit = async (data: Partial<User>) => {
    try {
      setLoading(true);
      await updateProfile(data);
    } catch (error) {
      // Error is handled in the context
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <LoadingSpinner className="h-64" />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Mon Profil</h1>
        <p className="mt-1 text-sm text-gray-500">
          Gérez vos informations personnelles
        </p>
      </div>

      {/* Profile Form */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input
                label="Prénom"
                {...register('first_name', { required: 'Le prénom est requis' })}
                error={errors.first_name?.message}
              />
              
              <Input
                label="Nom"
                {...register('last_name', { required: 'Le nom est requis' })}
                error={errors.last_name?.message}
              />
            </div>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input
                label="Nom d'utilisateur"
                {...register('username', { required: 'Le nom d\'utilisateur est requis' })}
                error={errors.username?.message}
                disabled
              />
              
              <Input
                label="Email"
                type="email"
                {...register('email', { 
                  required: 'L\'email est requis',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Email invalide'
                  }
                })}
                error={errors.email?.message}
              />
            </div>
            
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <Input
                label="Téléphone"
                {...register('phone')}
                error={errors.phone?.message}
              />
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rôle
                </label>
                <div className="mt-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500">
                  {user.role === 'admin' && 'Administrateur'}
                  {user.role === 'manager' && 'Manager'}
                  {user.role === 'technician' && 'Technicien'}
                  {user.role === 'client' && 'Client'}
                </div>
              </div>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                {...register('is_verified')}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Compte vérifié
              </label>
            </div>
            
            <div className="flex justify-end">
              <Button
                type="submit"
                variant="primary"
                loading={loading}
              >
                Mettre à jour
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* Account Info */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Informations du compte</h3>
          <dl className="space-y-3">
            <div>
              <dt className="text-sm font-medium text-gray-500">Membre depuis</dt>
              <dd className="text-sm text-gray-900">
                {new Date(user.date_joined).toLocaleDateString('fr-FR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </dd>
            </div>
            {user.last_login && (
              <div>
                <dt className="text-sm font-medium text-gray-500">Dernière connexion</dt>
                <dd className="text-sm text-gray-900">
                  {new Date(user.last_login).toLocaleString('fr-FR')}
                </dd>
              </div>
            )}
            <div>
              <dt className="text-sm font-medium text-gray-500">Statut</dt>
              <dd className="text-sm">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  user.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {user.is_active ? 'Actif' : 'Inactif'}
                </span>
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default Profile;
