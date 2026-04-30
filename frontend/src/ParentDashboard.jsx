import React, { useState, useEffect } from 'react';

function ParentDashboard() {
  // Core state
  const [parentName, setParentName] = useState(window.CURRENT_USER_NAME || 'Parent Guardian');
  const [linkedChildId, setLinkedChildId] = useState(null);
  const [student, setStudent] = useState(null);
  
  // Data arrays
  const [allAttendance, setAllAttendance] = useState([]);
  const [allNutrition, setAllNutrition] = useState([]);
  const [allBehavior, setAllBehavior] = useState([]);
  const [allMilestones, setAllMilestones] = useState([]);
  
  const [notifications, setNotifications] = useState([]);
  const [childrenList, setChildrenList] = useState([]);
  const [filterDate, setFilterDate] = useState(''); // YYYY-MM-DD
  const [loading, setLoading] = useState(true);

  const todayStr = new Date().toISOString().split('T')[0];
  const currentDate = filterDate || todayStr;
  const isToday = currentDate === todayStr;

  // Load parent profile (name & linked child id) from localStorage
  useEffect(() => {
    const currentUser = window.CURRENT_USER_USERNAME;
    let pStr = null;
    if (currentUser) {
      pStr = localStorage.getItem('bmv3_parent_profile_' + currentUser);
    }
    if (!pStr) {
      pStr = localStorage.getItem('bmv3_parent_profile_data');
    }
    if (!pStr) {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.startsWith('bmv3_parent_profile_') && key !== 'bmv3_parent_profile_img') {
          pStr = localStorage.getItem(key);
          break;
        }
      }
    }
    if (pStr) {
      try {
        const parsed = JSON.parse(pStr);
        if (!window.CURRENT_USER_NAME && parsed.name) {
            setParentName(parsed.name);
        }
        if (parsed.child_id) setLinkedChildId(parsed.child_id);
      } catch (e) { }
    }
  }, []);

  // Fetch child and related data
  useEffect(() => {
    fetch('/api/children/')
      .then((res) => res.json())
      .then((children) => {
        setChildrenList(children);
        setLoading(false);
        // If no child is linked yet, default to the first child
        if (!linkedChildId && children.length > 0) {
            const firstChildId = children[0].id;
            setLinkedChildId(firstChildId);
            localStorage.setItem('linked_child_id', firstChildId);
        }
        let myChild = null;
        if (linkedChildId) {
          myChild = children.find((c) => c.id === linkedChildId);
        }
        if (!myChild && children.length > 0) {
          myChild = children[0];
        }
        if (!myChild) return;
        setStudent(myChild);
        const childId = myChild.id;
        const notifs = [];

        // Fetch everything for this child
        Promise.all([
            fetch('/api/attendance/').then(r => r.json()),
            fetch('/api/nutrition/').then(r => r.json()),
            fetch('/api/behavior/').then(r => r.json()),
            fetch('/api/milestones/').then(r => r.json())
        ]).then(([attData, nutData, behData, mileData]) => {
            const childAtt = attData.filter((a) => a.child === childId);
            setAllAttendance(childAtt);
            
            const childNut = nutData.filter((n) => n.child === childId);
            setAllNutrition(childNut);
            
            const childBeh = behData.filter((b) => b.child === childId);
            setAllBehavior(childBeh);
            
            const childMile = mileData.filter((m) => m.child === childId);
            setAllMilestones(childMile);

            // Populate some basic today notifications if they exist
            const todayAtt = childAtt.find((a) => a.date.startsWith(todayStr));
            if (todayAtt && todayAtt.status.toLowerCase() === 'present') {
                 notifs.push({ title: 'Drop-off confirmed', desc: 'Drop-off by ' + (todayAtt.authorized_guardian || '--'), date: todayStr });
            }
            if (childNut.find((n) => n.date.startsWith(todayStr))) {
                 notifs.push({ title: 'Health & Nutrition', desc: 'Nutrition logs updated for today.', date: todayStr });
            }
            if (childBeh.find((b) => b.date.startsWith(todayStr))) {
                 notifs.push({ title: 'Behavior Update', desc: 'New behavioral note logged by teacher.', date: todayStr });
            }

            if (notifs.length === 0) {
                notifs.push({ title: 'System', desc: 'No new notifications at this time.', date: new Date().toLocaleDateString() });
            }
            setNotifications(notifs.slice(0, 4));
        });
      })
      .catch((e) => console.error('Children fetch error', e));
  }, [linkedChildId, todayStr]);

  const dateDisplay = new Date(currentDate).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const getAttColor = (status) => {
    if (status === 'PRESENT') return '#00cc00';
    if (status === 'ABSENT') return '#e74a3b';
    return '#888';
  };

  // Derive dashboard data based on currentDate
  const activeAtt = allAttendance.find(a => a.date.startsWith(currentDate));
  let attendanceToday = 'NO RECORD';
  let dropoffInfo = { time: '--', status: '--', guardian: '--', session: '--' };
  
  if (activeAtt) {
      attendanceToday = activeAtt.status.toUpperCase();
      if (activeAtt.status.toLowerCase() === 'present') {
          dropoffInfo = {
              time: activeAtt.dropoff_time || '--',
              status: 'Successful',
              guardian: activeAtt.authorized_guardian || '--',
              session: activeAtt.session || 'Morning'
          };
      } else if (activeAtt.status.toLowerCase() === 'absent') {
          dropoffInfo = { time: '--', status: 'Absent', guardian: '--', session: '--' };
      }
  }

  const activeNut = allNutrition.find(n => n.date.startsWith(currentDate));
  let nutrition = { breakfast: false, snack1: false, lunch: false, snack2: false, allergies: student?.allergies || 'None' };
  if (activeNut) {
      nutrition = {
          breakfast: activeNut.breakfast,
          snack1: activeNut.snack1,
          lunch: activeNut.lunch,
          snack2: activeNut.snack2,
          allergies: student?.allergies || 'None',
      };
  }

  const activeBehLogs = allBehavior.filter(b => b.date.startsWith(currentDate));
  let activities = ['No logs recorded for this date'];
  let teacherNote = 'None';
  if (activeBehLogs.length > 0) {
      activities = activeBehLogs.map(l => l.note);
      teacherNote = activeBehLogs[activeBehLogs.length - 1].note;
  }

  const activeMile = allMilestones.find(m => m.date.startsWith(currentDate)) || allMilestones[allMilestones.length - 1]; // fallback to latest if none for date
  let milestones = { motor: [], cognitive: [] };
  if (activeMile && activeMile.tasks) {
      const mot = [];
      const cog = [];
      if (activeMile.tasks['mot-1'] === 'achieved') mot.push('Hops on one foot');
      if (activeMile.tasks['mot-2'] === 'achieved') mot.push('Draws shapes');
      if (activeMile.tasks['mot-3'] === 'achieved') mot.push('Catches ball');
      if (activeMile.tasks['mot-4'] === 'achieved') mot.push('Uses scissors');
      if (activeMile.tasks['comm-1'] === 'achieved') cog.push('Speaks in complete sentences');
      if (activeMile.tasks['comm-2'] === 'achieved') cog.push('Tells stories');
      if (activeMile.tasks['soc-1'] === 'achieved') cog.push('Plays cooperatively');
      if (activeMile.tasks['self-1'] === 'achieved') cog.push('Uses toilet independently');
      milestones = { motor: mot, cognitive: cog };
  }

  if (loading) {
    return (
      <div style={{ animation: 'fadeIn 0.5s ease-in', padding: '40px', textAlign: 'center' }}>
        <h2>Welcome back, {parentName}</h2>
        <p>Loading dashboard data...</p>
      </div>
    );
  }

  if (!student) {
    return (
      <div style={{ animation: 'fadeIn 0.5s ease-in', padding: '40px', textAlign: 'center' }}>
        <h2>Welcome back, {parentName}</h2>
        <p>No child profile linked to this account yet. Please contact the administrator.</p>
      </div>
    );
  }

  // Meals list for selected date
  const mealsList = [];
  if (nutrition.breakfast) mealsList.push('Breakfast');
  if (nutrition.snack1) mealsList.push('Morning Snack');
  if (nutrition.lunch) mealsList.push('Lunch');
  if (nutrition.snack2) mealsList.push('Afternoon Snack');

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-in' }}>
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#063970', margin: 0 }}>Welcome back, {parentName}</h2>
      </div>

      {/* Header block */}
      <div className="resp-flex-between" style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ width: '60px', height: '60px', borderRadius: '10px', overflow: 'hidden', border: '1px solid #ccc', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e0f0ff', color: '#063970', fontWeight: 'bold', fontSize: '1.5rem' }}>
            <img
              src={student.img || localStorage.getItem('bmv3_parent_profile_img') || ('https://api.dicebear.com/7.x/fun-emoji/svg?seed=' + student.first_name)}
              style={{ width: '100%', height: '100%', objectFit: 'cover', background: '#fff' }}
              alt="avatar"
            />
          </div>
          <h3 style={{ margin: 0, fontSize: '1.2rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
            {student.first_name} {student.last_name}
          </h3>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '8px' }}>ATTENDANCE STATUS</div>
          <div style={{ background: getAttColor(attendanceToday), color: '#fff', padding: '5px 20px', borderRadius: '20px', display: 'inline-block', fontWeight: 800, fontSize: '0.9rem' }}>{attendanceToday}</div>
        </div>
      </div>

      {/* Controls Container */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', marginBottom: '20px', gap: '15px', background: '#fff', padding: '20px', borderRadius: '15px', border: '1px solid #ccc' }}>
          {/* Child selector */}
          <div>
            <label htmlFor="child-select" style={{ marginRight: '10px', fontWeight: 600 }}>Select Child:</label>
            <select id="child-select" value={linkedChildId || ''} onChange={(e) => {
              const newId = e.target.value ? parseInt(e.target.value) : null;
              setLinkedChildId(newId);
              if (newId) localStorage.setItem('linked_child_id', newId);
            }} style={{ padding: '8px', borderRadius: '5px', border: '1px solid #ccc', outline: 'none' }}>
              {childrenList.map((c) => (
                <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>
              ))}
            </select>
          </div>

          {/* Date filter */}
          <div>
            <label htmlFor="history-date" style={{ marginRight: '10px', fontWeight: 600 }}>View records for date:</label>
            <input id="history-date" type="date" value={filterDate} onChange={(e) => setFilterDate(e.target.value)} style={{ padding: '8px', borderRadius: '5px', border: '1px solid #ccc', outline: 'none' }} />
            <button onClick={() => setFilterDate('')} style={{ marginLeft: '10px', padding: '8px 15px', borderRadius: '5px', background: '#063970', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 600 }}>Clear to Today</button>
          </div>
      </div>

      {/* Main dashboard content */}
      <h4 style={{ margin: '20px 0 10px 0', fontSize: '1.1rem' }}>Overview for {isToday ? 'Today' : dateDisplay}</h4>
      <div className="resp-grid-4" style={{ marginBottom: '30px', textAlign: 'center' }}>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Drop-off time</div>
          <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>{dropoffInfo.time}</div>
        </div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Pick-up Status</div>
          <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>{dropoffInfo.status}</div>
        </div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Authorized Guardian</div>
          <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>{dropoffInfo.guardian}</div>
        </div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Session</div>
          <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>{dropoffInfo.session}</div>
        </div>
      </div>

      <div className="resp-grid-2">
        <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Health & Nutrition</h4>
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ fontSize: '0.9rem' }}>Meals logged</strong>
            {mealsList.length > 0 ? (
              <ul style={{ margin: '5px 0 0 0', paddingLeft: '20px', fontSize: '0.85rem' }}>
                {mealsList.map((m) => (
                  <li key={m}>{m} served</li>
                ))}
              </ul>
            ) : (
              <div style={{ fontSize: '0.85rem', marginTop: '5px', color: '#555' }}>No meals logged</div>
            )}
          </div>
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ fontSize: '0.9rem' }}>Health observation</strong>
            {activeNut ? (
                <ul style={{ margin: '5px 0 0 0', paddingLeft: '20px', fontSize: '0.85rem' }}>
                <li>Healthy</li>
                <li>Active</li>
                <li>No fever</li>
                </ul>
            ) : (
                <div style={{ fontSize: '0.85rem', marginTop: '5px', color: '#555' }}>No observations recorded</div>
            )}
          </div>
          <div>
            <strong style={{ fontSize: '0.9rem' }}>Allergies on record</strong>
            <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>{nutrition.allergies}</div>
          </div>
        </div>

        <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Activities & Notes</h4>
          <ul style={{ margin: '0 0 30px 0', paddingLeft: '20px', fontSize: '0.85rem' }}>
            {activities.map((act, i) => (
              <li key={i}>{act}</li>
            ))}
          </ul>
          <strong style={{ fontSize: '0.9rem' }}>Teacher's Note</strong>
          <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>{teacherNote}</div>
        </div>
      </div>

      <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', paddingBottom: '60px', borderRadius: '15px', position: 'relative', marginTop: '30px' }}>
        <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Milestone Progress (Latest available)</h4>
        <div className="resp-flex-between" style={{ gap: '30px', alignItems: 'flex-start' }}>
          <div>
            <strong style={{ fontSize: '0.9rem' }}>Motor Skills</strong>
            {milestones.motor.length > 0 ? milestones.motor.map((m, i) => (
              <div key={i} style={{ fontSize: '0.8rem', marginTop: '10px' }}>☑ {m}</div>
            )) : (<div style={{ fontSize: '0.8rem', marginTop: '10px', color: '#555' }}>Not started</div>)}
          </div>
          <div>
            <strong style={{ fontSize: '0.9rem' }}>Cognitive & Social</strong>
            {milestones.cognitive.length > 0 ? milestones.cognitive.map((m, i) => (
              <div key={i} style={{ fontSize: '0.8rem', marginTop: '10px' }}>☑ {m}</div>
            )) : (<div style={{ fontSize: '0.8rem', marginTop: '10px', color: '#555' }}>Not started</div>)}
          </div>
        </div>
        <a href="/parent/milestones/" style={{ position: 'absolute', bottom: '20px', right: '20px', background: '#063970', color: '#fff', border: 'none', padding: '8px 20px', borderRadius: '15px', fontWeight: 600, cursor: 'pointer', textDecoration: 'none', fontSize: '0.85rem' }}>See More</a>
      </div>

      <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px', marginTop: '30px' }}>
        <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Recent Notifications</h4>
        {notifications.map((notif, i) => (
          <div key={i} style={{ fontSize: '0.8rem', borderLeft: '2px solid #333', paddingLeft: '10px', marginBottom: '15px' }}>
            <strong>{notif.title}</strong><br />
            <span style={{ opacity: 0.8 }}>{notif.desc} - {notif.date}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ParentDashboard;