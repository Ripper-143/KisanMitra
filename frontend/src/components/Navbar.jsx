import React from 'react'
import { translations } from '../translations'
import { LogOut, Globe, User, LayoutDashboard, HeartPulse, CircleDollarSign, Landmark, BellRing } from 'lucide-react'

export default function Navbar({ activeTab, setActiveTab, lang, setLang, user, handleLogout }) {
  const t = translations[lang]

  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-brand-100 bg-white/80 shadow-sm backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-2">
            <span className="text-3xl">🌾</span>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-brand-700 to-earth-600 bg-clip-text text-transparent">
                {t.brand}
              </h1>
              <p className="text-[10px] text-gray-500 font-medium tracking-wide uppercase leading-none">
                {t.tagline}
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          {user && (
            <div className="hidden md:flex items-center space-x-1">
              {[
                { id: 'dashboard', label: t.dashboard, icon: LayoutDashboard },
                { id: 'crop', label: t.cropHealth, icon: HeartPulse },
                { id: 'market', label: t.marketPrices, icon: CircleDollarSign },
                { id: 'schemes', label: t.schemes, icon: Landmark },
                { id: 'alerts', label: t.alerts, icon: BellRing }
              ].map((item) => {
                const Icon = item.icon
                const isActive = activeTab === item.id
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                      isActive
                        ? 'bg-brand-500 text-white shadow-md shadow-brand-500/10'
                        : 'text-gray-600 hover:bg-brand-50 hover:text-brand-700'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </button>
                )
              })}
            </div>
          )}

          {/* Right Controls */}
          <div className="flex items-center gap-4">
            {/* Language Selector */}
            <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
              <Globe className="w-4 h-4 text-gray-500 ml-2" />
              <select
                value={lang}
                onChange={(e) => setLang(e.target.value)}
                className="bg-transparent border-none text-xs font-semibold focus:outline-none pr-4 text-gray-700 cursor-pointer"
              >
                <option value="en">English (EN)</option>
                <option value="te">తెలుగు (TE)</option>
                <option value="hi">हिन्दी (HI)</option>
              </select>
            </div>

            {user && (
              <div className="flex items-center gap-3 pl-2 border-l border-gray-200">
                <div className="flex items-center gap-2 text-sm font-semibold text-gray-700">
                  <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-brand-700">
                    <User className="w-4 h-4" />
                  </div>
                  <span className="hidden sm:inline max-w-[120px] truncate">{user.full_name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-150"
                  title={t.logout}
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Nav Links */}
      {user && (
        <div className="md:hidden flex items-center justify-around border-t border-brand-50 bg-white py-2 px-1">
          {[
            { id: 'dashboard', icon: LayoutDashboard, label: t.dashboard },
            { id: 'crop', icon: HeartPulse, label: t.cropHealth },
            { id: 'market', icon: CircleDollarSign, label: t.marketPrices },
            { id: 'schemes', icon: Landmark, label: t.schemes },
            { id: 'alerts', icon: BellRing, label: t.alerts }
          ].map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex flex-col items-center p-1 rounded-md text-[10px] font-semibold transition-all ${
                  isActive ? 'text-brand-600' : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                <Icon className="w-5 h-5 mb-0.5" />
                {item.label}
              </button>
            )
          })}
        </div>
      )}
    </nav>
  )
}
