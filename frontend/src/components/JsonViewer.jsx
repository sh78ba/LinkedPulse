import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export default function JsonViewer({ data }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="card fade-in" style={{ padding: '18px', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Response Payload
        </span>
        <button
          onClick={handleCopy}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 10px',
            borderRadius: 'var(--radius-sm)',
            background: 'var(--bg-card-subtle)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-muted)',
            fontSize: '0.78rem',
            cursor: 'pointer',
          }}
        >
          {copied ? <Check size={12} color="var(--success)" /> : <Copy size={12} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

      <pre style={{
        margin: 0,
        padding: '16px',
        borderRadius: 'var(--radius-md)',
        background: 'var(--bg-input)',
        border: '1px solid var(--border-color)',
        color: '#a5b4fc',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.8rem',
        overflowX: 'auto',
        maxHeight: '440px',
        lineHeight: 1.5
      }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
