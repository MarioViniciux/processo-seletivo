'use client'
import React, { useState, useEffect } from 'react';
import api from '@/api/axios'
import { AxiosError } from 'axios';
import { OwnerCreateData, OwnerFormProps, FastAPIError } from '@/app/types/data';

const OwnerForm: React.FC<OwnerFormProps> = ({ onOwnerUpdated, initialData, onCancelEdit }) => {
  const [formData, setFormData] = useState<OwnerCreateData>({
    name: '',
    email: '',
    phone: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name,
        email: initialData.email,
        phone: initialData.phone || ''
      });
      setError('');
      setSuccess('');
    } else {
      setFormData({ name: '', email: '', phone: '' });
    }
  }, [initialData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (initialData) {
        await api.put(`/integrations/owner/${initialData.id}`, formData);
        setSuccess(`Responsável atualizado com sucesso!`);
      } else {
        await api.post('/integrations/owner', formData);
        setSuccess(`Responsável cadastrado com sucesso!`);
      }
        
      setFormData({ name: '', email: '', phone: '' });
        

      setTimeout(() => {
        onOwnerUpdated(); 

        if (initialData) onCancelEdit(); 
      }, 1000);
        
    } catch (err) {
      setSuccess('');

      const axiosError = err as AxiosError;
      let errorMessage = "Erro ao conectar com o servidor";

      if (axiosError.response?.data) {
        const errorData = axiosError.response.data as FastAPIError;
            
        if (errorData && errorData.detail) { errorMessage = Array.isArray(errorData.detail) ? `${errorData.detail[0].loc[1]}: ${errorData.detail[0].msg}` : String(errorData.detail) }
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container" style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
      <h3>{initialData ? `Editar: ${initialData.name}` : 'Cadastrar Novo Responsável'}</h3>
      
      {error && <p style={{ color: 'red', fontWeight: 'bold' }}>{error}</p>}
      {success && <p style={{ color: 'green', fontWeight: 'bold' }}>{success}</p>}
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px' }}>
        <input type="text" name="name" value={formData.name} style={{ padding: '8px' }} onChange={(e) => setFormData({...formData, name: e.target.value})} placeholder="Nome" required />
        <input type="email" name="email" value={formData.email} style={{ padding: '8px' }} onChange={(e) => setFormData({...formData, email: e.target.value})} placeholder="Email" required />
        <input type="tel" name="phone" value={formData.phone} style={{ padding: '8px' }} onChange={(e) => setFormData({...formData, phone: e.target.value})} placeholder="Telefone" />
        
        <div style={{ display: 'flex', gap: '10px' }}>
          <button type="submit" disabled={loading} style={{ padding: '10px', flex: 1, backgroundColor: initialData ? '#faad14' : '#0070f3', color: 'white', border: 'none' }}>
            {loading ? 'Salvando...' : (initialData ? 'Atualizar' : 'Cadastrar')}
          </button>

          {initialData && (
            <button type="button" onClick={onCancelEdit} style={{ padding: '10px', backgroundColor: '#ccc', border: 'none', cursor: 'pointer' }}>
              Cancelar
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default OwnerForm;