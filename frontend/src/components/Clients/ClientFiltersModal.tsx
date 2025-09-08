import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import Modal from '../UI/Modal';
import Button from '../UI/Button';
import Input from '../UI/Input';
import { ClientFilters } from '../../types';

interface ClientFiltersModalProps {
  isOpen: boolean;
  onClose: () => void;
  filters: ClientFilters;
  onApply: (filters: ClientFilters) => void;
}

const ClientFiltersModal: React.FC<ClientFiltersModalProps> = ({
  isOpen,
  onClose,
  filters,
  onApply,
}) => {
  const { register, handleSubmit, reset } = useForm<ClientFilters>({
    defaultValues: filters,
  });

  const onSubmit = (data: ClientFilters) => {
    onApply(data);
  };

  const handleClear = () => {
    reset({});
    onApply({});
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Filtrer les clients"
      size="md"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type de client
            </label>
            <select
              {...register('client_type')}
              className="form-select w-full"
            >
              <option value="">Tous les types</option>
              <option value="individual">Particulier</option>
              <option value="company">Entreprise</option>
              <option value="public">Public</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Statut
            </label>
            <select
              {...register('is_active')}
              className="form-select w-full"
            >
              <option value="">Tous les statuts</option>
              <option value="true">Actif</option>
              <option value="false">Inactif</option>
            </select>
          </div>
        </div>
        
        <Input
          label="Ville"
          {...register('city')}
          placeholder="Filtrer par ville"
        />
        
        <div className="flex justify-end space-x-3 pt-4">
          <Button
            type="button"
            variant="secondary"
            onClick={handleClear}
          >
            Effacer
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
          >
            Annuler
          </Button>
          <Button
            type="submit"
            variant="primary"
          >
            Appliquer
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default ClientFiltersModal;
