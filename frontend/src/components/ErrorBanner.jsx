import React from 'react';
import { AlertCircle, X } from 'lucide-react';

export default function ErrorBanner({ message, error, onClose }) {
  const displayMsg = message || error?.message || (typeof error === 'string' ? error : 'An error occurred.');

  return (
    <div
      className="card fade-in"
      style={{
        padding: '14px 18px',
        borderColor: 'rgba(239, 68, 68, 0.3)',
        background: 'var(--error-soft)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '12px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <AlertCircle size={17} color="var(--error)" />
        <span style={{ fontSize: '0.88rem', color: '#fca5a5' }}>
          {displayMsg}
        </span>
      </div>

      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#fca5a5',
            cursor: 'pointer',
            padding: '4px',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <X size={15} />
        </button>
      )}
    </div>
  );
}
