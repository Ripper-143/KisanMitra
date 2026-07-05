import React, { useEffect, useState } from 'react'
import { translations, translateTerm, getTranslatedAdvisory } from '../translations'
import { Sprout, CloudSun, BadgeIndianRupee, Award, MailWarning, Droplets, Sun, Wind, CheckCircle, AlertTriangle, XCircle, ArrowUpRight } from 'lucide-react'
import { API_BASE } from '../api'

export default function Dashboard({ lang, user, setActiveTab }) {
  const t = translations[lang]
  const [weatherData, setWeatherData] = useState(null)
  const [marketData, setMarketData] = useState(null)
  const [schemesData, setSchemesData] = useState(null)
  const [alertsData, setAlertsData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showAllMarkets, setShowAllMarkets] = useState(false)

  const fetchAdvisoryData = async () => {
    setLoading(true)
    setError('')
    const token = localStorage.getItem('kisan_token')
    if (!token) return

    try {
      // 1. Fetch Weather Advisory
      const weatherRes = await fetch(`${API_BASE}/api/weather/advisory?city=${user.land_profile?.district || 'Guntur'}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const wData = await weatherRes.json()

      // 2. Fetch Market Prices
      const marketRes = await fetch(`${API_BASE}/api/market/prices?crop=${user.land_profile?.crop_type || 'Cotton'}&state=${user.land_profile?.state || 'Andhra Pradesh'}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const mData = await marketRes.json()

      // 3. Fetch Matching Schemes
      const schemesRes = await fetch(`${API_BASE}/api/schemes/match`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const sData = await schemesRes.json()

      // 4. Fetch Alert Logs
      const alertsRes = await fetch(`${API_BASE}/api/alerts`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const aData = await alertsRes.json()

      if (weatherRes.ok) setWeatherData(wData)
      if (marketRes.ok) setMarketData(mData)
      if (schemesRes.ok) setSchemesData(sData)
      if (alertsRes.ok) setAlertsData(aData)

    } catch (err) {
      console.error(err)
      setError('Failed to fetch data from farm advisory agents.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAdvisoryData()
  }, [user])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] gap-4">
        <div className="w-12 h-12 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm font-semibold text-gray-500 animate-pulse">{t.loading}</p>
      </div>
    )
  }

  // Helper colors for weather suitabilities
  const getColorClass = (color) => {
    switch (color) {
      case 'GREEN': return 'bg-emerald-100 text-emerald-800 border-emerald-200'
      case 'AMBER': return 'bg-amber-100 text-amber-800 border-amber-200'
      case 'RED': return 'bg-rose-100 text-rose-800 border-rose-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getIcon = (color) => {
    switch (color) {
      case 'GREEN': return <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
      case 'AMBER': return <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
      case 'RED': return <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
      default: return null
    }
  }

  // Extracted indices for today
  const todayForecast = weatherData?.forecast?.[0] || {}

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome & Overview Banner */}
      <div className="bg-gradient-to-r from-brand-800 to-earth-800 text-white rounded-2xl p-6 md:p-8 shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative overflow-hidden pulse-glow">
        <div className="relative z-10 space-y-2">
          <span className="bg-brand-500 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
            {t.brand} Workspace
          </span>
          <h2 className="text-2xl md:text-3xl font-extrabold">
            Namaste, {user.full_name}!
          </h2>
          <p className="text-brand-100 text-sm max-w-xl">
            {user.land_profile?.village}, {user.land_profile?.district} | {user.land_profile?.land_size_acres} Acres | {user.land_profile?.crop_type} ({user.land_profile?.soil_type})
          </p>
        </div>
        <button 
          onClick={fetchAdvisoryData}
          className="relative z-10 bg-white text-brand-800 hover:bg-brand-50 px-5 py-2.5 rounded-lg text-sm font-bold shadow-md cursor-pointer transition-colors duration-150 shrink-0"
        >
          Refresh Advisory
        </button>
        {/* Background leaf silhouette graphic */}
        <span className="absolute -right-10 -bottom-10 text-9xl text-white/5 select-none pointer-events-none font-bold">🌾</span>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-100 text-rose-700 text-sm p-4 rounded-xl font-medium">
          {error}
        </div>
      )}

      {/* Grid of Agent Widgets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Widget 1: Weather Advisory Agent */}
        <div className="bg-white rounded-2xl border border-brand-100 shadow-md p-6 space-y-6 premium-card">
          <div className="flex items-center justify-between border-b border-gray-100 pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-sky-100 text-sky-600 rounded-xl">
                <CloudSun className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-gray-800">{t.weatherWidgetTitle} {weatherData?.city}</h3>
            </div>
            <span className="text-[10px] text-gray-400 font-bold uppercase">{weatherData?.source}</span>
          </div>

          {/* Today's Weather Stats */}
          {todayForecast && (
            <div className="grid grid-cols-3 gap-3 bg-sky-50/50 p-4 rounded-xl text-center">
              <div className="space-y-1">
                <div className="flex justify-center text-sky-600"><Sun className="w-5 h-5" /></div>
                <p className="text-xs text-gray-500 font-medium">Temp</p>
                <p className="text-sm font-bold text-gray-800">{todayForecast.temp_celsius}°C</p>
              </div>
              <div className="space-y-1 border-x border-sky-100">
                <div className="flex justify-center text-sky-600"><Droplets className="w-5 h-5" /></div>
                <p className="text-xs text-gray-500 font-medium">Humidity</p>
                <p className="text-sm font-bold text-gray-800">{todayForecast.humidity_pct}%</p>
              </div>
              <div className="space-y-1">
                <div className="flex justify-center text-sky-600"><Wind className="w-5 h-5" /></div>
                <p className="text-xs text-gray-500 font-medium">Wind</p>
                <p className="text-sm font-bold text-gray-800">{todayForecast.wind_speed_kmh} k/h</p>
              </div>
            </div>
          )}

          {/* Sowing / Spraying / Irrigation Advisories */}
          {todayForecast && (
            <div className="space-y-4">
              <div className="space-y-2">
                <p className="text-xs font-bold text-gray-500 uppercase">{t.sprayingAdvice}</p>
                <div className={`flex items-start gap-2 p-3 rounded-lg border text-xs font-semibold ${getColorClass(todayForecast.spraying_suitability?.color)}`}>
                  {getIcon(todayForecast.spraying_suitability?.color)}
                  <span>{todayForecast.spraying_suitability?.status}</span>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-xs font-bold text-gray-500 uppercase">{t.irrigationAdvice}</p>
                <div className={`flex items-start gap-2 p-3 rounded-lg border text-xs font-semibold ${getColorClass(todayForecast.irrigation_advice?.color)}`}>
                  {getIcon(todayForecast.irrigation_advice?.color)}
                  <span>{todayForecast.irrigation_advice?.status}</span>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-xs font-bold text-gray-500 uppercase">{t.sowingAdvice}</p>
                <div className={`flex items-start gap-2 p-3 rounded-lg border text-xs font-semibold ${getColorClass(todayForecast.sowing_advice?.color)}`}>
                  {getIcon(todayForecast.sowing_advice?.color)}
                  <span>{todayForecast.sowing_advice?.status}</span>
                </div>
              </div>
            </div>
          )}

          <button 
            onClick={() => setActiveTab('dashboard')} 
            className="w-full text-center py-2 text-xs font-bold text-sky-600 hover:text-sky-700 bg-sky-50 rounded-lg block transition-colors duration-150"
          >
            Advisor Remarks: {weatherData?.recommendation?.substring(0, 80)}...
          </button>
        </div>

        {/* Widget 2: Market Price Agent */}
        <div className="bg-white rounded-2xl border border-brand-100 shadow-md p-6 space-y-6 premium-card">
          <div className="flex items-center justify-between border-b border-gray-100 pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-emerald-100 text-emerald-600 rounded-xl">
                <BadgeIndianRupee className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-gray-800">{t.mandiPriceTrends}</h3>
            </div>
            <span className="text-[10px] text-gray-400 font-bold uppercase">{translateTerm(marketData?.prices?.[0]?.crop || 'Crops', lang)}</span>
          </div>

          {/* Mandi Price List */}
          {/* Mandi Price List (5 items default, expands to 12) */}
          <div 
            className={`space-y-3 transition-all duration-300 overflow-y-auto pr-1`}
            style={{ maxHeight: showAllMarkets ? '440px' : '220px' }}
          >
            {marketData?.prices && marketData.prices.slice(0, showAllMarkets ? 12 : 5).map((item, idx) => (
              <div key={idx} className="flex justify-between items-center p-3 rounded-xl border border-gray-100 hover:bg-gray-50 transition-colors">
                <div>
                  <p className="text-xs font-bold text-gray-800">{translateTerm(item.mandi, lang)} {lang === 'te' ? 'మార్కెట్' : lang === 'hi' ? 'मंडी' : 'Mandi'}</p>
                  <p className="text-[10px] text-gray-400 font-semibold">{translateTerm(item.state, lang)}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-extrabold text-brand-600">₹{item.modal_price}</p>
                  <p className="text-[9px] text-gray-400 font-medium">₹{item.min_price} - ₹{item.max_price}</p>
                </div>
              </div>
            ))}
            {(!marketData?.prices || marketData.prices.length === 0) && (
              <p className="text-xs text-gray-400 py-6 text-center">No market prices found.</p>
            )}
          </div>

          <div className="bg-emerald-50/50 p-4 rounded-xl border border-emerald-100/50 space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-800">
              <span>💡</span>
              <span>{t.bestMarketPrice}: {translateTerm(marketData?.best_mandi, lang)} {lang === 'te' ? 'మార్కెట్' : lang === 'hi' ? 'मंडी' : 'Mandi'}</span>
            </div>
            <p className="text-xs text-gray-600 leading-relaxed font-medium">
              {marketData?.best_mandi
                ? getTranslatedAdvisory(
                    marketData.best_mandi,
                    user.land_profile?.state || 'Andhra Pradesh',
                    user.land_profile?.crop_type || 'Cotton',
                    marketData.prices?.find((p) => p.mandi === marketData.best_mandi)?.modal_price || 0,
                    marketData.prices?.find((p) => p.mandi === marketData.best_mandi)?.unit || 'Quintal (100kg)',
                    lang
                  )
                : (marketData?.recommendation || "No advisory details available.")}
            </p>
          </div>

          <button 
            onClick={() => setShowAllMarkets(!showAllMarkets)}
            className="w-full flex items-center justify-center gap-1 py-2.5 text-xs font-bold text-brand-700 hover:text-white bg-brand-50 hover:bg-brand-600 rounded-lg transition-all cursor-pointer"
          >
            <span>{showAllMarkets ? "Show Less" : "Show More Markets"}</span>
            <ArrowUpRight className={`w-4 h-4 transition-transform ${showAllMarkets ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Widget 3: Scheme Matcher Agent */}
        <div className="bg-white rounded-2xl border border-brand-100 shadow-md p-6 space-y-6 premium-card">
          <div className="flex items-center justify-between border-b border-gray-100 pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-amber-100 text-amber-600 rounded-xl">
                <Award className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-gray-800">{t.schemeEligibility}</h3>
            </div>
            <span className="text-[10px] text-gray-400 font-bold uppercase">RAG Matcher</span>
          </div>

          {/* Scheme Matches */}
          <div className="space-y-4 max-h-[220px] overflow-y-auto pr-1">
            {schemesData?.matched_schemes && schemesData.matched_schemes.map((item, idx) => (
              <div key={idx} className="p-3.5 rounded-xl border border-amber-100 bg-amber-50/30 space-y-1.5 hover:bg-amber-50/50 transition-colors">
                <div className="flex justify-between items-center">
                  <p className="text-xs font-bold text-amber-900">{item.name}</p>
                  <span className="text-[9px] bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-bold">Matched</span>
                </div>
                <p className="text-xs text-gray-700 font-semibold">{item.benefit}</p>
                <p className="text-[10px] text-gray-400 font-medium">Source: {item.source_doc}</p>
              </div>
            ))}
            {(!schemesData?.matched_schemes || schemesData.matched_schemes.length === 0) && (
              <p className="text-xs text-gray-400 py-6 text-center">No matching scheme matches found.</p>
            )}
          </div>

          <div className="text-xs text-gray-500 bg-gray-50 p-4 rounded-xl max-h-[140px] overflow-y-auto font-mono text-[10px] leading-relaxed border border-gray-100">
            <p className="font-bold text-gray-600 mb-1">RAG Context Reference:</p>
            {schemesData?.rag_evidence || "No semantic context fetched."}
          </div>

          <button 
            onClick={() => setActiveTab('schemes')}
            className="w-full flex items-center justify-center gap-1 py-2.5 text-xs font-bold text-amber-700 hover:text-white bg-amber-50 hover:bg-amber-600 rounded-lg transition-all cursor-pointer"
          >
            <span>Learn How to Apply</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>

      </div>

      {/* Alert logs and quick diagnosis section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Recent Alerts */}
        <div className="bg-white rounded-2xl border border-brand-100 shadow-md p-6 space-y-4">
          <div className="flex items-center gap-3 border-b border-gray-100 pb-3">
            <MailWarning className="w-5 h-5 text-brand-600" />
            <h3 className="font-bold text-gray-800">{t.recentAlerts}</h3>
          </div>
          <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1">
            {alertsData.map((log) => (
              <div key={log.id} className="p-3 rounded-lg border border-gray-100 flex items-start justify-between text-xs gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${
                      log.alert_type === 'Weather' ? 'bg-sky-100 text-sky-800' :
                      log.alert_type === 'Market Price' ? 'bg-emerald-100 text-emerald-800' :
                      'bg-amber-100 text-amber-800'
                    }`}>
                      {log.alert_type}
                    </span>
                    <span className="text-[10px] text-gray-400 font-semibold">{log.sent_at}</span>
                  </div>
                  <p className="text-gray-700 font-medium leading-relaxed">{log.message}</p>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  log.status.toLowerCase().includes('whatsapp') ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
                  log.status === 'Sent' ? 'bg-emerald-100 text-emerald-800' :
                  log.status === 'Simulated' ? 'bg-blue-100 text-blue-800' :
                  'bg-rose-100 text-rose-800'
                }`}>
                  {log.status}
                </span>
              </div>
            ))}
            {alertsData.length === 0 && (
              <p className="text-xs text-gray-400 py-6 text-center">No alert log history found.</p>
            )}
          </div>
        </div>

        {/* Quick Diagnostics */}
        <div className="bg-gradient-to-br from-brand-50 to-brand-100/50 rounded-2xl border border-brand-200/50 p-6 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-brand-800">
              <Sprout className="w-6 h-6" />
              <h3 className="font-extrabold text-lg">{t.cropHealth}</h3>
            </div>
            <p className="text-xs text-brand-900 leading-relaxed font-semibold">
              Is your crop leaf showing discoloration, spotting, or insect curling? 
              Take a picture and upload it to get an instant diagnosis and treatment plan from the Crop Health AI Agent.
            </p>
          </div>
          <button 
            onClick={() => setActiveTab('crop')}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 px-4 rounded-xl mt-6 transition-all duration-150 cursor-pointer shadow-md shadow-brand-600/10 text-sm text-center"
          >
            Diagnose Crop Now
          </button>
        </div>
      </div>
    </div>
  )
}
