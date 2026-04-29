import React from 'react';
import { createRoot } from 'react-dom/client';
import TeacherDashboard from './TeacherDashboard';
import ParentDashboard from './ParentDashboard';
import ChildrenList from './ChildrenList';

const globalResponsiveCss = `
  .resp-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
  .resp-grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
  .resp-grid-2-ratio { display: grid; grid-template-columns: minmax(0, 1.8fr) minmax(0, 1fr); gap: 15px; }
  .resp-flex-between { display: flex; justify-content: space-between; align-items: center; }
  
  @media (max-width: 768px) {
      .resp-grid-4 { grid-template-columns: 1fr !important; }
      .resp-grid-2 { grid-template-columns: 1fr !important; }
      .resp-grid-2-ratio { grid-template-columns: 1fr !important; }
      .resp-flex-between { flex-direction: column !important; align-items: flex-start !important; gap: 15px !important; }
  }
`;

const renderApp = (id, Component) => {
  const container = document.getElementById(id);
  if (container) {
    const root = createRoot(container);
    root.render(
      <>
        <style>{globalResponsiveCss}</style>
        <Component />
      </>
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
