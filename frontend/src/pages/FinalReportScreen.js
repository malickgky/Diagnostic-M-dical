import React from 'react';

export default function FinalReportScreen({ consultation, onRestart }) {
  const report = consultation?.final_report || 'Rapport non disponible.';

  const handlePrint = () => window.print();

  return (
    <div className="screen">
      <div className="card report-card">
        <div className="report-header">
          <h2>📋 Rapport Final</h2>
          <div className="report-actions">
            <button className="btn-secondary" onClick={handlePrint}>🖨️ Imprimer</button>
            <button className="btn-primary" onClick={onRestart}>+ Nouvelle consultation</button>
          </div>
        </div>

        <div className="success-badge">✅ Consultation complétée</div>

        <div className="report-content">
          <pre>{report}</pre>
        </div>

        <div className="legal-warning">
          <strong>⚠️ Avertissement légal :</strong> Ce système ne remplace pas une consultation médicale.
          Ce document est produit dans le cadre d'un exercice académique uniquement et
          ne constitue pas un diagnostic médical définitif.
        </div>
      </div>
    </div>
  );
}
