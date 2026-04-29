import React, { useState, useEffect } from 'react';

export default function ParentDashboard() {
  const [parentName, setParentName] = useState("Parent Guardian");
  const [student, setStudent] = useState(null);
  const [attendanceToday, setAttendanceToday] = useState("NO RECORD");
  const [dropoffInfo, setDropoffInfo] = useState({ time: '--', status: '--', guardian: '--', session: 'Morning' });
  const [nutrition, setNutrition] = useState({ breakfast: false, snack1: false, lunch: false, snack2: false, allergies: 'None' });
  const [activities, setActivities] = useState(['Waiting for teacher logs']);
  const [teacherNote, setTeacherNote] = useState("None");
  const [milestones, setMilestones] = useState({ motor: [], cognitive: [] });
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Attempt to load parent profile to identify the linked child
    let pStr = localStorage.getItem('bmv3_parent_profile_Parent') || localStorage.getItem('bmv3_parent_profile_data');
    if (!pStr) {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.startsWith('bmv3_parent_profile_')) {
          pStr = localStorage.getItem(key);
          break;
        }
      }
    }

    let linkedId = null;
    let loadedParentName = parentName;
    if (pStr) {
      const parsed = JSON.parse(pStr);
      if (parsed.name) {
        loadedParentName = parsed.name;
        setParentName(loadedParentName);
      }
      if (parsed.child_id) linkedId = parsed.child_id;
    }

    const studentsMaster = JSON.parse(localStorage.getItem('bmv3_students')) || [];
    let myChild = null;
    if (linkedId) {
      myChild = studentsMaster.find(st => st.id === linkedId);
    } else if (studentsMaster.length > 0) {
      // Fallback: If no linked child found but there are children, just show the first one to avoid blank dashboard
      myChild = studentsMaster[0]; 
    }

    if (myChild) {
      setStudent(myChild);
      const childId = myChild.id;
      const todayStr = new Date().toISOString().split('T')[0];
      const notifs = [];

      // Fetch Attendance
      const attDB = JSON.parse(localStorage.getItem('bmv3_attendance')) || {};
      if (attDB[todayStr] && attDB[todayStr][childId]) {
        const attStatus = attDB[todayStr][childId];
        setAttendanceToday(attStatus.toUpperCase());
        if (attStatus === 'present') {
          setDropoffInfo({ time: '8:00 AM', status: 'Successful', guardian: loadedParentName, session: 'Morning' });
          notifs.push({ title: 'Drop-off confirmed', desc: `Drop-off by ${loadedParentName} at 8:00 AM`, date: todayStr });
        } else if (attStatus === 'absent') {
          setDropoffInfo({ time: '--', status: 'Absent', guardian: '--', session: '--' });
          notifs.push({ title: 'Attendance Notice', desc: `Child marked absent for today.`, date: todayStr });
        }
      }

      // Fetch Nutrition & Health
      const nutDB = JSON.parse(localStorage.getItem('bmv3_nutrition')) || {};
      if (nutDB[childId] && nutDB[childId][todayStr]) {
        const mealObj = nutDB[childId][todayStr];
        setNutrition({
          breakfast: mealObj.b === 'true' || mealObj.b === true,
          snack1: mealObj.s1 === 'true' || mealObj.s1 === true,
          lunch: mealObj.l === 'true' || mealObj.l === true,
          snack2: mealObj.s2 === 'true' || mealObj.s2 === true,
          allergies: myChild.allergies || 'None'
        });
        notifs.push({ title: 'Health and Nutrition', desc: `Nutrition logs updated for today.`, date: todayStr });
      } else {
        setNutrition(prev => ({ ...prev, allergies: myChild.allergies || 'None' }));
      }

      // Fetch Behavior & Activities
      const behDB = JSON.parse(localStorage.getItem('bmv3_behavior')) || {};
      if (behDB[childId] && behDB[childId].length > 0) {
        const childLogs = behDB[childId];
        const todayLogs = childLogs.filter(r => r.date === todayStr);
        if (todayLogs.length > 0) {
          setActivities(todayLogs.map(l => l.note));
          setTeacherNote(todayLogs[todayLogs.length - 1].note);
          notifs.push({ title: 'Behavior Update', desc: `New behavioral note logged by teacher.`, date: todayStr });
        } else {
          // Show latest past logs
          setActivities([childLogs[childLogs.length - 1].note]);
          setTeacherNote(childLogs[childLogs.length - 1].note);
        }
      }

      // Fetch Milestones
      const mileDB = JSON.parse(localStorage.getItem('bmv3_milestones')) || {};
      if (mileDB[childId]) {
        const m = mileDB[childId];
        let mot = [];
        let cog = [];
        
        // Map standard tasks to readable strings
        if (m['mot-1'] === 'achieved') mot.push('Hops on one foot');
        if (m['mot-2'] === 'achieved') mot.push('Draws shapes');
        if (m['mot-3'] === 'achieved') mot.push('Catches ball');
        if (m['mot-4'] === 'achieved') mot.push('Uses scissors');
        
        if (m['comm-1'] === 'achieved') cog.push('Speaks in complete sentences');
        if (m['comm-2'] === 'achieved') cog.push('Tells stories');
        if (m['soc-1'] === 'achieved') cog.push('Plays cooperatively');
        if (m['self-1'] === 'achieved') cog.push('Uses toilet independently');

        setMilestones({ motor: mot, cognitive: cog });

        if (mot.length > 0 || cog.length > 0) {
            notifs.push({ title: 'New milestone recorded', desc: `Skills progression updated.`, date: new Date().toLocaleDateString() });
        }
      }

      if (notifs.length === 0) {
        notifs.push({ title: 'System', desc: 'No new notifications at this time.', date: new Date().toLocaleDateString() });
      }
      setNotifications(notifs.slice(0, 4)); // keep last 4
    }
  }, []);

  const dateDisplay = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

  if (!student) {
    return (
      <div style={{ animation: 'fadeIn 0.5s ease-in', padding: '40px', textAlign: 'center' }}>
        <h2>Welcome back, {parentName}</h2>
        <p>No child profile linked to this account yet. Please contact the administrator.</p>
      </div>
    );
  }

  // Generate Meal List
  const mealsList = [];
  if (nutrition.breakfast) mealsList.push('Breakfast');
  if (nutrition.snack1) mealsList.push('Morning Snack');
  if (nutrition.lunch) mealsList.push('Lunch');
  if (nutrition.snack2) mealsList.push('Afternoon Snack');

  const getAttColor = (status) => {
      if (status === 'PRESENT') return '#00cc00';
      if (status === 'ABSENT') return '#e74a3b';
      return '#888';
  };

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-in' }}>
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#063970', margin: 0 }}>Welcome back, {parentName}</h2>
        <p style={{ margin: '5px 0 0 0', color: '#777', fontSize: '1rem' }}>Date: {dateDisplay}</p>
      </div>

      <div className="resp-flex-between" style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ width: '60px', height: '60px', borderRadius: '10px', overflow: 'hidden', border: '1px solid #ccc', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e0f0ff', color: '#063970', fontWeight: 'bold', fontSize: '1.5rem' }}>
            {student.img ? <img src={student.img} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt="avatar" /> : student.initial}
          </div>
          <h3 style={{ margin: 0, fontSize: '1.2rem', textTransform: 'uppercase', letterSpacing: '1px' }}>{student.name}</h3>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '8px' }}>ATTENDANCE TODAY</div>
          <div style={{ background: getAttColor(attendanceToday), color: '#fff', padding: '5px 20px', borderRadius: '20px', display: 'inline-block', fontWeight: 800, fontSize: '0.9rem' }}>{attendanceToday}</div>
        </div>
      </div>

      <h4 style={{ margin: '20px 0 10px 0', fontSize: '1.1rem' }}>Today</h4>
      
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
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Today's health & nutrition</h4>
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ fontSize: '0.9rem' }}>Meals logged</strong>
            {mealsList.length > 0 ? (
                <ul style={{ margin: '5px 0 0 0', paddingLeft: '20px', fontSize: '0.85rem' }}>
                    {mealsList.map(m => <li key={m}>{m} served</li>)}
                </ul>
            ) : (
                <div style={{ fontSize: '0.85rem', marginTop: '5px', color: '#555' }}>No meals logged yet</div>
            )}
          </div>
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ fontSize: '0.9rem' }}>Health observation</strong>
            <ul style={{ margin: '5px 0 0 0', paddingLeft: '20px', fontSize: '0.85rem' }}>
              <li>Healthy</li>
              <li>Active</li>
              <li>No fever</li>
            </ul>
          </div>
          <div>
            <strong style={{ fontSize: '0.9rem' }}>Allergies on record</strong>
            <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>{nutrition.allergies}</div>
          </div>
        </div>

        <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Recent activities & notes</h4>
          <ul style={{ margin: '0 0 30px 0', paddingLeft: '20px', fontSize: '0.85rem' }}>
             {activities.map((act, i) => <li key={i}>{act}</li>)}
          </ul>
          <strong style={{ fontSize: '0.9rem' }}>Teacher's Note</strong>
          <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>{teacherNote}</div>
        </div>

        <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px', position: 'relative' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Latest milestone update</h4>
          <div className="resp-flex-between" style={{ gap: '30px', alignItems: 'flex-start' }}>
            <div>
              <strong style={{ fontSize: '0.9rem' }}>Motor Skills</strong>
              {milestones.motor.length > 0 ? milestones.motor.map((m, i) => (
                  <div key={i} style={{ fontSize: '0.8rem', marginTop: '10px' }}>☑ {m}</div>
              )) : <div style={{ fontSize: '0.8rem', marginTop: '10px', color: '#555' }}>Not started</div>}
            </div>
            <div>
              <strong style={{ fontSize: '0.9rem' }}>Cognitive & Social</strong>
              {milestones.cognitive.length > 0 ? milestones.cognitive.map((m, i) => (
                  <div key={i} style={{ fontSize: '0.8rem', marginTop: '10px' }}>☑ {m}</div>
              )) : <div style={{ fontSize: '0.8rem', marginTop: '10px', color: '#555' }}>Not started</div>}
            </div>
          </div>
          <a href="/parent/milestones/" style={{ position: 'absolute', bottom: '20px', right: '20px', background: '#063970', color: '#fff', border: 'none', padding: '8px 20px', borderRadius: '15px', fontWeight: 600, cursor: 'pointer', textDecoration: 'none', fontSize: '0.85rem' }}>See More</a>
        </div>

        <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Recent notifications</h4>
          {notifications.map((notif, i) => (
            <div key={i} style={{ fontSize: '0.8rem', borderLeft: '2px solid #333', paddingLeft: '10px', marginBottom: '15px' }}>
              <strong>{notif.title}</strong><br/>
              <span style={{ opacity: 0.8 }}>{notif.desc} - {notif.date}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
