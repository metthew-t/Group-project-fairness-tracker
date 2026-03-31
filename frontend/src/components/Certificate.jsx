import React from 'react';
import '../pages/Page.css';

export default function Certificate({ contribution, onClose }) {
  if (!contribution) return null;

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal certificate-modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '800px', width: '90%' }}>
        <div className="modal-header no-print">
          <h3>Contribution Certificate</h3>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-primary" onClick={handlePrint}>Print / Save PDF</button>
            <button className="btn btn-ghost btn-icon" onClick={onClose}>✕</button>
          </div>
        </div>
        <div className="certificate-content" style={{ padding: '60px', textAlign: 'center', border: '15px solid var(--primary)', borderRadius: '8px', background: 'var(--bg-secondary)', position: 'relative' }}>
          <div style={{ position: 'absolute', top: '20px', left: '20px', fontSize: '2rem', opacity: 0.1 }}>⚖️</div>
          <h1 style={{ color: 'var(--primary)', fontSize: '2.5rem', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '4px' }}>Certificate of Contribution</h1>
          <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)' }}>This is to certify that</p>
          <h2 style={{ fontSize: '2rem', margin: '20px 0', borderBottom: '2px solid var(--border)', display: 'inline-block', paddingBottom: '5px' }}>{contribution.username || 'Team Member'}</h2>
          <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)' }}>has successfully contributed to the project</p>
          <h3 style={{ fontSize: '1.8rem', margin: '15px 0', color: 'var(--accent-400)' }}>{contribution.task_title || 'Project Task'}</h3>
          <div style={{ marginTop: '40px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
            <div style={{ textAlign: 'left', padding: '20px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
              <p><b>Work Type:</b> {contribution.work_type}</p>
              <p><b>Hours Logged:</b> {contribution.hours_spent} hours</p>
              <p><b>Difficulty Rating:</b> {'⭐'.repeat(contribution.difficulty)}</p>
            </div>
            <div style={{ textAlign: 'left', padding: '20px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
              <p><b>Verification Status:</b> <span style={{ color: 'var(--success)' }}>{contribution.status}</span></p>
              <p><b>Date Issued:</b> {new Date().toLocaleDateString()}</p>
              <p><b>Tracker ID:</b> FT-{contribution.id}-{new Date().getFullYear()}</p>
            </div>
          </div>
          <div style={{ marginTop: '60px', borderTop: '1px dashed var(--border)', paddingTop: '20px', display: 'flex', justifyContent: 'space-between' }}>
            <div style={{ textAlign: 'center' }}>
                <div style={{ height: '40px' }}></div>
                <div style={{ borderTop: '1px solid var(--text-primary)', width: '200px', fontSize: '0.8rem' }}>Team Lead Signature</div>
            </div>
             <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.5rem', marginBottom: '5px' }}>⚖️</div>
                <div style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>FAIRNESS TRACKER</div>
            </div>
          </div>
        </div>
      </div>
      <style>{`
        @media print {
            body * { visibility: hidden; }
            .certificate-modal, .certificate-modal * { visibility: visible; }
            .certificate-modal { position: absolute; left: 0; top: 0; width: 100%; border: none; box-shadow: none; margin: 0; padding: 0; }
            .no-print { display: none !important; }
            .certificate-content { border: 15px solid #6366f1 !important; color: #000 !important; background: #fff !important; }
            h1 { color: #6366f1 !important; }
        }
      `}</style>
    </div>
  );
}
