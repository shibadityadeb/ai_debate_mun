import React from 'react'
import Landing from './Landing'
import Dashboard from './pages/Dashboard'

function App() {
  const [view, setView] = React.useState('landing')

  return view === 'landing' ? (
    <Landing onStart={() => setView('dashboard')} />
  ) : (
    <Dashboard onBack={() => setView('landing')} />
  )
}

export default App
