import React, { useState, useEffect } from 'react';

const PHILIPPINE_ADDRESSES = {
  "Region IV-A (CALABARZON)": {
    "Quezon": {
      "Lucena City": ["Market View", "Ilayang Dupay", "Ibabang Dupay", "Cotta", "Gulang-Gulang"],
      "Tayabas City": ["San Isidro", "San Roque", "Wakas", "Lalo", "Camasan"],
      "Pagbilao": ["Bukal", "Del Carmen", "Mapagong", "Santa Catalina", "Talipan"],
      "Sariaya": ["Balubal", "Bignay", "Guisguis", "Lutgarda", "Montecillo"]
    },
    "Laguna": {
      "San Pablo City": ["Barangay I-A", "Barangay I-B", "San Jose", "San Lucas"],
      "Calamba City": ["Halang", "Real", "Bucal", "Pansol"]
    },
    "Batangas": {
      "Batangas City": ["Alangilan", "Bolbok", "Kumintang Ibaba", "Kumintang Ilaya"],
      "Lipa City": ["Balintawak", "Marawoy", "Sabang", "Tambo"]
    }
  },
  "NCR": {
    "Metro Manila": {
      "Quezon City": ["Bagong Pila", "Commonwealth", "Fairview", "Holy Spirit"],
      "Manila": ["Binondo", "Ermita", "Malate", "Quiapo", "Tondo"]
    }
  }
};

