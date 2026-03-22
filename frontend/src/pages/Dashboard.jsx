import React from 'react'
import { ArrowLeft } from 'lucide-react'
import Header from '../components/Header'
import CountryPanel from '../components/CountryPanel'
import DebateFeed from '../components/DebateFeed'
import ControlPanel from '../components/ControlPanel'
import InsightPanel from '../components/InsightPanel'
import { runDebate } from '../services/api'
import { mockCountries, mockDebateTopic } from '../data/mockData'

const phaseLabels = {
  idle: 'Ready Room',
  loading: 'Initializing Session',
  opening: 'Opening Statements',
  'rebuttal-1': 'Rebuttal One',
  'rebuttal-2': 'Rebuttal Two',
  resolution: 'Draft Resolution',
  voting: 'Voting Bloc',
  vote: 'Voting Bloc',
  judging: 'Judge Review',
  error: 'Attention Needed',
}

const countryVisuals = Object.fromEntries(
  mockCountries.map((country) => [
    country.name,
    {
      flag: country.flag,
      color: country.color,
    },
  ]),
)

const createParticipants = () =>
  mockCountries.map((country, index) => ({
    ...country,
    score: (8.2 + index * 0.2).toFixed(1),
    status: 'waiting',
  }))

function Dashboard({ onBack }) {
  const [currentTopic, setCurrentTopic] = React.useState(mockDebateTopic)
  const [messages, setMessages] = React.useState([])
  const [activeSpeaker, setActiveSpeaker] = React.useState('United States')
  const [currentSpeaker, setCurrentSpeaker] = React.useState('')
  const [isTyping, setIsTyping] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(false)
  const [error, setError] = React.useState(null)
  const [phase, setPhase] = React.useState('idle')
  const [verdict, setVerdict] = React.useState(null)
  const [resolution, setResolution] = React.useState('')
  const [participants, setParticipants] = React.useState(createParticipants)
  const timeoutsRef = React.useRef([])

  const clearStreamingTimeouts = React.useCallback(() => {
    timeoutsRef.current.forEach((timeoutId) => clearTimeout(timeoutId))
    timeoutsRef.current = []
  }, [])

  React.useEffect(() => clearStreamingTimeouts, [clearStreamingTimeouts])

  const updateParticipantStatus = React.useCallback((speaker, spokenSet) => {
    setParticipants((prev) =>
      prev.map((country) => {
        if (country.name === speaker) {
          return { ...country, status: 'speaking' }
        }

        if (spokenSet.has(country.name)) {
          return { ...country, status: 'active' }
        }

        return { ...country, status: 'waiting' }
      }),
    )
  }, [])

  const parseVerdict = (judgeMessage) => {
    if (!judgeMessage?.content) {
      return null
    }

    try {
      return JSON.parse(judgeMessage.content)
    } catch {
      return {
        winner: judgeMessage.agent || 'Judge',
        reasoning: judgeMessage.content,
      }
    }
  }

  const transformMessage = (msg, index) => {
    const visuals = countryVisuals[msg.agent] || {}
    const role = msg.phase || msg.role

    return {
      id: `${role}-${index}-${msg.agent || msg.country || 'delegate'}`,
      country: msg.country || msg.agent,
      flag: msg.flag || visuals.flag || '🌐',
      color: msg.color || visuals.color || '#22d3ee',
      text: msg.content,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      round: msg.round || index + 1,
      role,
      agent: msg.agent,
    }
  }

  const simulateStreaming = React.useCallback(
    (history, finalState) => {
      clearStreamingTimeouts()
      setMessages([])
      setCurrentSpeaker('')
      setIsTyping(false)

      const spoken = new Set()
      const judgeMessage = history.find((item) => item.role === 'judging')
      const resolutionMessage = history.find((item) => item.role === 'resolution')
      const parsedVerdict = parseVerdict(judgeMessage)
      const moderatorConclusion = finalState?.resolution || resolutionMessage?.content || ''
      let elapsed = 0

      history.forEach((rawMessage, index) => {
        const message = transformMessage(rawMessage, index)
        const displayPhase = message.role === 'vote' ? 'voting' : message.role
        const typingDuration = Math.min(2200, Math.max(900, Math.ceil(message.text.length * 12)))
        const phaseDelay = index === 0 || history[index - 1].role !== message.role ? 300 : 0

        elapsed += phaseDelay

        const typingTimeout = window.setTimeout(() => {
          setPhase(displayPhase)
          setCurrentSpeaker(message.country)
          setActiveSpeaker(message.country)
          setIsTyping(true)

          if (!['Moderator', 'Judge'].includes(message.country)) {
            spoken.add(message.country)
          }

          updateParticipantStatus(message.country, spoken)
        }, elapsed)

        timeoutsRef.current.push(typingTimeout)
        elapsed += typingDuration

        const messageTimeout = window.setTimeout(() => {
          setMessages((prev) => [...prev, message])
          setIsTyping(false)

          if (message.role === 'resolution') {
            setResolution(message.text)
          }

          if (message.role === 'judging') {
            setVerdict(parsedVerdict)
          }
        }, elapsed)

        timeoutsRef.current.push(messageTimeout)
        elapsed += 450
      })

      const finishTimeout = window.setTimeout(() => {
        if (moderatorConclusion) {
          setResolution(moderatorConclusion)
        }

        if (parsedVerdict) {
          setVerdict(parsedVerdict)
        }

        setCurrentSpeaker('')
        setIsTyping(false)
        setActiveSpeaker('')
        setParticipants((prev) =>
          prev.map((country) => ({
            ...country,
            status: spoken.has(country.name) ? 'active' : 'waiting',
          })),
        )
        setPhase('judging')
        setIsLoading(false)
      }, elapsed + 250)

      timeoutsRef.current.push(finishTimeout)
    },
    [clearStreamingTimeouts, updateParticipantStatus],
  )

  const handleStartDebate = async (topic) => {
    if (!topic.trim()) {
      setError('Topic cannot be empty.')
      return
    }

    clearStreamingTimeouts()
    setIsLoading(true)
    setPhase('loading')
    setError(null)
    setMessages([])
    setVerdict(null)
    setResolution('')
    setCurrentSpeaker('')
    setIsTyping(false)
    setActiveSpeaker('')
    setParticipants(createParticipants())

    try {
      const response = await runDebate(topic, mockCountries.map((country) => country.name))

      if (!response.history || !Array.isArray(response.history)) {
        throw new Error('No debate history returned by the API.')
      }

      setCurrentTopic(topic)
      simulateStreaming(response.history, response.final_state)
    } catch (err) {
      setError(`Failed to start debate: ${err.message}`)
      setPhase('error')
      setIsLoading(false)
      setIsTyping(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 px-4 py-4 text-gray-200 sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-2rem)] max-w-[1600px] flex-col rounded-[2rem] border border-white/10 bg-slate-950/90 shadow-panel">
        <Header topic={currentTopic} phase={phaseLabels[phase] || phase} />

        <div className="border-b border-white/10 px-6 py-4 sm:px-8">
          <button
            onClick={onBack}
            className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-medium text-slate-300 backdrop-blur-xl transition duration-300 hover:scale-[1.02] hover:border-cyan-400/30 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to landing
          </button>
        </div>

        <main className="flex flex-1 flex-col gap-6 overflow-y-auto p-4 sm:p-6 lg:p-8">
          {error ? (
            <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-5 py-4 text-sm text-rose-100">
              {error}
            </div>
          ) : null}

          <div className="shrink-0">
            <ControlPanel onStartDebate={handleStartDebate} isLoading={isLoading} />
          </div>

          <div className="grid grid-cols-12 items-start gap-6 xl:grid-rows-[minmax(0,1fr)]">
            <div className="col-span-12 min-h-0 xl:col-span-3">
              <CountryPanel countries={participants} activeSpeaker={activeSpeaker || currentSpeaker} />
            </div>

            <div className="col-span-12 min-h-0 xl:col-span-6">
              <DebateFeed
                messages={messages}
                isLoading={isLoading}
                isTyping={isTyping}
                currentSpeaker={currentSpeaker}
                phase={phase}
              />
            </div>

            <div className="col-span-12 min-h-0 xl:col-span-3">
              <InsightPanel phase={phase} verdict={verdict} resolution={resolution} />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default Dashboard
