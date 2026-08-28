import React from 'react';
import { ExternalLink } from 'lucide-react';

export default function ExperienceView({ items }) {
  if (!items || items.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }} className="fade-in">
      {items.map((exp, idx) => (
        <div key={idx} className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-main)' }}>
                {exp.title || 'Role'}
              </h3>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '2px', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                  {exp.company}
                </span>
                {exp.company_url && (
                  <a
                    href={exp.company_url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '3px', fontSize: '0.78rem', textDecoration: 'none' }}
                  >
                    <span>Company</span>
                    <ExternalLink size={11} />
                  </a>
                )}
                {exp.location && (
                  <>
                    <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>•</span>
                    <span style={{ color: 'var(--text-dim)', fontSize: '0.84rem' }}>{exp.location}</span>
                  </>
                )}
              </div>
            </div>

            {(exp.start_date || exp.end_date) && (
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontWeight: 500 }}>
                {exp.start_date || 'Unknown'} — {exp.end_date || 'Present'}
              </span>
            )}
          </div>

          {exp.description && (
            <p style={{
              marginTop: '12px',
              fontSize: '0.88rem',
              color: 'var(--text-muted)',
              lineHeight: 1.5,
              whiteSpace: 'pre-line'
            }}>
              {exp.description}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
