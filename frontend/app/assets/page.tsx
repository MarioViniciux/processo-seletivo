'use client';
import React, { useState } from 'react';
import AssetForm from '@/app/components/AssetForm';
import AssetList from '@/app/components/AssetList';

const AssetsPage = () => {
    const [fetchTrigger, setFetchTrigger] = useState(0); 

    const handleAssetCreation = () => {
        setFetchTrigger(prev => prev + 1);
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Gestão de Ativos</h1>
            <AssetForm onAssetCreated={handleAssetCreation} />
            <hr style={{ margin: '20px 0' }} />
            <AssetList fetchTrigger={fetchTrigger} />
        </div>
    );
};

export default AssetsPage;