import React from 'react';
import { ExternalLink } from 'lucide-react';

export default function CertificationsView({ items }) {
  if (!items || items.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }} className="fade-in">
      {items.map((cert, idx) => (
        <div key={idx} className="card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
                {cert.name}
              </h3>
              {cert.authority && (
                <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {cert.authority}
                </p>
              )}
            </div>

            {cert.url && (
              <a
                href={cert.url}
                target="_blank"
                rel="noreferrer"
                style={{ color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', textDecoration: 'none' }}
              >
                <span>Credential</span>
                <ExternalLink size={12} />
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
