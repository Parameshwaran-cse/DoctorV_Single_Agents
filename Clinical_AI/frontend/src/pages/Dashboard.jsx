import { useState } from 'react';
import { Play, Loader2, FileText, AlertTriangle, Activity, Stethoscope, Clock, Mic } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import './Dashboard.css';

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    patient_name: '',
    patient_age: '',
    report_type: 'blood_panel',
    clinical_context: '',
    doctor_question: '',
    report_text: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        ...formData,
        patient_age: formData.patient_age ? parseInt(formData.patient_age) : null,
      };

      const res = await fetch('http://127.0.0.1:8080/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to analyze report');
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-layout animate-fade-in">
      <Sidebar />
      
      <main className="dashboard-content">
        <section className="enterprise-panel panel-col">
          <div className="panel-header">
            <FileText size={18} />
            Diagnostic Report Metadata
          </div>
          
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="form-group">
              <label className="form-label">PATIENT NAME</label>
              <input 
                type="text" 
                name="patient_name" 
                className="input-ent" 
                value={formData.patient_name} 
                onChange={handleChange} 
                placeholder="e.g. Paramesh Sharma" 
              />
            </div>
            
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">AGE</label>
                <input 
                  type="number" 
                  name="patient_age" 
                  className="input-ent" 
                  value={formData.patient_age} 
                  onChange={handleChange} 
                  placeholder="e.g. 46" 
                />
              </div>
              <div className="form-group">
                <label className="form-label">REPORT MODALITY</label>
                <select 
                  name="report_type" 
                  className="input-ent" 
                  value={formData.report_type} 
                  onChange={handleChange} 
                  required
                >
                  <option value="blood_panel">Comprehensive Metabolic Panel / CBC</option>
                  <option value="ecg">ECG / EKG</option>
                  <option value="xray">X-Ray Report</option>
                  <option value="mri">MRI Report</option>
                  <option value="urine">Urinalysis</option>
                  <option value="pathology">Pathology</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">CLINICAL BACKGROUND CONTEXT</label>
              <textarea 
                name="clinical_context" 
                className="input-ent" 
                value={formData.clinical_context} 
                onChange={handleChange} 
                placeholder="e.g. Type 2 Diabetes, Hypertension. Presenting with chest pain."
              ></textarea>
            </div>

            <div className="form-group">
              <label className="form-label">PHYSICIAN QUERY / FOCUS</label>
              <textarea 
                name="doctor_question" 
                className="input-ent" 
                value={formData.doctor_question} 
                onChange={handleChange} 
                placeholder="e.g. Any critical findings? Is the kidney function safe for Metformin?"
              ></textarea>
            </div>

            <div className="form-group" style={{ flexGrow: 1 }}>
              <label className="form-label">LAB RESULTS / REPORT FINDINGS (TEXT OR LAB VALUES)</label>
              <textarea 
                name="report_text" 
                className="input-ent large" 
                value={formData.report_text} 
                onChange={handleChange} 
                placeholder="Paste lab values or report text here (e.g. HbA1c 9.2%, Fasting Glucose 218 mg/dL, eGFR 58 mL/min)..." 
                required
              ></textarea>
            </div>

            {error && (
              <div style={{ color: '#fca5a5', background: 'rgba(239, 68, 68, 0.1)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.3)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                {error}
              </div>
            )}

            <button type="submit" className="btn-ent" disabled={loading || !formData.report_text} style={{ marginTop: '0.5rem' }}>
              {loading ? (
                <><Loader2 className="animate-spin" size={18} /> Executing...</>
              ) : (
                <><Play size={18} fill="currentColor" /> Execute Clinical Intelligence Agent</>
              )}
            </button>
          </form>
        </section>

        <section className="enterprise-panel panel-col">
          {!result && !loading ? (
            <div className="results-empty">
              <div className="results-empty-icon">
                <Mic size={24} />
              </div>
              <h2>Ready for Diagnostic Analysis</h2>
              <p>Enter patient report details or lab findings and click "Execute Clinical Intelligence Agent" to analyze diagnostic values using live Gemini AI.</p>
              
              <div className="powered-by">
                <Clock size={12} /> Powered by Google Gemini
              </div>
            </div>
          ) : loading ? (
            <div className="results-empty">
              <Loader2 className="animate-spin" size={48} color="var(--accent-primary)" />
              <h2 style={{ marginTop: '1.5rem' }}>Processing Data</h2>
              <p>Gemini AI is analyzing the clinical report...</p>
            </div>
          ) : result && (
            <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column' }}>
              <div className="panel-header" style={{ marginBottom: '1.5rem' }}>
                <Activity size={18} /> Analysis Results
              </div>
              
              <div className="form-label" style={{ marginBottom: '0.5rem' }}>EXECUTIVE SUMMARY</div>
              <div className="summary-card">
                {result.executive_summary}
              </div>

              {result.critical_findings && result.critical_findings.length > 0 && (
                <>
                  <div className="form-label" style={{ color: 'var(--danger)', marginBottom: '0.5rem', marginTop: '1rem' }}>CRITICAL FINDINGS</div>
                  <div className="data-grid">
                    {result.critical_findings.map((item, i) => (
                      <div key={i} className="data-card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}>
                        <div className="card-header">
                          <span style={{ fontWeight: 600 }}>{item.parameter}</span>
                          <span className={`badge ${item.urgency}`}>{item.urgency}</span>
                        </div>
                        <div className="card-value">{item.value}</div>
                        <div className="card-range">Normal: {item.normal_range}</div>
                        <div className="card-desc">{item.significance}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {result.abnormal_values && result.abnormal_values.length > 0 && (
                <>
                  <div className="form-label" style={{ color: 'var(--warning)', marginBottom: '0.5rem', marginTop: '0.5rem' }}>ABNORMAL VALUES</div>
                  <div className="data-grid">
                    {result.abnormal_values.map((item, i) => (
                      <div key={i} className="data-card">
                        <div className="card-header">
                          <span style={{ fontWeight: 600 }}>{item.parameter}</span>
                          <span className="badge high">{item.direction}</span>
                        </div>
                        <div className="card-value">{item.value}</div>
                        <div className="card-range">Normal: {item.normal_range}</div>
                        <div className="card-desc">{item.clinical_meaning}</div>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {result.suggested_investigations && result.suggested_investigations.length > 0 && (
                <>
                  <div className="form-label" style={{ marginBottom: '0.5rem', marginTop: '0.5rem' }}>SUGGESTED NEXT STEPS</div>
                  <div className="summary-card" style={{ borderLeftColor: 'var(--border-focus)', background: 'var(--bg-panel)' }}>
                    <ul style={{ listStylePosition: 'inside', margin: 0, padding: 0 }}>
                      {result.suggested_investigations.map((item, i) => (
                        <li key={i} style={{ marginBottom: '0.75rem', listStyle: 'none' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent-primary)' }}></span>
                            <strong style={{ color: 'var(--text-primary)' }}>{item.investigation}</strong>
                            <span className={`badge ${item.priority}`}>{item.priority}</span>
                          </div>
                          <div style={{ paddingLeft: '1rem', color: 'var(--text-secondary)' }}>
                            {item.rationale}
                          </div>
                        </li>
                      ))}
                    </ul>
                  </div>
                </>
              )}

              {result.doctor_answer && (
                 <>
                  <div className="form-label" style={{ color: 'var(--accent-primary)', marginBottom: '0.5rem', marginTop: '0.5rem' }}>PHYSICIAN QUERY ANSWER</div>
                  <div className="summary-card" style={{ borderLeftColor: 'var(--accent-primary)' }}>
                    {result.doctor_answer}
                  </div>
                 </>
              )}

              <div style={{ marginTop: 'auto', paddingTop: '2rem', textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {result.disclaimer || "These findings are for physician review only and do not constitute a diagnosis."}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
