import React, { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useDropzone } from 'react-dropzone';
import { extractData, refineData, addChatMessage } from '../redux/complaintSlice';
import { UploadCloud, FileText, Send, Bot } from 'lucide-react';

export default function AiAssistant() {
  const dispatch = useDispatch();
  const { status, progress, chatHistory } = useSelector((state) => state.complaint);
  const [pasteText, setPasteText] = useState('');
  const [chatInput, setChatInput] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      dispatch(extractData({ file: acceptedFiles[0] }));
    }
  }, [dispatch]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, maxFiles: 1 });

  const handlePasteSubmit = () => {
    if (pasteText.trim()) {
      dispatch(extractData({ text: pasteText }));
      setPasteText('');
    }
  };

  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    dispatch(addChatMessage({ role: 'user', text: chatInput }));
    dispatch(refineData({ prompt: chatInput }));
    setChatInput('');
  };

  return (
    <div className="bg-blue-50/50 p-6 rounded-lg shadow-sm border border-blue-100 flex flex-col h-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
          <Bot className="text-blue-600" size={24} /> AI Copilot Intake
        </h2>
      </div>

      <div className="space-y-4 flex-none">
        <div {...getRootProps()} className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors bg-white
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}>
          <input {...getInputProps()} />
          <UploadCloud className="mx-auto text-gray-400 mb-2" size={32} />
          <p className="text-sm font-medium text-gray-600">Drag & drop complaint document here</p>
          <p className="text-xs text-gray-400 mt-1">PDF, DOCX, TXT, EML</p>
        </div>

        <div className="text-center text-xs text-gray-400 font-semibold uppercase">OR</div>

        <div className="relative">
          <textarea 
            className="w-full text-sm border-gray-300 rounded-lg p-3 border shadow-sm focus:border-blue-500 focus:ring-blue-500" 
            rows="3" 
            placeholder="Paste Complaint Text here..."
            value={pasteText}
            onChange={(e) => setPasteText(e.target.value)}
          />
          <button 
            onClick={handlePasteSubmit}
            className="absolute bottom-3 right-3 bg-blue-100 text-blue-700 p-1.5 rounded-md hover:bg-blue-200"
          >
            <FileText size={16} />
          </button>
        </div>

        {status === 'loading' && (
          <div className="mt-4">
            <div className="flex justify-between text-xs font-semibold text-gray-600 mb-1">
              <span>EXTRACTION PROGRESS</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto my-6 space-y-4 bg-white border border-gray-200 rounded-lg p-4">
        {chatHistory.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`text-sm p-3 rounded-lg max-w-[85%] shadow-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-800'}`}>
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleChatSubmit} className="relative flex-none">
        <input 
          type="text" 
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder="Ask AI to update form fields..." 
          className="w-full pl-4 pr-12 py-3 rounded-full border border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
        />
        <button type="submit" className="absolute right-2 top-2 bg-blue-600 text-white p-1.5 rounded-full hover:bg-blue-700">
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}