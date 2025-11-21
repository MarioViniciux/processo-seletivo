import type { Metadata } from 'next'
import Navbar from '@/app/components/Navbar' 

export const metadata: Metadata = {
  title: 'EyesOnAsset CMMS',
  description: 'Gestão de Ativos e Responsáveis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body style={{ margin: 0, padding: 0, fontFamily: 'sans-serif', backgroundColor: '#f9f9f9' }}>
        <Navbar />
        <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
            {children}
        </main>
      </body>
    </html>
  )
}