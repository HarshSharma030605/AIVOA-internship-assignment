import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateField, resetForm, saveComplaint } from '../redux/complaintSlice';

const FormSection = ({ title, children }) => (
  <div className="mb-6">
    <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4 border-b pb-2">{title}</h3>
    <div className="grid grid-cols-2 gap-4">
      {children}
    </div>
  </div>
);

const InputField = ({ label, field, fullWidth = false, isTextArea = false }) => {
  const dispatch = useDispatch();
  // Handles nested Redux state structures (e.g. details.product_name or triage.initial_severity)
  const value = useSelector((state) => {
    const keys = field.split('.');
    let current = state.complaint.formData;
    for (let k of keys) {
      current = current?.[k];
    }
    return current || '';
  });

  const handleChange = (e) => {
    dispatch(updateField({ field, value: e.target.value }));
  };

  const baseClasses = "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm border p-2 bg-gray-50";

  return (
    <div className={fullWidth ? 'col-span-2' : 'col-span-1'}>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      {isTextArea ? (
        <textarea rows="3" className={baseClasses} value={value} onChange={handleChange} />
      ) : (
        <input type="text" className={baseClasses} value={value} onChange={handleChange} />
      )}
    </div>
  );
};

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const triage = useSelector((state) => state.complaint.formData.triage || {});

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 h-full overflow-y-auto">
      
      {/* ⚠️ FDA ADVERSE EVENT BANNER */}
      {triage.fda_reportable && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-600 rounded-r-md">
          <div className="flex items-center space-x-2 text-red-700 font-bold">
            <svg className="w-5 h-5 fill-current" viewBox="0 0 20 20">
              <path d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 10-2 0 1 1 0 002 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" />
            </svg>
            <span>⚠️ MANDATORY FDA ADVERSE EVENT FLAGGED</span>
          </div>
          <p className="text-sm text-red-600 mt-1">{triage.fda_reasoning}</p>
        </div>
      )}

      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">QMS Complaint Record</h2>
          <p className="text-sm text-gray-500">Quality Assurance & AI Triage Module</p>
        </div>
      </div>

      <FormSection title="1. Origin & Customer Details">
        <InputField label="Complaint Source" field="details.complaint_source" />
        <InputField label="Customer Name" field="details.customer_name" />
      </FormSection>

      <FormSection title="2. Product & Batch Identification">
        <InputField label="Product Name" field="details.product_name" />
        <InputField label="Batch/Lot Number" field="details.batch_number" />
        <InputField label="Manufacturing Date" field="details.manufacturing_date" />
        <InputField label="Expiry Date" field="details.expiry_date" />
        <InputField label="Quantity Affected" field="details.quantity_affected" />
      </FormSection>

      <FormSection title="3. Complaint Details">
        <InputField label="Complaint Type" field="details.complaint_type" />
        <InputField label="Complaint Date" field="details.complaint_date" />
        <InputField label="Detailed Description" field="details.detailed_description" fullWidth isTextArea />
      </FormSection>

      <FormSection title="4. Initial Assessment & Priority (Triage)">
        <InputField label="Initial Severity" field="triage.initial_severity" />
        <InputField label="Priority" field="triage.priority" />
        <InputField label="AI Risk Verdict" field="triage.ai_risk_verdict" fullWidth isTextArea />
      </FormSection>

      {/* 🔍 AI ROOT CAUSE RECOMMENDATIONS */}
      {triage.root_cause_recommendations?.length > 0 && (
        <div className="mb-6 bg-slate-50 p-4 rounded-lg border border-slate-200">
          <h3 className="text-sm font-bold text-slate-700 mb-2 flex items-center gap-1">
            🔍 AI Root Cause Recommendations
          </h3>
          <ul className="list-disc list-inside text-sm text-slate-600 space-y-1">
            {triage.root_cause_recommendations.map((cause, idx) => (
              <li key={idx}>{cause}</li>
            ))}
          </ul>
        </div>
      )}

      {/* 🛡️ AI CAPA RECOMMENDATIONS */}
      {(triage.immediate_containment || triage.corrective_action || triage.preventive_action) && (
        <div className="mb-6 bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h3 className="text-sm font-bold text-blue-900 mb-3 flex items-center gap-1">
            🛡️ AI CAPA Recommendations
          </h3>
          <div className="space-y-3 text-sm">
            {triage.immediate_containment && (
              <div>
                <span className="font-semibold text-blue-800">Immediate Containment:</span>
                <p className="text-blue-950">{triage.immediate_containment}</p>
              </div>
            )}
            {triage.corrective_action && (
              <div>
                <span className="font-semibold text-blue-800">Corrective Action:</span>
                <p className="text-blue-950">{triage.corrective_action}</p>
              </div>
            )}
            {triage.preventive_action && (
              <div>
                <span className="font-semibold text-blue-800">Preventive Action:</span>
                <p className="text-blue-950">{triage.preventive_action}</p>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="mt-8 flex justify-between border-t pt-4">
        <button onClick={() => dispatch(resetForm())} className="text-gray-600 hover:text-gray-900 text-sm font-medium">
          ⟲ Clear Form
        </button>
        <button 
          onClick={() => dispatch(saveComplaint())}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 font-medium shadow-sm"
        >
          Submit to Database
        </button>
      </div>
    </div>
  );
}