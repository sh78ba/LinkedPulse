import React from 'react';

export default function Tabs({ activeTab, setActiveTab, counts }) {
  const allTabs = [
    { id: 'experience', label: 'Experience', count: counts.experience },
    { id: 'education', label: 'Education', count: counts.education },
    { id: 'skills', label: 'Skills', count: counts.skills },
    { id: 'certifications', label: 'Certifications', count: counts.certifications },
    { id: 'languages', label: 'Languages', count: counts.languages },
    { id: 'json', label: 'Raw Data', count: null },
  ];

  // Only display tabs that have data, plus Raw Data
  const visibleTabs = allTabs.filter(t => t.id === 'json' || t.count > 0);

  return (
    <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
      {visibleTabs.map((tab) => {
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 16px',
              borderRadius: 'var(--radius-full)',
              background: isActive ? 'var(--primary)' : 'var(--bg-card)',
              border: `1px solid ${isActive ? 'var(--primary)' : 'var(--border-color)'}`,
              color: isActive ? '#ffffff' : 'var(--text-muted)',
              fontWeight: isActive ? 600 : 500,
              fontSize: '0.86rem',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s ease',
            }}
          >
            <span>{tab.label}</span>
            {tab.count !== null && tab.count > 0 && (
              <span style={{
                background: isActive ? 'rgba(255, 255, 255, 0.2)' : 'var(--bg-card-subtle)',
                color: isActive ? '#ffffff' : 'var(--text-dim)',
                fontSize: '0.72rem',
                padding: '1px 6px',
                borderRadius: 'var(--radius-full)',
                fontWeight: 600,
              }}>
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
