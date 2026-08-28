import React from 'react';
import { Search, Loader2, ArrowRight } from 'lucide-react';

const SUGGESTIONS = [
  { name: 'Bill Gates', url: 'https://www.linkedin.com/in/williamhgates/' },
  { name: 'Sundar Pichai', url: 'https://www.linkedin.com/in/sundarpichai/' },
  { name: 'Satya Nadella', url: 'https://www.linkedin.com/in/satyanadella/' },
];

export default function SearchBar({ url, setUrl, onSearch, isLoading }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    onSearch(url);
  };

  return (
    <div className="card" style={{ padding: '20px' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px' }}>
        <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center' }}>
          <Search size={17} style={{ position: 'absolute', left: '14px', color: 'var(--text-dim)' }} />
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste LinkedIn Profile URL..."
            style={{
              width: '100%',
              padding: '12px 14px 12px 40px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-input)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-main)',
              fontSize: '0.92rem',
              outline: 'none',
              transition: 'border-color 0.15s ease',
            }}
            onFocus={(e) => (e.target.style.borderColor = 'var(--border-focus)')}
            onBlur={(e) => (e.target.style.borderColor = 'var(--border-color)')}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '0 20px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--primary)',
            border: 'none',
            color: '#ffffff',
            fontSize: '0.9rem',
            fontWeight: 600,
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading || !url.trim() ? 0.6 : 1,
            transition: 'background-color 0.15s ease',
          }}
        >
          {isLoading ? (
            <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
          ) : (
            <>
              <span>Search</span>
              <ArrowRight size={15} />
            </>
          )}
        </button>
      </form>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '14px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Try:</span>
        {SUGGESTIONS.map((item) => (
          <button
            key={item.name}
            type="button"
            onClick={() => {
              setUrl(item.url);
              onSearch(item.url);
            }}
            disabled={isLoading}
            style={{
              padding: '4px 12px',
              borderRadius: 'var(--radius-full)',
              background: 'var(--bg-card-subtle)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-muted)',
              fontSize: '0.78rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {item.name}
          </button>
        ))}
      </div>
    </div>
  );
}
