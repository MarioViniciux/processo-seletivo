'use client';
import React, { useState, useEffect } from 'react';
import api from '@/api/axios';
import { Asset, AssetListProps } from '@/app/types/data';

const AssetList: React.FC<AssetListProps> = ({ fetchTrigger }) => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);

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

  if (loading) return <div>Carregando Ativos...</div>;

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