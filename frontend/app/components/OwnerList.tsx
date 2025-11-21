'use client'
import React, { useState, useEffect } from 'react';
import api from '@/api/axios';
import { Owner, OwnerListProps } from '@/app/types/data';

const OwnerList: React.FC<OwnerListProps> = ({ fetchTrigger, onEdit }) => {
  const [owners, setOwners] = useState<Owner[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    const fetchOwners = async () => {
      try {
        setLoading(true);

        const response = await api.get('/integrations/owner'); 
        
        setOwners(response.data);
        setError('')
      } catch (error) {
        console.error("Erro ao conectar na API:", error);
        setError("Erro ao carregar lista")
      } finally {
        setLoading(false);
      }
    };

    fetchOwners();
  }, [fetchTrigger]);

  const handleDelete = async (id: string, name: string) => {
    const confirmed = window.confirm("Confirmar exclusão?")

    if (!confirmed) return

    try {
      setDeletingId(id)

      await api.delete(`/integrations/owner/${id}`)

      setOwners(prevOwners => prevOwners.filter(owner => owner.id != id))
      alert("Excluído com sucesso")
    } catch (err) {
      console.error("Erro ao excluir:", err)
      alert("Erro ao excluir")
    } finally {
      setDeletingId(null)
    }
  }

  if (loading && owners.length === 0) return <div>Carregando...</div>;
  if (error) return <div style={{color: 'red'}}>{error}</div>

  return (
    <div className="list-container">
      <h2>Lista de Responsáveis</h2>
      <table border={1} cellPadding={5} style={{borderCollapse: 'collapse', width: '100%'}}>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Email</th>
            <th>Telefone</th>
            <th style={{ textAlign: 'center', width: '100px' }}>Ações</th>
          </tr>
        </thead>
        <tbody>
          {owners.length > 0 ? (
            owners.map(owner => (
              <tr key={owner.id}>
                <td>{owner.name}</td>
                <td>{owner.email}</td>
                <td>{owner.phone}</td>
                <td style={{ textAlign: 'center' }}>
                  <button 
                    onClick={() => handleDelete(owner.id, owner.name)}
                    disabled={deletingId === owner.id}
                    style={{ backgroundColor: '#ff4d4f', color: 'white', border: 'none', borderRadius: '4px', padding: '5px 10px', cursor: deletingId === owner.id ? 'not-allowed' : 'pointer', opacity: deletingId === owner.id ? 0.6 : 1 }}
                  >
                    {deletingId === owner.id ? '...' : 'Excluir'}
                  </button>
                  <button 
                    onClick={() => onEdit(owner)}
                    style={{ backgroundColor: '#faad14',color: 'white', border: 'none', borderRadius: '4px', padding: '5px 10px', cursor: 'pointer' }}
                  >
                    Editar
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <tr><td colSpan={3}>Nenhum responsável encontrado.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default OwnerList;