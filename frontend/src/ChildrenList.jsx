import React, { useState, useEffect } from 'react';

export default function ChildrenList() {
  const [children, setChildren] = useState([]);
  const [search, setSearch] = useState("");
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [selectedChild, setSelectedChild] = useState(null);
  const [activeTab, setActiveTab] = useState('Performance');
  
  const [newStudent, setNewStudent] = useState({ 
    firstName: '', lastName: '', age: '2 years', dob: '', doe: new Date().toISOString().split('T')[0],
    allergies: '', guardianName: '', phone: '', email: '', address: ''
  });

  const getDynamicStats = (students) => {
    const attDB = JSON.parse(localStorage.getItem('bmv3_attendance')) || {};
    const mileDB = JSON.parse(localStorage.getItem('bmv3_milestones')) || {};
    const behDB = JSON.parse(localStorage.getItem('bmv3_behavior')) || {};
    const nutDB = JSON.parse(localStorage.getItem('bmv3_nutrition')) || {};
    
    // Pre-fetch parent profiles to link to children
    const parentProfiles = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith('bmv3_parent_profile_') && key !== 'bmv3_parent_profile_img') {
        try {
          const pData = JSON.parse(localStorage.getItem(key));
          if (pData && pData.child_id) {
            parentProfiles[pData.child_id] = pData;
          }
        } catch(e) {}
      }
    }
    
    return students.map(st => {
      // 1. Attendance
      let totalDays = 0, presentDays = 0;
      Object.keys(attDB).forEach(date => {
        if (attDB[date] && attDB[date][st.id]) {
          totalDays++;
          if (attDB[date][st.id] === 'present') presentDays++;
        }
      });
      let calcAtt = totalDays > 0 ? Math.round((presentDays / totalDays) * 100) : 100;

      // 2. Milestones
      let mRec = mileDB[st.id] || {};
      let ach = 0;
      Object.values(mRec).forEach(v => { if(v === 'achieved') ach++; });
      let calcMile = Math.round((ach / 16) * 100);

      // 3. Behavior
      let bRec = behDB[st.id] || [];
      let pos = 0, neg = 0, neu = 0;
      bRec.forEach(r => {
        if(r.type === 'positive') pos++;
        else if(r.type === 'negative') neg++;
        else if(r.type === 'neutral') neu++;
      });
      let totBehaviors = pos + neg + neu;
      let calcBeh = 100;
      if (totBehaviors > 0) {
        calcBeh = Math.round(((pos + neu) / totBehaviors) * 100);
      }

      // 4. Nutrition
      let nutRec = nutDB[st.id] || {};
      let nDays = Object.keys(nutRec).length;
      let totalNPct = 0;
      Object.values(nutRec).forEach(day => {
        let eaten = 0;
        if(day.b === 'true' || day.b === true) eaten++;
        if(day.s1 === 'true' || day.s1 === true) eaten++;
        if(day.l === 'true' || day.l === true) eaten++;
        if(day.s2 === 'true' || day.s2 === true) eaten++;
        totalNPct += (eaten / 4) * 100;
      });
      let calcNut = nDays > 0 ? Math.round(totalNPct / nDays) : 80;

      const linkedParent = parentProfiles[st.id];

      return {
        ...st,
        guardianName: linkedParent?.name || st.guardian || 'No Guardian Info',
        guardianPhone: linkedParent?.contact || st.phone || 'N/A',
        guardianEmail: linkedParent?.email || st.email || 'N/A',
        guardianAddress: st.address || 'N/A',
        stats: { attendance: calcAtt, milestones: calcMile, behavior: calcBeh, nutrition: calcNut }
      };
    });
  };

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem('bmv3_students')) || [];
    setChildren(getDynamicStats(saved));
  }, []);

  const handleEnroll = () => {
    if(!newStudent.firstName || !newStudent.lastName) return;
    
    const initials = newStudent.firstName[0] + newStudent.lastName[0];
    const newEntry = {
      id: 'st_' + Date.now(),
      name: `${newStudent.firstName} ${newStudent.lastName}`,
      first_name: newStudent.firstName,
      last_name: newStudent.lastName,
      age: parseInt(newStudent.age),
      dob: newStudent.dob,
      doe: newStudent.doe,
      initial: initials.toUpperCase(),
      status: 'Active',
      allergies: newStudent.allergies,
      guardian: newStudent.guardianName,
      phone: newStudent.phone,
      email: newStudent.email,
      address: newStudent.address,
      stats: { attendance: 100, milestones: 0, behavior: 100, nutrition: 80 }
    };
    
    let rawSaved = JSON.parse(localStorage.getItem('bmv3_students')) || [];
    const updatedRaw = [...rawSaved, newEntry];
    localStorage.setItem('bmv3_students', JSON.stringify(updatedRaw));
    
    setChildren(getDynamicStats(updatedRaw));
    setShowEnrollModal(false);
    setNewStudent({ firstName: '', lastName: '', age: '2 years', dob: '', doe: new Date().toISOString().split('T')[0], allergies: '', guardianName: '', phone: '', email: '', address: '' });
  };

  const filteredChildren = children.filter(c => 
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  const getAgeCount = (age) => children.filter(c => Math.floor(c.age) === age).length;

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-in', fontFamily: "'Montserrat', sans-serif" }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: 0, color: '#333' }}>Children Directory</h2>
          <p style={{ margin: '5px 0 0 0', color: '#777', fontSize: '0.9rem' }}>Complete overview of all enrolled children</p>
        </div>
        <button 
          onClick={() => setShowEnrollModal(true)}
          style={{ background: '#1cc88a', color: '#fff', border: 'none', padding: '10px 20px', borderRadius: '8px', fontWeight: 700, cursor: 'pointer', boxShadow: '0 4px 6px rgba(28,200,138,0.2)', fontFamily: "'Montserrat', sans-serif" }}
        >
          + Enroll Student
        </button>
      </div>

      <div className="resp-grid-4" style={{ marginBottom: '20px' }}>
        <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', border: '1px solid #eee' }}>
          <div style={{ color: '#555', fontWeight: 600, fontSize: '0.9rem', marginBottom: '10px' }}>Total Enrolled</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#333' }}>{children.length}</div>
        </div>
        <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', border: '1px solid #eee' }}>
          <div style={{ color: '#555', fontWeight: 600, fontSize: '0.9rem', marginBottom: '10px' }}>Age 3 Years</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#333' }}>{getAgeCount(3)}</div>
        </div>
        <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', border: '1px solid #eee' }}>
          <div style={{ color: '#555', fontWeight: 600, fontSize: '0.9rem', marginBottom: '10px' }}>Age 4 Years</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#333' }}>{getAgeCount(4)}</div>
        </div>
        <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', border: '1px solid #eee' }}>
          <div style={{ color: '#555', fontWeight: 600, fontSize: '0.9rem', marginBottom: '10px' }}>Age 5 Years</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: '#333' }}>{getAgeCount(5)}</div>
        </div>
      </div>

      <div style={{ background: '#fff', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', border: '1px solid #eee', marginBottom: '20px' }}>
        <div style={{ fontWeight: 600, color: '#555', marginBottom: '10px' }}>Search Children</div>
        <input 
          type="text" 
          placeholder="🔍 Search by name..." 
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: '100%', padding: '12px 15px', borderRadius: '25px', border: '1px solid #ddd', outline: 'none', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}
        />
      </div>

      <div className="resp-grid-2">
        {filteredChildren.map(child => (
          <div key={child.id} style={{ background: '#fff', padding: '25px', borderRadius: '12px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', border: '1px solid #eee' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
              <div style={{ width: '50px', height: '50px', borderRadius: '50%', background: '#f0f4f8', color: '#4a90e2', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', fontWeight: 800 }}>
                {child.initial}
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#333' }}>{child.name}</h3>
                <div style={{ color: '#777', fontSize: '0.85rem' }}>{child.age} years old</div>
              </div>
            </div>

            <div style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, color: '#555', marginBottom: '5px' }}>
                <span>Attendance</span><span>{child.stats?.attendance}%</span>
              </div>
              <div style={{ width: '100%', height: '6px', background: '#e9ecef', borderRadius: '3px' }}><div style={{ width: `${child.stats?.attendance}%`, height: '100%', background: '#4a90e2', borderRadius: '3px' }}></div></div>
            </div>
            
            <div style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, color: '#555', marginBottom: '5px' }}>
                <span>Milestones</span><span>{child.stats?.milestones}%</span>
              </div>
              <div style={{ width: '100%', height: '6px', background: '#e9ecef', borderRadius: '3px' }}><div style={{ width: `${child.stats?.milestones}%`, height: '100%', background: '#9b59b6', borderRadius: '3px' }}></div></div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, color: '#555', marginBottom: '5px' }}>
                <span>Behavior Score</span><span>{child.stats?.behavior}/100</span>
              </div>
              <div style={{ width: '100%', height: '6px', background: '#e9ecef', borderRadius: '3px' }}><div style={{ width: `${child.stats?.behavior}%`, height: '100%', background: '#1cc88a', borderRadius: '3px' }}></div></div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              {child.allergies ? (
                <div style={{ color: '#e74a3b', fontSize: '0.8rem', fontWeight: 600 }}>⚠ {child.allergies}</div>
              ) : <div></div>}
              <button onClick={() => { setSelectedChild(child); setActiveTab('Performance'); setShowProfileModal(true); }} style={{ padding: '8px 25px', background: 'transparent', border: '1px solid #ccc', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', color: '#333', fontFamily: "'Montserrat', sans-serif" }}>View Details</button>
            </div>
          </div>
        ))}
      </div>

      {showEnrollModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: '#fff', padding: '30px', borderRadius: '12px', width: '600px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.4rem' }}>Student Enrollment Form</h3>
                <p style={{ margin: '5px 0 0 0', color: '#777', fontSize: '0.9rem' }}>Adding a student here immediately links them to all analytics tracking systems.</p>
              </div>
              <button onClick={() => setShowEnrollModal(false)} style={{ background:'none', border:'none', fontSize:'1.5rem', cursor:'pointer' }}>×</button>
            </div>

            <div style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Student First Name</label>
                <input type="text" placeholder="e.g. Liam" value={newStudent.firstName} onChange={e => setNewStudent({...newStudent, firstName: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}/>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Student Last Name</label>
                <input type="text" placeholder="e.g. Chen" value={newStudent.lastName} onChange={e => setNewStudent({...newStudent, lastName: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}/>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Age (Years)</label>
                <select value={newStudent.age} onChange={e => setNewStudent({...newStudent, age: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', fontFamily: "'Montserrat', sans-serif" }}>
                  <option>1 year</option><option>2 years</option><option>3 years</option><option>4 years</option><option>5 years</option>
                </select>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Date of Birth</label>
                <input type="date" value={newStudent.dob} onChange={e => setNewStudent({...newStudent, dob: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}/>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Date of Enrollment</label>
                <input type="date" value={newStudent.doe} onChange={e => setNewStudent({...newStudent, doe: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}/>
              </div>
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Known Allergies / Medical Notes</label>
              <input type="text" placeholder="e.g. Peanuts, Dairy (leave blank if none)" value={newStudent.allergies} onChange={e => setNewStudent({...newStudent, allergies: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}/>
            </div>

            <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '15px' }}>Guardian Contact Details</h4>
            
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Parent / Guardian Name</label>
              <input type="text" placeholder="Full Name" value={newStudent.guardianName} onChange={e => setNewStudent({...newStudent, guardianName: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}/>
            </div>

            <div style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Primary Phone</label>
                <input type="text" placeholder="(555) 000-0000" value={newStudent.phone} onChange={e => setNewStudent({...newStudent, phone: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}/>
              </div>
              <div style={{ flex: 1 }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Email Address</label>
                <input type="email" placeholder="parent@email.com" value={newStudent.email} onChange={e => setNewStudent({...newStudent, email: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}/>
              </div>
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Home Address</label>
              <textarea placeholder="Street layout" value={newStudent.address} onChange={e => setNewStudent({...newStudent, address: e.target.value})} rows="3" style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ccc', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}></textarea>
            </div>

            <button onClick={handleEnroll} style={{ width: '100%', padding: '15px', background: '#4a90e2', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 700, fontSize: '1rem', fontFamily: "'Montserrat', sans-serif" }}>Complete Enrollment</button>
          </div>
        </div>
      )}

      {showProfileModal && selectedChild && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: '#fff', padding: '30px', borderRadius: '12px', width: '600px' }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.4rem' }}>Child Profile</h3>
                <p style={{ margin: '5px 0 0 0', color: '#777', fontSize: '0.9rem' }}>Complete information and performance overview</p>
              </div>
              <button onClick={() => setShowProfileModal(false)} style={{ background:'none', border:'none', fontSize:'1.5rem', cursor:'pointer' }}>×</button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '20px' }}>
              <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: '#f0f4f8', color: '#4a90e2', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', fontWeight: 800 }}>
                {selectedChild.initial}
              </div>
              <div>
                <h2 style={{ margin: 0, fontSize: '1.5rem', color: '#333' }}>{selectedChild.name}</h2>
                <div style={{ color: '#777', fontSize: '0.9rem', marginTop: '5px' }}>
                  {selectedChild.age} years old &bull; 🎈 Born: {selectedChild.dob || 'April 15, 2022'} &bull; 📅 Enrolled: {selectedChild.doe || 'August 01, 2025'}
                </div>
              </div>
            </div>

            {selectedChild.allergies && (
              <div style={{ background: '#ffebeb', border: '1px solid #ffcaca', padding: '15px', borderRadius: '8px', color: '#d32f2f', marginBottom: '20px' }}>
                <strong>⚠ Allergies</strong><br/>
                {selectedChild.allergies}
              </div>
            )}

            <div style={{ display: 'flex', gap: '20px', borderBottom: '2px solid #eee', marginBottom: '20px', paddingBottom: '10px' }}>
              <div onClick={() => setActiveTab('Performance')} style={{ fontWeight: activeTab === 'Performance' ? 700 : 600, borderBottom: activeTab === 'Performance' ? '3px solid #333' : 'none', paddingBottom: '10px', marginBottom: '-13px', cursor: 'pointer', color: activeTab === 'Performance' ? '#333' : '#888' }}>Performance</div>
              <div onClick={() => setActiveTab('Guardians')} style={{ fontWeight: activeTab === 'Guardians' ? 700 : 600, borderBottom: activeTab === 'Guardians' ? '3px solid #333' : 'none', paddingBottom: '10px', marginBottom: '-13px', cursor: 'pointer', color: activeTab === 'Guardians' ? '#333' : '#888' }}>Guardians</div>
            </div>

            {activeTab === 'Performance' ? (
              <div style={{ background: '#fcfcfc', border: '1px solid #eee', padding: '20px', borderRadius: '12px' }}>
                <h4 style={{ margin: '0 0 20px 0' }}>30-Day Performance Summary</h4>
                <div className="resp-grid-2">
                  <div style={{ padding: '15px', border: '1px solid #e3e6f0', borderRadius: '8px', background: '#fff' }}>
                    <div style={{ color: '#4a90e2', fontWeight: 700, fontSize: '0.85rem' }}>Attendance</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#4a90e2' }}>{selectedChild.stats?.attendance}%</div>
                    <div style={{ height: '4px', background: '#e9ecef', borderRadius: '2px', marginTop: '10px' }}><div style={{ width: `${selectedChild.stats?.attendance}%`, height: '100%', background: '#4a90e2' }}></div></div>
                  </div>
                  <div style={{ padding: '15px', border: '1px solid #e3e6f0', borderRadius: '8px', background: '#fff' }}>
                    <div style={{ color: '#9b59b6', fontWeight: 700, fontSize: '0.85rem' }}>Milestones</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#9b59b6' }}>{selectedChild.stats?.milestones}%</div>
                    <div style={{ height: '4px', background: '#e9ecef', borderRadius: '2px', marginTop: '10px' }}><div style={{ width: `${selectedChild.stats?.milestones}%`, height: '100%', background: '#9b59b6' }}></div></div>
                  </div>
                  <div style={{ padding: '15px', border: '1px solid #e3e6f0', borderRadius: '8px', background: '#fff' }}>
                    <div style={{ color: '#1cc88a', fontWeight: 700, fontSize: '0.85rem' }}>Behavior</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#1cc88a' }}>{selectedChild.stats?.behavior}/100</div>
                    <div style={{ height: '4px', background: '#e9ecef', borderRadius: '2px', marginTop: '10px' }}><div style={{ width: `${selectedChild.stats?.behavior}%`, height: '100%', background: '#1cc88a' }}></div></div>
                  </div>
                  <div style={{ padding: '15px', border: '1px solid #e3e6f0', borderRadius: '8px', background: '#fff' }}>
                    <div style={{ color: '#f6c23e', fontWeight: 700, fontSize: '0.85rem' }}>Nutrition</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f6c23e' }}>{selectedChild.stats?.nutrition}%</div>
                    <div style={{ height: '4px', background: '#e9ecef', borderRadius: '2px', marginTop: '10px' }}><div style={{ width: `${selectedChild.stats?.nutrition}%`, height: '100%', background: '#f6c23e' }}></div></div>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ background: '#fcfcfc', border: '1px solid #eee', padding: '20px', borderRadius: '12px' }}>
                <h4 style={{ margin: '0 0 20px 0' }}>Guardian Contact Information</h4>
                <div className="resp-grid-2" style={{ marginBottom: '15px' }}>
                  <div style={{ padding: '15px', border: '1px solid #e3e6f0', borderRadius: '8px', background: '#fff' }}>
                    <div style={{ color: '#777', fontWeight: 600, fontSize: '0.85rem', marginBottom: '5px' }}>Primary Guardian Name</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#333' }}>{selectedChild.guardianName}</div>
                  </div>
                  <div style={{ padding: '15px', border: '1px solid #e3e6f0', borderRadius: '8px', background: '#fff' }}>
                    <div style={{ color: '#777', fontWeight: 600, fontSize: '0.85rem', marginBottom: '5px' }}>Phone Number</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#333' }}>{selectedChild.guardianPhone}</div>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '15px' }}>
                  <div style={{ padding: '15px', border: '1px solid #e3e6f0', borderRadius: '8px', background: '#fff' }}>
                    <div style={{ color: '#777', fontWeight: 600, fontSize: '0.85rem', marginBottom: '5px' }}>Email Address</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#333' }}>{selectedChild.guardianEmail}</div>
                  </div>
                  <div style={{ padding: '15px', border: '1px solid #e3e6f0', borderRadius: '8px', background: '#fff' }}>
                    <div style={{ color: '#777', fontWeight: 600, fontSize: '0.85rem', marginBottom: '5px' }}>Home Address</div>
                    <div style={{ fontSize: '1rem', fontWeight: 600, color: '#333', lineHeight: '1.4' }}>{selectedChild.guardianAddress}</div>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      )}
    </div>
  );
}
