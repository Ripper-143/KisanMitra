import React, { useEffect, useState } from 'react'
import { translations, translateTerm, getTranslatedAdvisory } from '../translations'
import { CircleDollarSign, Search, Sparkles, TrendingUp } from 'lucide-react'

export default function MarketPrices({ lang, user }) {
  const t = translations[lang]
  const [prices, setPrices] = useState([])
  const [recommendation, setRecommendation] = useState('')
  const [bestMandi, setBestMandi] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Filter settings
  const [crop, setCrop] = useState(user.land_profile?.crop_type || 'Cotton')
  const [state, setState] = useState(user.land_profile?.state || 'Andhra Pradesh')
  const [search, setSearch] = useState('')

  const fetchPrices = async () => {
    setLoading(true)
    setError('')
    const token = localStorage.getItem('kisan_token')
    if (!token) return

    try {
      const response = await fetch(`/api/market/prices?crop=${crop}&state=${state}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      
      if (response.ok) {
        setPrices(data.prices || [])
        setRecommendation(data.recommendation || '')
        setBestMandi(data.best_mandi || '')
      } else {
        setError(data.detail || 'Failed to fetch prices.')
      }
    } catch (err) {
      setError('Connection to backend failed.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPrices()
  }, [crop, state])

  // Filter local listings by search
  const filteredPrices = prices.filter(p => 
    p.mandi.toLowerCase().includes(search.toLowerCase()) || 
    p.crop.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-gray-100 pb-5">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-emerald-100 text-emerald-700 rounded-xl">
            <CircleDollarSign className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-800">{t.marketPrices}</h2>
            <p className="text-xs text-gray-500 font-medium uppercase tracking-wider">{t.tagline}</p>
          </div>
        </div>

        {/* Filter Toolbar */}
        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
          <div>
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="bg-white border border-gray-200 px-3 py-2 rounded-lg text-xs font-semibold focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              <option value="Cotton">Cotton (పత్తి / कपास)</option>
              <option value="Paddy">Paddy (వరి / धान)</option>
              <option value="Maize">Maize (మొక్కజొన్న / मक्का)</option>
              <option value="Chilli">Red Chilli (మిరప / लाल मिर्च)</option>
              <option value="Turmeric">Turmeric (పసుపు / हल्दी)</option>
              <option value="Wheat">Wheat (గోధుమలు / गेहूँ)</option>
              <option value="Onion">Onion (ఉల్లిపాయ / प्याज)</option>
              <option value="Potato">Potato (బంగాళాదుంప / आलू)</option>
              <option value="Ragi">Ragi (రాగులు / रागी)</option>
              <option value="Groundnut">Groundnut (వేరుశనగ / मूंगफली)</option>
              <option value="Mustard">Mustard (ఆవాలు / सरसों)</option>
            </select>
          </div>

          <div>
            <select
              value={state}
              onChange={(e) => setState(e.target.value)}
              className="bg-white border border-gray-200 px-3 py-2 rounded-lg text-xs font-semibold focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              <option value="Andhra Pradesh">{t.state_ap}</option>
              <option value="Telangana">{t.state_tg}</option>
              <option value="Maharashtra">Maharashtra (మహారాష్ట్ర)</option>
              <option value="Punjab">Punjab (పంజాబ్)</option>
              <option value="Uttar Pradesh">Uttar Pradesh (ఉత్తర ప్రదేశ్)</option>
              <option value="Karnataka">Karnataka (కర్ణాటక)</option>
              <option value="Tamil Nadu">Tamil Nadu (తమిళనాడు)</option>
              <option value="Gujarat">Gujarat (గుజరాత్)</option>
              <option value="Rajasthan">Rajasthan (రాజస్థాన్)</option>
            </select>
          </div>

          <div className="relative flex-grow sm:flex-grow-0">
            <Search className="w-3.5 h-3.5 text-gray-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search mandi..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-4 py-2 rounded-lg border border-gray-200 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-brand-500 w-full sm:w-48"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-100 text-rose-700 text-sm p-4 rounded-xl">
          {error}
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Columns: Table of prices */}
        <div className="lg:col-span-2 bg-white border border-brand-100 shadow-md rounded-2xl p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-extrabold text-sm text-gray-800 uppercase tracking-wider">
              Mandi Market Rates
            </h3>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">
              {translateTerm(crop, lang)} - {translateTerm(state, lang)}
            </span>
          </div>

          {loading ? (
            <div className="py-20 text-center space-y-3">
              <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-xs text-gray-400 font-bold animate-pulse">Fetching latest mandi boards...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-gray-100 text-gray-400 font-bold uppercase text-[10px]">
                    <th className="py-3 px-4">Mandi / Market</th>
                    <th className="py-3 px-4">Crop</th>
                    <th className="py-3 px-4 text-right">Min Rate</th>
                    <th className="py-3 px-4 text-right">Max Rate</th>
                    <th className="py-3 px-4 text-right">Modal Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50 font-medium">
                  {filteredPrices.map((item, idx) => (
                    <tr key={idx} className="hover:bg-gray-50/50 transition-colors">
                      <td className="py-3.5 px-4 font-bold text-gray-800">
                        {translateTerm(item.mandi, lang)}
                        <span className="block text-[9px] text-gray-400 font-semibold">{translateTerm(item.state, lang)}</span>
                      </td>
                      <td className="py-3.5 px-4 text-gray-600">{translateTerm(item.crop, lang)}</td>
                      <td className="py-3.5 px-4 text-right text-gray-500">₹{item.min_price}</td>
                      <td className="py-3.5 px-4 text-right text-gray-500">₹{item.max_price}</td>
                      <td className="py-3.5 px-4 text-right font-extrabold text-brand-600">₹{item.modal_price}</td>
                    </tr>
                  ))}
                  {filteredPrices.length === 0 && (
                    <tr>
                      <td colSpan="5" className="py-12 text-center text-gray-400 font-semibold">
                        No mandis found matching filter criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right Column: AI Analysis Card */}
        <div className="bg-white border border-brand-100 shadow-md rounded-2xl p-6 flex flex-col justify-between premium-card">
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-brand-800 pb-3 border-b border-gray-100">
              <TrendingUp className="w-5 h-5 text-emerald-600" />
              <h3 className="font-extrabold text-sm uppercase tracking-wider">AI Mandi Advisory</h3>
            </div>

            {loading ? (
              <div className="py-12 text-center text-gray-400 font-medium animate-pulse text-xs">
                Market Price Agent is compiling data charts...
              </div>
            ) : (
              <div className="space-y-4">
                {bestMandi && (
                  <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-xl space-y-1">
                    <p className="text-[10px] text-emerald-800 font-bold uppercase tracking-wider">Best Selling Market</p>
                    <p className="text-xl font-extrabold text-brand-800">
                      {translateTerm(bestMandi, lang)} {lang === 'te' ? 'మార్కెట్' : lang === 'hi' ? 'मंडी' : 'Mandi'}
                    </p>
                  </div>
                )}

                <div className="space-y-2">
                  <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">{t.recommendation}</p>
                  <div className="text-xs text-gray-600 leading-relaxed font-semibold bg-gray-50 p-4 rounded-xl border border-gray-100">
                    {bestMandi
                      ? getTranslatedAdvisory(
                          bestMandi,
                          state,
                          crop,
                          prices.find((p) => p.mandi === bestMandi)?.modal_price || 0,
                          prices.find((p) => p.mandi === bestMandi)?.unit || 'Quintal (100kg)',
                          lang
                        )
                      : (recommendation || "No advisory details available.")}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center gap-1.5 text-xs text-gray-400 font-semibold mt-6 pt-4 border-t border-gray-50">
            <Sparkles className="w-4 h-4 text-emerald-500 shrink-0" />
            <span>Mandi rates updated from data.gov.in Agmarknet feed.</span>
          </div>
        </div>
      </div>
    </div>
  )
}
