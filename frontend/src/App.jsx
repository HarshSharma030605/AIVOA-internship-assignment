import React from 'react';
import ComplaintForm from './components/ComplaintForm';
import AiAssistant from './components/AiAssistant';

function App() {
  return (
    <div className="min-h-screen p-4 md:p-6 bg-slate-50 text-slate-900 flex flex-col">
      
      {/* App Header Bar */}
      <header className="max-w-[1600px] w-full mx-auto mb-4 pb-4 border-b border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 bg-white px-6 py-4 rounded-2xl shadow-sm">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 flex items-center gap-2.5">
            <span className="w-3 h-3 rounded-full bg-sky-500 shadow-[0_0_10px_rgba(14,165,233,0.4)]"></span>
            Aivoa Pharma QMS Engine
          </h1>
          <p className="text-xs text-slate-500">Intelligent Complaint Management & Regulatory Triage System</p>
        </div>
        <div className="text-xs font-mono text-slate-600 bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200 flex items-center gap-2">
          <span>Environment:</span>
          <span className="text-emerald-600 font-semibold flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Active
          </span>
        </div>
      </header>

      {/* Main Split Layout: QMS Form on the Left, AI Assistant on the Right */}
      <main className="max-w-[1600px] w-full mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 items-start">
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-2">
          <ComplaintForm />
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-2">
          <AiAssistant />
        </div>
      </main>

    </div>
  );
}

export default App;