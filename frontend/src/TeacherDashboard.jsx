import React, { useState, useEffect } from 'react';

// Custom SVG Chart Components

function SVGDonutChart({ present, absent }) {
  const total = present + absent;
  const presentPct = total > 0 ? Math.round((present / total) * 100) : 0;
  const absentPct = total > 0 ? Math.round((absent / total) * 100) : 0;

  const radius = 40;
  const circ = 2 * Math.PI * radius; 
  const presentOffset = circ - (presentPct / 100) * circ;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
      <svg width="180" height="180" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r={radius} fill="none" stroke="var(--chart-grid)" strokeWidth="10" />
        {absent > 0 && (
          <circle 
            cx="50" 
            cy="50" 
            r={radius} 
            fill="none" 
            stroke="#e74a3b" 
            strokeWidth="10" 
            strokeDasharray={circ} 
            strokeDashoffset={0} 
            transform="rotate(-90 50 50)"
          />
        )}
        {present > 0 && (
          <circle 
            cx="50" 
            cy="50" 
            r={radius} 
            fill="none" 
            stroke="#1cc88a" 
            strokeWidth="10" 
            strokeDasharray={circ} 
            strokeDashoffset={presentOffset} 
            transform="rotate(-90 50 50)"
            strokeLinecap="round"
          />
        )}
        <text x="50" y="47" textAnchor="middle" dominantBaseline="middle" style={{ fontSize: '12px', fontWeight: 800, fontFamily: 'Montserrat', fill: 'var(--text-primary)' }}>
          {presentPct}%
        </text>
        <text x="50" y="62" textAnchor="middle" dominantBaseline="middle" style={{ fontSize: '6px', fontWeight: 600, fontFamily: 'Montserrat', fill: 'var(--text-muted)', textTransform: 'uppercase' }}>
          Present
        </text>
      </svg>
      <div style={{ display: 'flex', gap: '15px', marginTop: '10px', fontSize: '0.85rem', fontFamily: 'Montserrat', fontWeight: 600 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#1cc88a' }}></span>
          Present: {present}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#e74a3b' }}></span>
          Absent: {absent}
        </div>
      </div>
    </div>
  );
}

function SVGBarChart({ labels, data, total }) {
  const maxVal = Math.max(1, ...data, total || 1);
  const chartHeight = 160;
  const chartWidth = 400;
  const padding = { top: 20, right: 15, bottom: 30, left: 30 };
  const graphWidth = chartWidth - padding.left - padding.right;
  const graphHeight = chartHeight - padding.top - padding.bottom;

  const barWidth = Math.max(12, (graphWidth / (labels.length || 1)) - 12);

  return (
    <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ fontFamily: 'Montserrat' }}>
      {[0, 1, 2, 3, 4].map((i) => {
        const yVal = Math.round((maxVal / 4) * i);
        const yPos = padding.top + graphHeight - (yVal / maxVal) * graphHeight;
        return (
          <g key={i}>
            <text x={padding.left - 8} y={yPos + 3} textAnchor="end" style={{ fontSize: '8px', fill: 'var(--chart-text)', fontWeight: 600 }}>
              {yVal}
            </text>
            <line x1={padding.left} y1={yPos} x2={chartWidth - padding.right} y2={yPos} stroke="var(--chart-grid)" strokeWidth="1" strokeDasharray="2,2" />
          </g>
        );
      })}

      {data.map((val, i) => {
        const colWidth = graphWidth / data.length;
        const xPos = padding.left + i * colWidth + (colWidth - barWidth) / 2;
        const barHeight = (val / maxVal) * graphHeight;
        const yPos = padding.top + graphHeight - barHeight;

        let displayLabel = labels[i] || '';
        if (displayLabel.includes('-')) {
          const parts = displayLabel.split('-');
          displayLabel = `${parts[1]}-${parts[2]}`;
        }

        return (
          <g key={i}>
            <rect 
              x={xPos} 
              y={yPos} 
              width={barWidth} 
              height={barHeight} 
              fill="url(#barGradGreen)" 
              rx="3"
            />
            <text 
              x={xPos + barWidth / 2} 
              y={yPos - 4} 
              textAnchor="middle" 
              style={{ fontSize: '8px', fontWeight: 800, fill: 'var(--text-primary)' }}
            >
              {val}
            </text>
            <text 
              x={padding.left + i * colWidth + colWidth / 2} 
              y={chartHeight - 10} 
              textAnchor="middle" 
              style={{ fontSize: '8px', fill: 'var(--chart-text)', fontWeight: 600 }}
            >
              {displayLabel}
            </text>
          </g>
        );
      })}

      <defs>
        <linearGradient id="barGradGreen" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#34d399" />
          <stop offset="100%" stopColor="#059669" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function SVGNutritionBarChart({ finished, someLeft, notEaten }) {
  const maxVal = Math.max(1, finished, someLeft, notEaten);
  const chartHeight = 160;
  const chartWidth = 400;
  const padding = { top: 20, right: 15, bottom: 30, left: 30 };
  const graphWidth = chartWidth - padding.left - padding.right;
  const graphHeight = chartHeight - padding.top - padding.bottom;

  const barLabels = ['Finished', 'Some Left', 'Not Eaten'];
  const barValues = [finished, someLeft, notEaten];
  const barColors = ['url(#nutGradGreen)', 'url(#nutGradYellow)', 'url(#nutGradRed)'];
  
  const barWidth = 45;
  const colWidth = graphWidth / 3;

  return (
    <svg width="100%" height="100%" viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ fontFamily: 'Montserrat' }}>
      {[0, 1, 2, 3, 4].map((i) => {
        const yVal = Math.round((maxVal / 4) * i);
        const yPos = padding.top + graphHeight - (yVal / maxVal) * graphHeight;
        return (
          <g key={i}>
            <text x={padding.left - 8} y={yPos + 3} textAnchor="end" style={{ fontSize: '8px', fill: 'var(--chart-text)', fontWeight: 600 }}>
              {yVal}
            </text>
            <line x1={padding.left} y1={yPos} x2={chartWidth - padding.right} y2={yPos} stroke="var(--chart-grid)" strokeWidth="1" strokeDasharray="2,2" />
          </g>
        );
      })}

      {barValues.map((val, i) => {
        const xPos = padding.left + i * colWidth + (colWidth - barWidth) / 2;
        const barHeight = (val / maxVal) * graphHeight;
        const yPos = padding.top + graphHeight - barHeight;

        return (
          <g key={i}>
            <rect 
              x={xPos} 
              y={yPos} 
              width={barWidth} 
              height={barHeight} 
              fill={barColors[i]} 
              rx="3"
            />
            <text 
              x={xPos + barWidth / 2} 
              y={yPos - 4} 
              textAnchor="middle" 
              style={{ fontSize: '8px', fontWeight: 800, fill: 'var(--text-primary)' }}
            >
              {val}
            </text>
            <text 
              x={padding.left + i * colWidth + colWidth / 2} 
              y={chartHeight - 10} 
              textAnchor="middle" 
              style={{ fontSize: '8px', fill: 'var(--chart-text)', fontWeight: 600 }}
            >
              {barLabels[i]}
            </text>
          </g>
        );
      })}

      <defs>
        <linearGradient id="nutGradGreen" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#34d399" />
          <stop offset="100%" stopColor="#059669" />
        </linearGradient>
        <linearGradient id="nutGradYellow" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#fbbf24" />
          <stop offset="100%" stopColor="#d97706" />
        </linearGradient>
        <linearGradient id="nutGradRed" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#f87171" />
          <stop offset="100%" stopColor="#dc2626" />
        </linearGradient>
      </defs>
    </svg>
  );
}

