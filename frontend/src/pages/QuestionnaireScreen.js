import React, { useState, useEffect } from 'react';
import { answerQuestion } from '../api/consultationApi';

export default function QuestionnaireScreen({ consultation, onComplete }) {
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [state, setState] = useState(consultation);
  const [history, setHistory] = useState([]);

  const questionCount = state?.question_number || 1;
  const currentQuestion = state?.current_question;
  const status = state?.status;

  useEffect(() => {
    // Si toutes les questions ont été posées, passer à l'étape médecin
    if (status === 'awaiting_physician' || (status === 'running' && state?.diagnostic_summary)) {
      onComplete(state);
    }
  }, [status, state]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!answer.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await answerQuestion(state.thread_id, answer);
      setHistory(prev => [...prev, { question: currentQuestion, answer }]);
      setAnswer('');
      setState(res.data);

      // Vérifier si on doit passer à l'étape médecin
      if (res.data.status === 'awaiting_physician' || res.data.diagnostic_summary) {
        onComplete(res.data);
      }
    } catch (err) {
      setError("Erreur lors de l'envoi de la réponse.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screen">
      <div className="card">
        <h2>💬 Questionnaire Patient</h2>
        <div className="progress-bar-container">
          <div className="progress-bar" style={{ width: `${((questionCount - 1) / 5) * 100}%` }} />
          <span className="progress-text">Question {questionCount}/5</span>
        </div>

        {/* Historique des questions/réponses */}
        {history.length > 0 && (
          <div className="qa-history">
            {history.map((item, i) => (
              <div key={i} className="qa-item">
                <div className="qa-question">🤖 {item.question}</div>
                <div className="qa-answer">👤 {item.answer}</div>
              </div>
            ))}
          </div>
        )}

        {/* Question courante */}
        {currentQuestion && (
          <div className="current-question">
            <div className="question-bubble">
              <span className="q-icon">🤖</span>
              <p>{currentQuestion}</p>
            </div>

            <form onSubmit={handleSubmit} className="answer-form">
              <textarea
                value={answer}
                onChange={e => setAnswer(e.target.value)}
                placeholder="Votre réponse..."
                rows={3}
                autoFocus
              />
              {error && <div className="error-msg">⚠️ {error}</div>}
              <button type="submit" className="btn-primary" disabled={loading || !answer.trim()}>
                {loading ? '⏳ Envoi...' : 'Répondre →'}
              </button>
            </form>
          </div>
        )}

        {loading && !currentQuestion && (
          <div className="loading-state">
            <div className="spinner" />
            <p>Analyse des réponses en cours...</p>
          </div>
        )}
      </div>
    </div>
  );
}
