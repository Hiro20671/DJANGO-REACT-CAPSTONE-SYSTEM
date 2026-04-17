import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement } from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, ArcElement);

export default function TeacherDashboard() {
  const [stats, setStats] = useState({ total: 0, present: 0, absent: 0 });

  useEffect(() => {
    fetch('/api/teacher/dashboard/')
      .then(res => {
        if(res.ok) return res.json();
        throw new Error('Network response was not ok.');
      })
      .then(data => {
        setStats({
          total: data.total_children || 0,
          present: data.attendance?.present || 0,
          absent: data.attendance?.absent || 0
        });
      })
      .catch(error => console.error('Error fetching dashboard stats:', error));
  }, []);

  const pieData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{ data: [18, 11, 2], backgroundColor: ['#1cc88a', '#6c757d', '#e74a3b'] }]
  };

  const lineData = {
    labels: ['Mar 18', 'Mar 19', 'Mar 20', 'Mar 21', 'Mar 22', 'Mar 23', 'Mar 24'],
    datasets: [{
      label: 'Average Nutrition Intake (%)',
      data: [90, 92, 90, 0, 0, 88, 88],
      borderColor: '#f6c23e', fill: false, tension: 0.4
    }]
  };

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-in' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: 0, color: '#333' }}>Operational Dashboard</h2>
          <p style={{ margin: '5px 0 0 0', color: '#777', fontSize: '0.9rem' }}>Real-time monitoring and analytics • {new Date().toLocaleDateString()}</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px', marginBottom: '20px' }}>
        <a href="/children/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#063970', color: '#fff', padding: '15px', borderRadius: '10px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', height: '100%', cursor: 'pointer', border: 'none' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Total Enrolled</div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{stats.total}</div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)' }}>Active children</div>
          </div>
        </a>
        <a href="/attendance/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#063970', color: '#fff', padding: '15px', borderRadius: '10px', height: '100%', cursor: 'pointer', border: 'none' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Today's Attendance</div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{stats.present}/{stats.total}</div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)' }}>{stats.absent} absent today</div>
          </div>
        </a>
        <a href="/behavior/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#063970', color: '#fff', padding: '15px', borderRadius: '10px', border: '2px solid #e74a3b', height: '100%', cursor: 'pointer' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Children at Risk</div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>0</div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)' }}>Require attention</div>
          </div>
        </a>
        <a href="/milestones/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#063970', color: '#fff', padding: '15px', borderRadius: '10px', height: '100%', cursor: 'pointer', border: 'none' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Milestone Progress</div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>71.3%</div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)' }}>Overall completion</div>
          </div>
        </a>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
        <div style={{ background: '#063970', color: '#fff', padding: '20px', borderRadius: '10px', border: 'none' }}>
          <div style={{ fontWeight: 600, marginBottom: '20px' }}>Behavior Distribution (30 Days)</div>
          <div style={{ height: '200px', display: 'flex', justifyContent: 'center' }}>
            <Pie data={pieData} options={{ maintainAspectRatio: false, plugins: { legend: { labels: { color: '#fff' } } } }} />
          </div>
        </div>
        <div style={{ background: '#063970', color: '#fff', padding: '20px', borderRadius: '10px', border: 'none' }}>
          <div style={{ fontWeight: 600, marginBottom: '20px' }}>Average Nutrition Intake (7 Days)</div>
          <div style={{ height: '200px' }}>
            <Line data={lineData} options={{ maintainAspectRatio: false, scales: { x: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } }, y: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } } }, plugins: { legend: { labels: { color: '#fff' } } } }} />
          </div>
        </div>
      </div>

      <div style={{ background: '#fff', padding: '20px', borderRadius: '10px', border: '1px solid #ddd' }}>
        <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>System Status & Automation</h4>
        <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: '#777' }}>Real-time monitoring systems</p>
        <div style={{ display: 'flex', gap: '15px' }}>
          {['Access Control', 'Attendance Monitor', 'Behavior Analysis', 'Nutrition Tracking'].map(sys => (
            <div key={sys} style={{ flex: 1, border: '1px solid #ddd', padding: '10px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ color: '#1cc88a' }}>✓</div>
              <div>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#333' }}>{sys}</div>
                <div style={{ fontSize: '0.7rem', color: '#888' }}>Active</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