function SVGEccdDomainPerformanceChart({ labels, data1, data2, data3 }) {
  const chartHeight = 220;
  const chartWidth = 750;
  const padding = { top: 20, right: 30, bottom: 40, left: 35 };
  const graphWidth = chartWidth - padding.left - padding.right;
  const graphHeight = chartHeight - padding.top - padding.bottom;

  const count = labels.length || 7;
  const getCoordinates = (dataset) => {
    return dataset.map((val, i) => {
      const x = padding.left + i * (graphWidth / (count - 1 || 1));
      const y = padding.top + graphHeight - (val / 100) * graphHeight;
      return { x, y, val };
    });
  };

  const pts1 = getCoordinates(data1);
  const pts2 = getCoordinates(data2);
  const pts3 = getCoordinates(data3);

  const getPathD = (pts) => {
    if (pts.length === 0) return '';
    return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  };

  const getAreaD = (pts) => {
    if (pts.length === 0) return '';
    const linePath = getPathD(pts);
    return `${linePath} L ${pts[pts.length - 1].x} ${padding.top + graphHeight} L ${pts[0].x} ${padding.top + graphHeight} Z`;
  };

  const renderDataset = (pts, strokeColor, fillGrad) => {
    if (pts.length === 0) return null;
    return (
      <g>
        <path d={getAreaD(pts)} fill={fillGrad} opacity="0.1" />
        <path d={getPathD(pts)} fill="none" stroke={strokeColor} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        {pts.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r="4.5" fill="var(--bg-card)" stroke={strokeColor} strokeWidth="2" />
            <circle cx={p.x} cy={p.y} r="2" fill={strokeColor} />
            <text x={p.x} y={p.y - 8} textAnchor="middle" style={{ fontSize: '8px', fontWeight: 800, fill: strokeColor }}>
              {p.val}%
            </text>
          </g>
        ))}
      </g>
    );
  };

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <div style={{ minWidth: '700px' }}>
        <svg width="100%" height={chartHeight} viewBox={`0 0 ${chartWidth} ${chartHeight}`} style={{ fontFamily: 'Montserrat' }}>
          {[0, 25, 50, 75, 100].map((val) => {
            const yPos = padding.top + graphHeight - (val / 100) * graphHeight;
            return (
              <g key={val}>
                <text x={padding.left - 8} y={yPos + 3} textAnchor="end" style={{ fontSize: '8px', fill: 'var(--chart-text)', fontWeight: 600 }}>
                  {val}%
                </text>
                <line x1={padding.left} y1={yPos} x2={chartWidth - padding.right} y2={yPos} stroke="var(--chart-grid)" strokeWidth="1" strokeDasharray="3,3" />
              </g>
            );
          })}

          {renderDataset(pts1, '#e74a3b', 'url(#eccdGradRed)')}
          {renderDataset(pts2, '#fbbf24', 'url(#eccdGradYellow)')}
          {renderDataset(pts3, '#1cc88a', 'url(#eccdGradGreen)')}

          {labels.map((lbl, i) => {
            const xPos = padding.left + i * (graphWidth / (count - 1 || 1));
            let shortLabel = lbl;
            if (shortLabel.length > 15) {
              shortLabel = shortLabel.substring(0, 12) + '...';
            }
            return (
              <text 
                key={i} 
                x={xPos} 
                y={chartHeight - 15} 
                textAnchor="middle" 
                style={{ fontSize: '8px', fill: 'var(--chart-text)', fontWeight: 600 }}
                transform={`rotate(-10, ${xPos}, ${chartHeight - 15})`}
              >
                {shortLabel}
              </text>
            );
          })}

          <defs>
            <linearGradient id="eccdGradRed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#e74a3b" />
              <stop offset="100%" stopColor="#e74a3b" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="eccdGradYellow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#fbbf24" />
              <stop offset="100%" stopColor="#fbbf24" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="eccdGradGreen" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#1cc88a" />
              <stop offset="100%" stopColor="#1cc88a" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '25px', marginTop: '10px', fontSize: '0.8rem', fontWeight: 600 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '3px', borderRadius: '1px', background: '#e74a3b', display: 'inline-block' }}></span>
            1st Evaluation
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '3px', borderRadius: '1px', background: '#fbbf24', display: 'inline-block' }}></span>
            2nd Evaluation
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '12px', height: '3px', borderRadius: '1px', background: '#1cc88a', display: 'inline-block' }}></span>
            3rd Evaluation
          </div>
        </div>
      </div>
    </div>
  );
}


