'use client'
import React, { useState, useEffect } from 'react';
import api from '@/api/axios';
import { Owner, OwnerListProps } from '@/app/types/data';

const OwnerList: React.FC<OwnerListProps> = ({ fetchTrigger }) => {
  const [owners, setOwners] = useState<Owner[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOwners = async () => {
      try {
        const response = await api.get('/integrations/owner'); 
        
        setOwners(response.data);
      } catch (error) {
        console.error("Erro ao conectar na API:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchOwners();
  }, [fetchTrigger]);

  if (loading) return <div>Carregando...</div>;

  return (
    <div className="list-container">
      <h2>Lista de Responsáveis</h2>
      <table border={1} cellPadding={5} style={{borderCollapse: 'collapse', width: '100%'}}>
        <thead>
          <tr><th>Nome</th><th>Email</th><th>Telefone</th></tr>
        </thead>
        <tbody>
          {owners.length > 0 ? (
            owners.map(owner => (
              <tr key={owner.id}>
                <td>{owner.name}</td>
                <td>{owner.email}</td>
                <td>{owner.phone}</td>
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