const parseFullAddress = (fullText) => {
  if (!fullText) return null;
  const cleanText = fullText.toLowerCase().replace(/[\.,]/g, ' ');
  
  let matchedRegion = '';
  let matchedProvince = '';
  let matchedCity = '';
  let matchedBarangay = '';
  
  // 1. Match Region
  for (const region of Object.keys(PHILIPPINE_ADDRESSES)) {
    const regLower = region.toLowerCase();
    if (cleanText.includes("calabarzon") || cleanText.includes("region iv-a")) {
      matchedRegion = "Region IV-A (CALABARZON)";
      break;
    } else if (cleanText.includes("ncr") || cleanText.includes("national capital region") || cleanText.includes("metro manila")) {
      matchedRegion = "NCR";
      break;
    } else if (cleanText.includes(regLower)) {
      matchedRegion = region;
      break;
    }
  }
  
  // 2. Match Province
  let provincesToSearch = {};
  if (matchedRegion) {
    provincesToSearch = PHILIPPINE_ADDRESSES[matchedRegion];
  } else {
    Object.keys(PHILIPPINE_ADDRESSES).forEach(r => {
      Object.assign(provincesToSearch, PHILIPPINE_ADDRESSES[r]);
    });
  }
  
  for (const province of Object.keys(provincesToSearch)) {
    const provLower = province.toLowerCase();
    if (cleanText.includes(provLower)) {
      matchedProvince = province;
      if (!matchedRegion) {
        for (const r of Object.keys(PHILIPPINE_ADDRESSES)) {
          if (PHILIPPINE_ADDRESSES[r][province]) {
            matchedRegion = r;
            break;
          }
        }
      }
      break;
    }
  }
  
  // 3. Match City/Municipality
  let citiesToSearch = {};
  if (matchedRegion && matchedProvince) {
    citiesToSearch = PHILIPPINE_ADDRESSES[matchedRegion][matchedProvince] || {};
  } else if (matchedProvince) {
    for (const r of Object.keys(PHILIPPINE_ADDRESSES)) {
      if (PHILIPPINE_ADDRESSES[r][matchedProvince]) {
        citiesToSearch = PHILIPPINE_ADDRESSES[r][matchedProvince];
        break;
      }
    }
  } else {
    Object.keys(PHILIPPINE_ADDRESSES).forEach(r => {
      Object.keys(PHILIPPINE_ADDRESSES[r]).forEach(p => {
        Object.assign(citiesToSearch, PHILIPPINE_ADDRESSES[r][p]);
      });
    });
  }
  
  for (const city of Object.keys(citiesToSearch)) {
    const cityLower = city.toLowerCase();
    const cityBase = cityLower.replace(" city", "").replace(" municipality", "");
    if (cleanText.includes(cityLower) || cleanText.includes(cityBase)) {
      matchedCity = city;
      if (!matchedProvince) {
        outer: for (const r of Object.keys(PHILIPPINE_ADDRESSES)) {
          for (const p of Object.keys(PHILIPPINE_ADDRESSES[r])) {
            if (PHILIPPINE_ADDRESSES[r][p][city]) {
              matchedRegion = r;
              matchedProvince = p;
              break outer;
            }
          }
        }
      }
      break;
    }
  }
  
  // 4. Match Barangay
  let barangaysToSearch = [];
  if (matchedRegion && matchedProvince && matchedCity) {
    barangaysToSearch = PHILIPPINE_ADDRESSES[matchedRegion][matchedProvince][matchedCity] || [];
  } else if (matchedCity) {
    outer: for (const r of Object.keys(PHILIPPINE_ADDRESSES)) {
      for (const p of Object.keys(PHILIPPINE_ADDRESSES[r])) {
        if (PHILIPPINE_ADDRESSES[r][p][matchedCity]) {
          barangaysToSearch = PHILIPPINE_ADDRESSES[r][p][matchedCity];
          break outer;
        }
      }
    }
  } else {
    Object.keys(PHILIPPINE_ADDRESSES).forEach(r => {
      Object.keys(PHILIPPINE_ADDRESSES[r]).forEach(p => {
        Object.keys(PHILIPPINE_ADDRESSES[r][p]).forEach(c => {
          barangaysToSearch.push(...PHILIPPINE_ADDRESSES[r][p][c]);
        });
      });
    });
  }
  
  for (const brgy of barangaysToSearch) {
    const brgyLower = brgy.toLowerCase();
    if (cleanText.includes(brgyLower) || cleanText.includes(brgyLower.replace(' ', ''))) {
      matchedBarangay = brgy;
      if (!matchedCity) {
        outer: for (const r of Object.keys(PHILIPPINE_ADDRESSES)) {
          for (const p of Object.keys(PHILIPPINE_ADDRESSES[r])) {
            for (const c of Object.keys(PHILIPPINE_ADDRESSES[r][p])) {
              if (PHILIPPINE_ADDRESSES[r][p][c].includes(brgy)) {
                matchedRegion = r;
                matchedProvince = p;
                matchedCity = c;
                break outer;
              }
            }
          }
        }
      }
      break;
    }
  }
  
  let addressLine1 = fullText;
  const toRemove = [matchedRegion, matchedProvince, matchedCity, matchedBarangay, 'brgy', 'barangay', 'province', 'city', 'region', 'philippines', 'phil'];
  
  toRemove.forEach(word => {
    if (word) {
      const regex = new RegExp('\\b' + word.toLowerCase().replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&') + '\\b', 'gi');
      addressLine1 = addressLine1.replace(regex, '');
      if (word.includes(' ') || word.includes('(')) {
         const regexNoBound = new RegExp(word.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'gi');
         addressLine1 = addressLine1.replace(regexNoBound, '');
      }
    }
  });
  
  addressLine1 = addressLine1.replace(/,\s*,/g, ',')
                             .replace(/^[\s,]+/g, '')
                             .replace(/[\s,]+$/g, '')
                             .trim();
  
  return {
    region: matchedRegion || '',
    province: matchedProvince || '',
    city_municipality: matchedCity || '',
    barangay: matchedBarangay || '',
    address_line1: addressLine1 || 'Street Address'
  };
};

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
  const [allActivities, setAllActivities] = useState([]);
  const [allCompletions, setAllCompletions] = useState([]);
  
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
            fetch('/api/eccd-scores/').then(r => r.json()),
            fetch('/api/activities/').then(r => r.json()),
            fetch(`/api/activity-completions/?child=${childId}`).then(r => r.json())
        ]).then(([attData, nutData, eccdAss, eccdDomains, eccdMiles, eccdScores, activitiesData, completionsData]) => {
            const childAtt = attData.filter((a) => a.child === childId);
            setAllAttendance(childAtt);
            
            const childNut = nutData.filter((n) => n.child === childId);
            setAllNutrition(childNut);
            
            const childScores = eccdScores.filter(s => eccdAss.find(a => a.id === s.assessment));
            setEccdData({ domains: eccdDomains, scores: childScores, ass: eccdAss, miles: eccdMiles });

            setAllActivities(activitiesData || []);
            setAllCompletions(completionsData || []);

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
      // Find the latest assessment that actually has scores
      const periods = ['3rd', '2nd', '1st'];
      let latestAss = null;
      for (const p of periods) {
          const assOpt = eccdData.ass.find(a => a.assessment_period === p);
          if (assOpt) {
              const hasScores = eccdData.scores.some(sc => sc.assessment === assOpt.id);
              if (hasScores) {
                  latestAss = assOpt;
                  break;
              }
          }
      }
      // Fallback to latest initialized period if none have scores yet
      if (!latestAss) {
          latestAss = eccdData.ass.find(a => a.assessment_period === '3rd') || 
                      eccdData.ass.find(a => a.assessment_period === '2nd') || 
                      eccdData.ass.find(a => a.assessment_period === '1st');
      }
      
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
      const { name, value } = e.target;
      let updatedForm = { ...enrollForm, [name]: value };
      if (name === 'region') {
          updatedForm.province = '';
          updatedForm.city_municipality = '';
          updatedForm.barangay = '';
      } else if (name === 'province') {
          updatedForm.city_municipality = '';
          updatedForm.barangay = '';
      } else if (name === 'city_municipality') {
          updatedForm.barangay = '';
      }
      setEnrollForm(updatedForm);
      setEnrollError('');
  };

  const handleAddressPaste = (value, type) => {
      const parsed = parseFullAddress(value);
      if (parsed) {
          if (type === 'enroll') {
              setEnrollForm(prev => ({
                  ...prev,
                  region: parsed.region,
                  province: parsed.province,
                  city_municipality: parsed.city_municipality,
                  barangay: parsed.barangay,
                  address_line1: parsed.address_line1
              }));
          } else if (type === 'guardian') {
              setGuardianForm(prev => ({
                  ...prev,
                  region: parsed.region,
                  province: parsed.province,
                  city_municipality: parsed.city_municipality,
                  barangay: parsed.barangay,
                  address_line1: parsed.address_line1
              }));
          }
      }
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
      const { name, value } = e.target;
      let updatedForm = { ...guardianForm, [name]: value };
      if (name === 'region') {
          updatedForm.province = '';
          updatedForm.city_municipality = '';
          updatedForm.barangay = '';
      } else if (name === 'province') {
          updatedForm.city_municipality = '';
          updatedForm.barangay = '';
      } else if (name === 'city_municipality') {
          updatedForm.barangay = '';
      }
      setGuardianForm(updatedForm);
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
                    style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border-color)', padding: '30px', borderRadius: '15px', cursor: 'pointer', textAlign: 'center', transition: '0.2s', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}
                >
                    <div style={{ fontSize: '2.5rem', marginBottom: '15px' }}>📝</div>
                    <h3 style={{ margin: '0 0 10px 0', fontSize: '1.2rem', color: '#063970' }}>Enroll New Child</h3>
                    <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Fill out a new application for your child to join the center.</p>
                </div>
                <div 
                    onClick={() => setShowLinkGuardianForm(true)}
                    style={{ flex: 1, background: 'var(--bg-card)', border: '1px solid var(--border-color)', padding: '30px', borderRadius: '15px', cursor: 'pointer', textAlign: 'center', transition: '0.2s', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}
                >
                    <div style={{ fontSize: '2.5rem', marginBottom: '15px' }}>🔗</div>
                    <h3 style={{ margin: '0 0 10px 0', fontSize: '1.2rem', color: '#063970' }}>Link to Existing Child</h3>
                    <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>If your child is already enrolled, set up your guardian profile and connect to their records.</p>
                </div>
            </div>
        )}

        {showEnrollForm && (
        <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '30px', borderRadius: '15px' }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '1.4rem' }}>Child Enrollment Application</h3>
            
            {enrollError && <div style={{ background: '#fdf2f2', color: '#d9534f', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #f5c6cb' }}>{enrollError}</div>}
            {enrollSuccess && <div style={{ background: '#d4edda', color: '#155724', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #c3e6cb' }}>{enrollSuccess}</div>}

            <form onSubmit={submitEnrollment}>
                <div className="resp-grid-2-form" style={{ marginBottom: '20px' }}>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>First Name *</label>
                        <input required type="text" name="first_name" value={enrollForm.first_name} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Middle Initial</label>
                        <input type="text" name="middle_initial" value={enrollForm.middle_initial} onChange={handleEnrollChange} maxLength="5" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Last Name *</label>
                        <input required type="text" name="last_name" value={enrollForm.last_name} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div className="resp-grid-dob" style={{ gridColumn: '1 / -1' }}>
                        <div>
                            <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Date of Birth * (Must be 3-4 yrs old)</label>
                            <input required type="date" min="2020-01-01" name="dob" value={enrollForm.dob} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', boxSizing: 'border-box' }} />
                        </div>
                        <div>
                            <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Computed Age</label>
                            <input type="text" readOnly value={enrollForm.dob ? calculateAge(enrollForm.dob) + ' yrs' : ''} placeholder="Auto-calculated" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--input-bg)', color: 'var(--text-secondary)', cursor: 'not-allowed', boxSizing: 'border-box', fontWeight: 'bold' }} />
                        </div>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Gender</label>
                        <select name="gender" value={enrollForm.gender} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }}>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                        </select>
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Child Profile Picture (Optional)</label>
                        <input type="file" accept="image/*" onChange={(e) => setChildImg(e.target.files[0])} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }} />
                        <small style={{ color: 'var(--text-secondary)' }}>You can skip this and upload a picture later.</small>
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Address Details</h4>
                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Paste Full Address (Auto-detects fields)</label>
                    <textarea 
                        placeholder="e.g. 123 Mabini St., Market View, Lucena City, Quezon"
                        onChange={(e) => handleAddressPaste(e.target.value, 'enroll')} 
                        style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', height: '60px', boxSizing: 'border-box' }}
                    />
                </div>
                <div className="resp-grid-2-form" style={{ marginBottom: '20px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Address Line 1 (Street/House) *</label>
                        <input required type="text" name="address_line1" value={enrollForm.address_line1} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Region *</label>
                        <select required name="region" value={enrollForm.region} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select Region</option>
                            {Object.keys(PHILIPPINE_ADDRESSES).map(r => (
                                <option key={r} value={r}>{r}</option>
                            ))}
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Province *</label>
                        <select required name="province" value={enrollForm.province} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select Province</option>
                            {enrollForm.region && enrollForm.region !== 'Other' && Object.keys(PHILIPPINE_ADDRESSES[enrollForm.region] || {}).map(p => (
                                <option key={p} value={p}>{p}</option>
                            ))}
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>City/Municipality *</label>
                        <select required name="city_municipality" value={enrollForm.city_municipality} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select City/Municipality</option>
                            {enrollForm.region && enrollForm.region !== 'Other' && enrollForm.province && enrollForm.province !== 'Other' && Object.keys(PHILIPPINE_ADDRESSES[enrollForm.region][enrollForm.province] || {}).map(c => (
                                <option key={c} value={c}>{c}</option>
                            ))}
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Barangay *</label>
                        <select required name="barangay" value={enrollForm.barangay} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select Barangay</option>
                            {enrollForm.region && enrollForm.region !== 'Other' && enrollForm.province && enrollForm.province !== 'Other' && enrollForm.city_municipality && enrollForm.city_municipality !== 'Other' && (PHILIPPINE_ADDRESSES[enrollForm.region][enrollForm.province][enrollForm.city_municipality] || []).map(b => (
                                <option key={b} value={b}>{b}</option>
                            ))}
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div style={{ gridColumn: '1 / -1', marginTop: '10px' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Full Address Preview</label>
                        <input 
                            type="text" 
                            readOnly 
                            value={`${enrollForm.address_line1 || ''}${enrollForm.barangay ? ', ' + enrollForm.barangay : ''}${enrollForm.city_municipality ? ', ' + enrollForm.city_municipality : ''}${enrollForm.province ? ', ' + enrollForm.province : ''}${enrollForm.region ? ', ' + enrollForm.region : ''}`} 
                            style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--input-bg)', color: 'var(--text-secondary)', fontWeight: 500 }} 
                        />
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Health Details</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px', marginBottom: '30px' }}>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Allergies</label>
                        <select name="allergies" value={enrollForm.allergies} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
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
                        <input type="text" name="health_conditions" placeholder="e.g., Asthma (leave blank if none)" value={enrollForm.health_conditions} onChange={handleEnrollChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginTop: '40px', marginBottom: '20px' }}>Part 2: Guardian Profile Setup</h4>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>Fill out your information to link with this child.</p>
                
                <div className="resp-grid-2-form" style={{ marginBottom: '20px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Relationship to Child *</label>
                        <select required name="guardian_type" value={guardianForm.guardian_type} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="Mother">Mother</option>
                            <option value="Father">Father</option>
                            <option value="Other Relative">Other Relative</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>First Name *</label>
                        <input required type="text" name="first_name" value={guardianForm.first_name} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Middle Initial</label>
                        <input type="text" name="middle_initial" value={guardianForm.middle_initial} onChange={handleGuardianChange} maxLength="5" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Last Name *</label>
                        <input required type="text" name="last_name" value={guardianForm.last_name} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Email Address *</label>
                        <input required type="email" name="email" value={guardianForm.email} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Contact Number *</label>
                        <input required type="text" name="phone" value={guardianForm.phone} onChange={handleGuardianChange} placeholder="e.g. 09123456789" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Guardian Profile Picture (Optional)</label>
                        <input type="file" accept="image/*" onChange={(e) => setParentImg(e.target.files[0])} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }} />
                        <small style={{ color: 'var(--text-secondary)' }}>You can skip this and upload a picture later.</small>
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Guardian Address Details</h4>
                <div className="resp-grid-2-form" style={{ marginBottom: '30px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Address Line 1 (Street/House) *</label>
                        <input required type="text" name="address_line1" value={guardianForm.address_line1} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Region *</label>
                        <select required name="region" value={guardianForm.region} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select Region</option>
                            <option value="Region IV-A (CALABARZON)">Region IV-A (CALABARZON)</option>
                            <option value="NCR">NCR</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Province *</label>
                        <select required name="province" value={guardianForm.province} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select Province</option>
                            <option value="Quezon">Quezon Province</option>
                            <option value="Laguna">Laguna</option>
                            <option value="Batangas">Batangas</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>City/Municipality *</label>
                        <select required name="city_municipality" value={guardianForm.city_municipality} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
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
                        <select required name="barangay" value={guardianForm.barangay} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
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
                    <button type="button" onClick={() => setShowEnrollForm(false)} style={{ padding: '12px 25px', background: 'var(--btn-neutral-bg)', color: 'var(--text-primary)', border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600, cursor: 'pointer' }}>Cancel</button>
                </div>
            </form>
        </div>
        )}

        {showLinkGuardianForm && (
        <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '30px', borderRadius: '15px' }}>
            <h3 style={{ margin: '0 0 20px 0', fontSize: '1.4rem' }}>Guardian Profile Setup</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>Fill out your information to link with an enrolled child.</p>
            
            {guardianError && <div style={{ background: '#fdf2f2', color: '#d9534f', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #f5c6cb' }}>{guardianError}</div>}
            {guardianSuccess && <div style={{ background: '#d4edda', color: '#155724', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #c3e6cb' }}>{guardianSuccess}</div>}

            <form onSubmit={submitGuardianForm}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px', marginBottom: '20px' }}>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Select Child to Link *</label>
                        {guardianForm.child_id && childrenList.find(c => c.id === guardianForm.child_id) ? (
                            <div style={{ padding: '10px', background: 'var(--input-bg)', border: '1px solid var(--border-color)', borderRadius: '5px', fontWeight: 'bold' }}>
                                {childrenList.find(c => c.id === guardianForm.child_id).first_name} {childrenList.find(c => c.id === guardianForm.child_id).last_name}
                                <input type="hidden" name="child_id" value={guardianForm.child_id} />
                            </div>
                        ) : (
                            <select required name="child_id" value={guardianForm.child_id} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                                <option value="">-- Choose Child --</option>
                                {childrenList.map(c => <option key={c.id} value={c.id}>{c.first_name} {c.last_name}</option>)}
                            </select>
                        )}
                    </div>
                </div>

                <div className="resp-grid-2-form" style={{ marginBottom: '20px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Relationship to Child *</label>
                        <select required name="guardian_type" value={guardianForm.guardian_type} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="Mother">Mother</option>
                            <option value="Father">Father</option>
                            <option value="Other Relative">Other Relative</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>First Name *</label>
                        <input required type="text" name="first_name" value={guardianForm.first_name} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Middle Initial</label>
                        <input type="text" name="middle_initial" value={guardianForm.middle_initial} onChange={handleGuardianChange} maxLength="5" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Last Name *</label>
                        <input required type="text" name="last_name" value={guardianForm.last_name} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Email Address *</label>
                        <input required type="email" name="email" value={guardianForm.email} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Contact Number *</label>
                        <input required type="text" name="phone" value={guardianForm.phone} onChange={handleGuardianChange} placeholder="e.g. 09123456789" style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Guardian Profile Picture (Optional)</label>
                        <input type="file" accept="image/*" onChange={(e) => setParentImg(e.target.files[0])} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }} />
                        <small style={{ color: 'var(--text-secondary)' }}>You can skip this and upload a picture later.</small>
                    </div>
                </div>

                <h4 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', marginBottom: '20px' }}>Address Details</h4>
                <div style={{ marginBottom: '20px' }}>
                    <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Paste Full Address (Auto-detects fields)</label>
                    <textarea 
                        placeholder="e.g. 123 Mabini St., Market View, Lucena City, Quezon"
                        onChange={(e) => handleAddressPaste(e.target.value, 'guardian')} 
                        style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', height: '60px', boxSizing: 'border-box' }}
                    />
                </div>
                <div className="resp-grid-2-form" style={{ marginBottom: '30px' }}>
                    <div style={{ gridColumn: '1 / -1' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Address Line 1 (Street/House) *</label>
                        <input required type="text" name="address_line1" value={guardianForm.address_line1} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)' }} />
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Region *</label>
                        <select required name="region" value={guardianForm.region} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select Region</option>
                            {Object.keys(PHILIPPINE_ADDRESSES).map(r => (
                                <option key={r} value={r}>{r}</option>
                            ))}
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Province *</label>
                        <select required name="province" value={guardianForm.province} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select Province</option>
                            {guardianForm.region && guardianForm.region !== 'Other' && Object.keys(PHILIPPINE_ADDRESSES[guardianForm.region] || {}).map(p => (
                                <option key={p} value={p}>{p}</option>
                            ))}
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>City/Municipality *</label>
                        <select required name="city_municipality" value={guardianForm.city_municipality} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select City/Municipality</option>
                            {guardianForm.region && guardianForm.region !== 'Other' && guardianForm.province && guardianForm.province !== 'Other' && Object.keys(PHILIPPINE_ADDRESSES[guardianForm.region][guardianForm.province] || {}).map(c => (
                                <option key={c} value={c}>{c}</option>
                            ))}
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Barangay *</label>
                        <select required name="barangay" value={guardianForm.barangay} onChange={handleGuardianChange} style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--bg-card)' }}>
                            <option value="">Select Barangay</option>
                            {guardianForm.region && guardianForm.region !== 'Other' && guardianForm.province && guardianForm.province !== 'Other' && guardianForm.city_municipality && guardianForm.city_municipality !== 'Other' && (PHILIPPINE_ADDRESSES[guardianForm.region][guardianForm.province][guardianForm.city_municipality] || []).map(b => (
                                <option key={b} value={b}>{b}</option>
                            ))}
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div style={{ gridColumn: '1 / -1', marginTop: '10px' }}>
                        <label style={{ display:'block', marginBottom:'5px', fontWeight:600 }}>Full Address Preview</label>
                        <input 
                            type="text" 
                            readOnly 
                            value={`${guardianForm.address_line1 || ''}${guardianForm.barangay ? ', ' + guardianForm.barangay : ''}${guardianForm.city_municipality ? ', ' + guardianForm.city_municipality : ''}${guardianForm.province ? ', ' + guardianForm.province : ''}${guardianForm.region ? ', ' + guardianForm.region : ''}`} 
                            style={{ width: '100%', padding: '10px', borderRadius: '5px', border: '1px solid var(--border-color)', background: 'var(--input-bg)', color: 'var(--text-secondary)', fontWeight: 500 }} 
                        />
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '15px' }}>
                    <button type="submit" style={{ padding: '12px 25px', background: '#063970', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600, cursor: 'pointer' }}>Submit Profile & Link</button>
                    <button type="button" onClick={() => setShowLinkGuardianForm(false)} style={{ padding: '12px 25px', background: 'var(--btn-neutral-bg)', color: 'var(--text-primary)', border: 'none', borderRadius: '8px', fontSize: '1rem', fontWeight: 600, cursor: 'pointer' }}>Cancel</button>
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

      {/* Horizontal Child Profile Switcher */}
      <div style={{ display: 'flex', gap: '15px', overflowX: 'auto', paddingBottom: '15px', marginBottom: '25px', scrollbarWidth: 'thin' }}>
          {childrenList.map((c) => {
              const isSelected = c.id === linkedChildId;
              const statusColor = c.enrollment_status === 'Enrolled' ? '#1cc88a' : (c.enrollment_status === 'Pending' ? '#f6c23e' : '#e74a3b');
              const avatarUrl = c.img || ('https://api.dicebear.com/7.x/fun-emoji/svg?seed=' + c.first_name);
              return (
                  <div 
                      key={c.id}
                      onClick={() => {
                          setLinkedChildId(c.id);
                          localStorage.setItem('linked_child_id', c.id);
                      }}
                      style={{
                          flex: '0 0 auto',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                          padding: '12px 20px',
                          borderRadius: '12px',
                          cursor: 'pointer',
                          background: isSelected ? 'linear-gradient(135deg, #063970, #1b4f91)' : '#fff',
                          color: isSelected ? '#fff' : '#333',
                          border: isSelected ? '2px solid #063970' : '1px solid #ddd',
                          boxShadow: isSelected ? '0 4px 15px rgba(6, 57, 112, 0.25)' : '0 2px 4px rgba(0,0,0,0.05)',
                          transition: 'all 0.2s ease',
                          transform: isSelected ? 'scale(1.02)' : 'none',
                      }}
                  >
                      <img 
                          src={avatarUrl} 
                          alt={c.first_name} 
                          style={{ width: '40px', height: '40px', borderRadius: '50%', objectFit: 'cover', background: '#e0f0ff' }} 
                      />
                      <div>
                          <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{c.first_name} {c.last_name}</div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                              <span style={{ fontSize: '0.75rem', opacity: 0.8 }}>{c.age} yrs</span>
                              <span style={{ 
                                  fontSize: '0.7rem', 
                                  fontWeight: 800, 
                                  color: isSelected ? '#fff' : statusColor,
                                  background: isSelected ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.05)',
                                  padding: '2px 6px',
                                  borderRadius: '10px'
                              }}>
                                  {c.enrollment_status}
                              </span>
                          </div>
                      </div>
                  </div>
              );
          })}
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
      <div className="resp-flex-between" style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '25px', borderRadius: '15px', marginBottom: '20px', opacity: (student.enrollment_status !== 'Enrolled' ? 0.6 : 1) }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ width: '60px', height: '60px', borderRadius: '10px', overflow: 'hidden', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#e0f0ff', color: '#063970', fontWeight: 'bold', fontSize: '1.5rem' }}>
            <img
              src={student.img || localStorage.getItem('bmv3_parent_profile_img') || ('https://api.dicebear.com/7.x/fun-emoji/svg?seed=' + student.first_name)}
              style={{ width: '100%', height: '100%', objectFit: 'cover', background: 'var(--bg-card)' }}
              alt="avatar"
            />
          </div>
          <div>
              <h3 style={{ margin: 0, fontSize: '1.2rem', textTransform: 'uppercase', letterSpacing: '1px' }}>
                {student.first_name} {student.last_name}
              </h3>
              <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{student.age} years old</p>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '8px' }}>ATTENDANCE STATUS</div>
          <div style={{ background: getAttColor(attendanceToday), color: '#fff', padding: '5px 20px', borderRadius: '20px', display: 'inline-block', fontWeight: 800, fontSize: '0.9rem' }}>{attendanceToday}</div>
        </div>
      </div>

      {/* Controls Container */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', marginBottom: '20px', background: 'var(--bg-card)', padding: '20px', borderRadius: '15px', border: '1px solid var(--border-color)' }}>
          {/* Date filter */}
          <div>
            <label htmlFor="history-date" style={{ marginRight: '10px', fontWeight: 600 }}>View records for date:</label>
            <input id="history-date" type="date" value={filterDate} onChange={(e) => setFilterDate(e.target.value)} style={{ padding: '8px', borderRadius: '5px', border: '1px solid var(--border-color)', outline: 'none' }} />
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
                  <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>{dropoffInfo.time}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Pick-up Status</div>
                  <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>{dropoffInfo.status}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Authorized Guardian</div>
                  <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>{dropoffInfo.guardian}</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Session</div>
                  <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>{dropoffInfo.session}</div>
                </div>
              </div>

              {/* Daily Activities Card */}
              {(() => {
                const dateActivities = allActivities.filter(act => act.date === currentDate);
                const totalActCount = dateActivities.length;
                const completedActCount = dateActivities.filter(act => {
                  const completion = allCompletions.find(c => c.activity === act.id);
                  return completion ? completion.completed : false;
                }).length;
                const completionPct = totalActCount > 0 ? Math.round((completedActCount / totalActCount) * 100) : 0;

                return (
                  <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '25px', borderRadius: '15px', marginBottom: '30px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid #f1f5f9', paddingBottom: '15px', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: '#e0f2fe', color: '#0369a1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                          <i className="fa-solid fa-graduation-cap"></i>
                        </div>
                        <h4 style={{ margin: 0, fontSize: '1.2rem', fontFamily: "'Montserrat', sans-serif", fontWeight: 800 }}>Daily Activities & Learning Checklist</h4>
                      </div>
                      {totalActCount > 0 && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#64748b' }}>Progress:</span>
                          <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#0369a1', background: '#e0f2fe', padding: '4px 10px', borderRadius: '12px' }}>
                            {completedActCount} / {totalActCount} ({completionPct}%)
                          </span>
                        </div>
                      )}
                    </div>

                    {totalActCount > 0 ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                        {/* Progress Bar */}
                        <div style={{ width: '100%', height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden', marginBottom: '10px' }}>
                          <div style={{ width: `${completionPct}%`, height: '100%', background: '#0284c7', borderRadius: '4px', transition: 'width 0.4s ease' }}></div>
                        </div>

                        {/* Activities Table/List */}
                        <div style={{ overflowX: 'auto' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                            <thead>
                              <tr style={{ borderBottom: '2px solid #edf2f7', color: '#64748b', fontSize: '0.8rem', fontWeight: 700 }}>
                                <th style={{ padding: '10px 15px' }}>Activity Name</th>
                                <th style={{ padding: '10px 15px' }}>Description</th>
                                <th style={{ padding: '10px 15px', textAlign: 'center' }}>Status</th>
                                <th style={{ padding: '10px 15px' }}>Teacher Comments / Observations</th>
                              </tr>
                            </thead>
                            <tbody>
                              {dateActivities.map(act => {
                                const completion = allCompletions.find(c => c.activity === act.id);
                                const isCompleted = completion ? completion.completed : false;
                                const remarks = completion ? completion.remarks : '';
                                return (
                                  <tr key={act.id} style={{ borderBottom: '1px solid #f1f5f9', transition: 'background 0.2s' }}>
                                    <td style={{ padding: '12px 15px', fontWeight: 700, fontSize: '0.9rem', color: '#1e293b' }}>
                                      {act.name}
                                    </td>
                                    <td style={{ padding: '12px 15px', fontSize: '0.85rem', color: '#475569' }}>
                                      {act.description || <span style={{ color: '#94a3b8', fontStyle: 'italic' }}>No description</span>}
                                    </td>
                                    <td style={{ padding: '12px 15px', textAlign: 'center' }}>
                                      {isCompleted ? (
                                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', background: '#dcfce7', color: '#15803d', padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 700 }}>
                                          <i className="fa-solid fa-circle-check"></i> Completed
                                        </span>
                                      ) : (
                                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', background: '#f1f5f9', color: '#64748b', padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 700 }}>
                                          <i className="fa-solid fa-circle-minus"></i> Pending / Missed
                                        </span>
                                      )}
                                    </td>
                                    <td style={{ padding: '12px 15px', fontSize: '0.85rem', color: '#475569' }}>
                                      {remarks ? (
                                        <div style={{ background: '#f8fafc', borderLeft: '3px solid #0284c7', padding: '8px 12px', borderRadius: '0 8px 8px 0', fontSize: '0.8rem', fontStyle: 'italic' }}>
                                          "{remarks}"
                                        </div>
                                      ) : (
                                        <span style={{ color: '#94a3b8', fontStyle: 'italic', fontSize: '0.8rem' }}>No remarks yet</span>
                                      )}
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    ) : (
                      <div style={{ textAlign: 'center', padding: '30px 15px', color: '#64748b' }}>
                        <i className="fa-solid fa-calendar-xmark" style={{ fontSize: '2.5rem', color: '#cbd5e1', marginBottom: '10px', display: 'block' }}></i>
                        <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>No activities logged by the teacher for this date.</span>
                      </div>
                    )}
                  </div>
                );
              })()}
            </>
          )}

          {(!isMobile || mobileTab === 'health-milestones') && (
            <div className="resp-grid-2">
              <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '25px', borderRadius: '15px' }}>
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
                <div style={{ marginBottom: '15px' }}>
                  <strong style={{ fontSize: '0.9rem' }}>Allergies / Conditions</strong>
                  <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>
                      {student.allergies || 'None recorded'} 
                      {student.health_conditions ? ` / ${student.health_conditions}` : ''}
                  </div>
                </div>
                <div style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '15px' }}>
                  <strong style={{ fontSize: '0.9rem', display: 'block', marginBottom: '10px' }}>Quarterly Growth History</strong>
                  {(() => {
                    const bmiRecords = student.bmi_records || [];
                    if (bmiRecords.length === 0) {
                      return <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>No growth history recorded yet.</span>;
                    }
                    const sortedBmis = [...bmiRecords].sort((x, y) => {
                      const quarters = { '1st': 1, '2nd': 2, '3rd': 3 };
                      return quarters[x.quarter] - quarters[y.quarter];
                    });

                    return (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        {sortedBmis.map((rec, index) => {
                          const hM = rec.height / 100;
                          const bmiVal = (rec.weight / (hM * hM)).toFixed(1);
                          let cat = "Overweight";
                          if (bmiVal < 14) cat = "Underweight";
                          else if (bmiVal < 18) cat = "Normal weight";

                          let qName = "1st Quarter (Baseline)";
                          if (rec.quarter === '2nd') qName = "2nd Quarter (Interim)";
                          else if (rec.quarter === '3rd') qName = "3rd Quarter (Final)";

                          const isDraft = rec.status === 'Draft';

                          return (
                            <div key={index} style={{ padding: '10px', background: isDraft ? '#fffbeb' : '#f8fafc', border: isDraft ? '1px dashed #f59e0b' : '1px solid #e2e8f0', borderRadius: '8px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#063970' }}>{qName}</div>
                                {isDraft && (
                                  <span style={{ fontSize: '0.7rem', fontWeight: 'bold', background: '#fef3c7', color: '#d97706', padding: '2px 6px', borderRadius: '4px' }}>Ongoing / Draft</span>
                                )}
                              </div>
                              <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '4px' }}>Date: {new Date(rec.measurement_date).toLocaleDateString()}</div>
                              <div style={{ fontSize: '0.8rem', color: '#334155' }}>
                                Weight: <strong>{rec.weight} kg</strong> &bull; Height: <strong>{rec.height} cm</strong>
                              </div>
                              <div style={{ fontSize: '0.8rem', fontWeight: 700, marginTop: '2px', color: bmiVal < 14 ? '#b45309' : (bmiVal < 18 ? '#0f766e' : '#b91c1c') }}>
                                BMI: {bmiVal} ({cat})
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    );
                  })()}
                </div>
              </div>

              <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '25px', borderRadius: '15px', position: 'relative' }}>
                  <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>ECCD Milestone Progress</h4>
                  <div className="resp-grid-2-form">
                      {eccdProgress.length > 0 ? eccdProgress.map((p, i) => (
                          <div key={i}>
                              <div style={{ fontSize: '0.8rem', fontWeight: 600 }}>{p.name}</div>
                              <div style={{ width: '100%', height: '6px', background: 'var(--btn-neutral-bg)', borderRadius: '3px', marginTop: '5px' }}>
                                  <div style={{ width: `${p.pct}%`, height: '100%', background: '#1cc88a', borderRadius: '3px' }}></div>
                              </div>
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{p.pct}% Achieved</div>
                          </div>
                      )) : (
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', gridColumn: '1/-1' }}>No ECCD assessment records found. Click 'Milestones' in the menu to start your first evaluation!</div>
                      )}
                  </div>
              </div>
            </div>
          )}
      </>
      ) : (
          <div style={{ textAlign: 'center', padding: '40px', background: '#f8f9fa', borderRadius: '15px', border: '1px solid var(--border-color)' }}>
              <h3 style={{ color: 'var(--text-secondary)' }}>Profile is not currently active</h3>
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
        <div style={{ background: 'var(--bg-card)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '25px', borderRadius: '15px', marginTop: '30px' }}>
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