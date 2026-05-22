import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement, Filler } from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement, Filler);

export default function TeacherDashboard() {
  const [stats, setStats] = useState({ total: 0, present: 0, absent: 0, pending: 0, milestonePct: 0, nutritionPct: 0 });
  const [attendanceChart, setAttendanceChart] = useState({ labels: [], data: [] });
  const [nutritionChart, setNutritionChart] = useState({ finished: 0, someLeft: 0, notEaten: 0 });
  const [eccdChart, setEccdChart] = useState({ labels: [], data1: [], data2: [], data3: [] });
  
  // School Year Management
  const [schoolYears, setSchoolYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState('');
  
  // Mobile Layout Management
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [mobileTab, setMobileTab] = useState('overview'); // 'overview', 'performance', 'trends'

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const loadDashboardData = (yearId = '') => {
    const qs = yearId ? `?school_year=${yearId}` : '';
    Promise.all([
      fetch(`/api/children/${qs}`).then(r => r.json()),
      fetch(`/api/attendance/${qs}`).then(r => r.json()),
      fetch(`/api/nutrition/${qs}`).then(r => r.json()),
      fetch(`/api/milestones/${qs}`).then(r => r.json()),
      fetch('/api/nutrition-analytics/').then(r => r.json()),
      fetch('/api/eccd-domains/').then(r => r.json()),
      fetch('/api/eccd-milestones/').then(r => r.json()),
      fetch(`/api/eccd-assessments/${qs}`).then(r => r.json()),
      fetch('/api/eccd-scores/').then(r => r.json())
    ]).then(([students, attRecords, nutRecords, mileRecords, nutAnalytics, domainsList, milestonesList, allAss, allSco]) => {
      const todayStr = new Date().toISOString().split('T')[0];
      const isToday = (dStr) => dStr === todayStr || (dStr && dStr.startsWith(todayStr));
      
      let presentCount = 0, absentCount = 0;
      let pendingCount = 0;
      let enrolledStudents = [];

      students.forEach(st => {
        if (st.enrollment_status === 'Pending') {
            pendingCount++;
        } else if (st.enrollment_status === 'Enrolled') {
            enrolledStudents.push(st);
            const todayAtt = attRecords.find(a => a.child === st.id && isToday(a.date));
            if (todayAtt) {
              if (todayAtt.status.toLowerCase() === 'present') presentCount++;
              else if (todayAtt.status.toLowerCase() === 'absent') absentCount++;
            }
        }
      });

      // Milestones
      let totalMilestonePct = 0;
      enrolledStudents.forEach(st => {
        totalMilestonePct += (st.stats && typeof st.stats.milestones !== 'undefined') ? st.stats.milestones : 0;
      });
      let avgMilestone = enrolledStudents.length > 0 ? Math.round(totalMilestonePct / enrolledStudents.length) : 0;

      // Attendance Trend (Last 7 Days)
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

      // Nutrition Intake Number
      let classNutritionPct = 0;
      let studentsRated = 0;
      enrolledStudents.forEach(st => {
          const todayNut = nutRecords.find(n => n.child === st.id && isToday(n.date));
          if (todayNut && todayNut.snack_status) {
              let pct = 0;
              if (todayNut.snack_status === 'Finished') pct = 100;
              else if (todayNut.snack_status === 'Some Left') pct = 50;
              
              classNutritionPct += pct;
              studentsRated++;
          }
      });
      let avgNut = studentsRated > 0 ? Math.round(classNutritionPct / studentsRated) : 0;
      
      setNutritionChart({
          finished: nutAnalytics.weekly['Finished'] || 0,
          someLeft: nutAnalytics.weekly['Some Left'] || 0,
          notEaten: nutAnalytics.weekly['Not Eaten'] || 0
      });

      // ECCD Chart Logic
      const eccdLabels = domainsList.map(d => d.name);
      const d1 = [], d2 = [], d3 = [];

      domainsList.forEach(domain => {
          const dMilestones = milestonesList.filter(m => m.domain === domain.id);
          const mIds = dMilestones.map(m => m.id);
          const totalPossible = enrolledStudents.length * dMilestones.length;

          function getPeriodPct(periodName) {
              if(totalPossible === 0) return 0;
              const periodAssIds = allAss.filter(a => a.assessment_period === periodName && enrolledStudents.find(c => c.id === a.child)).map(a => a.id);
              const scored = allSco.filter(s => periodAssIds.includes(s.assessment) && mIds.includes(s.milestone) && s.teacher_score === 1).length;
              return Math.round((scored / totalPossible) * 100);
          }

          d1.push(getPeriodPct('1st'));
          d2.push(getPeriodPct('2nd'));
          d3.push(getPeriodPct('3rd'));
      });
      setEccdChart({ labels: eccdLabels, data1: d1, data2: d2, data3: d3 });

      setStats({ total: enrolledStudents.length, present: presentCount, absent: absentCount, pending: pendingCount, milestonePct: avgMilestone, nutritionPct: avgNut });
    }).catch(err => console.error(err));
  };

  useEffect(() => {
    // Initial load: fetch school years
    const archiveId = sessionStorage.getItem('bmv3_archive_year_id');
    fetch('/api/school-years/')
      .then(r => r.json())
      .then(years => {
          setSchoolYears(years);
          if (archiveId && years.some(y => y.id == archiveId)) {
              setSelectedYear(archiveId);
              loadDashboardData(archiveId);
          } else {
              const activeYear = years.find(y => y.is_active);
              if (activeYear) {
                  setSelectedYear(activeYear.id);
                  loadDashboardData(activeYear.id);
              } else {
                  loadDashboardData('');
              }
          }
      })
      .catch(err => {
          console.error(err);
          loadDashboardData('');
      });
  }, []);

  const handleYearChange = (e) => {
      const yId = e.target.value;
      if (!yId) {
          sessionStorage.removeItem('bmv3_archive_year_id');
          sessionStorage.removeItem('bmv3_archive_year_name');
          window.location.reload();
          return;
      }
      const selectedObj = schoolYears.find(y => y.id == yId);
      if (selectedObj) {
          if (selectedObj.is_active) {
              sessionStorage.removeItem('bmv3_archive_year_id');
              sessionStorage.removeItem('bmv3_archive_year_name');
          } else {
              sessionStorage.setItem('bmv3_archive_year_id', selectedObj.id);
              sessionStorage.setItem('bmv3_archive_year_name', selectedObj.name);
          }
          window.location.reload();
      }
  };

  const handleResetToActive = () => {
      sessionStorage.removeItem('bmv3_archive_year_id');
      sessionStorage.removeItem('bmv3_archive_year_name');
      window.location.reload();
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

  const nutBarData = {
      labels: ['Finished', 'Some Left', 'Not Eaten'],
      datasets: [{
          label: 'Snack Status (7 Days)',
          data: [nutritionChart.finished, nutritionChart.someLeft, nutritionChart.notEaten],
          backgroundColor: ['#1cc88a', '#f6c23e', '#e74a3b'],
          borderRadius: 4
      }]
  };

  const eccdLineData = {
      labels: eccdChart.labels,
      datasets: [
          { label: '1st Evaluation', data: eccdChart.data1, borderColor: '#e74a3b', backgroundColor: 'rgba(231, 74, 59, 0.1)', tension: 0.3, fill: true },
          { label: '2nd Evaluation', data: eccdChart.data2, borderColor: '#f6c23e', backgroundColor: 'rgba(246, 194, 62, 0.1)', tension: 0.3, fill: true },
          { label: '3rd Evaluation', data: eccdChart.data3, borderColor: '#1cc88a', backgroundColor: 'rgba(28, 200, 138, 0.1)', tension: 0.3, fill: true }
      ]
  };

  const isHistorical = schoolYears.find(y => y.id == selectedYear) && !schoolYears.find(y => y.id == selectedYear).is_active;

  return (
    <div className="resp-fade-in">
      {isHistorical && (
          <div style={{ background: '#f6c23e', color: '#fff', padding: '10px 15px', borderRadius: '8px', marginBottom: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div><i className="fa-solid fa-clock-rotate-left" style={{marginRight: '10px'}}></i><strong>Historical View:</strong> You are viewing data from a past school year.</div>
              <button onClick={handleResetToActive} style={{background: 'rgba(0,0,0,0.2)', border: 'none', color: '#fff', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer', fontWeight: 600}}>Back to Current</button>
          </div>
      )}

      <div className="resp-flex-between" style={{ marginBottom: '25px', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: 0, color: '#333' }}>Operational Dashboard</h2>
          <p style={{ margin: '5px 0 0 0', color: '#777', fontSize: '0.9rem' }}>Real-time monitoring and analytics • {new Date().toLocaleDateString()}</p>
        </div>
        <div>
            <select value={selectedYear} onChange={handleYearChange} style={{ padding: '8px 15px', borderRadius: '6px', border: '1px solid #ccc', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer' }}>
                <option value="">All Time / Default</option>
                {schoolYears.map(y => (
                    <option key={y.id} value={y.id}>{y.name} {y.is_active ? '(Active)' : '(Archived)'}</option>
                ))}
            </select>
        </div>
      </div>

      {/* Mobile Tab Switcher */}
      <div className="resp-mobile-tabs">
        <button className={`resp-mobile-tab-btn ${mobileTab === 'overview' ? 'active' : ''}`} onClick={() => setMobileTab('overview')}>Overview</button>
        <button className={`resp-mobile-tab-btn ${mobileTab === 'performance' ? 'active' : ''}`} onClick={() => setMobileTab('performance')}>Performance</button>
        <button className={`resp-mobile-tab-btn ${mobileTab === 'trends' ? 'active' : ''}`} onClick={() => setMobileTab('trends')}>Trends</button>
      </div>

      {/* KPI Cards Row */}
      {(!isMobile || mobileTab === 'overview') && (
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
              <div style={{ fontSize: '0.8rem', color: '#777', marginTop: 'auto' }}>{stats.absent} absent today</div>
            </div>
          </a>
          <a href="/children/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div style={{ background: '#fff', color: '#333', padding: '15px 20px', borderRadius: '8px', display: 'flex', flexDirection: 'column', border: stats.pending > 0 ? '2px solid #f6c23e' : '1px solid #000', height: '100%', cursor: 'pointer', position: 'relative' }}>
              <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '10px' }}>Pending Enrollments</div>
              <div style={{ position: 'absolute', top: '15px', right: '20px', color: stats.pending > 0 ? '#f6c23e' : '#1cc88a', fontSize: '1rem' }}><i className="fa-solid fa-file-signature"></i></div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{stats.pending}</div>
              <div style={{ fontSize: '0.8rem', color: '#777', marginTop: 'auto' }}>{stats.pending > 0 ? 'Requires your approval' : 'All caught up'}</div>
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
      )}

      {/* ECCD Chart Row */}
      {(!isMobile || mobileTab === 'performance') && (
        <div style={{ background: '#fff', color: '#333', padding: '20px', borderRadius: '8px', border: '1px solid #000', marginBottom: '25px' }}>
            <div style={{ fontWeight: 600, marginBottom: '5px' }}>Classroom Average Performance by Domain & Period</div>
            <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: '#777' }}>Average completion percentage across 7 ECCD domains</p>
            <div style={{ height: '250px', position: 'relative', width: '100%' }}>
              <Line data={eccdLineData} options={{ maintainAspectRatio: false, scales: { x: { ticks: { color: '#333', font: { family: 'Montserrat' } }, grid: { display: false } }, y: { beginAtZero: true, max: 100, ticks: { color: '#333', font: { family: 'Montserrat' } }, grid: { color: '#eee' } } }, plugins: { legend: { position: 'top', labels: { font: { family: 'Montserrat' }, color: '#333' } } } }} />
            </div>
        </div>
      )}

      {/* Row 2 */}
      {(!isMobile || mobileTab === 'trends' || mobileTab === 'overview') && (
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '20px' }}>
          {(!isMobile || mobileTab === 'trends') && (
            <div style={{ background: '#fff', color: '#333', padding: '20px', borderRadius: '8px', border: '1px solid #000' }}>
              <div style={{ fontWeight: 600, marginBottom: '5px' }}>Attendance Trend (7 Days)</div>
              <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: '#777' }}>Daily attendance tracking</p>
              <div style={{ height: '220px', position: 'relative', width: '100%' }}>
                <Bar data={attBarData} options={{ maintainAspectRatio: false, scales: { x: { ticks: { color: '#333', font: { family: 'Montserrat' } }, grid: { display: false } }, y: { ticks: { stepSize: 1, color: '#333', font: { family: 'Montserrat' } }, grid: { color: '#eee' } } }, plugins: { legend: { display: false } } }} />
              </div>
            </div>
          )}
          
          {(!isMobile || mobileTab === 'trends') && (
            <div style={{ background: '#fff', color: '#333', padding: '20px', borderRadius: '8px', border: '1px solid #000', display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontWeight: 600, marginBottom: '5px' }}>Nutrition Analytics (7 Days)</div>
              <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: '#777' }}>Weekly snack consumption summary</p>
              <div style={{ height: '220px', position: 'relative', width: '100%' }}>
                <Bar data={nutBarData} options={{ maintainAspectRatio: false, scales: { x: { ticks: { color: '#333', font: { family: 'Montserrat' } }, grid: { display: false } }, y: { ticks: { stepSize: 1, color: '#333', font: { family: 'Montserrat' } }, grid: { color: '#eee' } } }, plugins: { legend: { display: false } } }} />
              </div>
            </div>
          )}

          {(!isMobile || mobileTab === 'overview') && (
            <div style={{ background: '#fff', color: '#333', padding: '20px', borderRadius: '8px', border: '1px solid #000' }}>
              <div style={{ fontWeight: 600, marginBottom: '5px' }}>Today's Attendance</div>
              <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: '#777' }}>Present vs Absent distribution</p>
              <div style={{ height: '220px', position: 'relative', width: '100%', display: 'flex', justifyContent: 'center' }}>
                <Pie 
                  data={{
                      labels: ['Present', 'Absent'],
                      datasets: [{
                          data: [stats.present, stats.absent],
                          backgroundColor: ['#1cc88a', '#e74a3b'],
                          borderWidth: 1
                      }]
                  }} 
                  options={{ maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { font: { family: 'Montserrat' }, color: '#333' } } } }} 
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
