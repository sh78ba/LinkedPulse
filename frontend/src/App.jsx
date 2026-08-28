import React, { useState } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import ProfileHero from './components/ProfileHero';
import Tabs from './components/Tabs';
import ExperienceView from './components/ExperienceView';
import EducationView from './components/EducationView';
import SkillsView from './components/SkillsView';
import CertificationsView from './components/CertificationsView';
import LanguagesView from './components/LanguagesView';
import JsonViewer from './components/JsonViewer';
import ErrorBanner from './components/ErrorBanner';

import { API_BASE_URL } from './config';

export default function App() {
  const [url, setUrl] = useState('');
  const [profileData, setProfileData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('experience');

  const handleSearch = async (targetUrl) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: targetUrl }),
      });


      const data = await res.json();
      if (!res.ok || data.detail) {
        throw new Error(data.detail?.message || data.detail || 'Failed to fetch profile.');
      }

      setProfileData(data);
      if (data.experience && data.experience.length > 0) {
        setActiveTab('experience');
      } else if (data.education && data.education.length > 0) {
        setActiveTab('education');
      } else {
        setActiveTab('json');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while fetching the profile.');
    } finally {
      setIsLoading(false);
    }
  };

  const counts = {
    experience: profileData?.experience?.length || 0,
    education: profileData?.education?.length || 0,
    skills: profileData?.skills?.length || 0,
    certifications: profileData?.certifications?.length || 0,
    languages: profileData?.languages?.length || 0,
  };

  return (
    <div className="container">
      <Header />

      <SearchBar
        url={url}
        setUrl={setUrl}
        onSearch={handleSearch}
        isLoading={isLoading}
      />

      {error && <ErrorBanner message={error} onClose={() => setError(null)} />}

      {profileData && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <ProfileHero data={profileData} />

          <Tabs
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            counts={counts}
          />

          {activeTab === 'experience' && <ExperienceView items={profileData.experience} />}
          {activeTab === 'education' && <EducationView items={profileData.education} />}
          {activeTab === 'skills' && <SkillsView items={profileData.skills} />}
          {activeTab === 'certifications' && <CertificationsView items={profileData.certifications} />}
          {activeTab === 'languages' && <LanguagesView items={profileData.languages} />}
          {activeTab === 'json' && <JsonViewer data={profileData} />}
        </div>
      )}

      {!profileData && !isLoading && !error && (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-dim)' }}>
          <p style={{ fontSize: '0.95rem' }}>
            Enter a LinkedIn profile URL or click one of the suggestions above.
          </p>
        </div>
      )}
    </div>
  );
}
