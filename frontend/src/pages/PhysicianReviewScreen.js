import React, { useState } from 'react';
import { submitPhysicianReview } from '../api/consultationApi';

export default function PhysicianReviewScreen({ consultation, onComplete }) {
  const [treatment, setTreatment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!treatment.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await submitPhysicianReview(consultation.thread_id, treatment);
      onComplete(res.data);
    } catch (err) {
      setError("Erreur lors de l'envoi de l'avis médical.");
    } finally {
      setLoading(false);
    }
  };

  const templates = [
    "Repos au domicile, paracétamol 1g/8h, réévaluation si aggravation à 48h.",
    "Antibiothérapie probabiliste prescrite. Contrôle NFS dans 5 jours.",
    "Orientation aux urgences recommandée pour bilan complémentaire.",
  ];

  return (
    <div className="screen">
      <div className="card physician-card">
        <h2>👨‍⚕️ Revue du Médecin Traitant</h2>
        <div className="hitl-badge">⏸️ Human-in-the-Loop — Validation médicale requise</div>

        <div className="summary-box">
          <h3>Synthèse Clinique Préliminaire</h3>
          <p>{consultation?.diagnostic_summary || 'Synthèse en cours de chargement...'}</p>
        </div>

        {consultation?.interim_care && (
          <div className="interim-box">
            <h3>Recommandation Intermédiaire</h3>
            <p>{consultation.interim_care}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label>Conduite à tenir / Traitement prescrit</label>
            <div className="templates">
              {templates.map((t, i) => (
                <button key={i} type="button" className="example-btn" onClick={() => setTreatment(t)}>
                  {t.substring(0, 50)}...
                </button>
              ))}
            </div>
            <textarea
              value={treatment}
              onChange={e => setTreatment(e.target.value)}
              placeholder="Saisir la conduite à tenir, les prescriptions ou orientations..."
              rows={5}
              required
            />
          </div>

          {error && <div className="error-msg">⚠️ {error}</div>}

          <button type="submit" className="btn-primary btn-physician" disabled={loading || !treatment.trim()}>
            {loading ? '⏳ Génération du rapport...' : '✅ Valider et générer le rapport →'}
          </button>
        </form>
      </div>
    </div>
  );
}
