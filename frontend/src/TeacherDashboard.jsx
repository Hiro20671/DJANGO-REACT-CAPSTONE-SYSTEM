import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

export default function TeacherDashboard() {
  const [stats, setStats] = useState({ total: 0, present: 0, absent: 0, risk: 0, milestonePct: 0, nutritionPct: 0 });
  const [behaviorChart, setBehaviorChart] = useState([1, 1, 1]);
  const [attendanceChart, setAttendanceChart] = useState({ labels: [], data: [] });

  useEffect(() => {
    // Fetch students and attendance from API, read the rest from prototype localStorage
    Promise.all([
      fetch('/api/children/').then(r => r.json()),
      fetch('/api/attendance/').then(r => r.json())
    ]).then(([students, attRecords]) => {
      
      const todayStr = new Date().toISOString().split('T')[0];
      const isToday = (dStr) => dStr === todayStr || (dStr && dStr.startsWith(todayStr));
      
      const mileDB = JSON.parse(localStorage.getItem('bmv3_milestones')) || {};
      const behDB = JSON.parse(localStorage.getItem('bmv3_behavior')) || {};
      const nutDB = JSON.parse(localStorage.getItem('bmv3_nutrition')) || {};

      // 1. Attendance & Total
      let presentCount = 0, absentCount = 0;
      students.forEach(st => {
        const todayAtt = attRecords.find(a => a.child === st.id && isToday(a.date));
        if (todayAtt) {
          if (todayAtt.status.toLowerCase() === 'present') presentCount++;
          else if (todayAtt.status.toLowerCase() === 'absent') absentCount++;
        }
      });

      // 2. Milestones & Risk Analysis
      let riskCount = 0;
      let totalAchieved = 0;
      const TOTAL_POSSIBLE = 16;
      
      students.forEach(st => {
        let isRisk = false;
        
        let mStudent = mileDB[st.id] || {};
        let ach = 0;
        Object.values(mStudent).forEach(dateRecord => {
           let dailyAch = 0;
           Object.values(dateRecord).forEach(v => { if (v === 'achieved') dailyAch++; });
           if (dailyAch > ach) ach = dailyAch;
        });
        totalAchieved += ach;
        if (ach / TOTAL_POSSIBLE < 0.6) isRisk = true;
        
        let bRecs = behDB[st.id] || [];
        let negCount = 0, posCount = 0;
        bRecs.forEach(r => {
          if(r.type === 'negative') negCount++;
          else if (r.type === 'positive') posCount++;
        });
        if (negCount > posCount && negCount > 0) isRisk = true;

        if (isRisk) riskCount++;
      });

      let avgMilestone = students.length > 0 ? Math.round((totalAchieved / (students.length * TOTAL_POSSIBLE)) * 100) : 0;

      // 3. Behavior Distribution Chart
      let gPos = 0, gNeu = 0, gNeg = 0;
      Object.values(behDB).forEach(bRecs => {
        bRecs.forEach(r => {
          if(r.type === 'positive') gPos++;
          else if(r.type === 'neutral') gNeu++;
          else if(r.type === 'negative') gNeg++;
        });
      });
      setBehaviorChart([gPos, gNeu, gNeg]);

      // 4. Attendance Trend Bar Chart (Last 7 Days)
      let attLabels = [];
      let attData = [];
      
      const isSameDay = (d1, d2Str) => {
        const d2 = new Date(d2Str);
        return d1.getFullYear() === d2.getFullYear() && d1.getMonth() === d2.getMonth() && d1.getDate() === d2.getDate();
      };

      for (let i = 6; i >= 0; i--) {
        let d = new Date();
        d.setDate(d.getDate() - i);
        let ds = d.toISOString().split('T')[0];
        attLabels.push(ds);
        
        let presentOnDay = 0;
        attRecords.forEach(a => {
           if (isSameDay(d, a.date) && a.status.toLowerCase() === 'present') {
               presentOnDay++;
           }
        });
        attData.push(presentOnDay);
      }
      
      setAttendanceChart({ labels: attLabels, data: attData });

      // 5. Average Nutrition Intake Number (Latest)
      let classNutritionPct = 0;
      let studentsRated = 0;
      students.forEach(st => {
          const nStudent = nutDB[st.id] || {};
          const todayNut = nStudent[todayStr];
          if (todayNut) {
              let pct = Math.round(( (todayNut.breakfast || 0) + (todayNut.lunch || 0) + (todayNut.snack || 0) ) / 3);
              classNutritionPct += pct;
              studentsRated++;
          }
      });
      let avgNut = studentsRated > 0 ? Math.round(classNutritionPct / studentsRated) : 0;

      setStats({ total: students.length, present: presentCount, absent: absentCount, risk: riskCount, milestonePct: avgMilestone, nutritionPct: avgNut });
    }).catch(err => console.error(err));
  }, []);

  const pieData = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{ data: behaviorChart, backgroundColor: ['#1cc88a', '#6c757d', '#e74a3b'], borderColor: '#063970', borderWidth: 2 }]
  };

  const attBarData = {
    labels: attendanceChart.labels,
    datasets: [{
      label: 'Students Present',
      data: attendanceChart.data,
      backgroundColor: '#1cc88a',
      borderRadius: 4
    }]
  };

  return (
    <div className="resp-fade-in">
      <div className="resp-flex-between" style={{ marginBottom: '25px' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: 0, color: '#333' }}>Operational Dashboard</h2>
          <p style={{ margin: '5px 0 0 0', color: '#777', fontSize: '0.9rem' }}>Real-time monitoring and analytics • {new Date().toLocaleDateString()}</p>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="resp-grid-4" style={{ marginBottom: '25px' }}>
        <a href="/children/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#fff', color: '#333', padding: '15px 20px', borderRadius: '8px', display: 'flex', flexDirection: 'column', height: '100%', cursor: 'pointer', border: '1px solid #000', position: 'relative' }}>
            <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '10px' }}>Total Enrolled</div>
            <div style={{ position: 'absolute', top: '15px', right: '20px', color: '#777', fontSize: '1rem' }}><i className="fa-solid fa-users"></i></div>
            <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{stats.total}</div>
            <div style={{ fontSize: '0.8rem', color: '#777', marginTop: 'auto' }}>Active children</div>
          </div>
        </a>
        <a href="/attendance/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#fff', color: '#333', padding: '15px 20px', borderRadius: '8px', display: 'flex', flexDirection: 'column', height: '100%', cursor: 'pointer', border: '1px solid #000', position: 'relative' }}>
            <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '10px' }}>Today's Attendance</div>
            <div style={{ position: 'absolute', top: '15px', right: '20px', color: '#4a90e2', fontSize: '1rem' }}><i className="fa-solid fa-calendar-check"></i></div>
            <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{stats.present}/{stats.total}</div>
            <div style={{ fontSize: '0.8rem', color: '#777', marginTop: 'auto' }}>{stats.absent} absent today, {Math.max(0, stats.total - (stats.present + stats.absent))} untracked</div>
          </div>
        </a>
        <a href="/behavior/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#fff', color: '#333', padding: '15px 20px', borderRadius: '8px', display: 'flex', flexDirection: 'column', border: stats.risk > 0 ? '2px solid #e74a3b' : '1px solid #000', height: '100%', cursor: 'pointer', position: 'relative' }}>
            <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '10px' }}>Children at Risk</div>
            <div style={{ position: 'absolute', top: '15px', right: '20px', color: stats.risk > 0 ? '#e74a3b' : '#f6c23e', fontSize: '1rem' }}><i className="fa-solid fa-triangle-exclamation"></i></div>
            <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{stats.risk}</div>
            <div style={{ fontSize: '0.8rem', color: '#777', marginTop: 'auto' }}>{stats.risk > 0 ? 'Require attention' : 'All clear'}</div>
          </div>
        </a>
        <a href="/milestones/" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div style={{ background: '#fff', color: '#333', padding: '15px 20px', borderRadius: '8px', display: 'flex', flexDirection: 'column', height: '100%', cursor: 'pointer', border: '1px solid #000', position: 'relative' }}>
            <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '10px' }}>Milestone Progress</div>
            <div style={{ position: 'absolute', top: '15px', right: '20px', color: '#4a90e2', fontSize: '1rem' }}><i className="fa-solid fa-chart-line"></i></div>
            <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{stats.milestonePct}%</div>
            <div style={{ fontSize: '0.8rem', color: '#777', marginTop: 'auto' }}>Overall completion</div>
          </div>
        </a>
      </div>

      {/* Row 2: Attendance Trend (Wide) + Behavior Distribution (Narrow) */}
      <div className="resp-grid-2-ratio" style={{ marginBottom: '20px' }}>
        <div style={{ background: '#fff', color: '#333', padding: '20px', borderRadius: '8px', border: '1px solid #000' }}>
          <div style={{ fontWeight: 600, marginBottom: '5px' }}>Attendance Trend (7 Days)</div>
          <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: '#777' }}>Daily attendance tracking</p>
          <div style={{ height: '220px', position: 'relative', width: '100%' }}>
            <Bar data={attBarData} options={{ maintainAspectRatio: false, scales: { x: { ticks: { color: '#333', font: { family: 'Montserrat' } }, grid: { display: false } }, y: { ticks: { stepSize: 1, color: '#333', font: { family: 'Montserrat' } }, grid: { color: '#eee' } } }, plugins: { legend: { display: false } } }} />
          </div>
        </div>
        
        <div style={{ background: '#fff', color: '#333', padding: '20px', borderRadius: '8px', border: '1px solid #000' }}>
          <div style={{ fontWeight: 600, marginBottom: '5px' }}>Behavior Distribution (All Time)</div>
           <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: '#777' }}>Behavioral patterns analysis</p>
          <div style={{ height: '220px', display: 'flex', justifyContent: 'center', position: 'relative', width: '100%' }}>
            <Pie data={pieData} options={{ maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#333', boxWidth: 15, font: { family: 'Montserrat', size: 10 } } } } }} />
          </div>
        </div>
      </div>

      {/* Row 3: Nutrition (Wide Big Number) + Risk Alerts (Narrow) */}
      <div className="resp-grid-2-ratio" style={{ marginBottom: '20px' }}>
         <div style={{ background: '#fff', color: '#333', padding: '20px', borderRadius: '8px', border: '1px solid #000', display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontWeight: 600, marginBottom: '5px' }}>Average Nutrition Intake (Last Recorded)</div>
          <p style={{ margin: '0 0 auto 0', fontSize: '0.8rem', color: '#777' }}>Meal consumption percentage</p>
          
          <div style={{ alignSelf: 'center', textAlign: 'center', marginBottom: '30px' }}>
              <div style={{ fontSize: '4.5rem', fontWeight: 900, color: '#f6c23e', lineHeight: '1' }}>{stats.nutritionPct}%</div>
              <div style={{ fontSize: '1rem', color: '#777', fontWeight: 600, marginTop: '10px' }}>Class Average Intake</div>
          </div>
        </div>

        <div style={{ background: '#fff', color: '#333', padding: '20px', borderRadius: '8px', border: '1px solid #000', display: 'flex', flexDirection: 'column' }}>
          <div style={{ fontWeight: 600, marginBottom: '10px' }}>Risk Alerts Status</div>
          <p style={{ margin: '0 0 auto 0', fontSize: '0.8rem', color: '#777' }}>System intelligence monitoring</p>
          
          <div style={{ alignSelf: 'center', textAlign: 'center', marginBottom: '20px', display:'flex', flexDirection:'column', alignItems:'center' }}>
            {stats.risk === 0 ? (
              <>
                <div style={{ width: '60px', height: '60px', borderRadius: '50%', border: '2px solid #1cc88a', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#1cc88a', fontSize: '1.8rem', marginBottom: '15px' }}>✓</div>
                <div style={{ fontWeight: 600, color: '#1cc88a' }}>All children performing well!</div>
              </>
            ) : (
               <>
                <div style={{ width: '60px', height: '60px', borderRadius: '50%', border: '2px solid #e74a3b', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#e74a3b', fontSize: '1.8rem', marginBottom: '15px' }}>!</div>
                <div style={{ fontWeight: 600, color: '#e74a3b' }}>{stats.risk} Child(ren) require teacher review!</div>
               </>
            )}
          </div>
        </div>
      </div>


    </div>
  );
}
