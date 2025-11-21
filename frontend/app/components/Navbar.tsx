'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

const Navbar = () => {
    const pathname = usePathname();
    const router = useRouter();

    const hiddenRoutes = ['/login', '/register'];

    if (hiddenRoutes.includes(pathname)) {
        return null;
    }

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        router.push('/login');
    };

    return (
        <nav style={styles.nav}>
            <div style={styles.logo}>
                <span style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>EyesOnAsset</span>
            </div>

            <div style={styles.links}>
                <Link 
                    href="/assets" 
                    style={{ ...styles.link, ...(pathname.startsWith('/assets') ? styles.active : {}) }}
                >
                    Ativos
                </Link>

                <Link 
                    href="/owners" 
                    style={{ ...styles.link, ...(pathname.startsWith('/owners') ? styles.active : {}) }}
                >
                    Responsáveis
                </Link>
            </div>

            <button onClick={handleLogout} style={styles.logoutButton}>
                Sair
            </button>
        </nav>
    );
};

const styles = {
    nav: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '15px 30px',
        backgroundColor: '#001529',
        color: 'white',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
    },
    logo: {
        display: 'flex',
        alignItems: 'center',
    },
    links: {
        display: 'flex',
        gap: '20px',
    },
    link: {
        color: '#a6adb4',
        textDecoration: 'none',
        fontSize: '1rem',
        transition: 'color 0.3s',
        padding: '5px 10px',
        borderRadius: '4px',
    },
    active: {
        color: 'white',
        backgroundColor: '#1890ff',
        fontWeight: 'bold' as const,
    },
    logoutButton: {
        backgroundColor: 'transparent',
        border: '1px solid #ff4d4f',
        color: '#ff4d4f',
        padding: '6px 15px',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '0.9rem',
        transition: 'all 0.3s',
    }
};

export default Navbar;