import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement } from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, ArcElement);

export default function TeacherDashboard() {
  const [stats, setStats] = useState({ total: 0, present: 0, absent: 0, risk: 0, milestonePct: 0 });
  const [behaviorChart, setBehaviorChart] = useState([1, 1, 1]);
  const [nutritionChart, setNutritionChart] = useState({ labels: [], data: [] });

  useEffect(() => {
    // Read all feature databases from prototype storage
    const students = JSON.parse(localStorage.getItem('bmv3_students')) || [];
    const attDB = JSON.parse(localStorage.getItem('bmv3_attendance')) || {};
    const mileDB = JSON.parse(localStorage.getItem('bmv3_milestones')) || {};
    const behDB = JSON.parse(localStorage.getItem('bmv3_behavior')) || {};
    const nutDB = JSON.parse(localStorage.getItem('bmv3_nutrition')) || {};

    // 1. Attendance & Total
    const todayStr = new Date().toISOString().split('T')[0];
    let presentCount = 0, absentCount = 0;
    if (attDB[todayStr]) {
      students.forEach(st => {
        if (attDB[todayStr][st.id] === 'present') presentCount++;
        else if (attDB[todayStr][st.id] === 'absent') absentCount++;
      });
    }

    // 2. Milestones & Risk Analysis
    let riskCount = 0;
    let totalAchieved = 0;
    const TOTAL_POSSIBLE = 16;
    
    students.forEach(st => {
      let isRisk = false;
      
      // Milestone risk
      let mRecs = mileDB[st.id] || {};
      let ach = 0;
      Object.keys(mRecs).forEach(k => { if (mRecs[k] === 'achieved') ach++; });
      totalAchieved += ach;
      if (ach / TOTAL_POSSIBLE < 0.6) isRisk = true; // Delayed development trigger
      
      // Behavior risk
      let bRecs = behDB[st.id] || [];
      let negCount = 0, posCount = 0;
      bRecs.forEach(r => {
        if(r.type === 'negative') negCount++;
        else if (r.type === 'positive') posCount++;
      });
      if (negCount > posCount && negCount > 0) isRisk = true; // More negative than positive

      if (isRisk) riskCount++;
    });

    let avgMilestone = students.length > 0 ? Math.round((totalAchieved / (students.length * TOTAL_POSSIBLE)) * 100) : 0;

    // 3. Behavior Distribution Chart
    let gPos = 0, gNeu = 0, gNeg = 0;
    Object.values(behDB).forEach(records => {
      records.forEach(r => {
        if(r.type === 'positive') gPos++;
        else if(r.type === 'neutral') gNeu++;
        else if(r.type === 'negative') gNeg++;
      });
    });
    setBehaviorChart([gPos || 18, gNeu || 11, gNeg || 2]); // fallback mockup data if completely empty

    // 4. Nutrition Line Chart (Last 7 Days)
    let labels = [];
    let nutData = [];
    let hasNutData = false;
    for (let i = 6; i >= 0; i--) {
      let d = new Date();
      d.setDate(d.getDate() - i);
      let ds = d.toISOString().split('T')[0];
      labels.push(d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
      
      // Calculate average class nutrition % for this day
      let dayTotalPct = 0;
      let studentsRated = 0;
      students.forEach(st => {
        if (nutDB[st.id] && nutDB[st.id][ds]) {
          let mealObj = nutDB[st.id][ds];
          let eaten = 0;
          if (mealObj.b === 'true' || mealObj.b === true) eaten++;
          if (mealObj.s1 === 'true' || mealObj.s1 === true) eaten++;
          if (mealObj.l === 'true' || mealObj.l === true) eaten++;
          if (mealObj.s2 === 'true' || mealObj.s2 === true) eaten++;
          dayTotalPct += (eaten / 4) * 100;
          studentsRated++;
          hasNutData = true;
        }
      });
      
      nutData.push(studentsRated > 0 ? Math.round(dayTotalPct / studentsRated) : 0);
    }
    
    if(!hasNutData){
        nutData = [90, 92, 90, 0, 0, 88, 88]; // fallback if empty
    }
    setNutritionChart({ labels, data: nutData });

    setStats({ total: students.length, present: presentCount, absent: absentCount, risk: riskCount, milestonePct: avgMilestone });
  }, []);

  const pieData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{ data: behaviorChart, backgroundColor: ['#1cc88a', '#6c757d', '#e74a3b'], borderColor: '#063970', borderWidth: 2 }]
  };

  const lineData = {
    labels: nutritionChart.labels,
    datasets: [{
      label: 'Average Nutrition Intake (%)',
      data: nutritionChart.data,
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
            <div style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', justifyContent:'space-between' }}>Total Enrolled <i className="fa-solid fa-users" style={{opacity:0.8}}></i></div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{stats.total}</div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)' }}>Active children</div>
          </div>
        </a>
        <a href="/attendance/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#063970', color: '#fff', padding: '15px', borderRadius: '10px', height: '100%', cursor: 'pointer', border: 'none' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', justifyContent:'space-between' }}>Today's Attendance <i className="fa-solid fa-calendar-check" style={{color:'#4a90e2'}}></i></div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{stats.present}/{stats.total}</div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)' }}>{stats.absent} absent today, {Math.max(0, stats.total - (stats.present + stats.absent))} untracked</div>
          </div>
        </a>
        <a href="/behavior/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#063970', color: '#fff', padding: '15px', borderRadius: '10px', border: '1px solid ' + (stats.risk > 0 ? '#e74a3b' : 'transparent'), height: '100%', cursor: 'pointer' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', justifyContent:'space-between' }}>Children at Risk <i className="fa-solid fa-triangle-exclamation" style={{color: stats.risk > 0 ? '#e74a3b' : '#f6c23e'}}></i></div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{stats.risk}</div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)' }}>{stats.risk > 0 ? 'Require attention' : 'All clear'}</div>
          </div>
        </a>
        <a href="/milestones/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#063970', color: '#fff', padding: '15px', borderRadius: '10px', height: '100%', cursor: 'pointer', border: 'none' }}>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', display: 'flex', justifyContent:'space-between' }}>Milestone Progress <i className="fa-solid fa-chart-line" style={{color:'#f6c23e'}}></i></div>
            <div style={{ fontSize: '2rem', fontWeight: 800 }}>{stats.milestonePct}%</div>
            <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)' }}>Overall completion</div>
          </div>
        </a>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
        <div style={{ background: '#063970', color: '#fff', padding: '20px', borderRadius: '10px', border: 'none' }}>
          <div style={{ fontWeight: 600, marginBottom: '20px' }}>Behavior Distribution (All Time)</div>
          <div style={{ height: '200px', display: 'flex', justifyContent: 'center' }}>
            <Pie data={pieData} options={{ maintainAspectRatio: false, plugins: { legend: { labels: { color: '#fff' } } } }} />
          </div>
        </div>
        <div style={{ background: '#063970', color: '#fff', padding: '20px', borderRadius: '10px', border: 'none' }}>
          <div style={{ fontWeight: 600, marginBottom: '20px' }}>Average Nutrition Intake (Last 7 Days)</div>
          <div style={{ height: '200px' }}>
            <Line data={lineData} options={{ maintainAspectRatio: false, scales: { x: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } }, y: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } } }, plugins: { legend: { labels: { color: '#fff' } } } }} />
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.5fr) minmax(0, 1fr)', gap: '15px', marginBottom: '20px' }}>
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
        
        <div style={{ background: '#063970', color: '#fff', padding: '20px', borderRadius: '10px', border: 'none', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
          <div style={{ fontWeight: 600, marginBottom: '20px', alignSelf: 'flex-start' }}>Risk Alerts Status</div>
          {stats.risk === 0 ? (
            <>
              <div style={{ width: '50px', height: '50px', borderRadius: '50%', border: '2px solid #1cc88a', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#1cc88a', fontSize: '1.5rem', marginBottom: '15px' }}>✓</div>
              <div style={{ fontWeight: 600, color: '#1cc88a' }}>All children performing well!</div>
            </>
          ) : (
             <>
              <div style={{ width: '50px', height: '50px', borderRadius: '50%', border: '2px solid #e74a3b', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#e74a3b', fontSize: '1.5rem', marginBottom: '15px' }}>!</div>
              <div style={{ fontWeight: 600, color: '#e74a3b' }}>{stats.risk} Child(ren) require teacher review!</div>
             </>
          )}
        </div>
      </div>
    </div>
  );
}
