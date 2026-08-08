// src/pages/HomePage.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  const navigate = useNavigate();
  const [scholarships, setScholarships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filteredScholarships, setFilteredScholarships] = useState([]);
  const [filter, setFilter] = useState({
    category: '',
    deadline: '',
    search: '',
    eligibilitySearch: ''
  });

  useEffect(() => {
    const jwtoken = localStorage.getItem('jwtoken');
    if (!jwtoken) {
      navigate('/login');
    }
  });

  useEffect(() => {
    const fetchScholarships = async () => {
      const jwtoken = localStorage.getItem('jwtoken');
      if (!jwtoken) return;

      try {
        // /scholarships/match returns results already ranked by relevance
        // to this student's profile (course/cpi/region), not just a raw list.
        const response = await fetch('http://localhost:3000/scholarships/match', {
          headers: { Authorization: `Bearer ${jwtoken}` }
        });
        if (!response.ok) {
          throw new Error(`Server returned ${response.status}`);
        }
        const data = await response.json();
        setScholarships(data);
        setFilteredScholarships(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching scholarships:', err);
        setError('Could not load scholarships. Is the backend running?');
        setLoading(false);
      }
    };

    fetchScholarships();
  }, []);

  useEffect(() => {
    const applyFilters = () => {
      let filtered = scholarships;

      if (filter.category) {
        filtered = filtered.filter(s => s.awardCategory === filter.category);
      }

      if (filter.deadline === 'always-open') {
        filtered = filtered.filter(s => (s.deadlineRaw || '').toLowerCase() === 'always open');
      } else if (filter.deadline) {
        const daysMap = { week: 7, month: 30, 'six-months': 182 };
        const days = daysMap[filter.deadline];
        if (days) {
          const cutoff = new Date();
          cutoff.setDate(cutoff.getDate() + days);
          // only scholarships with a real, parsed deadline within the window -
          // "Always Open"/unparseable ones have deadline: null and are excluded here
          filtered = filtered.filter(s => s.deadline && new Date(s.deadline) <= cutoff);
        }
      }

      if (filter.search !== '') {
        const q = filter.search.toLowerCase();
        filtered = filtered.filter(s =>
          (s.name || '').toLowerCase().includes(q) ||
          (s.description || '').toLowerCase().includes(q)
        );
      }

      if (filter.eligibilitySearch !== '') {
        const q = filter.eligibilitySearch.toLowerCase();
        filtered = filtered.filter(s => (s.eligibilityRaw || '').toLowerCase().includes(q));
      }

      setFilteredScholarships(filtered);
    };

    applyFilters();
  }, [filter, scholarships]);

  const handleScholarshipClick = (id) => {
    navigate(`/scholarship/${id}`);
  };

  const urgentDeadlines = scholarships.filter(s => {
    if (!s.deadline) return false;
    const oneWeek = new Date();
    oneWeek.setDate(oneWeek.getDate() + 7);
    return new Date(s.deadline) <= oneWeek;
  });

  // Turns a matchBreakdown into short human-readable tags, e.g. "Matches your course"
  const matchTags = (breakdown) => {
    if (!breakdown) return [];
    const tags = [];
    if (breakdown.courseScore > 0) tags.push('Matches your course');
    if (breakdown.regionScore > 0) tags.push('Matches your region');
    if (breakdown.cpiScore >= 15) tags.push('Meets CPI requirement');
    if (breakdown.amountScore >= 12) tags.push('High-value award');
    return tags;
  };

  return (
    <div className="home-page">
      <div className="home-container">
        <header className="home-header">
          <h1 className='heading1'>Unlock Your Best Scholarship Match</h1>
          <div className="urgent-notifications">
            {urgentDeadlines.length > 0 && (
              <div className="urgent-alert">
                <span>⚠️</span> {urgentDeadlines.length} scholarships with approaching deadlines!
              </div>
            )}
          </div>
        </header>

        <div className="filter-section">
          <h2>Filters</h2>
          <div className="filter-grid">
            <div className="filter-group">
              <label htmlFor="category">Category:</label>
              <select onChange={(e) => setFilter({ ...filter, category: e.target.value })} id="category" name="category">
                <option value="">All Categories</option>
                <option value="monetary">Monetary</option>
                <option value="tuition_waiver">Tuition Waiver</option>
                <option value="mixed">Mixed</option>
                <option value="non_monetary">Non-monetary</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="filter-group">
              <label htmlFor="deadline">Deadline:</label>
              <select onChange={(e) => setFilter({ ...filter, deadline: e.target.value })} id="deadline" name="deadline">
                <option value="">All</option>
                <option value="week">Week</option>
                <option value="month">Month</option>
                <option value="six-months">Six Months</option>
                <option value="always-open">Always Open</option>
              </select>
            </div>
            <div className='filter-group'>
              <label>Search:</label>
              <input
                placeholder='Search Anything'
                type='text'
                onChange={(e) => setFilter({ ...filter, search: e.target.value })}
              />
            </div>
            <div className='filter-group'>
              <label>Eligibility Search:</label>
              <input
                placeholder='Eg: Undergraduate, PhD, etc.'
                type='text'
                onChange={(e) => setFilter({ ...filter, eligibilitySearch: e.target.value })}
              />
            </div>
          </div>
        </div>

        <div className="scholarships-list">
          {loading ? (
            <div className="loading">Loading scholarships...</div>
          ) : error ? (
            <div className="no-results">{error}</div>
          ) : filteredScholarships.length === 0 ? (
            <div className="no-results">No scholarships match your filters.</div>
          ) : (
            filteredScholarships.map(scholarship => (
              <div
                key={scholarship._id}
                className="scholarship-card"
                onClick={() => handleScholarshipClick(scholarship._id)}
              >
                <h3>{scholarship.name}</h3>
                <div className="scholarship-details">
                  <span className="amount-badge">
                    {scholarship.awardCategory}
                  </span>
                  <span>Deadline: {scholarship.deadlineRaw || 'Not specified'}</span>
                  {typeof scholarship.matchScore === 'number' && (
                    <span className="match-score-badge">Match score: {scholarship.matchScore}</span>
                  )}
                </div>
                <p className="description">{scholarship.awardRaw}</p>
                <div className="eligibility">
                  <span>Eligibility: {scholarship.eligibilityRaw || 'Not specified'}</span>
                  <span>Region: {scholarship.region || 'Not specified'}</span>
                </div>
                {matchTags(scholarship.matchBreakdown).length > 0 && (
                  <div className="match-tags">
                    {matchTags(scholarship.matchBreakdown).map(tag => (
                      <span key={tag} className="match-tag">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage;