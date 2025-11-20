'use client';
import React, { useState, useEffect } from 'react';
import api from '@/api/axios'; 
import { Asset } from '@/app/types/data';
import { useRouter } from 'next/navigation'; 

import { useParams } from 'next/navigation';

const AssetDetailsPage = () => {
    const { id } = useParams();
    const router = useRouter();
    
    const [asset, setAsset] = useState<Asset | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!id) return;

        const fetchAsset = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const response = await api.get(`/integrations/asset/${id}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setAsset(response.data);
            } catch (err) {
                console.error(err);
                setError('Não foi possível carregar os detalhes do ativo.');
            } finally {
                setLoading(false);
            }
        };

        fetchAsset();
    }, [id]);

    if (loading) return <div style={{padding: '20px'}}>Carregando detalhes...</div>;
    if (error) return <div style={{padding: '20px', color: 'red'}}>{error} <button onClick={() => router.back()}>Voltar</button></div>;
    if (!asset) return null;

    return (
        <div style={{ padding: '40px', maxWidth: '600px', margin: '0 auto' }}>
            <button 
                onClick={() => router.back()} 
                style={{ marginBottom: '20px', padding: '5px 10px', cursor: 'pointer' }}
            >
                Voltar
            </button>

            <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                <h1 style={{ marginTop: 0 }}>Detalhes do Ativo</h1>
                
                <div style={{ display: 'grid', gap: '15px' }}>
                    <div>
                        <strong>Nome:</strong>
                        <p style={{ margin: '5px 0', fontSize: '1.1rem' }}>{asset.name}</p>
                    </div>
                    
                    <div>
                        <strong>Categoria:</strong>
                        <span style={{ backgroundColor: '#e6f7ff', padding: '4px 8px', borderRadius: '4px', color: '#0050b3' }}>
                            {asset.category}
                        </span>
                    </div>

                    <hr />

                    <div>
                        <strong>Responsável (Owner):</strong>
                        {asset.owner_ref ? (
                            <div style={{ marginTop: '5px' }}>
                                <p style={{ margin: 0, fontWeight: 'bold' }}>{asset.owner_ref.name}</p>
                                <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>{asset.owner_ref.email}</p>
                                <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>{asset.owner_ref.phone}</p>
                            </div>
                        ) : (
                            <p style={{ color: 'red' }}>Sem responsável vinculado</p>
                        )}
                    </div>
                    
                    <hr />
                    
                    <div style={{ fontSize: '0.8rem', color: '#999' }}>
                        <strong>ID do Sistema:</strong> {asset.id}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssetDetailsPage;