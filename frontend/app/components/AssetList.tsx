'use client';
import React, { useState, useEffect } from 'react';
import api from '@/api/axios';
import { Asset, AssetListProps } from '@/app/types/data';
import { useRouter } from 'next/navigation'

const AssetList: React.FC<AssetListProps> = ({ fetchTrigger, onEdit }) => {
  const router = useRouter();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        const response = await api.get('/integrations/asset');

        setAssets(response.data);
      } catch (error) {
        console.error("Erro ao buscar ativos:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAssets();
  }, [fetchTrigger]);

  const handleDelete = async (id: string, name: string) => {
    const confirmed = window.confirm(`Tem certeza que deseja excluir o ativo "${name}"?`);

    if (!confirmed) return;

    try {
      setDeletingId(id); 

      await api.delete(`/integrations/asset/${id}`);

      setAssets(prev => prev.filter(asset => asset.id !== id));
      alert("Ativo excluído com sucesso.");

    } catch (error) {
      console.error("Erro ao excluir:", error);
      alert("Erro ao excluir o ativo.");
    } finally {
      setDeletingId(null);
    }
  };

  if (loading && assets.length === 0) return <div>Carregando Ativos...</div>;

  return (
    <div className="list-container">
      <h2>Lista de Ativos</h2>
      <table border={1} cellPadding={5} style={{borderCollapse: 'collapse', width: '100%'}}>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Categoria</th>
            {/* Descomentar para coluna responsável
            <th>Responsável</th>
            */}
            <th style={{ textAlign: 'center', width: '100px' }}>Ações</th>
          </tr>
        </thead>
        <tbody>
          {assets.length > 0 ? (
            assets.map(asset => (
              <tr key={asset.id}>
                <td>{asset.name}</td>
                <td>{asset.category}</td>
                {/* Caso fosse para exibir o nome do Owner, seria só descomentar esse trecho 
                <td>
                    {asset.owner_ref ? asset.owner_ref.name : <span style={{color:'red'}}>Sem Dono</span>}
                </td>
                */}
                <td style={{ textAlign: 'center' }}>
                  <button 
                    onClick={() => handleDelete(asset.id, asset.name)}
                    disabled={deletingId === asset.id}
                    style={{ backgroundColor: '#ff4d4f', color: 'white', border: 'none', borderRadius: '4px', padding: '5px 10px', cursor: deletingId === asset.id ? 'not-allowed' : 'pointer', opacity: deletingId === asset.id ? 0.6 : 1 }}
                  >
                    {deletingId === asset.id ? '...' : 'Excluir'}
                  </button>

                  <button onClick={() => onEdit(asset)} style={{ backgroundColor: '#faad14', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px' }}>
                    Editar
                  </button>

                  <button 
                      onClick={() => router.push(`/assets/${asset.id}`)}
                      style={{ backgroundColor: '#1890ff', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}
                  >
                      Ver
                  </button>

              </td>
              </tr>
            ))
          ) : (
            <tr><td colSpan={3}>Nenhum ativo cadastrado.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default AssetList;