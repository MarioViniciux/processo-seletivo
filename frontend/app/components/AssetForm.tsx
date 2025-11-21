'use client';
import React, { useState, useEffect } from 'react';
import api from '@/api/axios';
import { AxiosError } from 'axios';
import { AssetCreateData, AssetFormProps, Owner, FastAPIError } from '@/app/types/data';

const AssetForm: React.FC<AssetFormProps> = ({ onAssetUpdated, initialData, onCancelEdit }) => {
  const [formData, setFormData] = useState<AssetCreateData>({
    name: '',
    category: '',
    owner_id: '', 
  });

  const [owners, setOwners] = useState<Owner[]>([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialData) {
        setFormData({
            name: initialData.name,
            category: initialData.category,
            owner_id: initialData.owner_id 
        });
        
        setError('');
    } else {
        setFormData({ name: '', category: '', owner_id: '' });
    }
  }, [initialData]);

  useEffect(() => {
    const loadOwners = async () => {
        try {
            const response = await api.get('/integrations/owner');
            setOwners(response.data);
        } catch (err) {
            console.error("Erro ao carregar responsáveis:", err);
            setError("Não foi possível carregar a lista de responsáveis.");
        }
    };
    loadOwners();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (!formData.owner_id) {
        setError("Você deve selecionar um responsável.");
        setLoading(false);
        return;
    }

    try {
        if (initialData) {
            await api.put(`/integrations/asset/${initialData.id}`, formData);
            setSuccess(`Ativo atualizado!`)
        } else {
            await api.post('/integrations/asset', formData);
            setSuccess(`Ativo cadastrado!`)
        }

        setFormData({ name: '', category: '', owner_id: '' });
        setTimeout(() => {
            onAssetUpdated();
            if(initialData) onCancelEdit()
        }, 1000); 
    } catch (err) {
        const axiosError = err as AxiosError;
        let errorMessage = "Erro ao salvar.";
        if (axiosError.response) {
            const errorData = axiosError.response.data as FastAPIError;
            errorMessage = Array.isArray(errorData.detail) ? String(errorData.detail[0].msg) : String(errorData.detail)
        }
        setError(errorMessage);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="form-container" style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px', display: "flex", flexDirection: "column", alignItems: "center" }}>
      <h3>Cadastrar Novo Ativo</h3>
      
      {error && <div style={{ color: 'red', marginBottom: '10px', padding: '5px', backgroundColor: '#ffe6e6' }}>{error}</div>}
      {success && <div style={{ color: 'green', marginBottom: '10px', padding: '5px', backgroundColor: '#e6fffa' }}>{success}</div>}
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', minWidth: '600px', maxWidth: '900px' }}>
        <input 
            type="text" name="name" placeholder="Nome do Ativo" 
            value={formData.name} onChange={handleChange} required disabled={loading}
            style={{ padding: '8px' }}
        />
        <input 
            type="text" name="category" placeholder="Categoria (ex: Aeronave)" 
            value={formData.category} onChange={handleChange} required disabled={loading}
            style={{ padding: '8px' }}
        />

        <select 
            name="owner_id" 
            value={formData.owner_id} 
            onChange={handleChange} 
            required 
            disabled={loading || owners.length === 0}
            style={{ padding: '8px' }}
        >
            <option value="">Selecione o Responsável...</option>
                {owners.map(owner => (
                    <option key={owner.id} value={owner.id}>
                        {owner.name}
                    </option>
            ))}
        </select>
        {owners.length === 0 && <small style={{color: 'gray'}}>Nenhum responsável encontrado. Cadastre um primeiro.</small>}


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

export default AssetForm;