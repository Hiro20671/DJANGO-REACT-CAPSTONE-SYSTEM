import React from 'react';
import { createRoot } from 'react-dom/client';
import TeacherDashboard from './TeacherDashboard';
import ParentDashboard from './ParentDashboard';
import ChildrenList from './ChildrenList';

const renderApp = (id, Component) => {
  const container = document.getElementById(id);
  if (container) {
    const root = createRoot(container);
    root.render(<Component />);
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
