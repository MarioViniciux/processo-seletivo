'use client';
import React, { useState } from 'react';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link'; 

const LoginPage = () => {
    const router = useRouter();
    const [formData, setFormData] = useState({ login: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await api.post('/integrations/auth', formData);

            const { access_token } = response.data;
            localStorage.setItem('access_token', access_token);

            router.push('/assets');

        } catch (err: any) {
            const msg = err.response?.data?.detail || "Erro ao fazer login.";
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h2 style={{ textAlign: 'center', marginBottom: '20px' }}>Entrar no Sistema</h2>
                
                {error && <div style={styles.error}>{error}</div>}
                
                <form onSubmit={handleSubmit} style={styles.form}>
                    <input 
                        type="text" name="login" placeholder="Login" 
                        value={formData.login} onChange={handleChange} required 
                        style={styles.input}
                    />
                    <input 
                        type="password" name="password" placeholder="Senha" 
                        value={formData.password} onChange={handleChange} required 
                        style={styles.input}
                    />
                    <button type="submit" disabled={loading} style={styles.button}>
                        {loading ? 'Entrando...' : 'Entrar'}
                    </button>
                </form>

                <p style={{ marginTop: '15px', textAlign: 'center', fontSize: '0.9rem' }}>
                    Não tem conta? <Link href="/register" style={{ color: '#0070f3' }}>Crie uma agora</Link>
                </p>
            </div>
        </div>
    );
};

const styles = {
    container: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f0f2f5' },
    card: { padding: '30px', borderRadius: '8px', backgroundColor: 'white', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', width: '100%', maxWidth: '400px' },
    form: { display: 'flex', flexDirection: 'column' as const, gap: '15px' },
    input: { padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '16px' },
    button: { padding: '10px', borderRadius: '4px', border: 'none', backgroundColor: '#0070f3', color: 'white', fontSize: '16px', cursor: 'pointer' },
    error: { color: 'red', backgroundColor: '#ffe6e6', padding: '10px', borderRadius: '4px', marginBottom: '15px', fontSize: '0.9rem' }
};

export default LoginPage;