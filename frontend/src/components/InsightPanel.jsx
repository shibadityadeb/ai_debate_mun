import React from 'react'
import { BarChart3, Gavel } from 'lucide-react'
import { GlassPanel } from './ui'

const phaseDescriptions = {
  idle: 'Ready to brief delegates and launch the next moderated session.',
  loading: 'Building country context, strategy cards, and opening position summaries.',
  opening: 'Opening speeches are entering the chamber with primary policy framing.',
  'rebuttal-1': 'Delegates are testing each other’s claims and probing weak assumptions.',
  'rebuttal-2': 'Counter-positioning is escalating as blocs refine coalition strategy.',
  resolution: 'Key motions and compromise language are being synthesized.',
  voting: 'Delegates are aligning around the moderator-led draft resolution.',
  judging: 'Judge analysis is complete with winner selection and reasoning.',
  error: 'The room needs attention before the next simulation can proceed.',
}

const InsightPanel = ({ phase = 'idle', verdict = null, resolution = '' }) => {
  return (
    <div className="flex h-full min-h-0 flex-col gap-5 overflow-y-auto pr-2 [scrollbar-color:rgba(148,163,184,0.45)_transparent] [scrollbar-width:thin]">
      <GlassPanel className="p-5">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-cyan-400/10 p-3 text-cyan-300">
            <BarChart3 className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Insights</p>
            <h2 className="mt-1 text-xl font-semibold text-white">Live room telemetry</h2>
          </div>
        </div>

        <div className="mt-5 rounded-[1.5rem] border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Current phase</p>
          <p className="mt-2 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-2xl font-bold capitalize text-transparent">
            {phase}
          </p>
          <p className="mt-3 text-sm leading-6 text-slate-300">{phaseDescriptions[phase] || phaseDescriptions.idle}</p>
        </div>
      </GlassPanel>

      <GlassPanel className="p-5">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-blue-500/10 p-3 text-blue-300">
            <Gavel className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Moderator Verdict</p>
            <h3 className="mt-1 text-lg font-semibold text-white">Final committee conclusion</h3>
          </div>
        </div>

        <div className="mt-5 rounded-[1.5rem] border border-white/10 bg-slate-900 p-4">
          <p className="text-sm leading-6 text-slate-300">
            {resolution || 'The moderator conclusion will appear here once the draft resolution is finalized.'}
          </p>
        </div>
      </GlassPanel>

      <GlassPanel className="p-5">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-cyan-400/10 p-3 text-cyan-300">
            <Gavel className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Judge Result</p>
            <h3 className="mt-1 text-lg font-semibold text-white">Verdict summary</h3>
          </div>
        </div>

        <div className="mt-5 rounded-[1.5rem] border border-white/10 bg-white/5 p-4">
          <p className="text-sm leading-6 text-slate-300">
            {verdict?.reasoning || 'The judge panel will publish the winner and final rationale after deliberation.'}
          </p>
          <div className="mt-4 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3">
            <p className="text-xs uppercase tracking-[0.24em] text-cyan-200">Top outcome</p>
            <p className="mt-2 text-base font-semibold text-white">
              {verdict?.winner || 'Pending final committee judgment'}
            </p>
          </div>
        </div>
      </GlassPanel>
    </div>
  )
}

export default InsightPanel
