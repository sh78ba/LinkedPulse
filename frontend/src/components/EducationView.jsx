import React from 'react';

export default function EducationView({ items }) {
  if (!items || items.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }} className="fade-in">
      {items.map((edu, idx) => (
        <div key={idx} className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-main)' }}>
                {edu.school}
              </h3>

              {(edu.degree || edu.field_of_study) && (
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {[edu.degree, edu.field_of_study].filter(Boolean).join(' in ')}
                </p>
              )}
            </div>

            {(edu.start_date || edu.end_date) && (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 500 }}>
                {edu.start_date || 'Start'} — {edu.end_date || 'Graduation'}
              </span>
            )}
          </div>

          {edu.description && (
            <p style={{
              marginTop: '10px',
              fontSize: '0.88rem',
              color: 'var(--text-muted)',
              lineHeight: 1.5,
              whiteSpace: 'pre-line'
            }}>
              {edu.description}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
