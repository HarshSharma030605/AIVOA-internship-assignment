import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000/api';

const initialState = {
  formData: {
    complaint_source: '', customer_name: '',
    product_name: '', batch_number: '', manufacturing_date: '', expiry_date: '', quantity_affected: '',
    complaint_type: '', complaint_date: '', detailed_description: '',
    initial_severity: '', priority: '', ai_risk_verdict: ''
  },
  status: 'idle',
  chatHistory: [{ role: 'ai', text: 'Upload a complaint document or paste text above. I will automatically extract the details and populate the QMS form.' }],
  progress: 0,
};

export const extractData = createAsyncThunk('complaint/extract', async (payload) => {
  const formData = new FormData();
  if (payload.file) formData.append('file', payload.file);
  if (payload.text) formData.append('text', payload.text);
  
  const response = await axios.post(`${API_BASE}/extract`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
});

export const refineData = createAsyncThunk('complaint/refine', async (payload, { getState }) => {
  const currentState = getState().complaint.formData;
  const current_form_data = {
    details: currentState,
    triage: {
      initial_severity: currentState.initial_severity,
      priority: currentState.priority,
      ai_risk_verdict: currentState.ai_risk_verdict
    }
  };
  
  const response = await axios.post(`${API_BASE}/chat/refine`, {
    prompt: payload.prompt,
    current_form_data: current_form_data
  });
  return response.data;
});

export const saveComplaint = createAsyncThunk('complaint/save', async (_, { getState }) => {
  const currentState = getState().complaint.formData;
  const payload = {
    details: currentState,
    triage: {
      initial_severity: currentState.initial_severity,
      priority: currentState.priority,
      ai_risk_verdict: currentState.ai_risk_verdict
    }
  };
  const response = await axios.post(`${API_BASE}/complaints`, payload);
  return response.data;
});

const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    updateField: (state, action) => {
      state.formData[action.payload.field] = action.payload.value;
    },
    resetForm: () => initialState,
    addChatMessage: (state, action) => {
      state.chatHistory.push(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(extractData.pending, (state) => {
        state.status = 'loading';
        state.progress = 50;
      })
      .addCase(extractData.fulfilled, (state, action) => {
        state.status = 'success';
        state.progress = 100;
        const { details, triage } = action.payload;
        state.formData = { ...details, ...triage };
        state.chatHistory.push({ role: 'ai', text: 'Extraction complete. I have populated the QMS form.' });
      })
      .addCase(extractData.rejected, (state) => {
        state.status = 'failed';
        state.progress = 0;
        state.chatHistory.push({ role: 'ai', text: 'Error extracting data. Please check the backend connection.' });
      })
      .addCase(refineData.pending, (state) => { state.status = 'loading'; })
      .addCase(refineData.fulfilled, (state, action) => {
        state.status = 'success';
        const { details, triage } = action.payload;
        state.formData = { ...details, ...triage };
        state.chatHistory.push({ role: 'ai', text: 'Form fields updated successfully based on your instructions.' });
      })
      .addCase(saveComplaint.fulfilled, (state) => {
        alert("Complaint logged successfully in the Database!");
      });
  },
});

export const { updateField, resetForm, addChatMessage } = complaintSlice.actions;
export default complaintSlice.reducer;