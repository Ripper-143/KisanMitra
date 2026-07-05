import React, { useState } from 'react'
import { translations } from '../translations'
import { UploadCloud, CheckCircle2, ShieldAlert, HeartPulse, Sparkles, Activity, FileText } from 'lucide-react'
import { API_BASE } from '../api'

export default function CropUpload({ lang, user }) {
  const t = translations[lang]
  const [selectedFile, setSelectedFile] = useState(null)
  const [cropType, setCropType] = useState(user.land_profile?.crop_type || 'Paddy')
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [preview, setPreview] = useState(null)

  const handleDownloadPDF = async () => {
    if (!report || !report.id) return
    
    const token = localStorage.getItem('kisan_token')
    try {
      const response = await fetch(`${API_BASE}/api/crop/diagnose/${report.id}/pdf`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `KisanMitra_Report_${cropType}_Diagnosis.pdf`
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
      } else {
        alert('Failed to download report PDF.')
      }
    } catch (err) {
      console.error(err)
      alert('Error fetching report PDF.')
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setPreview(URL.createObjectURL(file))
      setReport(null)
      setError('')
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!selectedFile) {
      setError('Please select an image first.')
      return
    }

    setLoading(true)
    setError('')
    setReport(null)

    const token = localStorage.getItem('kisan_token')
    const formData = new FormData()
    formData.append('image', selectedFile)
    formData.append('crop_type', cropType)

    try {
      const response = await fetch(`${API_BASE}/api/crop/diagnose`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      const data = await response.json()
      if (response.ok) {
        setReport(data)
      } else {
        setError(data.detail || 'Failed to complete diagnosis. Try again.')
      }
    } catch (err) {
      setError('Error communicating with the crop diagnosis agent.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      <div className="flex items-center gap-3 border-b border-gray-100 pb-4">
        <div className="p-3 bg-brand-100 text-brand-700 rounded-xl">
          <HeartPulse className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">{t.cropHealth}</h2>
          <p className="text-xs text-gray-500 font-medium uppercase tracking-wider">{t.tagline}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Upload Form */}
        <div className="bg-white border border-brand-100 shadow-md rounded-2xl p-6 space-y-6">
          <form onSubmit={handleUpload} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-gray-600 uppercase mb-2">
                {t.cropType}
              </label>
              <select
                value={cropType}
                onChange={(e) => setCropType(e.target.value)}
                className="w-full px-3 py-3 rounded-lg border border-gray-200 text-sm font-semibold focus:ring-2 focus:ring-brand-500 focus:outline-none cursor-pointer"
              >
                <option value="Paddy">Paddy (వరి / धान)</option>
                <option value="Cotton">Cotton (పత్తి / कपास)</option>
                <option value="Maize">Maize (మొక్కజొన్న / मक्का)</option>
                <option value="Chilli">Red Chilli (మిరప / लाल मिर्च)</option>
                <option value="Turmeric">Turmeric (పసుపు / हल्दी)</option>
              </select>
            </div>

            {/* Drag & Drop Visual Panel */}
            <div className="space-y-2">
              <label className="block text-xs font-bold text-gray-600 uppercase">
                Upload Photo
              </label>
              <div className="border-2 border-dashed border-gray-200 hover:border-brand-400 rounded-xl p-6 transition-all text-center cursor-pointer relative bg-gray-50/50">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                
                {preview ? (
                  <div className="flex flex-col items-center">
                    <img src={preview} alt="Leaf Preview" className="h-40 object-cover rounded-lg border shadow-sm mb-3" />
                    <p className="text-xs text-gray-500 font-semibold truncate max-w-[200px]">{selectedFile?.name}</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="flex justify-center text-gray-400">
                      <UploadCloud className="w-12 h-12" />
                    </div>
                    <p className="text-sm font-semibold text-gray-600">{t.uploadPrompt}</p>
                    <p className="text-[10px] text-gray-400 font-medium">Supports PNG, JPG, JPEG, WEBP up to 8MB</p>
                  </div>
                )}
              </div>
            </div>

            {error && (
              <p className="text-xs text-rose-600 bg-rose-50 border border-rose-100 p-3 rounded-lg font-semibold flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4" />
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading || !selectedFile}
              className="w-full bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 cursor-pointer shadow-md shadow-brand-600/10 transition-all disabled:opacity-50"
            >
              <Activity className="w-4 h-4" />
              {loading ? 'Analyzing Plant Photo...' : t.diagnoseBtn}
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div className="bg-white border border-brand-100 shadow-md rounded-2xl p-6 flex flex-col justify-between">
          {!report && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center py-12 text-gray-400 space-y-2">
              <Sparkles className="w-12 h-12 text-gray-300 animate-pulse" />
              <p className="text-sm font-semibold">Diagnosis Pending</p>
              <p className="text-[10px] text-gray-400 max-w-[200px] leading-relaxed">
                Upload a plant photo and run analysis to receive agent diagnosis reports.
              </p>
            </div>
          )}

          {loading && (
            <div className="flex flex-col items-center justify-center h-full text-center py-12 space-y-4">
              <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-xs font-bold text-gray-500 animate-pulse">
                Crop Health Agent is evaluating plant symptoms...
              </p>
            </div>
          )}

          {report && (
            <div className="space-y-5">
              <div className="flex justify-between items-center border-b border-gray-100 pb-3">
                <h3 className="font-extrabold text-gray-800 text-sm uppercase tracking-wider">
                  Diagnosis Report
                </h3>
                <span className="text-[9px] text-gray-400 font-bold uppercase">
                  {report.agent}
                </span>
              </div>

              {/* Status Header */}
              <div className="p-4 rounded-xl border border-brand-100 bg-brand-50/20 space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-500 font-bold">{t.detectedDisease}:</span>
                  <span className="font-extrabold text-brand-700">{report.disease_detected}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-500 font-bold">{t.severity}:</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    report.severity === 'High' ? 'bg-rose-100 text-rose-800' :
                    report.severity === 'Moderate' ? 'bg-amber-100 text-amber-800' :
                    'bg-emerald-100 text-emerald-800'
                  }`}>
                    {report.severity}
                  </span>
                </div>
              </div>

              {/* Description & Treatment Details */}
              <div className="space-y-4 max-h-[300px] overflow-y-auto pr-1">
                {/* Visual rendering of raw report text */}
                <div className="text-xs text-gray-600 leading-relaxed font-semibold bg-gray-50 p-4 rounded-xl whitespace-pre-wrap border border-gray-100 font-mono">
                  {report.diagnosis_details}
                </div>
              </div>

              {/* Success Badge & Download PDF */}
              <div className="flex items-center justify-between gap-1.5 pt-4 border-t border-gray-100">
                <div className="flex items-center gap-1.5 text-xs text-emerald-700 font-bold">
                  <CheckCircle2 className="w-4.5 h-4.5 shrink-0" />
                  <span>Saved to history.</span>
                </div>
                <button
                  onClick={handleDownloadPDF}
                  type="button"
                  className="bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold py-2 px-3.5 rounded-lg flex items-center gap-1.5 shadow transition-colors cursor-pointer"
                >
                  <FileText className="w-3.5 h-3.5" />
                  Download PDF Report
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
