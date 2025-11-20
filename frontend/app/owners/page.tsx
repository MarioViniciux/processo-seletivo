'use client'; 
import React, { useState } from 'react';
import OwnerForm from '@/app/components/OwnerForm';
import OwnerList from '@/app/components/OwnerList';

const OwnersPage = () => {
    const [fetchTrigger, setFetchTrigger] = useState(0); 

    const handleOwnerCreation = () => { 
        setFetchTrigger(prev => prev + 1);
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Gestão de Responsáveis</h1>
            <OwnerForm onOwnerCreated={handleOwnerCreation} />
            
            <hr style={{ margin: '20px 0' }} />
            
            <OwnerList fetchTrigger={fetchTrigger} />
        </div>
    );
};

export default OwnersPage;