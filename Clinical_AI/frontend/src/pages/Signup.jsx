import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Activity, ArrowRight, Loader2 } from 'lucide-react';
import './Auth.css';

export default function Signup() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch('http://127.0.0.1:8080/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });
      
      if (!res.ok) throw new Error('Signup failed');
      
      const data = await res.json();
      localStorage.setItem('medflow_token', data.token);
      localStorage.setItem('medflow_user', JSON.stringify(data.user));
      navigate('/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container animate-fade-in">
      <div className="glass glass-panel auth-card">
        <div className="auth-header">
          <div className="logo-icon">
            <Activity size={32} color="white" />
          </div>
          <h1>Create an account</h1>
          <p>Join MedFlow to analyze clinical reports</p>
        </div>

        <form onSubmit={handleSignup} className="auth-form">
          {error && <div className="auth-error">{error}</div>}
          
          <div className="form-group">
            <label>Full Name</label>
            <input 
              type="text" 
              className="input-glass" 
              placeholder="Dr. Smith"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required 
            />
          </div>

          <div className="form-group">
            <label>Email Address</label>
            <input 
              type="email" 
              className="input-glass" 
              placeholder="doctor@medflow.ai"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input 
              type="password" 
              className="input-glass" 
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>

          <button type="submit" className="btn-glass" disabled={loading} style={{ marginTop: '1rem' }}>
            {loading ? <Loader2 className="animate-spin" size={20} /> : <>Sign Up <ArrowRight size={18} /></>}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
