'use client'; 
import React, { useState } from 'react';
import OwnerForm from '@/app/components/OwnerForm';
import OwnerList from '@/app/components/OwnerList';
import { Owner } from "@/app/types/data"

const OwnersPage = () => {
    const [fetchTrigger, setFetchTrigger] = useState(0); 
    const [editingOwner, setEditingOwner] = useState<Owner | null>(null);

    const refreshList = () => {
        setFetchTrigger(prev => prev + 1);
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>Gestão de Responsáveis</h1>
            <OwnerForm 
                onOwnerUpdated={refreshList} 
                initialData={editingOwner}
                onCancelEdit={() => setEditingOwner(null)}
            />
            
            <hr style={{ margin: '20px 0' }} />
            
            <OwnerList 
                fetchTrigger={fetchTrigger} 
                onEdit={(owner) => setEditingOwner(owner)}
            />
        </div>
    );
};

export default OwnersPage;