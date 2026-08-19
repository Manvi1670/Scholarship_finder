// src/pages/ScholarshipDetailPage.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './ScholarshipDetailPage.css';

const ScholarshipDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [scholarship, setScholarship] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchScholarshipDetails = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/scholarship/${id}`);
        const rawData = await response.json();

        if (!response.ok) {
          throw new Error(rawData.message || 'Failed to fetch scholarship details');
        }

        // /scholarship/:id returns an array (Scholarship.find({_id: id})) - take the first match
        const data = Array.isArray(rawData) ? rawData[0] : rawData;
        if (!data) {
          throw new Error('Scholarship not found');
        }

        setScholarship(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchScholarshipDetails();
  }, [id]);

  const handleBackClick = () => {
    navigate(-1);
  };

  const handleApplyClick = () => {
    // Not every scholarship had a direct external apply link scraped - fall
    // back to the original listing page so there's always somewhere useful
    // to go, instead of a dead end.
    const link = scholarship.applyLink || scholarship.sourceUrl;
    if (link) {
      window.open(link, '_blank');
    }
  };

  if (loading) {
    return <div className="loading">Loading scholarship details...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!scholarship) {
    return <div className="not-found">Scholarship not found</div>;
  }

  // scholarship.deadline is a real parsed date (or null for "Always Open"/
  // unparseable ones) - deadlineRaw is always the original text to fall back to.
  const hasParsedDeadline = Boolean(scholarship.deadline);
  const deadlineDate = hasParsedDeadline ? new Date(scholarship.deadline) : null;
  const diffDays = hasParsedDeadline
    ? Math.ceil((deadlineDate - new Date()) / (1000 * 60 * 60 * 24))
    : null;
  const isClosed = (scholarship.deadlineRaw || '').toLowerCase() === 'closed';

  return (
    <div className="scholarship-detail-container">
      <button onClick={handleBackClick} className="back-button">
        &larr; Back to Scholarships
      </button>

      <div className="scholarship-header">
        <h1>{scholarship.name}</h1>
        <div className="scholarship-meta">
          <span className="amount-badge">
            {scholarship.awardCategory} Funding
          </span>
          <span className="deadline">
            Deadline: {hasParsedDeadline
              ? `${deadlineDate.toLocaleDateString()}${diffDays > 0 ? ` (${diffDays} days left)` : ''}`
              : (scholarship.deadlineRaw || 'Not specified')}
          </span>
        </div>
      </div>

      <div className="scholarship-content">
        <div className="main-content">
          <div className="section">
            <h2>Description</h2>
            <p>{scholarship.description}</p>
          </div>

          <div className="section">
            <h2>Eligibility Criteria</h2>
            <ul>
              <li><strong>{scholarship.eligibilityRaw}</strong></li>
              <li><strong>Location:</strong> {scholarship.region || 'Not specified'}</li>
              {scholarship.minCPI && (
                <li><strong>Minimum CPI:</strong> {scholarship.minCPI}</li>
              )}
            </ul>
          </div>

          <div className="section">
            <h2>Benefits</h2>
            <p>{scholarship.awardRaw}</p>
          </div>

          <div className="sidebar">
            <div className="sidebar-section">
              <h3>Quick Facts</h3>
              <ul>
                <li><strong>Funding Type:</strong> {scholarship.awardCategory}</li>
              </ul>
            </div>

            <div className="sidebar-section">
              <h3>Contact Information</h3>
              {scholarship.contactEmail && <p>Email: {scholarship.contactEmail}</p>}
              {scholarship.contactPhone && <p>Phone: {scholarship.contactPhone}</p>}
              {!scholarship.contactEmail && !scholarship.contactPhone && <p>Not available</p>}
            </div>

            <button
              onClick={handleApplyClick}
              className="apply-button"
              disabled={isClosed || (!scholarship.applyLink && !scholarship.sourceUrl)}
            >
              {isClosed
                ? 'Application Closed'
                : scholarship.applyLink
                  ? 'Apply Now'
                  : scholarship.sourceUrl
                    ? 'View Scholarship Page'
                    : 'No Link Available'}
            </button>

            {isClosed && (
              <p className="expired-notice">This scholarship deadline has passed.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScholarshipDetailPage;