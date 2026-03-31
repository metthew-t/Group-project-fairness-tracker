import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './Page.css';

export default function Profile() {
  const { user } = useAuth();

  return (
    <div className="page-content animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Your Profile</h1>
          <p className="page-subtitle">Manage your personal information</p>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header"><h3>Personal Information</h3></div>
          <div className="card-body">
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '24px' }}>
              <div className="avatar-xl">{user?.username?.[0]?.toUpperCase()}</div>
              <div>
                <h2 style={{ fontSize: '1.5rem' }}>{user?.username}</h2>
                <p>{user?.email}</p>
              </div>
            </div>

            <div className="form-group mb-4">
              <label className="form-label">Full Name</label>
              <input className="form-input" value={`${user?.first_name || ''} ${user?.last_name || ''}`} readOnly />
            </div>
            <div className="form-group mb-4">
              <label className="form-label">Email</label>
              <input className="form-input" value={user?.email || ''} readOnly />
            </div>
            <button className="btn btn-secondary" onClick={() => toast.error('Edit profile coming soon!')}>Edit Profile</button>
          </div>
        </div>

        <div className="card">
          <div className="card-header"><h3>Account Security</h3></div>
          <div className="card-body">
            <p className="mb-4">Change your password and manage security settings.</p>
            <button className="btn btn-secondary">Change Password</button>
            <div className="divider" style={{ margin: '24px 0' }} />
            <h4 className="text-danger mb-2">Danger Zone</h4>
            <p className="text-xs mb-4">Deleting your account is permanent and cannot be undone.</p>
            <button className="btn btn-danger">Delete Account</button>
          </div>
        </div>
      </div>
    </div>
  );
}
