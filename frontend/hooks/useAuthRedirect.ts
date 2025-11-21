import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/api/axios';

export const useAuthRedirect = () => {
    const router = useRouter();

    useEffect(() => {
        const validateSession = async () => {
            const token = localStorage.getItem('access_token');

            if (!token) {
                router.push('/login');
                return;
            }

            try {
                await api.get('/integrations/user'); 
            } catch (error: any) {
                console.error("Sessão inválida:", error);
                if (error.response?.status === 401) {
                    localStorage.removeItem('access_token');
                    router.push('/login');
                }
            }
        };

        validateSession();
    }, [router]);
};