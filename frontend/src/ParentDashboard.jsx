import React, { useState, useEffect } from 'react';

export default function ParentDashboard() {
  const [parentName, setParentName] = useState("Mrs. Jane Doe");

  useEffect(() => {
    const pName = localStorage.getItem(`bmv3_parent_profile_Parent`);
    if(pName) {
      const parsed = JSON.parse(pName);
      if(parsed.name) setParentName(parsed.name);
    }
  }, []);

  return (
    <div style={{ animation: 'fadeIn 0.5s ease-in' }}>
      <div style={{ marginBottom: '30px' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#003366', margin: 0 }}>Welcome back, {parentName}</h2>
        <p style={{ margin: '5px 0 0 0', color: '#777', fontSize: '1rem' }}>Date: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>
      </div>

      <div style={{ background: '#003366', color: '#fff', padding: '25px', borderRadius: '15px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ width: '60px', height: '60px', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '10px' }}></div>
          <h3 style={{ margin: 0, fontSize: '1.2rem', textTransform: 'uppercase', letterSpacing: '1px' }}>JOHN DOE</h3>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '8px' }}>ATTENDANCE TODAY</div>
          <div style={{ background: '#00cc00', padding: '5px 20px', borderRadius: '20px', display: 'inline-block', fontWeight: 800, fontSize: '0.9rem' }}>PRESENT</div>
        </div>
      </div>

      <h4 style={{ margin: '20px 0 10px 0', fontSize: '1.1rem' }}>Today</h4>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '15px', marginBottom: '30px', textAlign: 'center' }}>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Drop-off time</div>
          <div style={{ background: '#003366', color: '#fff', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>8:00 AM</div>
        </div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Pick-up Status</div>
          <div style={{ background: '#003366', color: '#fff', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>Successful</div>
        </div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Authorized Guardian</div>
          <div style={{ background: '#003366', color: '#fff', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>{parentName}</div>
        </div>
        <div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '8px' }}>Session</div>
          <div style={{ background: '#003366', color: '#fff', padding: '10px', borderRadius: '25px', fontWeight: 600 }}>Morning</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ background: '#003366', color: '#fff', padding: '25px', borderRadius: '15px' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Today's health & nutrition</h4>
          <div style={{ marginBottom: '15px' }}>
            <strong style={{ fontSize: '0.9rem' }}>Meals logged</strong>
            <ul style={{ margin: '5px 0 0 0', paddingLeft: '20px', fontSize: '0.85rem' }}>
              <li>Breakfast: Lugaw with Egg</li>
              <li>Snack: Yosi with Coke</li>
            </ul>
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
            <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>None</div>
          </div>
        </div>

        <div style={{ background: '#003366', color: '#fff', padding: '25px', borderRadius: '15px' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Today's activities</h4>
          <ul style={{ margin: '0 0 30px 0', paddingLeft: '20px', fontSize: '0.85rem' }}>
            <li>Coloring Activity</li>
            <li>Storytime</li>
            <li>Read and Write</li>
            <li>Brushing of Teeth</li>
          </ul>
          <strong style={{ fontSize: '0.9rem' }}>Teacher's Note</strong>
          <div style={{ fontSize: '0.85rem', marginTop: '5px' }}>None</div>
        </div>

        <div style={{ background: '#003366', color: '#fff', padding: '25px', borderRadius: '15px', position: 'relative' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Latest milestone update</h4>
          <div style={{ display: 'flex', gap: '30px' }}>
            <div>
              <strong style={{ fontSize: '0.9rem' }}>Motor Skills</strong>
              <div style={{ fontSize: '0.8rem', marginTop: '10px' }}>☑ Holds pencil correctly</div>
              <div style={{ fontSize: '0.8rem', marginTop: '5px' }}>☑ Climbs stairs alone</div>
              <div style={{ fontSize: '0.8rem', marginTop: '5px' }}>☑ Catches a ball</div>
            </div>
            <div>
              <strong style={{ fontSize: '0.9rem' }}>Cognitive Skills</strong>
              <div style={{ fontSize: '0.8rem', marginTop: '10px' }}>☑ Counts up to 10</div>
              <div style={{ fontSize: '0.8rem', marginTop: '5px' }}>☑ Identifies basic shapes</div>
              <div style={{ fontSize: '0.8rem', marginTop: '5px' }}>☑ Recognizes own name</div>
            </div>
          </div>
          <button style={{ position: 'absolute', bottom: '20px', right: '20px', background: '#8ebf81', color: '#fff', border: 'none', padding: '8px 20px', borderRadius: '15px', fontWeight: 600, cursor: 'pointer' }}>See More</button>
        </div>

        <div style={{ background: '#003366', color: '#fff', padding: '25px', borderRadius: '15px' }}>
          <h4 style={{ margin: '0 0 20px 0', fontSize: '1.1rem' }}>Recent notifications</h4>
          <div style={{ fontSize: '0.8rem', borderLeft: '2px solid #fff', paddingLeft: '10px', marginBottom: '15px' }}>
            <strong>Drop-off confirmed</strong><br/>
            <span style={{ opacity: 0.8 }}>Drop-off by {parentName} - 8:01 AM - April 12, 2026</span>
          </div>
          <div style={{ fontSize: '0.8rem', borderLeft: '2px solid #fff', paddingLeft: '10px', marginBottom: '15px' }}>
            <strong>Health and Nutrition</strong><br/>
            <span style={{ opacity: 0.8 }}>Health observation - "No fever" - April 12, 2026</span>
          </div>
          <div style={{ fontSize: '0.8rem', borderLeft: '2px solid #fff', paddingLeft: '10px' }}>
            <strong>New milestone recorded</strong><br/>
            <span style={{ opacity: 0.8 }}>Social Skills - "Catches a ball" - April 6, 2026</span>
          </div>
        </div>
      </div>
    </div>
  );
}
