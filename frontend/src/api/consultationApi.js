import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE });

export const startConsultation = (patientName, initialComplaint) =>
  api.post('/consultation/start', { patient_name: patientName, initial_complaint: initialComplaint });

export const answerQuestion = (threadId, patientAnswer) =>
  api.post('/consultation/resume', {
    thread_id: threadId,
    patient_answer: patientAnswer,
    action: 'answer_patient'
  });

export const submitPhysicianReview = (threadId, physicianTreatment) =>
  api.post('/consultation/resume', {
    thread_id: threadId,
    physician_treatment: physicianTreatment,
    action: 'physician_review'
  });

export const getConsultation = (threadId) =>
  api.get(`/consultation/${threadId}`);

export const getReport = (threadId) =>
  api.get(`/consultation/${threadId}/report`);
