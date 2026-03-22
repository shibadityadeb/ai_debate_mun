import React, { useState } from 'react';
import Header from './Header';
import CountryPanel from './CountryPanel';
import DebateFeed from './DebateFeed';
import ControlPanel from './ControlPanel';
import InsightPanel from './InsightPanel';
import { runDebate } from '../services/api';
import {
  mockDebateTopic,
  mockCountries,
} from '../data/mockData';
import './Dashboard.css';

const Dashboard = () => {
  const [currentTopic, setCurrentTopic] = useState(mockDebateTopic);
  const [messages, setMessages] = useState([]);
  const [activeSpeaker, setActiveSpeaker] = useState('United States');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [phase, setPhase] = useState('idle');
  const [votes, setVotes] = useState({ yes: 0, no: 0, abstain: 0 });
  const [verdict, setVerdictData] = useState(null);
  const [participants, setParticipants] = useState(() => 
    mockCountries.map(c => ({ ...c, status: 'waiting' }))
  );
  const [spokenCountries, setSpokenCountries] = useState(new Set());

  const phases = ['opening', 'rebuttal-1', 'rebuttal-2', 'resolution', 'voting', 'judging'];
  const phaseLabels = {
    'idle': 'Ready',
    'loading': 'Loading...',
    'opening': 'Opening Statements',
    'rebuttal-1': 'First Rebuttal',
    'rebuttal-2': 'Second Rebuttal',
    'resolution': 'Resolution',
    'voting': 'Voting Round',
    'judging': 'Final Judgment'
  };

  // Update participant status based on speaking state
  const updateParticipantStatus = (speaker, spoken) => {
    setParticipants(prevParticipants => 
      prevParticipants.map(country => {
        if (country.name === speaker) {
          return { ...country, status: 'speaking' };
        } else if (spoken.has(country.name)) {
          return { ...country, status: 'active' };
        } else {
          return { ...country, status: 'waiting' };
        }
      })
    );
  };

  const handleStartDebate = async (topic) => {
    if (!topic.trim()) {
      setError('Topic cannot be empty');
      return;
    }

    setIsLoading(true);
    setPhase('loading');
    setError(null);
    setMessages([]);
    setActiveSpeaker('');
    setVotes({ yes: 0, no: 0, abstain: 0 });
    setVerdictData(null);
    setSpokenCountries(new Set());
    setParticipants(mockCountries.map(c => ({ ...c, status: 'waiting' })));

    try {
      console.log('📡 Calling API with topic:', topic);
      
      // Call backend API with selected countries
      const response = await runDebate(topic, mockCountries.map(c => c.name));

      console.log('✅ API Response:', response);

      // Generate messages with streaming simulation
      if (response.history && Array.isArray(response.history)) {
        // Extract judge verdict if available
        const judgeMessage = response.history.find(msg => msg.role === 'judging');
        if (judgeMessage && judgeMessage.content) {
          try {
            const verdictData = JSON.parse(judgeMessage.content);
            setVerdictData(verdictData);
          } catch (e) {
            console.warn('Could not parse judge verdict:', e);
          }
        }
        simulateDebateRounds(response.history, response.final_state);
        setCurrentTopic(topic);
      }
    } catch (err) {
      console.error('❌ API Error:', err.message);
      setError(`Failed to start debate: ${err.message}`);
      setPhase('error');
      setIsLoading(false);
    }
  };

  const simulateDebateRounds = (history, finalState) => {
    setPhase('opening');
    setMessages([]);

    // Group messages by phase
    const messagesByPhase = {};
    history.forEach((msg) => {
      const ph = msg.phase || msg.role;
      if (!messagesByPhase[ph]) {
        messagesByPhase[ph] = [];
      }
      messagesByPhase[ph].push(msg);
    });

    // Stream messages with delays (1.2 seconds per message)
    let totalDelay = 0;
    const delayPerMessage = 1200;

    phases.forEach((ph) => {
      const phaseMessages = messagesByPhase[ph] || [];
      
      if (phaseMessages.length > 0) {
        totalDelay += 500; // Phase transition delay

        // Add phase indicator
        setTimeout(() => {
          console.log(`🎭 Phase: ${ph}`);
          setPhase(ph);
        }, totalDelay);

        // Stream messages in this phase
        phaseMessages.forEach((msg, idx) => {
          totalDelay += delayPerMessage;
          
          setTimeout(() => {
            console.log(`💬 [${ph}] ${msg.agent}: ${msg.content.substring(0, 50)}...`);
            
            // Transform message format
            const transformedMsg = {
              id: Math.random(),
              country: msg.country || msg.agent,
              flag: msg.flag || '🌍',
              color: msg.color || '#38bdf8',
              text: msg.content,
              timestamp: new Date().toLocaleTimeString(),
              round: msg.round || 1,
              role: msg.role || ph,
              agent: msg.agent
            };
            
            setMessages((prev) => [...prev, transformedMsg]);
            setActiveSpeaker(msg.agent || '');
            
            // Update spoken countries and participant status
            setSpokenCountries((prevSpoken) => {
              const updated = new Set(prevSpoken);
              if (msg.agent && msg.agent !== 'Moderator' && msg.agent !== 'Judge') {
                updated.add(msg.agent);
              }
              updateParticipantStatus(msg.agent, updated);
              return updated;
            });
          }, totalDelay);
        });
      }
    });

    // Process and display final state
    if (finalState) {
      totalDelay += delayPerMessage;
      
      setTimeout(() => {
        console.log('✅ Debate Complete:', finalState);
        if (finalState.votes) {
          setVotes(finalState.votes);
        }
        // Keep participants in their final active state
        setParticipants(prevParticipants => 
          prevParticipants.map(country => ({
            ...country,
            status: spokenCountries.has(country.name) ? 'active' : 'waiting'
          }))
        );
        setPhase('judging');
        setIsLoading(false);
      }, totalDelay);
    }
  };

  return (
    <div className="dashboard">
      <Header topic={currentTopic} phase={phaseLabels[phase] || phase} />

      <main className="dashboard-main">
        {/* Error Alert */}
        {error && (
          <div className="error-alert">
            <span className="error-icon">⚠️</span>
            <p className="error-message">{error}</p>
            <button className="error-close" onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <div className="dashboard-container">
          {/* Left Sidebar */}
          <aside className="dashboard-sidebar-left">
            <CountryPanel countries={participants} activeSpeaker={activeSpeaker} />
          </aside>

          {/* Center Content */}
          <section className="dashboard-center">
            <DebateFeed messages={messages} isLoading={isLoading} phase={phase} />
          </section>

          {/* Right Sidebar */}
          <aside className="dashboard-sidebar-right">
            <InsightPanel
              phase={phase}
              votes={votes}
              verdict={verdict}
            />
          </aside>
        </div>

        {/* Bottom Control Panel */}
        <div className="dashboard-controls">
          <ControlPanel onStartDebate={handleStartDebate} isLoading={isLoading} />
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
