import React from 'react';
import { X, Key, ShieldCheck, Terminal, AlertCircle } from 'lucide-react';

export default function ConfigModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '20px'
    }}>
      <div className="glass-panel animate-fade-in" style={{
        maxWidth: '640px',
        width: '100%',
        padding: '28px',
        position: 'relative',
        maxHeight: '90vh',
        overflowY: 'auto'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'rgba(56, 189, 248, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Key size={18} color="#38bdf8" />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc' }}>
              LinkedIn Session Configuration
            </h3>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '6px',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px', fontSize: '0.9rem', color: '#cbd5e1', lineHeight: 1.6 }}>
          <p>
            The reverse-engineered LinkedIn client communicates directly with LinkedIn HTTP endpoints using your authorized session cookie.
          </p>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
            <h4 style={{ color: '#38bdf8', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldCheck size={16} />
              <span>How to extract your session cookie</span>
            </h4>
            <ol style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <li>Open <strong>LinkedIn.com</strong> in your browser and sign in.</li>
              <li>Open DevTools (<kbd style={{ background: '#1e293b', padding: '2px 6px', borderRadius: '4px' }}>F12</kbd> or <kbd style={{ background: '#1e293b', padding: '2px 6px', borderRadius: '4px' }}>Cmd+Option+I</kbd>).</li>
              <li>Go to <strong>Application</strong> / <strong>Storage</strong> &rarr; <strong>Cookies</strong> &rarr; <code>https://www.linkedin.com</code>.</li>
              <li>Copy the value of the <code>li_at</code> cookie.</li>
              <li>(Optional) Copy the <code>JSESSIONID</code> value for CSRF authentication.</li>
            </ol>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-glass)' }}>
            <h4 style={{ color: '#818cf8', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Terminal size={16} />
              <span>Configure in backend/.env</span>
            </h4>
            <pre style={{
              background: '#090d16',
              padding: '12px',
              borderRadius: 'var(--radius-sm)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.8rem',
              color: '#38bdf8',
              overflowX: 'auto'
            }}>
{`# backend/.env
LINKEDIN_SESSION_COOKIE="AQEDAU..."
LINKEDIN_CSRF_TOKEN="ajax:1234567890123456789"
LOG_LEVEL="INFO"`}
            </pre>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            background: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            color: '#fbbf24',
            fontSize: '0.82rem'
          }}>
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <span>Never share or commit your <code>li_at</code> session cookie to GitHub. It is securely ignored by <code>.gitignore</code>.</span>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
          <button
            onClick={onClose}
            style={{
              padding: '10px 22px',
              borderRadius: 'var(--radius-sm)',
              background: 'linear-gradient(135deg, #0a66c2, #0284c7)',
              border: 'none',
              color: '#ffffff',
              fontWeight: 700,
              cursor: 'pointer'
            }}
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
