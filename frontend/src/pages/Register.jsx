import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../api/auth';
import toast from 'react-hot-toast';
import './Auth.css';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1: Info, 2: Verification
  const [form, setForm] = useState({
    username: '', email: '', password: '', password2: '', first_name: '', last_name: '', user_type: 'STUDENT', phone_number: ''
  });
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    setForm((p) => ({ ...p, [e.target.name]: e.target.value }));
    setErrors((p) => { const n = { ...p }; delete n[e.target.name]; return n; });
  };

  const validate = () => {
    const e = {};
    if (!form.username) e.username = 'Username is required';
    if (!form.email) e.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Email is invalid';
    if (!form.password) e.password = 'Password is required';
    else if (form.password.length < 8) e.password = 'Password must be at least 8 characters';
    if (form.password !== form.password2) e.password2 = 'Passwords do not match';
    return e;
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    const v = validate();
    if (Object.keys(v).length) { setErrors(v); return; }
    setLoading(true);
    try {
      console.log('Registering user...', form);
      const userData = await register(form);
      console.log('Registration success, sending verification...', userData);
      
      try {
        await authAPI.sendVerification();
        toast.success('Account created! Please verify your email.');
        setStep(2);
      } catch (vErr) {
        console.error('Verification send failed:', vErr);
        toast.error('Account created, but failed to send verification code. Please login to retry.');
        navigate('/login');
      }
    } catch (err) {
      console.error('Registration error:', err);
      const data = err.response?.data || {};
      if (typeof data === 'object') {
        const mapped = {};
        Object.entries(data).forEach(([k, v]) => {
          mapped[k] = Array.isArray(v) ? v[0] : v;
        });
        setErrors(mapped);
        if (mapped.non_field_errors) toast.error(mapped.non_field_errors);
        else if (Object.keys(mapped).length > 0) toast.error('Check the form for errors');
        else toast.error('Registration failed. Please try again.');
      } else {
        toast.error('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!verificationCode) { toast.error('Please enter the code'); return; }
    setLoading(true);
    try {
      await authAPI.verifyEmail(verificationCode);
      toast.success('Email verified! Redirecting to dashboard...');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  if (step === 2) {
    return (
      <div className="auth-wrapper">
        <div className="auth-card animate-fade-in">
          <div className="auth-logo">
            <div className="auth-logo-icon">📧</div>
            <div>
              <h1 className="auth-brand">Verify Email</h1>
              <p className="auth-tagline">We sent a 6-digit code to {form.email}</p>
            </div>
          </div>
          <form onSubmit={handleVerify} className="auth-form">
            <div className="form-group">
              <label className="form-label">Verification Code</label>
              <input className="form-input" type="text" placeholder="123456" maxLength={6}
                value={verificationCode} onChange={(e) => setVerificationCode(e.target.value)}
                style={{ textAlign: 'center', fontSize: '1.5rem', letterSpacing: '0.2em' }} autoFocus />
            </div>
            <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading}>
              {loading ? <div className="spinner" /> : 'Verify Code →'}
            </button>
          </form>
          <button className="btn btn-ghost btn-full mt-2" onClick={() => authAPI.sendVerification()}>Resend Code</button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-bg-glow" />
      <div className="auth-card animate-fade-in">
        <div className="auth-logo">
          <div className="auth-logo-icon">⚖️</div>
          <div>
            <h1 className="auth-brand">FairnessTracker</h1>
            <p className="auth-tagline">Balanced collaboration, measured fairly</p>
          </div>
        </div>

        <h2 className="auth-title">Create your account</h2>
        <p className="auth-subtitle">Join your team and start tracking contributions</p>

        <form onSubmit={handleRegister} className="auth-form">
          <div className="auth-row">
            <div className="form-group">
              <label className="form-label">First Name</label>
              <input className="form-input" type="text" name="first_name" placeholder="First name"
                value={form.first_name} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Last Name</label>
              <input className="form-input" type="text" name="last_name" placeholder="Last name"
                value={form.last_name} onChange={handleChange} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Username *</label>
            <input className={`form-input ${errors.username ? 'error' : ''}`} type="text"
              name="username" placeholder="Choose a username"
              value={form.username} onChange={handleChange} />
            {errors.username && <span className="form-error">{errors.username}</span>}
          </div>
          <div className="form-group">
            <label className="form-label">Email *</label>
            <input className={`form-input ${errors.email ? 'error' : ''}`} type="email"
              name="email" placeholder="your@email.com"
              value={form.email} onChange={handleChange} />
            {errors.email && <span className="form-error">{errors.email}</span>}
          </div>
          <div className="form-group">
            <label className="form-label">Phone Number</label>
            <input className="form-input" type="text" name="phone_number" placeholder="+1..."
              value={form.phone_number} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label className="form-label">Password *</label>
            <input className={`form-input ${errors.password ? 'error' : ''}`} type="password"
              name="password" placeholder="Minimum 8 characters"
              value={form.password} onChange={handleChange} required />
            {errors.password && <span className="form-error">{errors.password}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Confirm Password *</label>
            <input className={`form-input ${errors.password2 ? 'error' : ''}`} type="password"
              name="password2" placeholder="Repeat your password"
              value={form.password2} onChange={handleChange} required />
            {errors.password2 && <span className="form-error">{errors.password2}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Account Type *</label>
            <select className="form-select" name="user_type" value={form.user_type} onChange={handleChange}>
              <option value="STUDENT">Student / Member</option>
              <option value="TEAM_LEAD">Team Lead / Head</option>
              <option value="INSTRUCTOR">Instructor / Professor</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary btn-full btn-lg" disabled={loading}>
            {loading ? <><div className="spinner" /> Creating account...</> : 'Create Account →'}
          </button>
        </form>

        <div className="divider-with-text" style={{ margin: '24px 0' }}>OR</div>

        <p className="auth-footer-text">
          Already have an account? <Link to="/login" className="auth-link">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
