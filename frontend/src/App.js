import React, { useState } from 'react';
import PatientIntakeScreen from './pages/PatientIntakeScreen';
import QuestionnaireScreen from './pages/QuestionnaireScreen';
import PhysicianReviewScreen from './pages/PhysicianReviewScreen';
import FinalReportScreen from './pages/FinalReportScreen';
import './App.css';

function App() {
  const [screen, setScreen] = useState('intake'); // intake | questionnaire | physician | report
  const [consultation, setConsultation] = useState(null);

  const handleConsultationStart = (data) => {
    setConsultation(data);
    setScreen('questionnaire');
  };

  const handleQuestionsDone = (data) => {
    setConsultation(data);
    setScreen('physician');
  };

  const handlePhysicianDone = (data) => {
    setConsultation(data);
    setScreen('report');
  };

  const handleRestart = () => {
    setConsultation(null);
    setScreen('intake');
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <span className="header-icon">🏥</span>
          <div>
            <h1>ClinicalLamah</h1>
            <p>Système d'orientation clinique préliminaire — Projet académique</p>
          </div>
        </div>
        <div className="steps-indicator">
          {['Accueil', 'Questionnaire', 'Médecin', 'Rapport'].map((step, i) => {
            const screens = ['intake', 'questionnaire', 'physician', 'report'];
            const active = screens.indexOf(screen) >= i;
            return (
              <div key={i} className={`step ${active ? 'active' : ''}`}>
                <span className="step-num">{i + 1}</span>
                <span className="step-label">{step}</span>
              </div>
            );
          })}
        </div>
      </header>

      <main className="app-main">
        {screen === 'intake' && (
          <PatientIntakeScreen onStart={handleConsultationStart} />
        )}
        {screen === 'questionnaire' && (
          <QuestionnaireScreen
            consultation={consultation}
            onComplete={handleQuestionsDone}
          />
        )}
        {screen === 'physician' && (
          <PhysicianReviewScreen
            consultation={consultation}
            onComplete={handlePhysicianDone}
          />
        )}
        {screen === 'report' && (
          <FinalReportScreen
            consultation={consultation}
            onRestart={handleRestart}
          />
        )}
      </main>

      <footer className="app-footer">
        <p> Ce système ne remplace pas une consultation médicale. Projet académique uniquement.</p>
      </footer>
    </div>
  );
}

export default App;
