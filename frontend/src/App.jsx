import React from 'react';
import ComplaintForm from './components/ComplaintForm';
import AiAssistant from './components/AiAssistant';

function App() {
  return (
    <div className="min-h-screen p-4 md:p-8 bg-slate-50">
      {/* Layout: QMS Form on the Left, AI Assistant on the Right */}
      <div className="max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-4rem)]">
        <ComplaintForm />
        <AiAssistant />
      </div>
    </div>
  );
}

export default App;