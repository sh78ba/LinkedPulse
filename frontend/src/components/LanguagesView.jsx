import React from 'react';

export default function LanguagesView({ items }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="card fade-in" style={{ padding: '24px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
        {items.map((lang, idx) => (
          <div key={idx} style={{
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--bg-card-subtle)',
            border: '1px solid var(--border-color)',
          }}>
            <p style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.92rem' }}>{lang.name}</p>
            {lang.proficiency && (
              <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginTop: '2px' }}>{lang.proficiency}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
