import React, { useEffect, useState } from 'react'
import { translations } from '../translations'
import { BellRing, Send, HelpCircle, AlertTriangle, ShieldCheck, Smartphone, MessageSquare } from 'lucide-react'

export default function Alerts({ lang, user }) {
  const t = translations[lang]
  const [alerts, setAlerts] = useState([])
  const [message, setMessage] = useState('')
  const [type, setType] = useState('Weather')
  const [channel, setChannel] = useState('SMS') // 'SMS' or 'WhatsApp'
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(false)
  const [statusMsg, setStatusMsg] = useState('')
  const [error, setError] = useState('')
  
  // WhatsApp / SMS phone preview toggle
  const [previewTab, setPreviewTab] = useState('whatsapp')

  const fetchAlerts = async () => {
    setFetching(true)
    const token = localStorage.getItem('kisan_token')
    if (!token) return

    try {
      const response = await fetch('/api/alerts', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      if (response.ok) {
        setAlerts(data)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setFetching(false)
    }
  }

  const getPresetMessage = (alertType) => {
    switch (alertType) {
      case 'Weather':
        return `🌾 KisanMitra Weather Warning: Cloudy skies and moderate rain forecasted for ${user.land_profile?.district || 'Guntur'}. Postpone pesticide sprays for ${user.land_profile?.crop_type || 'Cotton'} to avoid wash-off.`
      case 'Market Price':
        return `🌾 KisanMitra Mandi Alert: ${user.land_profile?.crop_type || 'Cotton'} prices in local mandis reached a peak of ₹7,460/Quintal. Great time to sell your produce!`
      case 'Scheme':
        return `🌾 KisanMitra Scheme Reminder: Last date to enroll for 90% micro-irrigation subsidy under APMIP is closing next week. Register online.`
      case 'System':
        return `🌾 KisanMitra Notice: Advisory models have been updated for ${user.land_profile?.district || 'Guntur'}. Please review your dashboard for the latest guidelines.`
      default:
        return ''
    }
  }

  useEffect(() => {
    // Automatically set preset message when type changes or user context changes
    setMessage(getPresetMessage(type))
  }, [type, user])

  const handleSendAlert = async (e) => {
    e.preventDefault()
    if (!message.trim()) return

    setLoading(true)
    setError('')
    setStatusMsg('')

    const token = localStorage.getItem('kisan_token')
    try {
      const response = await fetch('/api/alerts/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          alert_type: type,
          message: message,
          channel: channel
        })
      })

      const data = await response.json()
      if (response.ok) {
        setStatusMsg(data.message || 'Alert dispatched successfully!')
        setMessage(getPresetMessage(type))
        
        // Auto switch preview tab to match sent channel
        setPreviewTab(channel.toLowerCase())
        
        fetchAlerts() // Refresh list
      } else {
        setError(data.detail || 'Failed to dispatch alert.')
      }
    } catch (err) {
      setError('Communication with the dispatch gateway failed.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAlerts()
  }, [user])

  // Filter alerts for the phone mockup preview
  const whatsappAlerts = alerts.filter(a => a.status.toLowerCase().includes('whatsapp'))
  const smsAlerts = alerts.filter(a => !a.status.toLowerCase().includes('whatsapp'))

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center border-b border-gray-100 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-brand-100 text-brand-700 rounded-xl">
            <BellRing className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-800">{t.alerts}</h2>
            <p className="text-xs text-gray-500 font-medium uppercase tracking-wider">{t.tagline}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        
        {/* Column 1: Dispatcher Form */}
        <div className="bg-white border border-brand-100 shadow-md rounded-2xl p-6 flex flex-col justify-between premium-card">
          <div className="space-y-5">
            <h3 className="font-extrabold text-sm text-gray-800 uppercase tracking-wider border-b border-gray-50 pb-3 flex items-center gap-2">
              <span>✉️</span> {t.sendCustomAlert}
            </h3>

            {statusMsg && (
              <div className="bg-emerald-50 border border-emerald-100 text-emerald-800 p-3.5 rounded-xl text-xs font-semibold flex items-center gap-1.5 animate-fade-in">
                <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-600" />
                {statusMsg}
              </div>
            )}

            {error && (
              <div className="bg-rose-50 border border-rose-100 text-rose-800 p-3.5 rounded-xl text-xs font-semibold flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 shrink-0 text-rose-600" />
                {error}
              </div>
            )}

            <form onSubmit={handleSendAlert} className="space-y-5">
              {/* Alert Type Selector */}
              <div>
                <label className="block text-[10px] font-extrabold text-gray-500 uppercase tracking-wider mb-2">
                  Alert Category
                </label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full px-3 py-3 rounded-lg border border-gray-200 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  <option value="Weather">Weather Advisory Warning</option>
                  <option value="Market Price">Mandi Price Warning</option>
                  <option value="Scheme">Scheme Application Deadline</option>
                  <option value="System">System Configuration Message</option>
                </select>
              </div>

              {/* Delivery Channel (SMS / WhatsApp) Selector */}
              <div>
                <label className="block text-[10px] font-extrabold text-gray-500 uppercase tracking-wider mb-2">
                  Delivery Channel
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setChannel('SMS')}
                    className={`py-2.5 px-4 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
                      channel === 'SMS' 
                        ? 'border-brand-600 bg-brand-50/55 text-brand-800' 
                        : 'border-gray-200 bg-white text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    💬 Standard SMS
                  </button>
                  <button
                    type="button"
                    onClick={() => setChannel('WhatsApp')}
                    className={`py-2.5 px-4 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
                      channel === 'WhatsApp' 
                        ? 'border-emerald-600 bg-emerald-50/50 text-emerald-800' 
                        : 'border-gray-200 bg-white text-gray-500 hover:bg-gray-50'
                    }`}
                  >
                    🟢 WhatsApp Msg
                  </button>
                </div>
              </div>

              {/* Message Textarea */}
              <div>
                <label className="block text-[10px] font-extrabold text-gray-600 uppercase mb-2">
                  Message Content
                </label>
                <textarea
                  value={message}
                  readOnly
                  rows="4"
                  className="w-full px-3 py-3 rounded-lg border border-gray-200 text-xs font-semibold bg-gray-50 text-gray-500 cursor-not-allowed focus:outline-none"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading || !message.trim()}
                className="w-full bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 cursor-pointer shadow-md shadow-brand-600/10 transition-all disabled:opacity-50"
              >
                <Send className="w-4 h-4" />
                {loading ? 'Transmitting via gateway...' : t.sendAlertBtn}
              </button>
            </form>
          </div>

          <div className="flex items-center gap-1.5 text-[9px] text-gray-400 font-semibold border-t border-gray-50 pt-4 mt-6">
            <HelpCircle className="w-4 h-4 shrink-0" />
            <span>Target: {user.phone_number || "No Phone Registered"}. Gateway automatically simulates Twilio triggers.</span>
          </div>
        </div>

        {/* Column 2: Log of Transmission Histories */}
        <div className="bg-white border border-brand-100 shadow-md rounded-2xl p-6 space-y-4">
          <h3 className="font-extrabold text-sm text-gray-800 uppercase tracking-wider flex items-center gap-2">
            <span>📋</span> Transmission History Log
          </h3>

          {fetching ? (
            <div className="py-20 text-center text-gray-400 animate-pulse text-xs font-bold">
              Fetching dispatch histories...
            </div>
          ) : (
            <div className="space-y-4 max-h-[460px] overflow-y-auto pr-1">
              {alerts.map((log) => {
                const isWA = log.status.toLowerCase().includes('whatsapp')
                return (
                  <div key={log.id} className="p-3.5 rounded-xl border border-gray-100 hover:bg-gray-50/50 transition-all space-y-2 relative group">
                    <div className="flex justify-between items-center">
                      <span className={`px-2 py-0.5 rounded text-[8px] font-extrabold uppercase ${
                        log.alert_type === 'Weather' ? 'bg-sky-100 text-sky-800' :
                        log.alert_type === 'Market Price' ? 'bg-emerald-100 text-emerald-800' :
                        'bg-amber-100 text-amber-800'
                      }`}>
                        {log.alert_type}
                      </span>
                      
                      <span className={`text-[8px] font-extrabold px-2 py-0.5 rounded-full ${
                        isWA 
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' 
                          : 'bg-blue-100 text-blue-800 border border-blue-200'
                      }`}>
                        {isWA ? '🟢 WhatsApp' : '💬 SMS'}
                      </span>
                    </div>
                    
                    <p className="text-xs text-gray-700 font-semibold leading-relaxed">{log.message}</p>
                    
                    <div className="flex justify-between items-center text-[8px] text-gray-400 font-bold pt-1">
                      <span>Status: <span className={log.status.includes('Failed') ? 'text-rose-600' : 'text-emerald-600'}>{log.status}</span></span>
                      <span>Sent: {log.sent_at}</span>
                    </div>
                  </div>
                )
              })}
              {alerts.length === 0 && (
                <p className="text-xs text-gray-400 py-16 text-center font-semibold bg-gray-50/50 border border-dashed rounded-xl">
                  No alert dispatches logged yet.
                </p>
              )}
            </div>
          )}
        </div>

        {/* Column 3: Smartphone Chat Preview Mockup */}
        <div className="flex flex-col items-center justify-start">
          {/* Channel selector on top of mockup */}
          <div className="bg-gray-100 p-1 rounded-xl flex gap-1 mb-4 shadow-inner w-full max-w-[280px]">
            <button
              onClick={() => setPreviewTab('whatsapp')}
              type="button"
              className={`flex-1 py-1.5 rounded-lg text-[10px] font-extrabold transition-all cursor-pointer flex items-center justify-center gap-1 ${
                previewTab === 'whatsapp' 
                  ? 'bg-white text-emerald-700 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" /> WhatsApp
            </button>
            <button
              onClick={() => setPreviewTab('sms')}
              type="button"
              className={`flex-1 py-1.5 rounded-lg text-[10px] font-extrabold transition-all cursor-pointer flex items-center justify-center gap-1 ${
                previewTab === 'sms' 
                  ? 'bg-white text-blue-700 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" /> SMS App
            </button>
          </div>

          {/* Smartphone Shell Outer container */}
          <div className="relative border-[8px] border-gray-800 rounded-[36px] w-[280px] h-[520px] shadow-2xl overflow-hidden bg-gray-900 flex flex-col justify-between">
            {/* Phone Notch/Speaker */}
            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 h-4 w-28 bg-gray-800 rounded-b-xl z-20 flex items-center justify-center">
              <div className="w-10 h-1 bg-gray-600 rounded-full mb-1"></div>
            </div>

            {/* PREVIEW 1: WHATSAPP INTERFACE */}
            {previewTab === 'whatsapp' && (
              <div className="h-full flex flex-col justify-between bg-[#efeae2] relative pt-4">
                {/* WhatsApp Chat Top Header */}
                <div className="bg-[#075e54] text-white p-3.5 pt-6 flex items-center gap-2 shadow-md">
                  <div className="w-7 h-7 bg-emerald-700 rounded-full flex items-center justify-center text-xs font-black ring-1 ring-white/50">
                    KM
                  </div>
                  <div>
                    <h4 className="text-[10px] font-black leading-tight">KisanMitra Advisory Service</h4>
                    <p className="text-[8px] text-emerald-300 font-bold">Online</p>
                  </div>
                </div>

                {/* WhatsApp Chat Speech bubbles area */}
                <div className="flex-1 p-3 overflow-y-auto space-y-3 flex flex-col justify-start">
                  {/* System Welcome Date bubble */}
                  <div className="mx-auto bg-white/80 shadow-sm rounded px-2.5 py-0.5 text-[8px] text-gray-500 font-extrabold uppercase">
                    Today
                  </div>

                  {whatsappAlerts.map((wa) => (
                    <div key={wa.id} className="self-end bg-[#dcf8c6] border border-[#d4f2bc] shadow-sm rounded-lg p-2.5 max-w-[85%] space-y-1 relative animate-fade-in">
                      {/* Alert Tag inside bubble */}
                      <span className="text-[7px] font-black text-emerald-800 uppercase tracking-wide block">
                        🌾 KisanMitra {wa.alert_type}
                      </span>
                      <p className="text-[10px] text-gray-800 leading-snug font-medium pr-2">
                        {wa.message}
                      </p>
                      <div className="flex justify-end items-center gap-0.5 mt-1">
                        <span className="text-[7px] text-gray-400 font-bold">{wa.sent_at.split(' ')[1]?.substring(0, 5) || '10:00'}</span>
                        {/* Blue Double Checkmarks */}
                        <span className="text-[9px] text-[#34b7f1] font-black leading-none">✔✔</span>
                      </div>
                    </div>
                  ))}

                  {whatsappAlerts.length === 0 && (
                    <div className="flex flex-col items-center justify-center text-center h-full text-gray-400 px-4 space-y-2 mt-12">
                      <span className="text-2xl">🟢</span>
                      <p className="text-[10px] font-bold">No WhatsApp Alerts Dispatch</p>
                      <p className="text-[8px] text-gray-400 leading-relaxed font-semibold">
                        Toggle the delivery channel to "WhatsApp" and send an alert to see it appear here live!
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* PREVIEW 2: STANDARD SMS INTERFACE */}
            {previewTab === 'sms' && (
              <div className="h-full flex flex-col justify-between bg-white pt-4">
                {/* SMS Chat Top Header */}
                <div className="bg-gray-50 border-b border-gray-100 p-3 pt-6 flex items-center gap-3">
                  <div className="w-7 h-7 bg-brand-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                    ✉️
                  </div>
                  <div>
                    <h4 className="text-[10px] font-extrabold text-gray-800 leading-tight">Govt Alert Gateway</h4>
                    <p className="text-[8px] text-gray-400 font-semibold">{user.phone_number || "+91 99999 99999"}</p>
                  </div>
                </div>

                {/* SMS Chat Message threads */}
                <div className="flex-1 p-3 overflow-y-auto space-y-3 flex flex-col justify-start bg-gray-50/30">
                  <div className="mx-auto bg-gray-100 rounded-full px-2 py-0.5 text-[8px] text-gray-400 font-bold">
                    Text Message Thread
                  </div>

                  {smsAlerts.map((sms) => (
                    <div key={sms.id} className="self-end bg-brand-600 text-white shadow-md rounded-2xl rounded-tr-none p-2.5 max-w-[85%] space-y-1 relative animate-fade-in">
                      <p className="text-[10px] leading-snug font-medium">
                        {sms.message}
                      </p>
                      <p className="text-[7px] text-brand-100 font-bold text-right mt-1">
                        {sms.sent_at.split(' ')[1]?.substring(0, 5) || '10:00'} • Carrier Logged
                      </p>
                    </div>
                  ))}

                  {smsAlerts.length === 0 && (
                    <div className="flex flex-col items-center justify-center text-center h-full text-gray-400 px-4 space-y-2 mt-12">
                      <span className="text-2xl">💬</span>
                      <p className="text-[10px] font-bold">No SMS Alerts Dispatch</p>
                      <p className="text-[8px] text-gray-400 leading-relaxed font-semibold">
                        Toggle the delivery channel to "SMS" and dispatch an alert to see it appear here!
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  )
}
