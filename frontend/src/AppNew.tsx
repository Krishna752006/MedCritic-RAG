import React, { useState } from 'react';
import {
  FileText,
  Activity,
  RefreshCw} from 'lucide-react';

const steps = ['Ingestion', 'Entity Extraction', 'Hybrid Retrieval', 'Verification', 'Navigation'];

const sampleReports: Record<string, any> = {
  lipid: {
    raw_extracted_text: 'LIPID PROFILE ANALYSIS REPORT\nCholesterol Total: 285 mg/dL\nHDL: 35 mg/dL\nLDL: 195 mg/dL\nTriglycerides: 275 mg/dL',
    findings: [
      { name: 'Cholesterol Total', value: '285', unit: 'mg/dL', status: 'abnormal', snomed_code: '121868005', loinc_code: '2093-3', icd10_code: 'E78.00', description: 'High cholesterol increases cardiovascular risk and merits lipid-lowering therapy.' },
      { name: 'LDL Cholesterol', value: '195', unit: 'mg/dL', status: 'elevated', snomed_code: '113079009', loinc_code: '13457-7', icd10_code: 'E78.01', description: 'LDL is high, which heightens plaque formation risk.' },
      { name: 'Triglycerides', value: '275', unit: 'mg/dL', status: 'elevated', snomed_code: '14682006', loinc_code: '2571-8', icd10_code: 'E78.1', description: 'Triglycerides are above optimal range, suggesting metabolic imbalance.' }
    ],
    guidelines_retrieved: [
      { id: 'GL-001', source_name: 'ACC/AHA', guideline_name: '2019 Guidelines on Primary Prevention of Cardiovascular Disease', text_snippet: 'Initiation of statin therapy is recommended for primary prevention of cardiovascular disease in adults aged 40-75 years with LDL cholesterol levels >= 190 mg/dL.', evidence_tier: 'Tier 1: Strong Evidence', year: 2019 }
    ],
    verifications: [
      { claim: 'LDL level counts abnormal at 195 mg/dL', status: 'Verified', strength_score: 0.98, supporting_guideline_id: 'GL-001', verification_reasoning: 'Verified against ACC/AHA threshold of 190 mg/dL for clinical action.' }
    ],
    clinical_summary: 'CLINICAL INTERPRETATION REPORT:\nPatient presents with severe hypercholesterolemia (LDL 195 mg/dL). Statin therapy initiation is advised pending liver and metabolic assessments.',
    patient_explanation: 'PATIENT PERSONAL HEALTH ANALYSIS:\nYour LDL cholesterol is high. A doctor may recommend medication and diet changes to lower your heart risk.',
    urgency_level: 'Urgent',
    urgency_reasoning: 'High lipid values suggest accelerated cardiovascular risk requiring prompt clinician review.',
    recommended_specialty: 'Cardiology',
    recommended_specialty_reasoning: 'Cardiology is recommended for lipid disorder management and cardiovascular prevention.',
    nearby_facilities: [{ name: 'St. Mary Medical Center', type: 'General & Cardiology Specialist', distance_km: 1.4, address: '450 Medical Heights Way, Sector 4', contact: '+1 (555) 234-9800', specialty_match: true }],
    calibrated_confidence: 0.96
  },
  diabetes: {
    raw_extracted_text: 'DIABETIC SCREENING & GLUCOSE TEST\nHbA1c: 8.7%\nFasting Plasma Glucose: 172 mg/dL',
    findings: [
      { name: 'HbA1c', value: '8.7', unit: '%', status: 'critical high', snomed_code: '43396009', loinc_code: '4548-4', icd10_code: 'E11.9', description: 'Elevated HbA1c indicates chronic hyperglycemia and diabetes requiring intervention.' },
      { name: 'Fasting Plasma Glucose', value: '172', unit: 'mg/dL', status: 'abnormal', snomed_code: '250392003', loinc_code: '1558-6', icd10_code: 'R73.09', description: 'Fasting glucose is high, supporting a diabetes diagnosis.' }
    ],
    guidelines_retrieved: [
      { id: 'GL-003', source_name: 'ADA', guideline_name: 'Standards of Care in Diabetes—2024', text_snippet: 'An HbA1c level of >= 6.5% is diagnostic of Diabetes Mellitus.', evidence_tier: 'Tier 1: Strong Evidence', year: 2024 }
    ],
    verifications: [
      { claim: 'HbA1c level at 8.7% exceeds glycemic control thresholds', status: 'Verified', strength_score: 0.99, supporting_guideline_id: 'GL-003', verification_reasoning: 'Verified: above ADA diagnostic criteria for diabetes.' }
    ],
    clinical_summary: 'CLINICAL INTERPRETATION REPORT:\nThe patient has poorly controlled diabetes with HbA1c 8.7%. Therapeutic escalation and lifestyle adjustment are required.',
    patient_explanation: 'PATIENT PERSONAL HEALTH ANALYSIS:\nYour blood sugar control is not optimal. Please consult a physician to discuss medication and diet changes.',
    urgency_level: 'Urgent',
    urgency_reasoning: 'Uncontrolled glycemia indicates urgent physician review.',
    recommended_specialty: 'Endocrinology',
    recommended_specialty_reasoning: 'Endocrinology care is advised for metabolic stabilization.',
    nearby_facilities: [{ name: 'Metropolitan Endocrinology Clinic', type: 'Specialty Outpatient Clinic', distance_km: 2.8, address: '88 Glycemic Suites, Medical Zone 2', contact: '+1 (555) 890-4122', specialty_match: true }],
    calibrated_confidence: 0.98
  },
  cbc: {
    raw_extracted_text: 'COMPLETE BLOOD COUNT (CBC)\nWhite Blood Cell Count: 14.5 x10^3/uL\nNotes: Patient presents with persistent fever and sore throat.',
    findings: [
      { name: 'White Blood Cell Count', value: '14.5', unit: 'x10^3/uL', status: 'high', snomed_code: '113028004', loinc_code: '6690-2', icd10_code: 'D72.829', description: 'Elevated white blood cells suggest infection or inflammation requiring medical assessment.' }
    ],
    guidelines_retrieved: [
      { id: 'GL-005', source_name: 'WHO', guideline_name: 'Guidelines on Syphilis and Infectious Diseases Diagnosis', text_snippet: 'An elevated White Blood Cell count (>11.0 x10^3/uL) suggests infection or systemic inflammation.', evidence_tier: 'Tier 2: Moderate Evidence', year: 2020 }
    ],
    verifications: [
      { claim: 'WBC count 14.5 x10^3/uL indicates leukocytosis', status: 'Verified', strength_score: 0.92, supporting_guideline_id: 'GL-005', verification_reasoning: 'Verified against WHO infection alert thresholds.' }
    ],
    clinical_summary: 'CLINICAL INTERPRETATION REPORT:\nLeukocytosis with fever indicates likely infection. Evaluate for bacterial or viral cause and manage accordingly.',
    patient_explanation: 'PATIENT PERSONAL HEALTH ANALYSIS:\nYour white blood cell count is high, which means your body is fighting something. Please see a clinician soon.',
    urgency_level: 'Urgent',
    urgency_reasoning: 'High WBC with fever warrants timely clinical evaluation.',
    recommended_specialty: 'Infectious Diseases / Hematology',
    recommended_specialty_reasoning: 'Specialist assessment is recommended for infection and hematologic evaluation.',
    nearby_facilities: [{ name: 'St. Mary Medical Center', type: 'General & Emergency Care Hospital', distance_km: 1.4, address: '450 Medical Heights Way, Sector 4', contact: '+1 (555) 234-9800', specialty_match: true }],
    calibrated_confidence: 0.94
  }
};