export default function TeacherDashboard() {
  const [stats, setStats] = useState({ total: 0, present: 0, absent: 0, pending: 0, milestonePct: 0, nutritionPct: 0 });
  const [attendanceChart, setAttendanceChart] = useState({ labels: [], data: [] });
  const [nutritionChart, setNutritionChart] = useState({ finished: 0, someLeft: 0, notEaten: 0 });
  const [eccdChart, setEccdChart] = useState({ labels: [], data1: [], data2: [], data3: [] });
  const [dssAlerts, setDssAlerts] = useState([]);
  
  // School Year Management
  const [schoolYears, setSchoolYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState('');
  
  // Mobile Layout Management
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [mobileTab, setMobileTab] = useState('overview'); // 'overview', 'performance', 'attendance-nutrition'

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
            if (todayAtt && todayAtt.status) {
              const statusLower = todayAtt.status.toLowerCase();
              if (statusLower === 'present') presentCount++;
              else if (statusLower === 'absent') absentCount++;
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
           if (isSameDay(d, a.date) && a.status && a.status.toLowerCase() === 'present') {
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

      // Heuristic DSS Alerts
      let computedAlerts = [];
      enrolledStudents.forEach(st => {
         const studentAtt = attRecords
             .filter(a => a.child === st.id)
             .sort((a,b) => new Date(b.date) - new Date(a.date));
             
         let consecutiveAbsences = 0;
         for (let att of studentAtt) {
             const statusLower = (att.status || '').toLowerCase();
             if (statusLower === 'absent') {
                 consecutiveAbsences++;
             } else if (statusLower === 'present') {
                 break;
             }
         }
         
         let studentAlerts = [];
         if (consecutiveAbsences > 3) {
             studentAlerts.push({
                 type: 'attendance',
                 message: `Logged ${consecutiveAbsences} consecutive absences.`,
                 severity: 'danger',
                 recommendation: 'Initiate contact with parent/guardian to check status, schedule support.'
             });
         }
         
         const milestonePct = (st.stats && typeof st.stats.milestones !== 'undefined') ? st.stats.milestones : 0;
         if (milestonePct < 60) {
             studentAlerts.push({
                 type: 'milestone',
                 message: `Milestone completion is low (${milestonePct}%).`,
                 severity: 'warning',
                 recommendation: 'Target Gross/Fine Motor exercises or refer to developmental boosting activities in the Milestones tab.'
             });
         }
         
         const bmiRecs = st.bmi_records || [];
         const finalizedBmi = bmiRecs
             .filter(r => r.status === 'Finalized')
             .sort((a,b) => new Date(b.measurement_date) - new Date(a.measurement_date))[0];
             
         if (finalizedBmi) {
             const w = parseFloat(finalizedBmi.weight);
             const h = parseFloat(finalizedBmi.height) / 100;
             const bmiVal = w / (h * h);
             if (bmiVal < 14.0) {
                 studentAlerts.push({
                     type: 'nutrition',
                     message: `Underweight BMI of ${bmiVal.toFixed(1)} recorded.`,
                     severity: 'warning',
                     recommendation: 'Encourage protein/healthy fats snacks; monitor dietary intake closely.'
                 });
             } else if (bmiVal >= 18.0) {
                 studentAlerts.push({
                     type: 'nutrition',
                     message: `Overweight/Obese BMI of ${bmiVal.toFixed(1)} recorded.`,
                     severity: 'danger',
                     recommendation: 'Limit sugary snacks, promote active physical play.'
                 });
             }
         }
         
         if (studentAlerts.length > 0) {
             computedAlerts.push({
                 student: st,
                 alerts: studentAlerts
             });
         }
      });
      setDssAlerts(computedAlerts);

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
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>Operational Dashboard</h2>
          <p style={{ margin: '5px 0 0 0', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Real-time monitoring and analytics • {new Date().toLocaleDateString()}</p>
        </div>
        <div>
            <select value={selectedYear} onChange={handleYearChange} style={{ padding: '8px 15px', borderRadius: '6px', border: '1px solid var(--border-color)', background: 'var(--input-bg)', color: 'var(--input-text)', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer' }}>
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
        <button className={`resp-mobile-tab-btn ${mobileTab === 'performance' ? 'active' : ''}`} onClick={() => setMobileTab('performance')}>Domain Performance</button>
        <button className={`resp-mobile-tab-btn ${mobileTab === 'attendance-nutrition' ? 'active' : ''}`} onClick={() => setMobileTab('attendance-nutrition')}>Attendance & Nutrition</button>
      </div>

      {/* KPI Cards Row */}
      {(!isMobile || mobileTab === 'overview') && (
        <div className="resp-grid-4" style={{ marginBottom: '25px' }}>
          <a href="/children/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', padding: '15px 20px', borderRadius: '8px', display: 'flex', flexDirection: 'column', height: '100%', cursor: 'pointer', border: '1px solid var(--border-color)', position: 'relative' }}>
              <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '10px' }}>Total Enrolled</div>
              <div style={{ position: 'absolute', top: '15px', right: '20px', color: 'var(--text-muted)', fontSize: '1rem' }}><i className="fa-solid fa-users"></i></div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{stats.total}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 'auto' }}>Active children</div>
            </div>
          </a>
          <a href="/attendance/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', padding: '15px 20px', borderRadius: '8px', display: 'flex', flexDirection: 'column', height: '100%', cursor: 'pointer', border: '1px solid var(--border-color)', position: 'relative' }}>
              <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '10px' }}>Today's Attendance</div>
              <div style={{ position: 'absolute', top: '15px', right: '20px', color: '#4a90e2', fontSize: '1rem' }}><i className="fa-solid fa-calendar-check"></i></div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{stats.present}/{stats.total}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 'auto' }}>{stats.absent} absent today</div>
            </div>
          </a>
          <a href="/children/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', padding: '15px 20px', borderRadius: '8px', display: 'flex', flexDirection: 'column', border: stats.pending > 0 ? '2px solid #f6c23e' : '1px solid var(--border-color)', height: '100%', cursor: 'pointer', position: 'relative' }}>
              <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '10px' }}>Pending Enrollments</div>
              <div style={{ position: 'absolute', top: '15px', right: '20px', color: stats.pending > 0 ? '#f6c23e' : '#1cc88a', fontSize: '1rem' }}><i className="fa-solid fa-file-signature"></i></div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{stats.pending}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 'auto' }}>{stats.pending > 0 ? 'Requires your approval' : 'All caught up'}</div>
            </div>
          </a>
          <a href="/milestones/" style={{ textDecoration: 'none', color: 'inherit' }}>
            <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', padding: '15px 20px', borderRadius: '8px', display: 'flex', flexDirection: 'column', height: '100%', cursor: 'pointer', border: '1px solid var(--border-color)', position: 'relative' }}>
              <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '10px' }}>Milestone Progress</div>
              <div style={{ position: 'absolute', top: '15px', right: '20px', color: '#4a90e2', fontSize: '1rem' }}><i className="fa-solid fa-chart-line"></i></div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800 }}>{stats.milestonePct}%</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 'auto' }}>Overall completion</div>
            </div>
          </a>
        </div>
      )}

      {/* Decision Support System (DSS) Advisory Panel */}
      {(!isMobile || mobileTab === 'overview') && (
        <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', padding: '20px', borderRadius: '8px', border: '1px solid var(--border-color)', borderLeft: `5px solid ${dssAlerts.length > 0 ? '#f6c23e' : '#1cc88a'}`, marginBottom: '25px' }}>
          <div style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <i className="fa-solid fa-lightbulb" style={{ color: dssAlerts.length > 0 ? '#f6c23e' : '#1cc88a' }}></i>
            <span>Decision Support System (DSS) Advisory</span>
          </div>
          {dssAlerts.length > 0 ? (
            <>
              <p style={{ margin: '0 0 15px 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                 The following students have flag-worthy attendance, growth, or milestone metrics:
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {dssAlerts.map(({ student, alerts }) => (
                  <div key={student.id} style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
                    <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: '6px' }}>
                      {student.first_name} {student.last_name}
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', paddingLeft: '10px' }}>
                      {alerts.map((alert, idx) => (
                        <div key={idx} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          <strong style={{ color: alert.severity === 'danger' ? '#e74a3b' : '#f6c23e' }}>
                             {alert.message}
                          </strong>
                          <span style={{ marginLeft: '8px' }}>
                             Advisory: {alert.recommendation}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <>
              <div style={{ fontWeight: 600, color: 'var(--success, #1cc88a)', marginBottom: '8px', fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <i className="fa-solid fa-circle-check" style={{ color: '#1cc88a' }}></i> All classroom milestones, attendance, and nutritional indicators are on track!
              </div>
              <p style={{ margin: '0 0 12px 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                General child development guidelines to maintain this excellent progress:
              </p>
              <ul style={{ margin: '0 0 0 20px', padding: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                <li style={{ marginBottom: '4px' }}>Maintain active outdoor play daily to support motor coordination and bone strength.</li>
                <li style={{ marginBottom: '4px' }}>Integrate interactive drawing and modeling tasks to build finger muscle strength.</li>
                <li style={{ marginBottom: '4px' }}>Provide fresh water and nutritional snacks while limiting processed foods and screen time.</li>
                <li style={{ marginBottom: '4px' }}>Establish clear schedules for sleep, hygiene, and developmental routines.</li>
              </ul>
            </>
          )}
        </div>
      )}

      {/* ECCD Chart Row */}
      {(!isMobile || mobileTab === 'performance') && (
        <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', padding: '20px', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '25px' }}>
            <div style={{ fontWeight: 600, marginBottom: '5px' }}>Classroom Average Performance by Domain & Period</div>
            <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Average completion percentage across 7 ECCD domains</p>
            <div style={{ height: '250px', position: 'relative', width: '100%' }}>
              <SVGEccdDomainPerformanceChart labels={eccdChart.labels} data1={eccdChart.data1} data2={eccdChart.data2} data3={eccdChart.data3} />
            </div>
        </div>
      )}

      {/* Row 2 */}
      {(!isMobile || mobileTab === 'attendance-nutrition') && (
        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '20px' }}>
          {(!isMobile || mobileTab === 'attendance-nutrition') && (
            <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', padding: '20px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, marginBottom: '5px' }}>Attendance Trend (7 Days)</div>
              <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Daily attendance tracking</p>
              <div style={{ height: '220px', position: 'relative', width: '100%' }}>
                <SVGBarChart labels={attendanceChart.labels} data={attendanceChart.data} total={stats.total} />
              </div>
            </div>
          )}
          
          {(!isMobile || mobileTab === 'attendance-nutrition') && (
            <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', padding: '20px', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column' }}>
              <div style={{ fontWeight: 600, marginBottom: '5px' }}>Nutrition Analytics (7 Days)</div>
              <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Weekly snack consumption summary</p>
              <div style={{ height: '220px', position: 'relative', width: '100%' }}>
                <SVGNutritionBarChart finished={nutritionChart.finished} someLeft={nutritionChart.someLeft} notEaten={nutritionChart.notEaten} />
              </div>
            </div>
          )}

          {(!isMobile || mobileTab === 'attendance-nutrition') && (
            <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', padding: '20px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontWeight: 600, marginBottom: '5px' }}>Today's Attendance</div>
              <p style={{ margin: '0 0 20px 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Present vs Absent distribution</p>
              <div style={{ height: '220px', position: 'relative', width: '100%', display: 'flex', justifyContent: 'center' }}>
                <SVGDonutChart present={stats.present} absent={stats.absent} />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
