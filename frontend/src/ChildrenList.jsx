import React, { useState, useEffect } from 'react';

export default function ChildrenList() {
  const [children, setChildren] = useState([]);
  const [search, setSearch] = useState("");
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [showGenerateAccountModal, setShowGenerateAccountModal] = useState(false);
  const [selectedChild, setSelectedChild] = useState(null);
  const [activeTab, setActiveTab] = useState('Enrolled');
  const [profileTab, setProfileTab] = useState('Performance');
  const [feedback, setFeedback] = useState("");
  
  const [genAccForm, setGenAccForm] = useState({ child_id: '', parent_name: '', email: '' });
  const [genAccResult, setGenAccResult] = useState(null);
  const [genAccError, setGenAccError] = useState('');

  const fetchChildren = () => {
    fetch('/api/children/')
      .then(res => res.json())
      .then(data => {
        const formattedChildren = data.map(st => {
          return {
            ...st,
            name: `${st.first_name} ${st.middle_initial ? st.middle_initial + '. ' : ''}${st.last_name}`,
            initial: (st.first_name[0] + st.last_name[0]).toUpperCase(),
            motherName: `${st.mother_first_name || ''} ${st.mother_last_name || 'No Info'}`.trim(),
            motherPhone: st.mother_phone || 'N/A',
            motherEmail: st.mother_email || 'N/A',
            motherAddress: st.mother_address || 'N/A',
            
            fatherName: `${st.father_first_name || ''} ${st.father_last_name || 'No Info'}`.trim(),
            fatherPhone: st.father_phone || 'N/A',
            fatherEmail: st.father_email || 'N/A',
            fatherAddress: st.father_address || 'N/A',
            
            otherGuardianName: `${st.other_guardian_first_name || ''} ${st.other_guardian_last_name || 'No Info'}`.trim(),
            otherGuardianPhone: st.other_guardian_phone || 'N/A',
            otherGuardianEmail: st.other_guardian_email || 'N/A',
            otherGuardianAddress: st.other_guardian_address || 'N/A',
          };
        });
        setChildren(formattedChildren);
      })
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchChildren();
  }, []);

  const handleEnrollmentStatus = (status) => {
      if (status === 'Rejected' && !feedback.trim()) {
          alert('Please provide feedback for rejection.');
          return;
      }
      
      const payload = {
          enrollment_status: status,
          teacher_feedback: status === 'Rejected' ? feedback : ''
      };

      fetch(`/api/children/${selectedChild.id}/`, {
          method: 'PATCH',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify(payload)
      })
      .then(res => res.json())
      .then(data => {
          setShowReviewModal(false);
          setFeedback("");
          fetchChildren();
      })
      .catch(err => console.error(err));
  };

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  const handleGenerateAccount = (e) => {
      e.preventDefault();
      setGenAccError('');
      setGenAccResult(null);

      fetch('/api/generate_parent_account/', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify(genAccForm)
      })
      .then(async (res) => {
          if (!res.ok) {
              const data = await res.json();
              throw new Error(data.detail || data.error || 'Failed to generate account');
          }
          return res.json();
      })
      .then((data) => {
          setGenAccResult(data);
          setGenAccForm({ child_id: '', parent_name: '', email: '' });
      })
      .catch((err) => {
          setGenAccError(err.message);
      });
  };

  const enrolledChildren = children.filter(c => c.enrollment_status === 'Enrolled');
  const pendingChildren = children.filter(c => c.enrollment_status === 'Pending');

  const sortedChildren = [...enrolledChildren].sort((a, b) => {
    const lastA = (a.last_name || '').toLowerCase();
    const lastB = (b.last_name || '').toLowerCase();
    if (lastA !== lastB) return lastA.localeCompare(lastB);
    return (a.first_name || '').toLowerCase().localeCompare((b.first_name || '').toLowerCase());
  });

  const filteredChildren = sortedChildren.filter(c => 
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  const getAgeCount = (age) => enrolledChildren.filter(c => Math.floor(c.age) === age).length;

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-in', fontFamily: "'Montserrat', sans-serif" }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: 0, color: 'var(--text-primary)' }}>Children Directory</h2>
          <p style={{ margin: '5px 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Manage enrollments and view student profiles</p>
        </div>
        <button onClick={() => setShowGenerateAccountModal(true)} style={{ padding: '10px 20px', background: '#1b3b5c', color: '#fff', border: 'none', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', fontFamily: "'Montserrat', sans-serif" }}>
            + Generate Parent Account
        </button>
      </div>

      {/* TABS */}
      <div style={{ display: 'flex', gap: '20px', borderBottom: '2px solid #eee', marginBottom: '20px', paddingBottom: '10px' }}>
        <div onClick={() => setActiveTab('Enrolled')} style={{ fontWeight: activeTab === 'Enrolled' ? 700 : 600, borderBottom: activeTab === 'Enrolled' ? '3px solid #333' : 'none', paddingBottom: '10px', marginBottom: '-13px', cursor: 'pointer', color: activeTab === 'Enrolled' ? '#333' : '#888' }}>
            Enrolled Students ({enrolledChildren.length})
        </div>
        <div onClick={() => setActiveTab('Pending')} style={{ fontWeight: activeTab === 'Pending' ? 700 : 600, borderBottom: activeTab === 'Pending' ? '3px solid #333' : 'none', paddingBottom: '10px', marginBottom: '-13px', cursor: 'pointer', color: activeTab === 'Pending' ? '#333' : '#888', display: 'flex', alignItems: 'center', gap: '8px' }}>
            Pending Approvals
            {pendingChildren.length > 0 && (
                <span style={{ background: '#f6c23e', color: '#fff', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 800 }}>{pendingChildren.length}</span>
            )}
        </div>
      </div>

      {activeTab === 'Enrolled' ? (
        <>
          <div className="resp-grid-3" style={{ marginBottom: '20px' }}>
            <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', border: '1px solid var(--border-color)' }}>
              <div style={{ color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.9rem', marginBottom: '10px' }}>Total Enrolled</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)' }}>{enrolledChildren.length}</div>
            </div>
            <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', border: '1px solid var(--border-color)' }}>
              <div style={{ color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.9rem', marginBottom: '10px' }}>Age 3 Years</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)' }}>{getAgeCount(3)}</div>
            </div>
            <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', border: '1px solid var(--border-color)' }}>
              <div style={{ color: 'var(--text-secondary)', fontWeight: 600, fontSize: '0.9rem', marginBottom: '10px' }}>Age 4 Years</div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)' }}>{getAgeCount(4)}</div>
            </div>
          </div>

          <div style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.05)', border: '1px solid var(--border-color)', marginBottom: '20px' }}>
            <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '10px' }}>Search Children</div>
            <input 
              type="text" 
              placeholder="🔍 Search by name..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: '100%', padding: '12px 15px', borderRadius: '25px', border: '1px solid #ddd', outline: 'none', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}
            />
          </div>
          <div style={{ background: 'var(--bg-card)', borderRadius: '12px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', border: '1px solid var(--border-color)', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', margin: 0 }}>
              <thead>
                <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ padding: '15px', textAlign: 'left', fontWeight: 700, color: '#475569', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Student</th>
                  <th style={{ padding: '15px', textAlign: 'left', fontWeight: 700, color: '#475569', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px', width: '120px' }}>Age</th>
                  <th style={{ padding: '15px', textAlign: 'left', fontWeight: 700, color: '#475569', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px', width: '220px' }}>Attendance Rate</th>
                  <th style={{ padding: '15px', textAlign: 'left', fontWeight: 700, color: '#475569', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px', width: '220px' }}>Milestone Progress</th>
                  <th style={{ padding: '15px', textAlign: 'left', fontWeight: 700, color: '#475569', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px', width: '150px' }}>Health Flags</th>
                  <th style={{ padding: '15px', textAlign: 'center', fontWeight: 700, color: '#475569', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.5px', width: '150px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredChildren.map(child => (
                  <tr key={child.id} style={{ borderBottom: '1px solid #edf2f7', transition: 'background 0.2s' }}>
                    <td style={{ padding: '15px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: '#f0f4f8', color: '#4a90e2', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.9rem', fontWeight: 800, overflow: 'hidden', flexShrink: 0, border: '1px solid #cbd5e1' }}>
                        {child.img ? (
                          <img src={child.img} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt="avatar" />
                        ) : (
                          <span>{child.initial}</span>
                        )}
                      </div>
                      <span style={{ fontWeight: 750, color: '#1e293b', fontSize: '0.95rem' }}>{child.last_name}, {child.first_name}</span>
                    </td>
                    <td style={{ padding: '15px', color: '#475569', fontWeight: 500, fontSize: '0.9rem' }}>{child.age} years</td>
                    <td style={{ padding: '15px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{ flexGrow: 1, height: '6px', background: '#e9ecef', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${child.stats?.attendance || 0}%`, height: '100%', background: '#4a90e2', borderRadius: '3px' }}></div>
                        </div>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#4a90e2', width: '40px', textAlign: 'right' }}>{child.stats?.attendance || 0}%</span>
                      </div>
                    </td>
                    <td style={{ padding: '15px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{ flexGrow: 1, height: '6px', background: '#e9ecef', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${child.stats?.milestones || 0}%`, height: '100%', background: '#9b59b6', borderRadius: '3px' }}></div>
                        </div>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#9b59b6', width: '40px', textAlign: 'right' }}>{child.stats?.milestones || 0}%</span>
                      </div>
                    </td>
                    <td style={{ padding: '15px' }}>
                      {child.allergies ? (
                        <span style={{ color: '#e74a3b', background: '#fdedec', border: '1px solid #fadbd8', padding: '4px 8px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 600 }}>
                          ⚠ Allergies
                        </span>
                      ) : (
                        <span style={{ color: '#64748b', fontSize: '0.85rem' }}>None</span>
                      )}
                    </td>
                    <td style={{ padding: '15px', textAlign: 'center' }}>
                      <button onClick={() => { setSelectedChild(child); setProfileTab('Performance'); setShowProfileModal(true); }} style={{ padding: '6px 12px', background: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '8px', fontWeight: 700, cursor: 'pointer', color: '#334155', fontFamily: "'Montserrat', sans-serif", fontSize: '0.8rem' }}>
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
                {filteredChildren.length === 0 && (
                  <tr>
                    <td colSpan="6" style={{ color: 'var(--text-muted)', padding: '30px', textAlign: 'center' }}>No enrolled students found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        // PENDING APPROVALS TAB
        <div>
            {pendingChildren.length === 0 ? (
                <div style={{ background: 'var(--bg-card)', padding: '40px', borderRadius: '12px', textAlign: 'center', color: 'var(--text-muted)', border: '1px solid var(--border-color)' }}>
                    <i className="fa-solid fa-check-circle" style={{fontSize: '3rem', color: '#1cc88a', marginBottom: '15px'}}></i>
                    <h3 style={{margin: '0 0 10px 0', color: 'var(--text-primary)'}}>All Caught Up!</h3>
                    <p style={{margin: 0}}>There are no pending enrollments to review at this time.</p>
                </div>
            ) : (
                <div style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
                    {pendingChildren.map(child => (
                        <div key={child.id} style={{ background: 'var(--bg-card)', padding: '20px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <h3 style={{margin: '0 0 5px 0', color: 'var(--text-primary)'}}>{child.name}</h3>
                                <div style={{color: 'var(--text-muted)', fontSize: '0.9rem'}}>{child.age} years old &bull; Applied: {new Date(child.date_added).toLocaleDateString()}</div>
                            </div>
                            <button onClick={() => { setSelectedChild(child); setFeedback(''); setShowReviewModal(true); }} style={{ padding: '8px 25px', background: '#4a90e2', border: 'none', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', color: '#fff', fontFamily: "'Montserrat', sans-serif" }}>Review Application</button>
                        </div>
                    ))}
                </div>
            )}
        </div>
      )}


      {/* REVIEW MODAL */}
      {showReviewModal && selectedChild && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: 'var(--bg-card)', padding: '30px', borderRadius: '12px', width: '600px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.4rem' }}>Review Enrollment Application</h3>
                <p style={{ margin: '5px 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Verify the submitted information before approving.</p>
              </div>
              <button onClick={() => setShowReviewModal(false)} style={{ background:'none', border:'none', fontSize:'1.5rem', cursor:'pointer' }}>×</button>
            </div>

            <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid var(--border-color)' }}>
                <div className="resp-grid-2-form">
                    <div>
                        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '3px'}}>Child Name</div>
                        <div style={{fontWeight: 700}}>{selectedChild.name}</div>
                    </div>
                    <div>
                        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '3px'}}>Computed Age</div>
                        <div style={{fontWeight: 700}}>{selectedChild.age} years old</div>
                    </div>
                    <div>
                        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '3px'}}>Date of Birth</div>
                        <div style={{fontWeight: 700}}>{selectedChild.dob}</div>
                    </div>
                    <div>
                        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '3px'}}>Known Allergies</div>
                        <div style={{fontWeight: 700, color: selectedChild.allergies ? '#e74a3b' : '#333'}}>{selectedChild.allergies || 'None reported'}</div>
                    </div>
                </div>
            </div>

            <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid var(--border-color)' }}>
                <h4 style={{margin: '0 0 10px 0', borderBottom: '1px solid #ddd', paddingBottom: '5px'}}>Guardian Information</h4>
                <div className="resp-grid-2-form">
                    <div>
                        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '3px'}}>Mother's Name</div>
                        <div style={{fontWeight: 700}}>{selectedChild.motherName}</div>
                    </div>
                    <div>
                        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '3px'}}>Father's Name</div>
                        <div style={{fontWeight: 700}}>{selectedChild.fatherName}</div>
                    </div>
                    <div>
                        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '3px'}}>Contact Number</div>
                        <div style={{fontWeight: 700}}>{selectedChild.guardianPhone}</div>
                    </div>
                    <div>
                        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '3px'}}>Email Address</div>
                        <div style={{fontWeight: 700}}>{selectedChild.guardianEmail}</div>
                    </div>
                    <div style={{gridColumn: '1 / -1'}}>
                        <div style={{fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '3px'}}>Address</div>
                        <div style={{fontWeight: 700}}>{selectedChild.guardianAddress}</div>
                    </div>
                </div>
            </div>

            <div style={{marginBottom: '20px'}}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Feedback (Required if rejecting)</label>
                <textarea 
                    placeholder="Provide instructions for the parent on what to correct..." 
                    value={feedback} 
                    onChange={e => setFeedback(e.target.value)} 
                    rows="3" 
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)', boxSizing: 'border-box', fontFamily: "'Montserrat', sans-serif" }}
                ></textarea>
            </div>

            <div style={{ display: 'flex', gap: '15px' }}>
                <button onClick={() => handleEnrollmentStatus('Enrolled')} style={{ flex: 1, padding: '15px', background: '#1cc88a', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 700, fontSize: '1rem', fontFamily: "'Montserrat', sans-serif" }}>Approve Enrollment</button>
                <button onClick={() => handleEnrollmentStatus('Rejected')} style={{ flex: 1, padding: '15px', background: '#e74a3b', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 700, fontSize: '1rem', fontFamily: "'Montserrat', sans-serif" }}>Reject & Send Feedback</button>
            </div>

          </div>
        </div>
      )}


      {/* CHILD PROFILE MODAL (Enrolled) */}
      {showProfileModal && selectedChild && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: 'var(--bg-card)', padding: '30px', borderRadius: '12px', width: '600px', maxHeight: '90vh', overflowY: 'auto' }}>
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.4rem' }}>Child Profile</h3>
                <p style={{ margin: '5px 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Complete information and performance overview</p>
              </div>
              <button onClick={() => setShowProfileModal(false)} style={{ background:'none', border:'none', fontSize:'1.5rem', cursor:'pointer' }}>×</button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '20px' }}>
              <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: '#f0f4f8', color: '#4a90e2', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', fontWeight: 800, overflow: 'hidden' }}>
                {selectedChild.img ? (
                  <img src={selectedChild.img} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt="avatar" />
                ) : (
                  <span>{selectedChild.initial}</span>
                )}
              </div>
              <div>
                <h2 style={{ margin: 0, fontSize: '1.5rem', color: 'var(--text-primary)' }}>{selectedChild.name}</h2>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '5px' }}>
                  {selectedChild.age} years old &bull; 🎈 Born: {selectedChild.dob} &bull; 📅 Enrolled: {selectedChild.doe}
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
              <div onClick={() => setProfileTab('Performance')} style={{ fontWeight: profileTab === 'Performance' ? 700 : 600, borderBottom: profileTab === 'Performance' ? '3px solid #333' : 'none', paddingBottom: '10px', marginBottom: '-13px', cursor: 'pointer', color: profileTab === 'Performance' ? '#333' : '#888' }}>Performance</div>
              <div onClick={() => setProfileTab('ChildInfo')} style={{ fontWeight: profileTab === 'ChildInfo' ? 700 : 600, borderBottom: profileTab === 'ChildInfo' ? '3px solid #333' : 'none', paddingBottom: '10px', marginBottom: '-13px', cursor: 'pointer', color: profileTab === 'ChildInfo' ? '#333' : '#888' }}>Child's Info</div>
              <div onClick={() => setProfileTab('Guardians')} style={{ fontWeight: profileTab === 'Guardians' ? 700 : 600, borderBottom: profileTab === 'Guardians' ? '3px solid #333' : 'none', paddingBottom: '10px', marginBottom: '-13px', cursor: 'pointer', color: profileTab === 'Guardians' ? '#333' : '#888' }}>Guardian's Info</div>
            </div>

            {profileTab === 'Performance' && (
              <div style={{ background: '#fcfcfc', border: '1px solid var(--border-color)', padding: '20px', borderRadius: '12px' }}>
                <h4 style={{ margin: '0 0 20px 0' }}>Performance Summary</h4>
                <div className="resp-grid-2">
                  <div style={{ padding: '15px', border: '1px solid var(--border-color)', borderRadius: '8px', background: 'var(--bg-card)' }}>
                    <div style={{ color: '#4a90e2', fontWeight: 700, fontSize: '0.85rem' }}>Attendance</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#4a90e2' }}>{selectedChild.stats?.attendance || 0}%</div>
                    <div style={{ height: '4px', background: '#e9ecef', borderRadius: '2px', marginTop: '10px' }}><div style={{ width: `${selectedChild.stats?.attendance || 0}%`, height: '100%', background: '#4a90e2' }}></div></div>
                  </div>
                  <div style={{ padding: '15px', border: '1px solid var(--border-color)', borderRadius: '8px', background: 'var(--bg-card)' }}>
                    <div style={{ color: '#9b59b6', fontWeight: 700, fontSize: '0.85rem' }}>Milestones</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#9b59b6' }}>{selectedChild.stats?.milestones || 0}%</div>
                    <div style={{ height: '4px', background: '#e9ecef', borderRadius: '2px', marginTop: '10px' }}><div style={{ width: `${selectedChild.stats?.milestones || 0}%`, height: '100%', background: '#9b59b6' }}></div></div>
                  </div>
                  <div style={{ padding: '15px', border: '1px solid var(--border-color)', borderRadius: '8px', background: 'var(--bg-card)' }}>
                    <div style={{ color: '#f6c23e', fontWeight: 700, fontSize: '0.85rem' }}>Nutrition (Latest Snack Status)</div>
                    <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f6c23e', marginTop: '10px' }}>{selectedChild.stats?.nutrition_status || 'No Data'}</div>
                  </div>
                </div>
              </div>
            )}
            
            {profileTab === 'ChildInfo' && (
              <div style={{ background: '#fcfcfc', border: '1px solid var(--border-color)', padding: '20px', borderRadius: '12px' }}>
                <h4 style={{ margin: '0 0 20px 0' }}>Child's Personal Information</h4>
                <div style={{ padding: '15px', border: '1px solid var(--border-color)', borderRadius: '8px', background: 'var(--bg-card)' }}>
                  <div className="resp-grid-2-form">
                    <div><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Full Name:</span> <br/><strong>{selectedChild.name}</strong></div>
                    <div><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Gender:</span> <br/><strong>{selectedChild.gender}</strong></div>
                    <div><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Date of Birth:</span> <br/><strong>{selectedChild.dob} (Age {selectedChild.age})</strong></div>
                    <div style={{ gridColumn: '1 / -1' }}><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Home Address:</span> <br/><strong>{selectedChild.address_line1}, {selectedChild.barangay}, {selectedChild.city_municipality}, {selectedChild.province}, {selectedChild.region}</strong></div>
                    <div style={{ gridColumn: '1 / -1' }}><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Health Conditions:</span> <br/><strong>{selectedChild.health_conditions || 'None Reported'}</strong></div>
                  </div>
                </div>
              </div>
            )}

            {profileTab === 'Guardians' && (
              <div style={{ background: '#fcfcfc', border: '1px solid var(--border-color)', padding: '20px', borderRadius: '12px' }}>
                <h4 style={{ margin: '0 0 20px 0' }}>Guardian Contact Information</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '15px', marginBottom: '15px' }}>
                  
                  {selectedChild.motherName && selectedChild.motherName !== 'No Info' && (
                  <div style={{ padding: '15px', border: '1px solid var(--border-color)', borderRadius: '8px', background: 'var(--bg-card)' }}>
                    <div style={{ color: '#4a90e2', fontWeight: 700, fontSize: '1rem', marginBottom: '10px' }}>Mother's Information</div>
                    <div className="resp-grid-2-form">
                      <div><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Name:</span> <br/><strong>{selectedChild.motherName}</strong></div>
                      <div><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Phone:</span> <br/><strong>{selectedChild.motherPhone}</strong></div>
                      <div style={{ gridColumn: '1 / -1' }}><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Email:</span> <br/><strong>{selectedChild.motherEmail}</strong></div>
                      <div style={{ gridColumn: '1 / -1' }}><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Address:</span> <br/><strong>{selectedChild.motherAddress}</strong></div>
                    </div>
                  </div>
                  )}
                  
                  {selectedChild.fatherName && selectedChild.fatherName !== 'No Info' && (
                  <div style={{ padding: '15px', border: '1px solid var(--border-color)', borderRadius: '8px', background: 'var(--bg-card)' }}>
                    <div style={{ color: '#4a90e2', fontWeight: 700, fontSize: '1rem', marginBottom: '10px' }}>Father's Information</div>
                    <div className="resp-grid-2-form">
                      <div><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Name:</span> <br/><strong>{selectedChild.fatherName}</strong></div>
                      <div><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Phone:</span> <br/><strong>{selectedChild.fatherPhone}</strong></div>
                      <div style={{ gridColumn: '1 / -1' }}><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Email:</span> <br/><strong>{selectedChild.fatherEmail}</strong></div>
                      <div style={{ gridColumn: '1 / -1' }}><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Address:</span> <br/><strong>{selectedChild.fatherAddress}</strong></div>
                    </div>
                  </div>
                  )}
                  
                  {selectedChild.otherGuardianName && selectedChild.otherGuardianName !== 'No Info' && (
                  <div style={{ padding: '15px', border: '1px solid var(--border-color)', borderRadius: '8px', background: 'var(--bg-card)' }}>
                    <div style={{ color: '#4a90e2', fontWeight: 700, fontSize: '1rem', marginBottom: '10px' }}>Other Guardian Information</div>
                    <div className="resp-grid-2-form">
                      <div><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Name:</span> <br/><strong>{selectedChild.otherGuardianName}</strong></div>
                      <div><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Phone:</span> <br/><strong>{selectedChild.otherGuardianPhone}</strong></div>
                      <div style={{ gridColumn: '1 / -1' }}><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Email:</span> <br/><strong>{selectedChild.otherGuardianEmail}</strong></div>
                      <div style={{ gridColumn: '1 / -1' }}><span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Address:</span> <br/><strong>{selectedChild.otherGuardianAddress}</strong></div>
                    </div>
                  </div>
                  )}

                  {(!selectedChild.motherName || selectedChild.motherName === 'No Info') && 
                   (!selectedChild.fatherName || selectedChild.fatherName === 'No Info') && 
                   (!selectedChild.otherGuardianName || selectedChild.otherGuardianName === 'No Info') && (
                      <div style={{ padding: '15px', textAlign: 'center', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                        No guardian information has been linked to this profile yet.
                      </div>
                  )}

                </div>
              </div>
            )}

          </div>
        </div>
      )}

      {/* GENERATE ACCOUNT MODAL */}
      {showGenerateAccountModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: 'var(--bg-card)', padding: '30px', borderRadius: '12px', width: '500px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.4rem' }}>Generate Parent Account</h3>
                <p style={{ margin: '5px 0 0 0', color: 'var(--text-muted)', fontSize: '0.9rem' }}>Create a temporary account to distribute to parents for enrollment.</p>
              </div>
              <button onClick={() => { setShowGenerateAccountModal(false); setGenAccResult(null); setGenAccError(''); }} style={{ background:'none', border:'none', fontSize:'1.5rem', cursor:'pointer' }}>×</button>
            </div>

            {genAccError && <div style={{ background: '#fdf2f2', color: '#d9534f', padding: '10px', borderRadius: '8px', marginBottom: '15px' }}>{genAccError}</div>}

            {genAccResult ? (
                <div style={{ background: '#e0f0ff', color: '#063970', padding: '20px', borderRadius: '12px', border: '1px solid #b3d7ff' }}>
                    <h4 style={{ margin: '0 0 10px 0', fontSize: '1.1rem' }}>✅ Account Generated!</h4>
                    <p style={{ margin: '0 0 15px 0', fontSize: '0.9rem', lineHeight: '1.4' }}>The temporary username and password have been successfully emailed directly to the parent's email address. They will be prompted to verify their email upon logging in.</p>
                    <button onClick={() => { setGenAccResult(null); setShowGenerateAccountModal(false); }} style={{ width: '100%', padding: '12px', background: '#1b3b5c', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}>Done</button>
                </div>
            ) : (
                <form onSubmit={handleGenerateAccount}>
                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Link to Enrolled Student (Optional)</label>
                        <select value={genAccForm.child_id} onChange={(e) => setGenAccForm({...genAccForm, child_id: e.target.value})} style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)', boxSizing: 'border-box', background: 'var(--bg-card)' }}>
                            <option value="">-- No Child (Parent will enroll) --</option>
                            {children.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                    </div>
                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Parent Name</label>
                        <input required type="text" value={genAccForm.parent_name} onChange={(e) => setGenAccForm({...genAccForm, parent_name: e.target.value})} placeholder="e.g. John Doe" style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)', boxSizing: 'border-box' }} />
                    </div>
                    <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 600, fontSize: '0.9rem' }}>Email Address</label>
                        <input required type="email" value={genAccForm.email} onChange={(e) => setGenAccForm({...genAccForm, email: e.target.value})} placeholder="e.g. parent@example.com" style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-color)', boxSizing: 'border-box' }} />
                    </div>
                    <button type="submit" style={{ width: '100%', padding: '12px', background: '#4a90e2', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 700, fontSize: '1rem' }}>Generate Credentials</button>
                </form>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
