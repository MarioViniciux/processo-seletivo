'use client';
import React, { useState } from 'react';
import AssetForm from '@/app/components/AssetForm';
import AssetList from '@/app/components/AssetList';
import { Asset } from '@/app/types/data'; 

const AssetsPage = () => {
    const [fetchTrigger, setFetchTrigger] = useState(0); 
    const [editingAsset, setEditingAsset] = useState<Asset | null>(null);

    const refreshList = () => {
        setFetchTrigger(prev => prev + 1);
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Gestão de Ativos</h1>
            <AssetForm 
                onAssetUpdated={refreshList}
                initialData={editingAsset}
                onCancelEdit={() => setEditingAsset(null)}
            />

            <hr style={{ margin: '20px 0' }} />

            <AssetList 
                fetchTrigger={fetchTrigger} 
                onEdit={(asset) => setEditingAsset(asset)}
            />
        </div>
    );
};

export default AssetsPage;