import React from 'react';
import { createRoot } from 'react-dom/client';
import TeacherDashboard from './TeacherDashboard';
import ParentDashboard from './ParentDashboard';
import ChildrenList from './ChildrenList';

const globalResponsiveCss = `
  .resp-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
  .resp-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
  .resp-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
  .resp-grid-2-form { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
  .resp-grid-dob { display: grid; grid-template-columns: 2fr 1fr; gap: 15px; }
  .resp-grid-2-ratio { display: grid; grid-template-columns: minmax(0, 1.8fr) minmax(0, 1fr); gap: 15px; }
  .resp-flex-between { display: flex; justify-content: space-between; align-items: center; }
  .resp-mobile-tabs { display: none !important; }
  
  .resp-fade-in { 
      animation: reactPageFadeIn 0.55s cubic-bezier(0.16, 1, 0.3, 1) both; 
  }

  @keyframes reactPageFadeIn {
      from {
          opacity: 0;
          transform: translateY(18px);
      }
      to {
          opacity: 1;
          transform: translateY(0);
      }
  }

  /* React Modern Bento Cards */
  .modern-card, .stat-card-modern {
      position: relative;
      overflow: hidden;
      border-radius: 12px;
      transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), 
                  box-shadow 0.3s ease, 
                  border-color 0.3s ease !important;
      will-change: transform, box-shadow;
  }

  .modern-card:hover, .stat-card-modern:hover {
      transform: translateY(-5px) scale(1.01) !important;
      box-shadow: 0 16px 32px -8px rgba(15, 43, 92, 0.14), 0 6px 12px -4px rgba(0, 0, 0, 0.04) !important;
  }

  .dark-mode .modern-card:hover, .dark-mode .stat-card-modern:hover {
      box-shadow: 0 18px 36px -8px rgba(0, 0, 0, 0.65), 0 0 18px rgba(56, 189, 248, 0.12) !important;
  }

  /* Stat Card Icon Badges */
  .stat-icon-badge {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      background: #f1f5f9;
      color: #0f172a;
      border: 1px solid #cbd5e1;
      transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .stat-card-modern:hover .stat-icon-badge {
      transform: scale(1.12) rotate(-6deg);
  }
  .stat-icon-blue, .stat-icon-emerald, .stat-icon-amber, .stat-icon-purple {
      background: #f1f5f9;
      color: #0f172a;
      border: 1px solid #cbd5e1;
  }

  .dark-mode .stat-icon-badge,
  .dark-mode .stat-icon-blue,
  .dark-mode .stat-icon-emerald,
  .dark-mode .stat-icon-amber,
  .dark-mode .stat-icon-purple {
      background: rgba(255, 255, 255, 0.08);
      color: #f8fafc;
      border-color: rgba(255, 255, 255, 0.15);
  }

  /* Tab Buttons Polish */
  .resp-mobile-tab-btn {
      transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
  }

  .resp-mobile-tab-btn:hover {
      transform: translateY(-2px);
  }

  .resp-mobile-tab-btn:active {
      transform: scale(0.96);
  }

  @media (max-width: 768px) {
      .resp-grid-4 { grid-template-columns: 1fr !important; }
      .resp-grid-3 { grid-template-columns: 1fr !important; }
      .resp-grid-2 { grid-template-columns: 1fr !important; }
      .resp-grid-2-form { grid-template-columns: 1fr !important; }
      .resp-grid-dob { grid-template-columns: 1fr !important; }
      .resp-grid-2-ratio { grid-template-columns: 1fr !important; }
      .resp-flex-between { flex-direction: column !important; align-items: flex-start !important; gap: 15px !important; }
      
      .resp-mobile-tabs { 
          display: flex !important; 
          gap: 8px; 
          margin-bottom: 20px; 
          width: 100%; 
          overflow-x: auto; 
          -webkit-overflow-scrolling: touch; 
          padding-bottom: 8px;
          border-bottom: 1px solid #eee;
      }
      .resp-mobile-tab-btn {
          flex: 1;
          min-width: max-content;
          padding: 8px 16px;
          border-radius: 20px;
          background: #f0f4f8;
          border: 1px solid #cbd5e1;
          color: #475569;
          font-weight: 600;
          font-size: 0.85rem;
          cursor: pointer;
          text-align: center;
          white-space: nowrap;
          transition: all 0.2s ease;
          font-family: 'Montserrat', sans-serif;
      }
      .resp-mobile-tab-btn.active {
          background: linear-gradient(135deg, #1e40af 0%, #091e42 100%) !important;
          color: #ffffff !important;
          border-color: #1e40af !important;
          box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
          transform: scale(1.02);
      }
  }
`;


class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '40px', color: 'red', background: '#fee' }}>
          <h2>Something went wrong in the Dashboard.</h2>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{this.state.error.toString()}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}


const renderApp = (id, Component) => {
  const container = document.getElementById(id);
  if (container) {
    const root = createRoot(container);
    root.render(
      <ErrorBoundary>
        <style>{globalResponsiveCss}</style>
        <Component />
      </ErrorBoundary>
    );
  }
};

const init = () => {
  renderApp('react-teacher-dashboard-root', TeacherDashboard);
  renderApp('react-parent-dashboard-root', ParentDashboard);
  renderApp('react-children-root', ChildrenList);
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