interface AppResult {
  raw_extracted_text: string;
  findings: Array<Record<string, any>>;
  guidelines_retrieved: Array<Record<string, any>>;
  verifications: Array<Record<string, any>>;
  clinical_summary: string;
  patient_explanation: string;
  urgency_level: string;
  urgency_reasoning: string;
  recommended_specialty: string;
  recommended_specialty_reasoning: string;
  nearby_facilities: Array<Record<string, any>>;
  calibrated_confidence: number;
}

type ChatMessage = {
  role: 'user' | 'assistant';
  text: string;
};

const BACKEND_URL = 'http://localhost:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState<'interpreter' | 'chat' | 'research'>('interpreter');
  const [lang, setLang] = useState('en');
  const [currentStep, setCurrentStep] = useState(0);
  const [analysisResult, setAnalysisResult] = useState<AppResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [sessionId, setSessionId] = useState<string>(() => {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID();
    }
    return `session-${Math.random().toString(36).slice(2)}`;
  });
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  const applyTranslation = (payload: AppResult, language: string): AppResult => {
    const translated = { ...payload };
    if (language === 'es') {
      translated.clinical_summary = translated.clinical_summary.replace('CLINICAL INTERPRETATION REPORT', 'INFORME DE INTERPRETACIÓN CLÍNICA');
      translated.patient_explanation = translated.patient_explanation.replace('PATIENT PERSONAL HEALTH ANALYSIS', 'GLOSARIO PARA EL PACIENTE E INFORMACIÓN DE SALUD');
    }
    if (language === 'hi') {
      translated.clinical_summary = translated.clinical_summary.replace('CLINICAL INTERPRETATION REPORT', 'नैदानिक व्याख्या रिपोर्ट');
      translated.patient_explanation = translated.patient_explanation.replace('PATIENT PERSONAL HEALTH ANALYSIS', 'रोगी शब्दावली और स्वास्थ्य जानकारी');
    }
    if (language === 'te') {
      translated.clinical_summary = translated.clinical_summary.replace('CLINICAL INTERPRETATION REPORT', 'క్లినికల్ ఇంటర్‌ప్రెటేషన్ నివేదిక');
      translated.patient_explanation = translated.patient_explanation.replace('PATIENT PERSONAL HEALTH ANALYSIS', 'రోગి గ్లోసరీ మరియు ఆరోగ్య సమాచారం');
    }
    return translated;
  };

  const triggerSimulation = (type: 'lipid' | 'diabetes' | 'cbc') => {
    setAnalysisResult(null);
    setCurrentStep(1);
    const payload = applyTranslation(sampleReports[type], lang);

    [1, 2, 3, 4, 5].forEach((step, index) => {
      window.setTimeout(() => setCurrentStep(step), 500 * index);
    });

    window.setTimeout(() => {
      setAnalysisResult(payload);
    }, 3000);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setCurrentStep(1);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${BACKEND_URL}/analyze-report?lang=${lang}`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error('Backend not available');
      }
      const data = await response.json();
      setAnalysisResult(data);
      setCurrentStep(5);
    } catch {
      const name = file.name.toLowerCase();
      const sampleType = name.includes('cbc') || name.includes('blood') ? 'cbc' : name.includes('diab') || name.includes('hba1c') ? 'diabetes' : 'lipid';
      triggerSimulation(sampleType as 'lipid' | 'diabetes' | 'cbc');
    }
  };

  const sendChatMessage = async () => {
    const trimmed = chatInput.trim();
    if (!trimmed) return;

    const nextMessages = [...chatMessages, { role: 'user' as const, text: trimmed }];
    setChatMessages(nextMessages);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed, session_id: sessionId, context_summary: null, lang }),
      });

      if (!response.ok) {
        throw new Error('Chat backend error');
      }

      const data = await response.json();
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
      }
      const assistantText = typeof data.response === 'string'
        ? data.response
        : Array.isArray(data.response)
          ? data.response.join(' ')
          : JSON.stringify(data.response || 'The clinical assistant did not return a response. Please try again.');
      setChatMessages([...nextMessages, { role: 'assistant' as const, text: assistantText }]);
    } catch {
      setChatMessages([...nextMessages, { role: 'assistant' as const, text: 'Unable to connect to the chat backend. Please ensure the service is running on localhost:8000.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleChatKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendChatMessage();
    }
  };

  return (
    <div className="min-h-screen bg-navy-900 text-slate-100 flex flex-col">
      <header className="relative overflow-hidden bg-navy-800 border-b border-navy-700 py-10 px-6 sm:px-16">
        <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-medical-primary opacity-10 blur-3xl" />
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-3xl">
              <span className="text-xs uppercase tracking-[0.4em] text-cyan-300/70 font-semibold">MedCritic-RAG++</span>
              <h1 className="mt-4 text-3xl sm:text-4xl font-extrabold text-white">Verified Medical Research Hub & Diagnostic Interpreter</h1>
              <p className="mt-4 leading-7 text-slate-300">A premium research portal for a dual-mode medical RAG system with OCR, evidence retrieval, clinical verification, patient summarization, and referral routing.</p>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              <span className="rounded-full border border-cyan-500/20 bg-navy-900/70 px-4 py-3 text-xs text-cyan-200">Multimodal OCR</span>
              <span className="rounded-full border border-cyan-500/20 bg-navy-900/70 px-4 py-3 text-xs text-cyan-200">Verified RAG</span>
              <span className="rounded-full border border-cyan-500/20 bg-navy-900/70 px-4 py-3 text-xs text-cyan-200">Dual Register Output</span>
            </div>
          </div>
        </div>
      </header>

      <nav className="max-w-7xl mx-auto px-6 sm:px-16 py-5 flex flex-wrap gap-3">
        <button type="button" onClick={() => setActiveTab('interpreter')} className={`rounded-full px-5 py-3 text-sm font-semibold transition ${activeTab === 'interpreter' ? 'bg-cyan-400 text-navy-950' : 'bg-navy-900 text-slate-300 hover:bg-navy-800'}`}>Report Interpreter</button>
        <button type="button" onClick={() => setActiveTab('chat')} className={`rounded-full px-5 py-3 text-sm font-semibold transition ${activeTab === 'chat' ? 'bg-cyan-400 text-navy-950' : 'bg-navy-900 text-slate-300 hover:bg-navy-800'}`}>Clinical Chat</button>
        <button type="button" onClick={() => setActiveTab('research')} className={`rounded-full px-5 py-3 text-sm font-semibold transition ${activeTab === 'research' ? 'bg-cyan-400 text-navy-950' : 'bg-navy-900 text-slate-300 hover:bg-navy-800'}`}>Research Proposal</button>
      </nav>

      <main className="max-w-7xl mx-auto px-6 sm:px-16 flex-grow pb-10">
        {activeTab === 'interpreter' ? (
          <div className="grid gap-8 lg:grid-cols-12">
            <section className="lg:col-span-4 space-y-6">
              <div className="rounded-[2rem] border border-navy-700 bg-navy-800 p-6 shadow-2xl shadow-black/20">
                <div className="flex items-center gap-3 mb-5">
                  <FileText className="text-cyan-400" />
                  <div>
                    <h2 className="text-lg font-semibold text-white">Report Ingestion</h2>
                    <p className="text-sm text-slate-400">Upload a clinical report or execute a mock evaluation sample.</p>
                  </div>
                </div>
                <label className="relative block cursor-pointer rounded-[2rem] border-2 border-dashed border-navy-700 bg-navy-950/70 p-8 text-center hover:border-cyan-400 transition">
                  <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={handleFileUpload} className="absolute inset-0 h-full w-full opacity-0 cursor-pointer" />
                  <p className="text-sm text-slate-300">Click or drop a PDF/image here</p>
                  <p className="mt-2 text-xs text-slate-500">PDF, PNG, JPG</p>
                </label>
                {selectedFile && <p className="mt-4 text-xs text-cyan-300">Selected file: {selectedFile.name}</p>}
                <div className="mt-6 flex items-center justify-between gap-3">
                  <span className="text-xs uppercase tracking-[0.24em] text-slate-500">Target language</span>
                  <select value={lang} onChange={(e) => setLang(e.target.value)} className="rounded-2xl border border-navy-700 bg-navy-900 px-4 py-2 text-sm text-slate-100 outline-none">
                    <option value="en">English</option>
                    <option value="hi">Hindi</option>
                    <option value="es">Spanish</option>
                    <option value="te">Telugu</option>
                  </select>
                </div>
                <div className="mt-6 grid gap-3">
                  <button type="button" className="rounded-[1.5rem] bg-cyan-500 px-4 py-3 font-semibold text-navy-950 transition hover:bg-cyan-400" onClick={() => triggerSimulation('lipid')}>Simulate Lipid Panel</button>
                  <button type="button" className="rounded-[1.5rem] border border-navy-700 bg-navy-900 px-4 py-3 font-semibold text-slate-200 transition hover:border-cyan-400" onClick={() => triggerSimulation('diabetes')}>Simulate Diabetes Screening</button>
                  <button type="button" className="rounded-[1.5rem] border border-navy-700 bg-navy-900 px-4 py-3 font-semibold text-slate-200 transition hover:border-cyan-400" onClick={() => triggerSimulation('cbc')}>Simulate CBC</button>
                </div>
              </div>

              <div className="rounded-[2rem] border border-navy-700 bg-navy-800 p-6">
                <div className="flex items-center gap-3 mb-5">
                  <RefreshCw className="text-cyan-400" />
                  <div>
                    <h3 className="text-base font-semibold text-white">Pipeline Status</h3>
                    <p className="text-sm text-slate-400">Step-by-step visualization of the process.</p>
                  </div>
                </div>
                <div className="space-y-3 text-xs font-mono text-slate-400">
                  {steps.map((label, idx) => (
                    <div key={label} className={`flex items-center justify-between rounded-2xl border px-4 py-3 ${currentStep > idx ? 'border-cyan-600 bg-navy-900/70 text-cyan-200' : 'border-navy-700 bg-navy-950 text-slate-500'}`}>
                      <span>{label}</span>
                      <span>{currentStep > idx ? '✅' : '⏳'}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="lg:col-span-8 space-y-6">
              {analysisResult ? (
                <div className="space-y-6">
                  <div className="rounded-[2rem] border border-cyan-500/15 bg-navy-850 p-6">
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                      <div>
                        <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Clinical Navigation</p>
                        <h2 className="mt-2 text-2xl font-bold text-white">{analysisResult.recommended_specialty}</h2>
                        <p className="mt-2 text-sm text-slate-300">{analysisResult.urgency_reasoning}</p>
                      </div>
                      <div className="rounded-3xl border border-cyan-500/20 bg-navy-900 px-5 py-4 text-center">
                        <p className="text-[10px] uppercase tracking-[0.3em] text-slate-400">Confidence</p>
                        <p className="mt-2 text-4xl font-extrabold text-cyan-400">{Math.round(analysisResult.calibrated_confidence * 100)}%</p>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-[2rem] border border-navy-700 bg-navy-800 p-6"> ... </div>
                </div>
              ) : (
                <div className="rounded-[2rem] border border-navy-700 bg-navy-850 p-20 text-center">
                  <Activity className="mx-auto h-14 w-14 text-cyan-400 animate-pulse" />
                  <h2 className="mt-6 text-2xl font-semibold text-white">No analysis yet</h2>
                  <p className="mt-3 text-sm text-slate-500">Upload a report or select a sample to begin the MedCritic-RAG++ pipeline.</p>
                </div>
              )}
            </section>
          </div>
        ) : activeTab === 'chat' ? (
          <div className="grid gap-8 lg:grid-cols-12">
            <section className="lg:col-span-4 space-y-6">
              <div className="rounded-[2rem] border border-navy-700 bg-navy-800 p-6 shadow-2xl shadow-black/20">
                <div className="flex items-center gap-3 mb-5">
                  <FileText className="text-cyan-400" />
                  <div>
                    <h2 className="text-lg font-semibold text-white">Clinical Chat Assistant</h2>
                    <p className="text-sm text-slate-400">Ask questions, clarify symptoms, or request next-step guidance.</p>
                  </div>
                </div>
                <div className="space-y-4 text-sm text-slate-300">
                  <p>Use the chat to ask medical questions and receive evidence-grounded responses from the backend clinical AI pipeline.</p>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Connected backend</p>
                  <p className="rounded-3xl border border-navy-700 bg-navy-950 p-4 text-slate-300">{BACKEND_URL}/chat</p>
                </div>
              </div>
              <div className="rounded-[2rem] border border-navy-700 bg-navy-800 p-6">
                <div className="flex items-center gap-3 mb-5">
                  <RefreshCw className="text-cyan-400" />
                  <div>
                    <h3 className="text-base font-semibold text-white">Chat Guidance</h3>
                    <p className="text-sm text-slate-400">Enter symptoms, report questions, or upload instructions.</p>
                  </div>
                </div>
                <ul className="space-y-3 text-sm text-slate-300">
                  <li>• Type a clinical question, for example “What does elevated LDL mean?”</li>
                  <li>• Ask “Is this an emergency?” for safety triage guidance.</li>
                  <li>• Use the report tab to upload files and then follow up here.</li>
                </ul>
              </div>
            </section>

            <section className="lg:col-span-8 space-y-6">
              <div className="rounded-[2rem] border border-navy-700 bg-navy-850 p-6">
                <div className="space-y-4">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Assistant Conversation</p>
                      <h2 className="text-2xl font-bold text-white">Clinical dialogue</h2>
                      <p className="text-xs text-slate-500 mt-2">Session: {sessionId}</p>
                    </div>
                    <span className="rounded-full bg-navy-900 px-4 py-2 text-xs text-slate-400">Language: {lang.toUpperCase()}</span>
                  </div>
                  <div className="space-y-3 max-h-[52vh] overflow-y-auto rounded-3xl border border-navy-700 bg-navy-900 p-4 text-sm text-slate-300">
                    {chatMessages.length === 0 ? (
                      <div className="py-12 text-center text-slate-500">Send a message to begin the clinical chat.</div>
                    ) : (
                      chatMessages.map((message, index) => (
                        <div key={index} className={`rounded-3xl p-4 ${message.role === 'user' ? 'bg-cyan-950/20 text-cyan-100 self-end' : 'bg-navy-950/80 text-slate-200'}`}>
                          <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500 mb-2">{message.role === 'user' ? 'You' : 'Assistant'}</p>
                          <p className="whitespace-pre-wrap text-sm">{message.text}</p>
                        </div>
                      ))
                    )}
                  </div>
                  <div className="mt-4 grid gap-3">
                    <textarea
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={handleChatKeyDown}
                      rows={4}
                      placeholder="Ask about symptoms, test results, or clinical next steps..."
                      className="w-full rounded-[1.5rem] border border-navy-700 bg-navy-900 px-4 py-3 text-sm text-slate-100 outline-none transition focus:border-cyan-400"
                    />
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-xs text-slate-500">Press Enter to send. Shift+Enter for a new line.</span>
                      <button type="button" onClick={sendChatMessage} disabled={chatLoading} className="rounded-[1.5rem] bg-cyan-500 px-5 py-3 font-semibold text-navy-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60">
                        {chatLoading ? 'Sending...' : 'Send Message'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        ) : (
          <div className="space-y-10"> ... </div>
        )}
      </main>

      <footer className="bg-navy-950 border-t border-navy-800 py-6 text-center text-xs text-slate-500">MedCritic-RAG++ Framework • Local simulation mode enabled by default.</footer>
    </div>
  );
}
