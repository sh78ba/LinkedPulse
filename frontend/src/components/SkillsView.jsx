import React from 'react';

export default function SkillsView({ items }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="card fade-in" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {items.map((skill, idx) => (
          <span
            key={idx}
            style={{
              padding: '6px 14px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--bg-card-subtle)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-main)',
              fontSize: '0.86rem',
              fontWeight: 500
            }}
          >
            {skill.name}
          </span>
        ))}
      </div>
    </div>
  );
}
