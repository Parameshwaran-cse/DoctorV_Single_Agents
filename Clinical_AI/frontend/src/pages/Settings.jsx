import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Cpu, Check, Loader2, Info, Zap } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import './Settings.css';
import './Dashboard.css';

const API_BASE = 'http://127.0.0.1:8080';

// Icon component for providers
function ProviderIcon({ type }) {
  if (type === 'gemini') {
    return (
      <div className="provider-icon gemini">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L2 19h20L12 2z" fill="#4285F4" opacity="0.8"/>
          <path d="M12 8l-4 8h8l-4-8z" fill="#8A63D2"/>
        </svg>
      </div>
    );
  }
  if (type === 'groq') {
    return (
      <div className="provider-icon groq">
        <Zap size={18} color="#f97316" />
      </div>
    );
  }
  return <div className="provider-icon"><Cpu size={18} /></div>;
}

export default function Settings() {
  const [providers, setProviders] = useState([]);
  const [activeProvider, setActiveProvider] = useState('');
  const [switching, setSwitching] = useState(null); // provider id being switched to
  const [toast, setToast] = useState(null); // { type: 'success'|'error', message: '' }
  const [fetchError, setFetchError] = useState(null);

  // Fetch providers on mount
  useEffect(() => {
    fetchProviders();
  }, []);

  // Auto-dismiss toast after 3.5s
  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(null), 3500);
      return () => clearTimeout(t);
    }
  }, [toast]);

  const fetchProviders = async () => {
    try {
      const res = await fetch(`${API_BASE}/config/providers`);
      if (!res.ok) throw new Error('Failed to fetch provider config');
      const data = await res.json();
      setProviders(data.providers);
      setActiveProvider(data.active_provider);
      setFetchError(null);
    } catch (err) {
      setFetchError(err.message);
    }
  };

  const handleSelectProvider = async (providerId) => {
    if (providerId === activeProvider) return;
    setSwitching(providerId);

    try {
      const res = await fetch(`${API_BASE}/config/providers/active`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider_id: providerId }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to switch provider');
      }

      setActiveProvider(data.active_provider);
      setProviders(prev =>
        prev.map(p => ({ ...p, is_active: p.id === data.active_provider }))
      );
      setToast({ type: 'success', message: data.message });
    } catch (err) {
      setToast({ type: 'error', message: err.message });
    } finally {
      setSwitching(null);
    }
  };

  const ENV_KEY_HINTS = [
    { label: 'GEMINI_API_KEY', description: 'Primary Gemini key' },
    { label: 'GEMINI_API_KEY_2', description: 'Fallback / Backup Gemini key' },
    { label: 'GROQ_API_KEY', description: 'Groq LLaMA key' },
  ];

  return (
    <div className="dashboard-layout animate-fade-in">
      <Sidebar />

      <main className="dashboard-content">
        <section className="enterprise-panel panel-col" style={{ maxWidth: '800px' }}>
          <div className="panel-header">
            <SettingsIcon size={18} />
            Settings
          </div>

          <div className="settings-wrapper">
            {/* AI Provider Selection */}
            <div className="settings-section">
              <div className="settings-section-title">
                <Cpu size={13} />
                AI PROVIDER SELECTION
              </div>

              {fetchError ? (
                <div style={{
                  color: 'var(--danger)',
                  background: 'rgba(239,68,68,0.08)',
                  border: '1px solid rgba(239,68,68,0.25)',
                  borderRadius: '8px',
                  padding: '1rem',
                  fontSize: '0.85rem',
                }}>
                  ⚠️ Could not connect to backend: {fetchError}
                  <div style={{ marginTop: '0.5rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    Make sure the backend server is running on port 8001.
                  </div>
                </div>
              ) : (
                <div className="provider-grid">
                  {providers.map((provider) => (
                    <div
                      key={provider.id}
                      className={`provider-card ${provider.is_active ? 'active' : ''} ${switching === provider.id ? 'loading' : ''}`}
                      onClick={() => handleSelectProvider(provider.id)}
                    >
                      <div className="provider-left">
                        <ProviderIcon type={provider.provider_type} />
                        <div className="provider-info">
                          <span className="provider-name">{provider.label}</span>
                          <span className="provider-model">{provider.model}</span>
                        </div>
                      </div>

                      <div className="provider-right">
                        {/* Key status badge */}
                        <span className={`provider-status-badge ${provider.api_key_configured ? 'configured' : 'not-configured'}`}>
                          {provider.api_key_configured ? '✓ Key Set' : '✗ No Key'}
                        </span>

                        {/* Active badge */}
                        {provider.is_active && !switching && (
                          <span className="provider-status-badge active-badge">Active</span>
                        )}

                        {/* Spinner or radio */}
                        {switching === provider.id ? (
                          <Loader2 size={18} className="animate-spin" style={{ color: 'var(--accent-primary)' }} />
                        ) : (
                          <div className={`provider-radio ${provider.is_active ? 'checked' : ''}`} />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="info-box">
                <Info size={14} />
                <span>
                  Click any provider to switch instantly. The selected AI engine will be used for all subsequent
                  <strong> /analyze</strong> requests. The Groq provider uses LLaMA 3.3 70B and is significantly
                  faster for real-time clinical analysis.
                </span>
              </div>
            </div>

            {/* Environment Keys Reference */}
            <div className="settings-section">
              <div className="settings-section-title">
                <Info size={13} />
                ENVIRONMENT VARIABLES REFERENCE
              </div>
              <div>
                {ENV_KEY_HINTS.map((hint) => (
                  <div key={hint.label} className="env-key-row">
                    <span className="env-key-label">{hint.label}</span>
                    <span className="env-key-value">{hint.description}</span>
                  </div>
                ))}
              </div>
              <div style={{ marginTop: '1rem', fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>
                Set these in <code style={{ background: 'var(--bg-input)', padding: '1px 5px', borderRadius: '3px' }}>clinical_intelligence_service/.env</code> and restart the server.
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Toast Notification */}
      {toast && (
        <div className={`settings-toast ${toast.type}`}>
          {toast.type === 'success' ? <Check size={16} /> : null}
          {toast.message}
        </div>
      )}
    </div>
  );
}
