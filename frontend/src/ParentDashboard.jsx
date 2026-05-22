import React, { useState, useEffect } from 'react';

function ParentDashboard() {
  // Core state
  const [parentName, setParentName] = useState(window.CURRENT_USER_NAME || 'Parent Guardian');
  const [parentUserId, setParentUserId] = useState(window.CURRENT_USER_ID || null);

  // Mobile states
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [mobileTab, setMobileTab] = useState('overview'); // 'overview', 'health-milestones', 'notifications'

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth <= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  const [parentPic, setParentPic] = useState(null);
  const [linkedChildId, setLinkedChildId] = useState(null);
  const [student, setStudent] = useState(null);
  
  // Data arrays
  const [allAttendance, setAllAttendance] = useState([]);
  const [allNutrition, setAllNutrition] = useState([]);
  const [eccdData, setEccdData] = useState({ domains: [], scores: [], ass: [], miles: [] });
  
  const [notifications, setNotifications] = useState([]);
  const [childrenList, setChildrenList] = useState([]);
  const [filterDate, setFilterDate] = useState(''); // YYYY-MM-DD
  const [loading, setLoading] = useState(true);
  const [showEnrollForm, setShowEnrollForm] = useState(false);

  // Enrollment Form State
  const [enrollForm, setEnrollForm] = useState({
      first_name: '', middle_initial: '', last_name: '', dob: '', gender: 'Male',
      address_line1: '', barangay: '', city_municipality: '', province: '', region: '',
      allergies: '', health_conditions: ''
  });
  const [childImg, setChildImg] = useState(null);
  const [enrollError, setEnrollError] = useState('');
  const [enrollSuccess, setEnrollSuccess] = useState('');

  // Guardian Form State
  const [showLinkGuardianForm, setShowLinkGuardianForm] = useState(false);
  const [guardianForm, setGuardianForm] = useState({
      child_id: '', guardian_type: 'Mother', first_name: '', middle_initial: '', last_name: '',
      email: '', phone: '', address_line1: '', barangay: '', city_municipality: '', province: '', region: ''
  });
  const [parentImg, setParentImg] = useState(null);
  const [guardianError, setGuardianError] = useState('');
  const [guardianSuccess, setGuardianSuccess] = useState('');

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
        const savedLinkedId = localStorage.getItem('linked_child_id');
        if (savedLinkedId) {
            setLinkedChildId(parseInt(savedLinkedId));
        } else if (parsed.child_id) {
            setLinkedChildId(parsed.child_id);
            localStorage.setItem('linked_child_id', parsed.child_id);
        }
      } catch (e) { }
    } else {
        const savedLinkedId = localStorage.getItem('linked_child_id');
        if (savedLinkedId) {
            setLinkedChildId(parseInt(savedLinkedId));
        }
    }
    
    // Fetch user settings for profile pic
    fetch('/api/settings/')
      .then(res => res.json())
      .then(data => {
          if (data.profile_pic) {
              setParentPic(data.profile_pic);
          }
      }).catch(e => console.error("Error fetching settings:", e));
  }, []);

  const fetchData = () => {
    setLoading(true);
    fetch('/api/children/')
      .then((res) => res.json())
      .then((children) => {
        // filter children by parent_account or assume all returned are for this parent (backend filters it usually)
        setChildrenList(children);
        
        // If no child is linked yet, default to the first child
        let currentLinkedId = localStorage.getItem('linked_child_id');
        if (!currentLinkedId && children.length > 0) {
            const firstChildId = children[0].id;
            setLinkedChildId(firstChildId);
            localStorage.setItem('linked_child_id', firstChildId);
            currentLinkedId = firstChildId;
        }
        
        let myChild = null;
        if (currentLinkedId) {
          myChild = children.find((c) => c.id == currentLinkedId);
        }
        if (!myChild && children.length > 0) {
          myChild = children[0];
        }
        
        if (!myChild) {
            setLoading(false);
            return;
        }
        
        setStudent(myChild);
        const childId = myChild.id;
        const notifs = [];

        // Fetch everything for this child
        Promise.all([
            fetch('/api/attendance/').then(r => r.json()),
            fetch('/api/nutrition/').then(r => r.json()),
            fetch(`/api/eccd-assessments/?child=${childId}`).then(r => r.json()),
            fetch('/api/eccd-domains/').then(r => r.json()),
            fetch('/api/eccd-milestones/').then(r => r.json()),
            fetch('/api/eccd-scores/').then(r => r.json())
        ]).then(([attData, nutData, eccdAss, eccdDomains, eccdMiles, eccdScores]) => {
            const childAtt = attData.filter((a) => a.child === childId);
            setAllAttendance(childAtt);
            
            const childNut = nutData.filter((n) => n.child === childId);
            setAllNutrition(childNut);
            
            const childScores = eccdScores.filter(s => eccdAss.find(a => a.id === s.assessment));
            setEccdData({ domains: eccdDomains, scores: childScores, ass: eccdAss, miles: eccdMiles });

            // Populate some basic today notifications if they exist
            const todayAtt = childAtt.find((a) => a.date.startsWith(todayStr));
            if (todayAtt && todayAtt.status.toLowerCase() === 'present') {
                 notifs.push({ title: 'Drop-off confirmed', desc: 'Drop-off by ' + (todayAtt.authorized_guardian || '--'), date: todayStr });
            }
            if (childNut.find((n) => n.date.startsWith(todayStr))) {
                 notifs.push({ title: 'Health & Nutrition', desc: 'Nutrition logs updated for today.', date: todayStr });
            }
            
            if (myChild.enrollment_status === 'Rejected') {
                 notifs.push({ title: 'Enrollment Update', desc: 'Your enrollment application was rejected. Please see feedback.', date: todayStr });
            } else if (myChild.enrollment_status === 'Pending') {
                 notifs.push({ title: 'Enrollment Pending', desc: 'Your application is awaiting teacher review.', date: todayStr });
            }

            if (notifs.length === 0) {
                notifs.push({ title: 'System', desc: 'No new notifications at this time.', date: new Date().toLocaleDateString() });
            }
            setNotifications(notifs.slice(0, 4));
            setLoading(false);
        }).catch((e) => {
            console.error('Child specific data fetch error', e);
            setLoading(false);
        });
      })
      .catch((e) => {
          console.error('Children fetch error', e);
          setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, [linkedChildId, todayStr]);

  const dateDisplay = new Date(currentDate).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const getAttColor = (status) => {
    if (status === 'PRESENT') return '#1cc88a';
    if (status === 'ABSENT') return '#e74a3b';
    if (status === 'LATE') return '#f6c23e';
    return '#888';
  };

  // Derive dashboard data based on currentDate
  const activeAtt = allAttendance.find(a => a.date.startsWith(currentDate));
  let attendanceToday = 'NO RECORD';
  let dropoffInfo = { time: '--', status: '--', guardian: '--', session: '--' };
  
  if (activeAtt) {
      attendanceToday = activeAtt.status.toUpperCase();
      if (activeAtt.status.toLowerCase() === 'present' || activeAtt.status.toLowerCase() === 'late') {
          dropoffInfo = {
              time: activeAtt.dropoff_time || '--',
              status: activeAtt.status === 'late' ? 'Late Arrival' : 'Successful',
              guardian: activeAtt.authorized_guardian || '--',
              session: activeAtt.session || 'Morning'
          };
      } else if (activeAtt.status.toLowerCase() === 'absent') {
          dropoffInfo = { time: '--', status: 'Absent', guardian: '--', session: '--' };
      }
  }

  const activeNut = allNutrition.find(n => n.date.startsWith(currentDate));
  let nutritionStatus = 'No Data';
  if (activeNut && activeNut.snack_status) {
      nutritionStatus = activeNut.snack_status;
  }

  let eccdProgress = [];
  if (eccdData.domains && eccdData.domains.length > 0) {
      // Find the latest assessment
      let latestAss = eccdData.ass.find(a => a.assessment_period === '3rd') || 
                      eccdData.ass.find(a => a.assessment_period === '2nd') || 
                      eccdData.ass.find(a => a.assessment_period === '1st');
      
      if (latestAss) {
          eccdData.domains.forEach(d => {
              const dMiles = eccdData.miles.filter(m => m.domain === d.id);
              const total = dMiles.length;
              let achieved = 0;
              dMiles.forEach(m => {
                  const s = eccdData.scores.find(sc => sc.assessment === latestAss.id && sc.milestone === m.id);
                  if (s && s.teacher_score === 1) achieved++;
              });
              let pct = total === 0 ? 0 : Math.round((achieved / total) * 100);
              eccdProgress.push({ name: d.name, pct: pct, icon: d.icon });
          });
      }
  }

  // Handle Enrollment
  const handleEnrollChange = (e) => {
      setEnrollForm({ ...enrollForm, [e.target.name]: e.target.value });
      setEnrollError('');
  };

  const calculateAge = (dobString) => {
      if (!dobString) return 0;
      const dob = new Date(dobString);
      const diffMs = Date.now() - dob.getTime();
      const ageDt = new Date(diffMs);
      return Math.abs(ageDt.getUTCFullYear() - 1970);
  };

  const getCookie = (name) => {
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
  };

  const submitEnrollment = (e) => {
      e.preventDefault();
      
      const age = calculateAge(enrollForm.dob);
      if (age < 3 || age > 4) {
          setEnrollError(`Age must be between 3 and 4 years old. Computed age is ${age}.`);
          return;
      }

      const formData = new FormData();
      Object.keys(enrollForm).forEach(key => formData.append(key, enrollForm[key]));
      if (childImg) {
          formData.append('img', childImg);
      }

      fetch('/api/children/', {
          method: 'POST',
          headers: {
              'X-CSRFToken': getCookie('csrftoken')
          },
          body: formData
      })
      .then(async (res) => {
          if (!res.ok) {
              const data = await res.json();
              throw new Error(JSON.stringify(data));
          }
          return res.json();
      })
      .then((data) => {
          setEnrollSuccess('Child profile created successfully! Saving Guardian details...');
          
          // Instantly update local state
          setChildrenList(prev => [...prev, data]);
          
          // Fire the Guardian linking API immediately
          const gData = new FormData();
          Object.keys(guardianForm).forEach(key => gData.append(key, guardianForm[key]));
          gData.append('child_id', data.id);
          if (parentImg) {
              gData.append('profile_pic', parentImg);
          }

          return fetch('/api/link_guardian/', {
              method: 'POST',
              headers: { 'X-CSRFToken': getCookie('csrftoken') },
              body: gData
          });
      })
      .then(async (res) => {
          if (!res.ok) {
              const errData = await res.json();
              throw new Error(errData.detail || 'Failed to link guardian.');
          }
          return res.json();
      })
      .then((data) => {
          setEnrollSuccess('Enrollment completed successfully!');
          setTimeout(() => {
              setShowEnrollForm(false);
              setLinkedChildId(data.child_id);
              window.location.reload();
          }, 1500);
      })
      .catch((err) => {
          console.error(err);
          setEnrollError('Failed to submit enrollment. Please check your inputs.');
      });
  };

  const handleGuardianChange = (e) => {
      setGuardianForm({ ...guardianForm, [e.target.name]: e.target.value });
      setGuardianError('');
  };

  const submitGuardianForm = (e) => {
      e.preventDefault();
      if (!guardianForm.child_id) {
          setGuardianError('Please select a child to link.');
          return;
      }

      const formData = new FormData();
      Object.keys(guardianForm).forEach(key => formData.append(key, guardianForm[key]));
      if (parentImg) {
          formData.append('profile_pic', parentImg);
      }

      fetch('/api/link_guardian/', {
          method: 'POST',
          headers: {
              'X-CSRFToken': getCookie('csrftoken')
          },
          body: formData
      })
      .then(async (res) => {
          if (!res.ok) {
              const data = await res.json();
              throw new Error(data.detail || 'Failed to link guardian.');
          }
          return res.json();
      })
      .then((data) => {
          setGuardianSuccess('Guardian profile linked successfully!');
          setShowLinkGuardianForm(false);
          setLinkedChildId(data.child_id);
          fetchData();
      })
      .catch((err) => {
          console.error(err);
          setGuardianError(err.message || 'An error occurred.');
      });
  };


  if (loading) {
    return (
      <div style={{ animation: 'fadeIn 0.5s ease-in', padding: '40px', textAlign: 'center' }}>
        <h2>Welcome back, {parentName}</h2>
        <p>Loading dashboard data...</p>
      </div>
    );
  }

  // Show Enroll form if no student and showEnrollForm is true, or if no students exist
  if (!student || showEnrollForm || showLinkGuardianForm) {
    return (
      <div style={{ animation: 'fadeIn 0.5s ease-in', maxWidth: '800px', margin: '0 auto' }}>
        <div style={{ marginBottom: '30px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              {parentPic && (
                 <img src={parentPic} alt="Parent Profile" style={{ width: '50px', height: '50px', borderRadius: '50%', objectFit: 'cover', border: '2px solid #063970' }} />
              )}
              <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#063970', margin: 0 }}>Welcome back, {parentName}</h2>
            </div>
            {!showEnrollForm && !showLinkGuardianForm && <p>No child profile linked to this account yet. Please choose an option below.</p>}
        </div>

        {!showEnrollForm && !showLinkGuardianForm && (
            <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                <div 
                    onClick={() => setShowEnrollForm(true)}
                    style={{ flex: 1, background: '#fff', border: '1px solid #ccc', padding: '30px', borderRadius: '15px', cursor: 'pointer', textAlign: 'center', transition: '0.2s', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}
                >
                    <div style={{ fontSize: '2.5rem', marginBottom: '15px' }}>📝</div>
                    <h3 style={{ margin: '0 0 10px 0', fontSize: '1.2rem', color: '#063970' }}>Enroll New Child</h3>
                    <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>Fill out a new application for your child to join the center.</p>
                </div>
                <div 
                    onClick={() => setShowLinkGuardianForm(true)}
                    style={{ flex: 1, background: '#fff', border: '1px solid #ccc', padding: '30px', borderRadius: '15px', cursor: 'pointer', textAlign: 'center', transition: '0.2s', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}
                >
                    <div style={{ fontSize: '2.5rem', marginBottom: '15px' }}>🔗</div>
                    <h3 style={{ margin: '0 0 10px 0', fontSize: '1.2rem', color: '#063970' }}>Link to Existing Child</h3>
                    <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>If your child is already enrolled, set up your guardian profile and connect to their records.</p>
                </div>
            </div>
        )}

        {showEnrollForm && (
        <div style={{ background: '#fff', color: '#333', border: '1px solid #ccc', padding: '30px', borderRadius: '15px' }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '1.4rem' }}>Child Enrollment Application</h3>
            
            {enrollError && <div style={{ background: '#fdf2f2', color: '#d9534f', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #f5c6cb' }}>{enrollError}</div>}
            {enrollSuccess && <div style={{ background: '#d4edda', color: '#155724', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #c3e6cb' }}>{enrollSuccess}</div>}

            <form onSubmit={submitEnrollment}>
                <div className="resp-grid-2-form" style={{ marginBottom: '20px' }}>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>First Name *</label>
                        <input required type="text" name="first_name" value={enrollForm.first_name} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Middle Initial</label>
                        <input type="text" name="middle_initial" value={enrollForm.middle_initial} onChange={handleEnrollChange} maxLength="5" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Last Name *</label>
                        <input required type="text" name="last_name" value={enrollForm.last_name} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div className="resp-grid-dob" style={{ gridColumn: '1 / -1' }}>
                        <div>
                            <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Date of Birth * (Must be 3-4 yrs old)</label>
                            <input required type="date" min="2020-01-01" name="dob" value={enrollForm.dob} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', boxSizing: 'border-box' }} />
                        </div>
                        <div>
                            <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Computed Age</label>
                            <input type="text" readOnly value={enrollForm.dob ? calculateAge(enrollForm.dob) + ' yrs' : ''} placeholder="Auto-calculated" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#f5f5f5', color: '#666', cursor: 'not-allowed', boxSizing: 'border-box', fontWeight: 'bold' }} />
                        </div>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Gender</label>
                        <select name="gender" value={enrollForm.gender} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }}>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                        </select>
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Child Profile Picture (Optional)</label>
                        <input type="file" accept="image/*" onChange={(e) => setChildImg(e.target.files[0])} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }} />
                        <small style={{ color: '#666' }}>You can skip this and upload a picture later.</small>
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Address Details</h4>
                <div className="resp-grid-2-form" style={{ marginBottom: '20px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Address Line 1 (Street/House) *</label>
                        <input required type="text" name="address_line1" value={enrollForm.address_line1} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Region *</label>
                        <select required name="region" value={enrollForm.region} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select Region</option>
                            <option value="Region IV-A (CALABARZON)">Region IV-A (CALABARZON)</option>
                            <option value="NCR">NCR</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Province *</label>
                        <select required name="province" value={enrollForm.province} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select Province</option>
                            <option value="Quezon">Quezon Province</option>
                            <option value="Laguna">Laguna</option>
                            <option value="Batangas">Batangas</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>City/Municipality *</label>
                        <select required name="city_municipality" value={enrollForm.city_municipality} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select City/Municipality</option>
                            <option value="Lucena City">Lucena City</option>
                            <option value="Tayabas City">Tayabas City</option>
                            <option value="Pagbilao">Pagbilao</option>
                            <option value="Sariaya">Sariaya</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Barangay *</label>
                        <select required name="barangay" value={enrollForm.barangay} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select Barangay</option>
                            <option value="Market View">Market View</option>
                            <option value="Ilayang Dupay">Ilayang Dupay</option>
                            <option value="Ibabang Dupay">Ibabang Dupay</option>
                            <option value="Cotta">Cotta</option>
                            <option value="Gulang-Gulang">Gulang-Gulang</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Health Details</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px', marginBottom: '30px' }}>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Allergies</label>
                        <select name="allergies" value={enrollForm.allergies} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">None</option>
                            <option value="Peanuts">Peanuts</option>
                            <option value="Dairy / Milk">Dairy / Milk</option>
                            <option value="Seafood / Shellfish">Seafood / Shellfish</option>
                            <option value="Eggs">Eggs</option>
                            <option value="Soy">Soy</option>
                            <option value="Wheat">Wheat</option>
                            <option value="Tree Nuts">Tree Nuts</option>
                            <option value="Others">Others</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Other Health Conditions</label>
                        <input type="text" name="health_conditions" placeholder="e.g., Asthma (leave blank if none)" value={enrollForm.health_conditions} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginTop: '40px', marginBottom: '20px' }}>Part 2: Guardian Profile Setup</h4>
                <p style={{ color: '#666', marginBottom: '20px' }}>Fill out your information to link with this child.</p>
                
                <div className="resp-grid-2-form" style={{ marginBottom: '20px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Relationship to Child *</label>
                        <select required name="guardian_type" value={guardianForm.guardian_type} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="Mother">Mother</option>
                            <option value="Father">Father</option>
                            <option value="Other Relative">Other Relative</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>First Name *</label>
                        <input required type="text" name="first_name" value={guardianForm.first_name} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Middle Initial</label>
                        <input type="text" name="middle_initial" value={guardianForm.middle_initial} onChange={handleGuardianChange} maxLength="5" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Last Name *</label>
                        <input required type="text" name="last_name" value={guardianForm.last_name} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Email Address *</label>
                        <input required type="email" name="email" value={guardianForm.email} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Contact Number *</label>
                        <input required type="text" name="phone" value={guardianForm.phone} onChange={handleGuardianChange} placeholder="e.g. 09123456789" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Guardian Profile Picture (Optional)</label>
                        <input type="file" accept="image/*" onChange={(e) => setParentImg(e.target.files[0])} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }} />
                        <small style={{ color: '#666' }}>You can skip this and upload a picture later.</small>
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Guardian Address Details</h4>
                <div className="resp-grid-2-form" style={{ marginBottom: '30px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Address Line 1 (Street/House) *</label>
                        <input required type="text" name="address_line1" value={guardianForm.address_line1} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Region *</label>
                        <select required name="region" value={guardianForm.region} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select Region</option>
                            <option value="Region IV-A (CALABARZON)">Region IV-A (CALABARZON)</option>
                            <option value="NCR">NCR</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Province *</label>
                        <select required name="province" value={guardianForm.province} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select Province</option>
                            <option value="Quezon">Quezon Province</option>
                            <option value="Laguna">Laguna</option>
                            <option value="Batangas">Batangas</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>City/Municipality *</label>
                        <select required name="city_municipality" value={guardianForm.city_municipality} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select City/Municipality</option>
                            <option value="Lucena City">Lucena City</option>
                            <option value="Tayabas City">Tayabas City</option>
                            <option value="Pagbilao">Pagbilao</option>
                            <option value="Sariaya">Sariaya</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Barangay *</label>
                        <select required name="barangay" value={guardianForm.barangay} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select Barangay</option>
                            <option value="Market View">Market View</option>
                            <option value="Ilayang Dupay">Ilayang Dupay</option>
                            <option value="Ibabang Dupay">Ibabang Dupay</option>
                            <option value="Cotta">Cotta</option>
                            <option value="Gulang-Gulang">Gulang-Gulang</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '15px' }}>
                    <button type="submit" style={{ padding: '12px 25px', background: '#063970', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600, cursor: 'pointer' }}>Submit Application</button>
                    <button type="button" onClick={() => setShowEnrollForm(false)} style={{ padding: '12px 25px', background: '#eee', color: '#333', border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600, cursor: 'pointer' }}>Cancel</button>
                </div>
            </form>
        </div>
        )}

        {showLinkGuardianForm && (
        <div style={{ background: '#fff', color: '#333', border: '1px solid #ccc', padding: '30px', borderRadius: '15px' }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '1.4rem' }}>Guardian Profile Setup</h3>
            <p style={{ color: '#666', marginBottom: '20px' }}>Fill out your information to link with an enrolled child.</p>
            
            {guardianError && <div style={{ background: '#fdf2f2', color: '#d9534f', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #f5c6cb' }}>{guardianError}</div>}
            {guardianSuccess && <div style={{ background: '#d4edda', color: '#155724', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #c3e6cb' }}>{guardianSuccess}</div>}

            <form onSubmit={submitGuardianForm}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Select Child to Link *</label>
                        {guardianForm.child_id && childrenList.find(c => c.id === guardianForm.child_id) ? (
                            <div style={{ padding: '10px', background: '#f5f5f5', border: '1px solid #ccc', borderRadius: '5px', fontWeight: 'bold' }}>
                                {childrenList.find(c => c.id === guardianForm.child_id).first_name} {childrenList.find(c => c.id === guardianForm.child_id).last_name}
                                <input type="hidden" name="child_id" value={guardianForm.child_id} />
                            </div>
                        ) : (
                            <select required name="child_id" value={guardianForm.child_id} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                                <option value="">-- Choose Child --</option>
                                {childrenList.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}
                            </select>
                        )}
                    </div>
                </div>

                <div className="resp-grid-2-form" style={{ marginBottom: '20px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Relationship to Child *</label>
                        <select required name="guardian_type" value={guardianForm.guardian_type} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="Mother">Mother</option>
                            <option value="Father">Father</option>
                            <option value="Other Relative">Other Relative</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>First Name *</label>
                        <input required type="text" name="first_name" value={guardianForm.first_name} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Middle Initial</label>
                        <input type="text" name="middle_initial" value={guardianForm.middle_initial} onChange={handleGuardianChange} maxLength="5" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Last Name *</label>
                        <input required type="text" name="last_name" value={guardianForm.last_name} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Email Address *</label>
                        <input required type="email" name="email" value={guardianForm.email} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Contact Number *</label>
                        <input required type="text" name="phone" value={guardianForm.phone} onChange={handleGuardianChange} placeholder="e.g. 09123456789" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Guardian Profile Picture (Optional)</label>
                        <input type="file" accept="image/*" onChange={(e) => setParentImg(e.target.files[0])} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }} />
                        <small style={{ color: '#666' }}>You can skip this and upload a picture later.</small>
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Address Details</h4>
                <div className="resp-grid-2-form" style={{ marginBottom: '30px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Address Line 1 (Street/House) *</label>
                        <input required type="text" name="address_line1" value={guardianForm.address_line1} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Region *</label>
                        <select required name="region" value={guardianForm.region} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select Region</option>
                            <option value="Region IV-A (CALABARZON)">Region IV-A (CALABARZON)</option>
                            <option value="NCR">NCR</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Province *</label>
                        <select required name="province" value={guardianForm.province} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select Province</option>
                            <option value="Quezon">Quezon Province</option>
                            <option value="Laguna">Laguna</option>
                            <option value="Batangas">Batangas</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>City/Municipality *</label>
                        <select required name="city_municipality" value={guardianForm.city_municipality} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select City/Municipality</option>
                            <option value="Lucena City">Lucena City</option>
                            <option value="Tayabas City">Tayabas City</option>
                            <option value="Pagbilao">Pagbilao</option>
                            <option value="Sariaya">Sariaya</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Barangay *</label>
                        <select required name="barangay" value={guardianForm.barangay} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid #ccc', background: '#fff' }}>
                            <option value="">Select Barangay</option>
                            <option value="Market View">Market View</option>
                            <option value="Ilayang Dupay">Ilayang Dupay</option>
                            <option value="Ibabang Dupay">Ibabang Dupay</option>
                            <option value="Cotta">Cotta</option>
                            <option value="Gulang-Gulang">Gulang-Gulang</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '15px' }}>
                    <button type="submit" style={{ padding: '12px 25px', background: '#063970', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600, cursor: 'pointer' }}>Submit Profile & Link</button>
                    <button type="button" onClick={() => setShowLinkGuardianForm(false)} style={{ padding: '12px 25px', background: '#eee', color: '#333', border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600, cursor: 'pointer' }}>Cancel</button>
                </div>
            </form>
        </div>
        )}
      </div>
    );
  }

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-in' }}>
      <div style={{ marginBottom: '30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
          {parentPic && (
             <img src={parentPic} alt="Parent Profile" style={{ width: '50px', height: '50px', borderRadius: '50%', objectFit: 'cover', border: '2px solid #063970' }} />
          )}
          <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#063970', margin: 0 }}>Welcome back, {parentName}</h2>
        </div>
        <button onClick={() => setShowEnrollForm(true)} style={{ padding: '10px 20px', background: '#4a90e2', color: '#fff', border: 'none', borderRadius: '20px', fontWeight: 600, cursor: 'pointer' }}>+ Enroll Another Child</button>
      </div>

      {/* Enrollment Status Warning */}
      {student.enrollment_status === 'Pending' && (
          <div style={{ background: '#fff3cd', color: '#856404', padding: '15px', borderRadius: '10px', marginBottom: '20px', border: '1px solid #ffeeba' }}>
              <strong>Application Pending:</strong> Your child's enrollment application is currently being reviewed by the teacher. Check back later for updates.
          </div>
      )}
      {student.enrollment_status === 'Rejected' && (
          <div style={{ background: '#fdf2f2', color: '#d9534f', padding: '15px', borderRadius: '10px', marginBottom: '20px', border: '1px solid #f5c6cb' }}>
              <strong>Application Rejected:</strong> {student.teacher_feedback || "Please contact the administrator for details."}
          </div>
      )}

      {/* Header block */}
      <div className="resp-flex-between" style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px', marginBottom: '20px', opacity: (student.enrollment_status !== 'Enrolled' ? 0.6 : 1) }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ width: '60px', height: '60px', borderRadius: '10px', overflow: 'hidden', border: '1px solid #ccc', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e0f0ff', color: '#063970', fontWeight: 'bold', fontSize: '1.5rem' }}>
            <img
              src={student.img || localStorage.getItem('bmv3_parent_profile_img') || ('https://api.dicebear.com/7.x/fun-emoji/svg?seed=' + student.first_name)}
              style={{ width: '100%', height: '100%', objectFit: 'cover', background: '#fff' }}
              alt="avatar"
            />
          </div>
          <div>
              <h3 style={{ margin: 0, fontSize: '1.2rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                {student.first_name} {student.last_name}
              </h3>
              <p style={{ margin: 0, fontSize: '0.85rem', color: '#666' }}>{student.age} years old</p>
          </div>
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
                <option key={c.id} value={c.id}>{c.first_name} {c.last_name} ({c.enrollment_status})</option>
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

      {/* Mobile Tab Switcher */}
      {student.enrollment_status === 'Enrolled' && isMobile && (
        <div className="resp-mobile-tabs">
          <button className={`resp-mobile-tab-btn ${mobileTab === 'overview' ? 'active' : ''}`} onClick={() => setMobileTab('overview')}>Overview</button>
          <button className={`resp-mobile-tab-btn ${mobileTab === 'health-milestones' ? 'active' : ''}`} onClick={() => setMobileTab('health-milestones')}>Health & Milestones</button>
          <button className={`resp-mobile-tab-btn ${mobileTab === 'notifications' ? 'active' : ''}`} onClick={() => setMobileTab('notifications')}>Notifications</button>
        </div>
      )}

      {/* Main dashboard content */}
      {student.enrollment_status === 'Enrolled' ? (
      <>
          {(!isMobile || mobileTab === 'overview') && (
            <>
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
            </>
          )}

          {(!isMobile || mobileTab === 'health-milestones') && (
            <div className="resp-grid-2">
              <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px' }}>
                <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Health & Nutrition</h4>
                <div style={{ marginBottom: '15px' }}>
                  <strong style={{ fontSize: '0.9rem' }}>Snack Status</strong>
                  <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>{nutritionStatus}</div>
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
                  <strong style={{ fontSize: '0.9rem' }}>Allergies / Conditions</strong>
                  <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>
                      {student.allergies || 'None recorded'} 
                      {student.health_conditions ? ` / ${student.health_conditions}` : ''}
                  </div>
                </div>
              </div>

              <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px', position: 'relative' }}>
                  <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>ECCD Milestone Progress</h4>
                  <div className="resp-grid-2-form">
                      {eccdProgress.length > 0 ? eccdProgress.map((p, i) => (
                          <div key={i}>
                              <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>{p.name}</div>
                              <div style={{ width: '100%', height: '6px', background: '#eee', borderRadius: '3px', marginTop: '5px' }}>
                                  <div style={{ width: `${p.pct}%`, height: '100%', background: '#1cc88a', borderRadius: '3px' }}></div>
                              </div>
                              <div style={{ fontSize: '0.7rem', color: '#666', marginTop: '2px' }}>{p.pct}% Achieved</div>
                          </div>
                      )) : (
                          <div style={{ fontSize: '0.8rem', color: '#555', gridColumn: '1/-1' }}>No ECCD assessment records found. Click 'Milestones' in the menu to start your first evaluation!</div>
                      )}
                  </div>
              </div>
            </div>
          )}
      </>
      ) : (
          <div style={{ textAlign: 'center', padding: '40px', background: '#f8f9fa', borderRadius: '15px', border: '1px solid #ccc' }}>
              <h3 style={{ color: '#555' }}>Profile is not currently active</h3>
              <p style={{ color: '#888' }}>You will see the dashboard once the enrollment is approved.</p>
              <button 
                  onClick={() => {
                      if(window.confirm('Are you sure you want to cancel and delete this application?')) {
                          fetch(`/api/children/${student.id}/`, {
                              method: 'DELETE',
                              headers: { 'X-CSRFToken': getCookie('csrftoken') }
                          }).then(() => {
                              window.location.reload();
                          });
                      }
                  }}
                  style={{ marginTop: '20px', padding: '10px 20px', background: '#e74a3b', color: '#fff', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 600 }}>
                  Cancel Application
              </button>
          </div>
      )}

      {(!isMobile || mobileTab === 'notifications') && (
        <div style={{ background: '#fff', color: '#333', border: '1px solid #000', padding: '25px', borderRadius: '15px', marginTop: '30px' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Recent Notifications</h4>
          {notifications.map((notif, i) => (
            <div key={i} style={{ fontSize: '0.8rem', borderLeft: '2px solid #333', paddingLeft: '10px', marginBottom: '15px' }}>
              <strong>{notif.title}</strong><br />
              <span style={{ opacity: 0.8 }}>{notif.desc} - {notif.date}</span>
            </div>
          ))}
        </div>
      )}
      </div>
  );
}

export default ParentDashboard;