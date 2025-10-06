import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface RegisterFormData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
}

interface FormErrors {
  email?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  password?: string;
  password_confirm?: string;
}

const Register: React.FC = () => {
  const [formData, setFormData] = useState<RegisterFormData>({
    email: '',
    username: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: '',
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    
    // Clear error when user starts typing
    if (errors[e.target.name as keyof FormErrors]) {
      setErrors({
        ...errors,
        [e.target.name]: '',
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.username) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!formData.first_name) {
      newErrors.first_name = 'First name is required';
    }

    if (!formData.last_name) {
      newErrors.last_name = 'Last name is required';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    const result = await register(formData);
    
    if (result.success) {
      navigate('/chat');
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-6">Create Account</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.email ? 'border-red-300' : 'border-gray-300'
                }`}
                required
                disabled={loading}
              />
              {errors.email && <div className="mt-1 text-sm text-red-600">{errors.email}</div>}
            </div>
            
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.username ? 'border-red-300' : 'border-gray-300'
                }`}
                required
                disabled={loading}
              />
              {errors.username && <div className="mt-1 text-sm text-red-600">{errors.username}</div>}
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
                  First Name
                </label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                    errors.first_name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  required
                  disabled={loading}
                />
                {errors.first_name && <div className="mt-1 text-sm text-red-600">{errors.first_name}</div>}
              </div>
              
              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
                  Last Name
                </label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                    errors.last_name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  required
                  disabled={loading}
                />
                {errors.last_name && <div className="mt-1 text-sm text-red-600">{errors.last_name}</div>}
              </div>
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                }`}
                required
                disabled={loading}
              />
              {errors.password && <div className="mt-1 text-sm text-red-600">{errors.password}</div>}
            </div>
            
            <div>
              <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                id="password_confirm"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${
                  errors.password_confirm ? 'border-red-300' : 'border-gray-300'
                }`}
                required
                disabled={loading}
              />
              {errors.password_confirm && <div className="mt-1 text-sm text-red-600">{errors.password_confirm}</div>}
            </div>
            
            <button
              type="submit"
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>
          
          <div className="mt-6 text-center">
            <span className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
                Login here
              </Link>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
