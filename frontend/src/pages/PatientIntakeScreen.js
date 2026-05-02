import React, { useState } from 'react';
import { startConsultation } from '../api/consultationApi';

export default function PatientIntakeScreen({ onStart }) {
  const [patientName, setPatientName] = useState('');
  const [complaint, setComplaint] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!patientName.trim() || !complaint.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await startConsultation(patientName, complaint);
      onStart(res.data);
    } catch (err) {
      setError("Erreur de connexion au serveur. Vérifiez que le backend est démarré.");
    } finally {
      setLoading(false);
    }
  };

  const examples = [
    "J'ai de la fièvre et une toux depuis 3 jours",
    "Douleur thoracique intense depuis ce matin",
    "Nausées et maux de ventre depuis hier soir"
  ];

  return (
    <div className="screen">
      <div className="card">
        <h2>🩺 Nouvelle Consultation</h2>
        <p className="subtitle">Saisissez les informations initiales du patient pour démarrer l'orientation clinique préliminaire.</p>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label>Nom du patient</label>
            <input
              type="text"
              value={patientName}
              onChange={e => setPatientName(e.target.value)}
              placeholder="Ex. : Jean Dupont"
              required
            />
          </div>

          <div className="form-group">
            <label>Motif de consultation</label>
            <textarea
              value={complaint}
              onChange={e => setComplaint(e.target.value)}
              placeholder="Décrivez le problème de santé en quelques mots..."
              rows={4}
              required
            />
            <div className="examples">
              <span>Exemples : </span>
              {examples.map((ex, i) => (
                <button key={i} type="button" className="example-btn" onClick={() => setComplaint(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          </div>

          {error && <div className="error-msg">⚠️ {error}</div>}

          <button type="submit" className="btn-primary" disabled={loading || !patientName || !complaint}>
            {loading ? '⏳ Démarrage...' : 'Démarrer la consultation →'}
          </button>
        </form>
      </div>
    </div>
  );
}
