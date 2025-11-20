'use client'
import React, { useState } from 'react';
import api from '@/api/axios'
import { AxiosError } from 'axios';
import { OwnerCreateData, OwnerFormProps, FastAPIError } from '@/app/types/data';

const OwnerForm: React.FC<OwnerFormProps> = ({ onOwnerCreated }) => {
  const [formData, setFormData] = useState<OwnerCreateData>({
    name: '',
    email: '',
    phone: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
        await api.post('/integrations/owner', formData);
        
        setSuccess(`Sucesso! ${formData.name} cadastrado.`);
        setError('');
        setFormData({ name: '', email: '', phone: '' });
        onOwnerCreated();

        setTimeout(() => {
          onOwnerCreated;
        }, 100);
        
    } catch (err) {
        setSuccess('');

        const axiosError = err as AxiosError;
        let errorMessage = "Erro ao conectar com o servidor";

        if (axiosError.response) {
            const errorData = axiosError.response.data as FastAPIError;
            
            if (errorData && errorData.detail) {
                errorMessage = Array.isArray(errorData.detail) 
                    ? `${errorData.detail[0].loc[1]}: ${errorData.detail[0].msg}`
                    : String(errorData.detail);
            }
        }
        setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container" style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h3>Cadastrar novo responsável</h3>
      
      {error && <p style={{ color: 'red', fontWeight: 'bold' }}>{error}</p>}
      {success && <p style={{ color: 'green', fontWeight: 'bold' }}>{success}</p>}
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px' }}>
        
        <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '0.9rem' }}>Nome completo *</label>
            <input 
                type="text" name="name" 
                value={formData.name} onChange={handleChange} 
                required maxLength={140}
                style={{ padding: '8px' }}
            />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '0.9rem' }}>Email *</label>
            <input 
                type="email" name="email" 
                value={formData.email} onChange={handleChange} 
                required maxLength={140}
                style={{ padding: '8px' }}
            />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
            <label style={{ fontSize: '0.9rem' }}>Telefone</label>
            <input 
                type="tel" name="phone" 
                value={formData.phone} onChange={handleChange} 
                maxLength={20}
                style={{ padding: '8px' }}
            />
        </div>

        <button 
            type="submit" 
            disabled={loading}
            style={{ padding: '10px', marginTop: '10px', cursor: 'pointer', backgroundColor: '#0070f3', color: 'white', border: 'none', borderRadius: '4px' }}
        >
            {loading ? 'Salvando...' : 'Cadastrar'}
        </button>
      </form>
    </div>
  );
};

export default OwnerForm;