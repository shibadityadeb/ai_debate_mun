import React from 'react'
import { Mic2, TimerReset, Users2 } from 'lucide-react'
import { GlassPanel, cn } from './ui'

const statusStyles = {
  speaking: {
    ring: 'border-cyan-400/40 bg-cyan-400/10',
    dot: 'bg-cyan-300',
    label: 'Speaking now',
  },
  active: {
    ring: 'border-blue-400/30 bg-blue-500/10',
    dot: 'bg-blue-300',
    label: 'Engaged',
  },
  waiting: {
    ring: 'border-white/10 bg-white/5',
    dot: 'bg-slate-500',
    label: 'Queued',
  },
}

const CountryPanel = ({ countries, activeSpeaker }) => {
  return (
    <GlassPanel className="flex h-full min-h-0 flex-col overflow-hidden p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Country Panel</p>
          <h2 className="mt-2 text-xl font-semibold text-white">Delegation roster</h2>
        </div>
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/5 text-cyan-300">
          <Users2 className="h-5 w-5" />
        </div>
      </div>

      <div className="mt-6 min-h-0 flex-1 space-y-3 overflow-y-auto pr-2 [scrollbar-color:rgba(148,163,184,0.45)_transparent] [scrollbar-width:thin]">
        {countries.map((country) => {
          const style = statusStyles[country.status] || statusStyles.waiting
          const isActiveSpeaker = country.name === activeSpeaker

          return (
            <div
              key={country.id}
              className={cn(
                'rounded-[1.5rem] border p-4 transition duration-300 hover:scale-[1.01] hover:border-cyan-400/30',
                style.ring,
                isActiveSpeaker && 'shadow-glow',
              )}
            >
              <div className="flex items-center gap-3">
                <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950/80 text-2xl">
                  <span>{country.flag}</span>
                  <span
                    className={cn(
                      'absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full ring-4 ring-slate-900',
                      style.dot,
                    )}
                  />
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-3">
                    <p className="truncate font-semibold text-white">{country.name}</p>
                    <span className="text-sm font-semibold text-slate-200">{country.score}</span>
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-slate-400">
                    {country.status === 'speaking' ? <Mic2 className="h-3.5 w-3.5" /> : <TimerReset className="h-3.5 w-3.5" />}
                    <span>{style.label}</span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </GlassPanel>
  )
}

export default CountryPanel
