import React, { useState } from 'react'
import { translations } from '../translations'
import { UserPlus, User, Phone, Mail, Key, ShieldAlert } from 'lucide-react'
import { API_BASE } from '../api'

export default function Signup({ setAuth, lang, onToggleAuth }) {
  const t = translations[lang]
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone_number: '',
    state: 'Andhra Pradesh',
    district: '',
    village: '',
    crop_type: 'Cotton',
    land_size_acres: '',
    soil_type: 'Black Cotton Soil'
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    // Formulate payload matching API SignupRequest
    const payload = {
      email: formData.email,
      password: formData.password,
      full_name: formData.full_name,
      phone_number: formData.phone_number,
      land_profile: {
        state: formData.state,
        district: formData.district || 'Guntur',
        village: formData.village || 'Vilage_Name',
        crop_type: formData.crop_type,
        land_size_acres: parseFloat(formData.land_size_acres) || 1.0,
        soil_type: formData.soil_type
      }
    }

    try {
      const response = await fetch(`${API_BASE}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      const data = await response.json()
      if (response.ok) {
        localStorage.setItem('kisan_token', data.access_token)
        localStorage.setItem('kisan_user', JSON.stringify(data))
        setAuth(data)
      } else {
        setError(data.detail || 'Signup failed. Please verify your inputs.')
      }
    } catch (err) {
      setError('Connection to backend failed. Make sure FastAPI server is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-64px)] py-12 px-4 bg-gradient-to-br from-brand-50 via-gray-50 to-earth-50">
      <div className="w-full max-w-2xl bg-white/95 rounded-2xl border border-brand-100 shadow-xl p-8 premium-card">
        <div className="text-center mb-8">
          <span className="text-5xl">🌾</span>
          <h2 className="text-2xl font-bold text-gray-800 mt-4">{t.signupTitle}</h2>
          <p className="text-sm text-gray-500 mt-1">{t.brand} — {t.tagline}</p>
        </div>

        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded-lg text-xs font-semibold mb-6 border border-red-100 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4" />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Section 1: Farmer Account */}
          <div>
            <h3 className="text-sm font-bold text-brand-700 uppercase tracking-wider border-b border-gray-100 pb-2 mb-4">
              1. Account Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.fullName}</label>
                <div className="relative">
                  <User className="w-4 h-4 text-gray-400 absolute left-3 top-3.5" />
                  <input
                    type="text"
                    required
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    placeholder="e.g. P. Venkateswarlu"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.phoneNumber}</label>
                <div className="relative">
                  <Phone className="w-4 h-4 text-gray-400 absolute left-3 top-3.5" />
                  <input
                    type="tel"
                    required
                    name="phone_number"
                    value={formData.phone_number}
                    onChange={handleChange}
                    placeholder="+91 XXXXX XXXXX"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.email}</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-3.5" />
                  <input
                    type="email"
                    required
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="farmer@kisanmitra.org"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.password}</label>
                <div className="relative">
                  <Key className="w-4 h-4 text-gray-400 absolute left-3 top-3.5" />
                  <input
                    type="password"
                    required
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Section 2: Land details */}
          <div>
            <h3 className="text-sm font-bold text-brand-700 uppercase tracking-wider border-b border-gray-100 pb-2 mb-4">
              2. Agricultural Land Profile
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.state}</label>
                <select
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                  className="w-full px-3 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
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

              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.district}</label>
                <input
                  type="text"
                  required
                  name="district"
                  value={formData.district}
                  onChange={handleChange}
                  placeholder="e.g. Guntur / Warangal"
                  className="w-full px-3 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.village}</label>
                <input
                  type="text"
                  required
                  name="village"
                  value={formData.village}
                  onChange={handleChange}
                  placeholder="e.g. Amaravati"
                  className="w-full px-3 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.cropType}</label>
                <select
                  name="crop_type"
                  value={formData.crop_type}
                  onChange={handleChange}
                  className="w-full px-3 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
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
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.landSize}</label>
                <input
                  type="number"
                  step="0.1"
                  required
                  name="land_size_acres"
                  value={formData.land_size_acres}
                  onChange={handleChange}
                  placeholder="e.g. 3.5"
                  className="w-full px-3 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-2">{t.soilType}</label>
                <select
                  name="soil_type"
                  value={formData.soil_type}
                  onChange={handleChange}
                  className="w-full px-3 py-3 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  <option value="Black Cotton Soil">{t.soil_black}</option>
                  <option value="Red Sandy Soil">{t.soil_red}</option>
                  <option value="Alluvial Soil">{t.soil_alluvial}</option>
                  <option value="Clay Loam">{t.soil_clay}</option>
                </select>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all duration-200 shadow-md shadow-brand-600/10 cursor-pointer disabled:opacity-50"
          >
            <UserPlus className="w-4 h-4" />
            {loading ? 'Submitting Details...' : t.signupBtn}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-100 text-center">
          <button
            onClick={onToggleAuth}
            className="text-sm font-semibold text-brand-600 hover:text-brand-700 hover:underline"
          >
            {t.alreadyHaveAccount}
          </button>
        </div>
      </div>
    </div>
  )
}
