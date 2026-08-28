import React from 'react';
import { MapPin, User, ExternalLink } from 'lucide-react';

export default function ProfileHero({ data }) {
  if (!data || !data.profile) return null;

  const { profile } = data;
  const avatarUrl = profile.images && profile.images.length > 0 ? profile.images[0] : null;

  return (
    <div className="card fade-in" style={{ padding: '28px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', gap: '22px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
        {/* Avatar */}
        <div style={{
          width: '84px',
          height: '84px',
          borderRadius: '50%',
          backgroundColor: '#1c2230',
          border: '2px solid rgba(255, 255, 255, 0.1)',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={profile.name || 'User'}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              onError={(e) => { e.target.style.display = 'none'; }}
            />
          ) : (
            <User size={38} color="var(--text-dim)" />
          )}
        </div>

        {/* Info */}
        <div style={{ flex: 1, minWidth: '240px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.02em' }}>
                {profile.name || 'LinkedIn Member'}
              </h2>

              {profile.headline && (
                <p style={{ fontSize: '0.96rem', color: 'var(--text-muted)', marginTop: '4px', lineHeight: 1.4 }}>
                  {profile.headline}
                </p>
              )}
            </div>

            {profile.profile_url && (
              <a
                href={profile.profile_url}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '6px 14px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-card-subtle)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-main)',
                  textDecoration: 'none',
                  fontSize: '0.82rem',
                  fontWeight: 500,
                  transition: 'all 0.15s ease'
                }}
              >
                <span>LinkedIn</span>
                <ExternalLink size={13} color="var(--text-muted)" />
              </a>
            )}
          </div>

          {profile.location && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: 'var(--text-dim)', fontSize: '0.85rem', marginTop: '10px' }}>
              <MapPin size={14} />
              <span>{profile.location}</span>
            </div>
          )}
        </div>
      </div>

      {/* About Summary */}
      {profile.about && (
        <div style={{
          padding: '16px 18px',
          borderRadius: 'var(--radius-md)',
          background: 'var(--bg-input)',
          border: '1px solid var(--border-color)',
          fontSize: '0.9rem',
          color: 'var(--text-muted)',
          lineHeight: 1.6,
          whiteSpace: 'pre-line'
        }}>
          {profile.about}
        </div>
      )}
    </div>
  );
}
