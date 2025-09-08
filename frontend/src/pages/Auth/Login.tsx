import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../contexts/AuthContext';
import { LoginForm } from '../../types';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';

const Login: React.FC = () => {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>();

  const onSubmit = async (data: LoginForm) => {
    try {
      setLoading(true);
      await login(data);
    } catch (error) {
      // Error is handled in the context
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Connexion à SmartLeakPro
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Accédez à votre compte pour gérer vos inspections
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            <Input
              label="Nom d'utilisateur"
              {...register('username', { required: 'Le nom d\'utilisateur est requis' })}
              error={errors.username?.message}
              autoComplete="username"
            />
            
            <Input
              label="Mot de passe"
              type="password"
              {...register('password', { required: 'Le mot de passe est requis' })}
              error={errors.password?.message}
              autoComplete="current-password"
            />
          </div>
          
          <div>
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="w-full"
            >
              Se connecter
            </Button>
          </div>
        </form>
        
        <div className="text-center">
          <p className="text-sm text-gray-600">
            Application de gestion d'inspections de fuites d'eau
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
