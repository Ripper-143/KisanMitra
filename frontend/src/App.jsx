import React, { useEffect, useState } from 'react'
import Navbar from './components/Navbar'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import CropUpload from './pages/CropUpload'
import MarketPrices from './pages/MarketPrices'
import Schemes from './pages/Schemes'
import Alerts from './pages/Alerts'

export default function App() {
  const [auth, setAuth] = useState(null)
  const [isLoginView, setIsLoginView] = useState(true)
  const [activeTab, setActiveTab] = useState('dashboard')
  const [lang, setLang] = useState('en') // Default language is English

  // Restore session
  useEffect(() => {
    const token = localStorage.getItem('kisan_token')
    const savedUser = localStorage.getItem('kisan_user')
    if (token && savedUser) {
      setAuth(JSON.parse(savedUser))
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('kisan_token')
    localStorage.removeItem('kisan_user')
    setAuth(null)
    setActiveTab('dashboard')
  }

  // Render active workspace page
  const renderPage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard lang={lang} user={auth} setActiveTab={setActiveTab} />
      case 'crop':
        return <CropUpload lang={lang} user={auth} />
      case 'market':
        return <MarketPrices lang={lang} user={auth} />
      case 'schemes':
        return <Schemes lang={lang} user={auth} />
      case 'alerts':
        return <Alerts lang={lang} user={auth} />
      default:
        return <Dashboard lang={lang} user={auth} setActiveTab={setActiveTab} />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        lang={lang}
        setLang={setLang}
        user={auth}
        handleLogout={handleLogout}
      />

      <main className="flex-grow">
        {auth ? (
          renderPage()
        ) : isLoginView ? (
          <Login setAuth={setAuth} lang={lang} onToggleAuth={() => setIsLoginView(false)} />
        ) : (
          <Signup setAuth={setAuth} lang={lang} onToggleAuth={() => setIsLoginView(true)} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-brand-100 py-6 text-center text-xs font-semibold text-gray-400">
        <p>© 2026 KisanMitra AI. Built for small and marginal landholders in Andhra Pradesh & Telangana.</p>
      </footer>
    </div>
  )
}
