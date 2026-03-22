import React from 'react';
import './InsightPanel.css';

const InsightPanel = ({ phase = 'idle', votes = {}, verdict = null }) => {
  const phaseLabels = {
    'idle': '🎯 Ready',
    'loading': '⏳ Loading',
    'opening': '🎤 Opening',
    'rebuttal-1': '🔄 Rebuttal 1',
    'rebuttal-2': '🔄 Rebuttal 2',
    'resolution': '📋 Resolution',
    'voting': '🗳️ Voting',
    'judging': '⚖️ Judging',
    'error': '❌ Error'
  };

  const isJudgingPhase = phase === 'judging';
  const isVotingOrAfter = ['voting', 'judging'].includes(phase);

  return (
    <div className="insight-panel">
      {/* Phase Status Card */}
      <div className="insight-card glass-card">
        <div className="card-header">
          <h4 className="card-title">📍 Current Phase</h4>
        </div>
        <div className="phase-status">
          <div className="phase-badge">
            {phaseLabels[phase] || phase}
          </div>
          <p className="phase-description">
            {phase === 'idle' && 'Ready to start debate'}
            {phase === 'loading' && 'Initializing agents...'}
            {phase === 'opening' && 'Countries present opening statements'}
            {phase === 'rebuttal-1' && 'First rebuttal round in progress'}
            {phase === 'rebuttal-2' && 'Second rebuttal round in progress'}
            {phase === 'resolution' && 'Moderator synthesizing positions'}
            {phase === 'voting' && 'Countries casting votes'}
            {phase === 'judging' && 'Final judgment complete'}
          </p>
        </div>
      </div>

      {/* Votes Card - Only show from voting phase onwards */}
      {isVotingOrAfter && (
        <div className="insight-card glass-card">
          <div className="card-header">
            <h4 className="card-title">🗳️ Votes</h4>
          </div>
          <div className="votes-container">
            {Object.entries(votes).length > 0 ? (
              Object.entries(votes).map(([position, count], idx) => (
                <div key={idx} className="vote-item">
                  <div className="vote-info">
                    <p className="vote-label">{position}</p>
                    <p className="vote-count">{count}</p>
                  </div>
                  <div className="vote-bar">
                    <div
                      className="vote-fill"
                      style={{ width: `${(count / 5) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))
            ) : (
              <p className="empty-votes">Tabulating votes...</p>
            )}
          </div>
        </div>
      )}

      {/* Judge Verdict Card - Only show in judging phase */}
      {isJudgingPhase && (
        <div className="insight-card glass-card">
          <div className="card-header">
            <h4 className="card-title">⚖️ Final Verdict</h4>
          </div>
          <div className="verdict-content">
            {verdict && verdict.winner ? (
              <>
                <p className="verdict-text">
                  {verdict.reasoning || 'Debate concluded with balanced perspectives.'}
                </p>
                <div className="verdict-highlight">
                  <p className="verdict-label">Winner</p>
                  <p className="verdict-outcome">{verdict.winner}</p>
                </div>
              </>
            ) : (
              <>
                <p className="verdict-text">
                  Debate concluded with balanced perspectives across all participants.
                </p>
                <div className="verdict-highlight">
                  <p className="verdict-label">Key Outcome</p>
                  <p className="verdict-outcome">
                    Collaborative approach with mutual understanding
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Waiting Message for other phases */}
      {!isVotingOrAfter && phase !== 'idle' && (
        <div className="insight-card glass-card waiting-message">
          <div className="card-header">
            <h4 className="card-title">⏳ Debate in Progress</h4>
          </div>
          <p className="waiting-text">
            Results and verdicts will appear when voting phase begins.
          </p>
        </div>
      )}

      {/* Ready Message for idle */}
      {phase === 'idle' && (
        <div className="insight-card glass-card ready-message">
          <div className="card-header">
            <h4 className="card-title">🚀 Ready to Start</h4>
          </div>
          <p className="ready-text">
            Enter a debate topic and select participants to begin.
          </p>
        </div>
      )}
    </div>
  );
};

export default InsightPanel;
