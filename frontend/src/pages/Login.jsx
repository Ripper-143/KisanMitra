import React, { useState } from 'react'
import { translations } from '../translations'
import { LogIn, Key, Mail } from 'lucide-react'

export default function Login({ setAuth, lang, onToggleAuth }) {
  const t = translations[lang]
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()
      if (response.ok) {
        localStorage.setItem('kisan_token', data.access_token)
        localStorage.setItem('kisan_user', JSON.stringify(data))
        setAuth(data)
      } else {
        setError(data.detail || 'Login failed. Please check your credentials.')
      }
    } catch (err) {
      setError('Connection to backend failed. Make sure FastAPI server is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-64px)] px-4 bg-gradient-to-br from-brand-50 via-gray-50 to-earth-50">
      <div className="w-full max-w-md bg-white/95 rounded-2xl border border-brand-100 shadow-xl p-8 premium-card">
        <div className="text-center mb-8">
          <span className="text-5xl">🌾</span>
          <h2 className="text-2xl font-bold text-gray-800 mt-4">{t.loginTitle}</h2>
          <p className="text-sm text-gray-500 mt-1">{t.brand} — {t.tagline}</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded-lg text-xs font-semibold mb-6 border border-red-100">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-bold text-gray-600 uppercase mb-2">
              {t.email}
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-3.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="farmer@kisanmitra.org"
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-600 uppercase mb-2">
              {t.password}
            </label>
            <div className="relative">
              <Key className="w-4 h-4 text-gray-400 absolute left-3 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent text-sm"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all duration-200 shadow-md shadow-brand-600/10 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <LogIn className="w-4 h-4" />
            {loading ? 'Please wait...' : t.loginBtn}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-100 text-center">
          <button
            onClick={onToggleAuth}
            className="text-sm font-semibold text-brand-600 hover:text-brand-700 hover:underline"
          >
            {t.dontHaveAccount}
          </button>
        </div>
      </div>
    </div>
  )
}
