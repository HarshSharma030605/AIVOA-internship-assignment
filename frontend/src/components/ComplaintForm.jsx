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
  const value = useSelector((state) => state.complaint.formData[field] || '');

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

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">QMS Complaint Record</h2>
          <p className="text-sm text-gray-500">Quality Assurance Module</p>
        </div>
      </div>

      <FormSection title="1. Origin & Customer Details">
        <InputField label="Complaint Source" field="complaint_source" />
        <InputField label="Customer Name" field="customer_name" />
      </FormSection>

      <FormSection title="2. Product & Batch Identification">
        <InputField label="Product Name" field="product_name" />
        <InputField label="Batch/Lot Number" field="batch_number" />
        <InputField label="Manufacturing Date" field="manufacturing_date" />
        <InputField label="Expiry Date" field="expiry_date" />
        <InputField label="Quantity Affected" field="quantity_affected" />
      </FormSection>

      <FormSection title="3. Complaint Details">
        <InputField label="Complaint Type" field="complaint_type" />
        <InputField label="Complaint Date" field="complaint_date" />
        <InputField label="Detailed Description" field="detailed_description" fullWidth isTextArea />
      </FormSection>

      <FormSection title="4. Initial Assessment & Priority (Triage)">
        <InputField label="Initial Severity" field="initial_severity" />
        <InputField label="Priority" field="priority" />
        <InputField label="AI Risk Verdict" field="ai_risk_verdict" fullWidth isTextArea />
      </FormSection>

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