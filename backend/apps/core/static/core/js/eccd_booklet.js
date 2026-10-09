/**
 * ECCD Booklet Interactive Management System
 * Mirrors the physical DepEd / Province of Quezon Child's Record 2 (Age 3y 1m to 5y) Booklet
 */

const MCHAT_QUESTIONS = [
    { no: 1, text: "Kapag may tinuturo ka sa kabilang bahagi ng silid, tinitingnan ba ng anak mo ang iyong itinuturo? (Halimbawa, kapag tinuturo mo ang isang laruan o hayop, tinitingnan ba niya ang laruan o hayop?)", reverse: false },
    { no: 2, text: "Naisip mo ba kung bingi ang iyong anak?", reverse: true },
    { no: 3, text: "Ang anak mo ba ay naglalaro ng mga larong kailangan niyang magkunwari? (Halimbawa, kunwaring umiinom mula sa tasang walang laman, kunwaring nakikipag-usap sa telepono, o kunwaring nagpapakain ng manika o laruang hayop?)", reverse: false },
    { no: 4, text: "Mahilig bang umakyat sa mga bagay ang iyong anak? (Halimbawa, mga upuan, mesa, kagamitan sa palaruan o hagdan?)", reverse: false },
    { no: 5, text: "May kakaibang galaw bang ginagawa ang iyong anak na gamit ang kanyang daliri habang nilalapit ito sa kanyang mga mata?", reverse: true },
    { no: 6, text: "Ang anak mo ba ay nagtuturo ng isang bagay gamit ang isang daliri para humingi nito o kaya'y para humingi ng tulong? (Halimbawa, nagtuturo sa pagkain o laruan na hindi niya abot?)", reverse: false },
    { no: 7, text: "Ang anak mo ba ay nagtuturo gamit ang isang daliri para ipakita sa iyo ang isang bagay na nakakuha ng kaniyang interes? (Halimbawa, pagturo sa eroplano sa himpapawid o sa isang malaking trak sa kalye?)", reverse: false },
    { no: 8, text: "Ang anak mo ba ay interesado sa ibang bata? (Halimbawa, siya ba ay nanunuod sa ibang bata, ngumingiti sa kanila, o lumalapit sa kanila?)", reverse: false },
    { no: 9, text: "Nagpapakita ba sayo ng mga bagay ang iyong anak sa pamamagitan ng pagdala ng mga ito sayo o paglapit ng bagay na ito sa iyong paningin. Hindi para humingi ng tulong kung hindi para ibigay sayo? (Halimbawa, pagpapakita sa iyo ng bulaklak o laruang animal o laruang trak?)", reverse: false },
    { no: 10, text: "Sinasagot ka ba ng iyong anak kapag tinatawag mo ang kaniyang pangalan? (Halimbawa, siya ba ay titingin, magsasalita o gagamitin ang boses para may magawang ingay, o ititigil ang kaniyang ginagawa kapag tinawag mo ang pangalan niya?)", reverse: false },
    { no: 11, text: "Kapag ngumiti ka sa anak mo, siya ba ay ngumingiti pabalik sayo?", reverse: false },
    { no: 12, text: "Naiinis o naiirita ba siya sa mga pang araw-araw na ingay? (Halimbawa, umiiyak o humihiyaw ba ang anak mo sa ingay gaya ng vacuum cleaner o malakas na musika?)", reverse: true },
    { no: 13, text: "Naglalakad ba ang iyong anak?", reverse: false },
    { no: 14, text: "Tinitingnan ka ba ng anak mo sa mata kapag kinakausap mo siya, o nilalaro, o binibihisan?", reverse: false },
    { no: 15, text: "Sinusubukan ba ng anak mo na gayahin ang mga ginagawa mo? (Halimbawa, pagkaway ng kamay ng paalam, o paggawa ng nakakatawang ingay tulad ng sayo?)", reverse: false },
    { no: 16, text: "Kapag lumingon ka para tingnan ang isang bagay, ang anak mo ba ay lilingon rin para makita ang iyong tinitingnan?", reverse: false },
    { no: 17, text: "Sinubukan ba ng anak na kunin ang iyong atensyon para panuorin siya? (Halimbawa, tumingin ba siya sa iyo para purihin mo siya, o sinasabi ba niyang \"Panoorin mo ako\"?)", reverse: false },
    { no: 18, text: "Naiintindihan ba ng anak mo pag may inuutos ka sa kanya? (Halimbawa, kapag di ka nagtuturo, maiintindihan ba niya ang \"ilagay mo ang libro sa ibaba ng upuan\" o \"dalhin mo sa akin ang kumot\"?)", reverse: false },
    { no: 19, text: "Kapag may bagong pangyayari, tinitingnan ba ng anak mo ang mukha mo para makita niya kung ano ang nararamdaman mo tungkol dito? (Halimbawa, kapag may narinig siyang kakaiba o nakakatawang ingay, o kapag may nakita siyang bagong laruan, titingnan ba niya ang mukha mo?)", reverse: false },
    { no: 20, text: "Mahilig ba ang iyong anak sa mga gawaing nangangailangan ng kilos o galaw? (Halimbawa, kapag dinuduyan o tinatalbog sa tuhod mo?)", reverse: false }
];

const EYE_SYMPTOMS = [
    { key: "blurred", label: "Blurred (malabo, maulap o mausok)" },
    { key: "floaters", label: "Floaters (may lumulutang)" },
    { key: "tearing", label: "Tearing (pagluluha)" },
    { key: "pain", label: "Pain (mahapdi, masakit o mabigat sa pakiramdam)" },
    { key: "redness", label: "Redness (namumula)" },
    { key: "glare", label: "Glare (nasisilaw)" },
    { key: "discharge", label: "Discharge (may muta)" },
    { key: "photopsia", label: "Photopsia (may kumikislap)" },
    { key: "itchiness", label: "Itchiness (makati)" },
    { key: "eye_injury", label: "Eye Injury (aksidente sa mata)" },
    { key: "foreign_body", label: "Foreign Body (puwing)" }
];

window.currentBookletData = null;

// Initialize Eye and MCHAT Tables
document.addEventListener('DOMContentLoaded', () => {
    initEyeSymptomsTable();
    initMChatQuestionsTable();
});

function initEyeSymptomsTable() {
    const tbody = document.getElementById('eyeSymptomsTbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    EYE_SYMPTOMS.forEach(s => {
        tbody.innerHTML += `
            <tr style="border-bottom:1px solid #e2e8f0;">
                <td style="padding:8px 12px; font-weight:600; color:#1e293b;">${s.label}</td>
                <td align="center"><input type="checkbox" id="eye_r_${s.key}" style="transform:scale(1.2); cursor:pointer;"></td>
                <td align="center"><input type="checkbox" id="eye_l_${s.key}" style="transform:scale(1.2); cursor:pointer;"></td>
                <td style="padding:6px 12px;"><input type="text" id="eye_rem_${s.key}" class="form-control" style="width:100%; padding:4px 8px; font-size:0.8rem;" placeholder="Remarks..."></td>
            </tr>
        `;
    });
}

function initMChatQuestionsTable() {
    const tbody = document.getElementById('mchatQuestionsTbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    MCHAT_QUESTIONS.forEach(q => {
        tbody.innerHTML += `
            <tr style="border-bottom:1px solid #e2e8f0; transition:background 0.2s;" onmouseover="this.style.background='#f8fafc';" onmouseout="this.style.background='transparent';">
                <td align="center" style="padding:10px; font-weight:800; color:#475569;">${q.no}</td>
                <td style="padding:10px; line-height:1.5; color:#1e293b;">
                    ${q.text}
                    ${q.reverse ? '<span style="font-size:0.7rem; color:#b91c1c; font-weight:bold; margin-left:6px;">[Baliktad na pagsukat]</span>' : ''}
                </td>
                <td align="center" style="padding:10px;">
                    <input type="radio" name="mchat_q_${q.no}" value="OO" onchange="calculateMChatScore()" style="transform:scale(1.3); cursor:pointer;">
                </td>
                <td align="center" style="padding:10px;">
                    <input type="radio" name="mchat_q_${q.no}" value="HINDI" onchange="calculateMChatScore()" style="transform:scale(1.3); cursor:pointer;">
                </td>
            </tr>
        `;
    });
}

/**
 * Open the ECCD Booklet for a selected student
 */
window.openStudentBooklet = async function(childId) {
    document.getElementById('childSelect').value = childId;
    if (typeof loadChildAssessment === 'function') {
        await loadChildAssessment();
    }
    await loadChildBooklet(childId);
    switchTab('cover');
};

/**
 * Fetch and load complete ECCD Booklet data for the child
 */
window.loadChildBooklet = async function(childId) {
    if (!childId) return;

    const childObj = (typeof childrenList !== 'undefined') ? childrenList.find(c => c.id == childId) : null;
    
    // Show active student booklet bar
    const bar = document.getElementById('activeChildBookletBar');
    if (bar && childObj) {
        bar.style.display = 'flex';
        document.getElementById('activeChildName').innerText = `${childObj.last_name}, ${childObj.first_name} ${childObj.middle_initial || ''}`.trim();
        const init = ((childObj.first_name ? childObj.first_name[0] : '') + (childObj.last_name ? childObj.last_name[0] : '')).toUpperCase();
        document.getElementById('activeChildAvatar').innerHTML = childObj.img ? `<img src="${childObj.img}" style="width:100%; height:100%; object-fit:cover;">` : init;
        
        const isMorning = (childObj.shift || 'Morning').toLowerCase().includes('morning');
        document.getElementById('activeChildShiftBadge').innerHTML = isMorning
            ? '<span style="background:#e0f2fe; color:#0284c7; padding:4px 10px; border-radius:12px; font-size:0.75rem; font-weight:800;"><i class="fa-solid fa-sun"></i> Morning Shift</span>'
            : '<span style="background:#ffedd5; color:#ea580c; padding:4px 10px; border-radius:12px; font-size:0.75rem; font-weight:800;"><i class="fa-solid fa-cloud-sun"></i> Afternoon Shift</span>';

        document.getElementById('activeChildAgeText').innerText = childObj.age ? `${childObj.age} Years Old` : 'N/A';
        document.getElementById('activeChildDobText').innerText = childObj.dob || 'Not Set';
        
        const consentChildName = document.getElementById('consent_child_name_text');
        if (consentChildName) consentChildName.innerText = `${childObj.first_name} ${childObj.last_name}`;
    }

    // Unhide booklet navigation tabs
    const bookletTabs = ['tab-cover', 'tab-dashboard', 'tab-summary18', 'tab-graphs', 'tab-notes17', 'tab-mchat', 'tab-health', 'tab-intake'];
    bookletTabs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'inline-flex';
    });

    try {
        const res = await fetch(`/api/eccd-booklet/by-child/${childId}/`);
        if (!res.ok) throw new Error("Failed to load booklet");
        const booklet = await res.json();
        window.currentBookletData = booklet;

        // 1. Populate Sociodemographic Profile
        const s = booklet.sociodemographic || {};
        if (document.getElementById('socio_child_name')) document.getElementById('socio_child_name').value = s.child_name || (childObj ? `${childObj.first_name} ${childObj.last_name}` : '');
        if (document.getElementById('socio_sex')) document.getElementById('socio_sex').value = s.sex || (childObj ? childObj.gender : '');
        if (document.getElementById('socio_dob')) document.getElementById('socio_dob').value = s.dob || (childObj ? childObj.dob : '');
        if (document.getElementById('socio_barangay')) document.getElementById('socio_barangay').value = s.barangay || (childObj ? childObj.barangay : '');
        if (document.getElementById('socio_city')) document.getElementById('socio_city').value = s.city || (childObj ? childObj.city_municipality : 'Lucena City');
        if (document.getElementById('socio_province')) document.getElementById('socio_province').value = s.province || 'Quezon';
        if (document.getElementById('socio_region')) document.getElementById('socio_region').value = s.region || 'Region IV-A';
        
        if (s.handedness) {
            const hRadio = document.querySelector(`input[name="socio_handedness"][value="${s.handedness}"]`);
            if (hRadio) hRadio.checked = true;
        }
        if (s.is_studying) {
            const stRadio = document.querySelector(`input[name="socio_is_studying"][value="${s.is_studying}"]`);
            if (stRadio) stRadio.checked = true;
        }
        if (document.getElementById('socio_school_name')) document.getElementById('socio_school_name').value = s.school_name || 'Barangay Market View 3 Child Development Center';
        if (document.getElementById('socio_father_name')) document.getElementById('socio_father_name').value = s.father_name || '';
        if (document.getElementById('socio_father_age')) document.getElementById('socio_father_age').value = s.father_age || '';
        if (document.getElementById('socio_father_occupation')) document.getElementById('socio_father_occupation').value = s.father_occupation || '';
        if (document.getElementById('socio_father_education')) document.getElementById('socio_father_education').value = s.father_education || '';
        if (document.getElementById('socio_mother_name')) document.getElementById('socio_mother_name').value = s.mother_name || '';
        if (document.getElementById('socio_mother_age')) document.getElementById('socio_mother_age').value = s.mother_age || '';
        if (document.getElementById('socio_mother_occupation')) document.getElementById('socio_mother_occupation').value = s.mother_occupation || '';
        if (document.getElementById('socio_mother_education')) document.getElementById('socio_mother_education').value = s.mother_education || '';
        if (document.getElementById('socio_siblings_count')) document.getElementById('socio_siblings_count').value = s.siblings_count || '';
        if (document.getElementById('socio_birth_order')) document.getElementById('socio_birth_order').value = s.birth_order || '1st';

        // 2. Populate Examiner's Notes
        const n = booklet.examiner_notes || {};
        ['1', '2', '3'].forEach(i => {
            const row = n[`eval_${i}`] || {};
            if (document.getElementById(`notes_examiner_${i}`)) document.getElementById(`notes_examiner_${i}`).value = row.examiner || '';
            if (document.getElementById(`notes_date_${i}`)) document.getElementById(`notes_date_${i}`).value = row.date || '';
            if (document.getElementById(`notes_place_${i}`)) document.getElementById(`notes_place_${i}`).value = row.place || 'BMV3 Child Development Center';
            if (document.getElementById(`notes_child_bg_${i}`)) document.getElementById(`notes_child_bg_${i}`).value = row.child_bg || '';
            if (document.getElementById(`notes_family_env_${i}`)) document.getElementById(`notes_family_env_${i}`).value = row.family_env || '';
            if (document.getElementById(`notes_stimulating_${i}`)) document.getElementById(`notes_stimulating_${i}`).value = row.stimulating || '';
            if (document.getElementById(`notes_home_env_${i}`)) document.getElementById(`notes_home_env_${i}`).value = row.home_env || '';
            if (document.getElementById(`notes_others_${i}`)) document.getElementById(`notes_others_${i}`).value = row.others || '';
        });

        // 3. Populate M-CHAT-R
        const mAnswers = (booklet.mchat_r && booklet.mchat_r.answers) ? booklet.mchat_r.answers : {};
        MCHAT_QUESTIONS.forEach(q => {
            const ans = mAnswers[q.no];
            if (ans) {
                const radio = document.querySelector(`input[name="mchat_q_${q.no}"][value="${ans}"]`);
                if (radio) radio.checked = true;
            }
        });
        calculateMChatScore();

        // 4. Populate Health & Growth
        const h = booklet.health_record || {};
        const g = booklet.growth_chart_data || {};
        const eye = booklet.eye_vision || {};

        if (g.vitamin_a) {
            const r = document.querySelector(`input[name="health_vitamin_a"][value="${g.vitamin_a}"]`);
            if (r) r.checked = true;
        }
        if (g.dental) {
            const r = document.querySelector(`input[name="health_dental"][value="${g.dental}"]`);
            if (r) r.checked = true;
        }
        if (g.deworming) {
            const r = document.querySelector(`input[name="health_deworming"][value="${g.deworming}"]`);
            if (r) r.checked = true;
        }

        // Illness Table
        const illnessTbody = document.getElementById('illnessTbody');
        if (illnessTbody) {
            illnessTbody.innerHTML = '';
            const illnesses = g.illnesses || [];
            if (illnesses.length === 0) {
                addIllnessRow();
            } else {
                illnesses.forEach(item => addIllnessRow(item));
            }
        }

        // Physician Form (Page 27)
        const mat = h.maternal_history || {};
        if (document.getElementById('mat_goiter')) document.getElementById('mat_goiter').checked = !!mat.goiter;
        if (document.getElementById('mat_diabetes')) document.getElementById('mat_diabetes').checked = !!mat.diabetes;
        if (document.getElementById('mat_measles')) document.getElementById('mat_measles').checked = !!mat.measles;
        if (document.getElementById('mat_hepatitis')) document.getElementById('mat_hepatitis').checked = !!mat.hepatitis;
        if (document.getElementById('mat_heart')) document.getElementById('mat_heart').checked = !!mat.heart;
        if (document.getElementById('mat_other')) document.getElementById('mat_other').value = mat.other || '';

        if (document.getElementById('del_type')) document.getElementById('del_type').value = h.delivery_type || 'Normal';
        if (document.getElementById('del_place')) document.getElementById('del_place').value = h.delivery_place || 'Hospital';
        if (document.getElementById('del_complications')) document.getElementById('del_complications').value = h.complications || '';
        if (document.getElementById('del_allergies')) document.getElementById('del_allergies').value = h.allergies || (childObj ? childObj.allergies : '');

        const imm = h.immunization || {};
        ['dpt', 'polio', 'bcg', 'measles', 'tetanus', 'hepa_b'].forEach(k => {
            if (document.getElementById(`imm_${k}`)) document.getElementById(`imm_${k}`).value = imm[k] || '';
        });

        if (h.deworming_status) {
            const r = document.querySelector(`input[name="deworm_radio"][value="${h.deworming_status}"]`);
            if (r) r.checked = true;
        }
        if (document.getElementById('deworm_date')) document.getElementById('deworm_date').value = h.deworming_date || '';

        const dis = h.disabilities || {};
        if (document.getElementById('dis_deformities')) document.getElementById('dis_deformities').checked = !!dis.deformities;
        if (document.getElementById('dis_deafness')) document.getElementById('dis_deafness').checked = !!dis.deafness;
        if (document.getElementById('dis_speech')) document.getElementById('dis_speech').checked = !!dis.speech;
        if (document.getElementById('dis_emotional')) document.getElementById('dis_emotional').checked = !!dis.emotional;

        const pe = h.physical_exam || {};
        ['heent', 'abdomen', 'gut', 'muscular', 'neuro'].forEach(k => {
            if (document.getElementById(`pe_${k}`)) document.getElementById(`pe_${k}`).value = pe[k] || 'Normal';
        });

        if (document.getElementById('physician_sig_name')) document.getElementById('physician_sig_name').value = h.physician_sig_name || '';
        if (document.getElementById('dental_sig_name')) document.getElementById('dental_sig_name').value = h.dental_sig_name || '';

        // Eye Assessment
        const sym = eye.symptoms || {};
        EYE_SYMPTOMS.forEach(s => {
            const sData = sym[s.key] || {};
            if (document.getElementById(`eye_r_${s.key}`)) document.getElementById(`eye_r_${s.key}`).checked = !!sData.r;
            if (document.getElementById(`eye_l_${s.key}`)) document.getElementById(`eye_l_${s.key}`).checked = !!sData.l;
            if (document.getElementById(`eye_rem_${s.key}`)) document.getElementById(`eye_rem_${s.key}`).value = sData.rem || '';
        });

        const va = eye.visual_acuity || {};
        ['aided_far', 'aided_near', 'unaided_far', 'unaided_near'].forEach(k => {
            const vData = va[k] || {};
            if (document.getElementById(`va_${k}_r`)) document.getElementById(`va_${k}_r`).value = vData.r || '';
            if (document.getElementById(`va_${k}_l`)) document.getElementById(`va_${k}_l`).value = vData.l || '';
            if (document.getElementById(`va_${k}_rem`)) document.getElementById(`va_${k}_rem`).value = vData.rem || '';
        });

        if (document.getElementById('eye_screener_name')) document.getElementById('eye_screener_name').value = eye.screener_name || '';
        if (document.getElementById('eye_exam_date')) document.getElementById('eye_exam_date').value = eye.exam_date || '';
        if (document.getElementById('eye_recommendations')) document.getElementById('eye_recommendations').value = eye.recommendations || '';
        if (document.getElementById('eye_practitioner_name')) document.getElementById('eye_practitioner_name').value = eye.practitioner_name || '';

        // 5. Populate Intake & Consent
        const itk = booklet.intake_form || {};
        if (document.getElementById('intake_religion')) document.getElementById('intake_religion').value = itk.religion || '';
        if (document.getElementById('intake_birthplace')) document.getElementById('intake_birthplace').value = itk.birthplace || '';
        if (document.getElementById('intake_nutritional_status')) document.getElementById('intake_nutritional_status').value = itk.nutritional_status || 'Normal';
        if (document.getElementById('intake_handicap')) document.getElementById('intake_handicap').value = itk.handicap || 'None';

        if (itk.birth_cert) {
            const r = document.querySelector(`input[name="intake_birth_cert"][value="${itk.birth_cert}"]`);
            if (r) r.checked = true;
        }

        const devInfo = itk.dev_indicators || {};
        ['motor', 'personal_social', 'cognitive', 'language', 'val_god', 'val_self', 'val_family', 'val_nonrelatives', 'val_community'].forEach(k => {
            if (document.getElementById(`dev_${k}`)) document.getElementById(`dev_${k}`).checked = !!devInfo[k];
        });

        const hc = itk.home_conditions || {};
        if (document.getElementById('home_detrimental_home')) document.getElementById('home_detrimental_home').value = hc.detrimental_home || '';
        if (document.getElementById('home_detrimental_neigh')) document.getElementById('home_detrimental_neigh').value = hc.detrimental_neighborhood || '';
        if (document.getElementById('home_distance')) document.getElementById('home_distance').value = hc.distance || '';
        if (document.getElementById('home_transpo')) document.getElementById('home_transpo').value = hc.transpo || '';
        if (document.getElementById('home_escort')) document.getElementById('home_escort').value = hc.escort || '';
        if (document.getElementById('home_receiver')) document.getElementById('home_receiver').value = hc.receiver || '';

        const peExp = itk.parental_expectations || {};
        for (let i = 1; i <= 7; i++) {
            if (document.getElementById(`pexpect_${i}`)) document.getElementById(`pexpect_${i}`).value = peExp[`q${i}`] || '';
        }

        const ev = itk.evaluation || {};
        if (document.getElementById('eval_eligibility')) document.getElementById('eval_eligibility').value = ev.eligibility || 'Eligible for Day Care Service Program';
        if (document.getElementById('eval_period')) document.getElementById('eval_period').value = ev.period || '1 School Year (10 months)';
        if (document.getElementById('eval_worker_name')) document.getElementById('eval_worker_name').value = ev.worker_name || '';
        if (document.getElementById('eval_social_worker_name')) document.getElementById('eval_social_worker_name').value = ev.social_worker_name || '';

        // Family Composition Table
        const fcTbody = document.getElementById('familyCompTbody');
        if (fcTbody) {
            fcTbody.innerHTML = '';
            const members = itk.family_members || [];
            if (members.length === 0) {
                addFamilyMemberRow();
            } else {
                members.forEach(m => addFamilyMemberRow(m));
            }
        }

        // Consent Form
        const cf = booklet.consent_form || {};
        if (document.getElementById('consent_father_name')) document.getElementById('consent_father_name').value = cf.father_name || '';
        if (document.getElementById('consent_mother_name')) document.getElementById('consent_mother_name').value = cf.mother_name || '';
        if (document.getElementById('consent_residence')) document.getElementById('consent_residence').value = cf.residence || 'Barangay Market View 3, Lucena City';
        if (document.getElementById('consent_birthdate')) document.getElementById('consent_birthdate').value = cf.birthdate || (childObj ? childObj.dob : '');
        if (document.getElementById('consent_birthplace')) document.getElementById('consent_birthplace').value = cf.birthplace || '';
        if (document.getElementById('consent_referred_to')) document.getElementById('consent_referred_to').value = cf.referred_to || 'BMV3 Child Development Center';
        if (document.getElementById('consent_referred_by')) document.getElementById('consent_referred_by').value = cf.referred_by || '';
        if (document.getElementById('consent_period')) document.getElementById('consent_period').value = cf.period || '1 School Year';
        if (document.getElementById('consent_issued_date')) document.getElementById('consent_issued_date').value = cf.issued_date || '';
        if (document.getElementById('consent_issued_place')) document.getElementById('consent_issued_place').value = cf.issued_place || 'Lucena City, Quezon';
        if (document.getElementById('consent_witness_social')) document.getElementById('consent_witness_social').value = cf.witness_social || '';
        if (document.getElementById('consent_witness_worker')) document.getElementById('consent_witness_worker').value = cf.witness_worker || '';

        // Behavior Records Table
        const behTbody = document.getElementById('behaviorRecordsTbody');
        if (behTbody) {
            behTbody.innerHTML = '';
            const behList = booklet.behavior_records || [];
            if (behList.length === 0) {
                addBehaviorRow();
            } else {
                behList.forEach(b => addBehaviorRow(b));
            }
        }

        // Render Page 18, 19, 20 & Growth Curve
        renderPage18Table();
        renderPage19Graph();
        renderPage20Graph();
        renderGrowthChartSvg();

    } catch (err) {
        console.error("Error loading booklet:", err);
    }
};

/**
 * Save all updated ECCD Booklet records to the backend
 */
window.saveBooklet = async function() {
    const childId = document.getElementById('childSelect').value;
    if (!childId) {
        alert("Please select a child to save booklet details.");
        return;
    }

    // Collect Sociodemographic
    const handednessChecked = document.querySelector('input[name="socio_handedness"]:checked');
    const studyingChecked = document.querySelector('input[name="socio_is_studying"]:checked');
    const socio = {
        child_name: document.getElementById('socio_child_name') ? document.getElementById('socio_child_name').value : '',
        sex: document.getElementById('socio_sex') ? document.getElementById('socio_sex').value : '',
        dob: document.getElementById('socio_dob') ? document.getElementById('socio_dob').value : '',
        barangay: document.getElementById('socio_barangay') ? document.getElementById('socio_barangay').value : '',
        city: document.getElementById('socio_city') ? document.getElementById('socio_city').value : '',
        province: document.getElementById('socio_province') ? document.getElementById('socio_province').value : '',
        region: document.getElementById('socio_region') ? document.getElementById('socio_region').value : '',
        handedness: handednessChecked ? handednessChecked.value : '',
        is_studying: studyingChecked ? studyingChecked.value : 'Yes',
        school_name: document.getElementById('socio_school_name') ? document.getElementById('socio_school_name').value : '',
        father_name: document.getElementById('socio_father_name') ? document.getElementById('socio_father_name').value : '',
        father_age: document.getElementById('socio_father_age') ? document.getElementById('socio_father_age').value : '',
        father_occupation: document.getElementById('socio_father_occupation') ? document.getElementById('socio_father_occupation').value : '',
        father_education: document.getElementById('socio_father_education') ? document.getElementById('socio_father_education').value : '',
        mother_name: document.getElementById('socio_mother_name') ? document.getElementById('socio_mother_name').value : '',
        mother_age: document.getElementById('socio_mother_age') ? document.getElementById('socio_mother_age').value : '',
        mother_occupation: document.getElementById('socio_mother_occupation') ? document.getElementById('socio_mother_occupation').value : '',
        mother_education: document.getElementById('socio_mother_education') ? document.getElementById('socio_mother_education').value : '',
        siblings_count: document.getElementById('socio_siblings_count') ? document.getElementById('socio_siblings_count').value : '',
        birth_order: document.getElementById('socio_birth_order') ? document.getElementById('socio_birth_order').value : ''
    };

    // Collect Examiner's Notes
    const notes = {};
    ['1', '2', '3'].forEach(i => {
        notes[`eval_${i}`] = {
            examiner: document.getElementById(`notes_examiner_${i}`) ? document.getElementById(`notes_examiner_${i}`).value : '',
            date: document.getElementById(`notes_date_${i}`) ? document.getElementById(`notes_date_${i}`).value : '',
            place: document.getElementById(`notes_place_${i}`) ? document.getElementById(`notes_place_${i}`).value : '',
            child_bg: document.getElementById(`notes_child_bg_${i}`) ? document.getElementById(`notes_child_bg_${i}`).value : '',
            family_env: document.getElementById(`notes_family_env_${i}`) ? document.getElementById(`notes_family_env_${i}`).value : '',
            stimulating: document.getElementById(`notes_stimulating_${i}`) ? document.getElementById(`notes_stimulating_${i}`).value : '',
            home_env: document.getElementById(`notes_home_env_${i}`) ? document.getElementById(`notes_home_env_${i}`).value : '',
            others: document.getElementById(`notes_others_${i}`) ? document.getElementById(`notes_others_${i}`).value : ''
        };
    });

    // Collect M-CHAT-R
    const mAnswers = {};
    let mScore = 0;
    MCHAT_QUESTIONS.forEach(q => {
        const sel = document.querySelector(`input[name="mchat_q_${q.no}"]:checked`);
        if (sel) {
            mAnswers[q.no] = sel.value;
            if (q.reverse) {
                if (sel.value === 'OO') mScore++;
            } else {
                if (sel.value === 'HINDI') mScore++;
            }
        }
    });
    const mchat = {
        answers: mAnswers,
        risk_score: mScore,
        risk_level: mScore <= 2 ? 'Low Risk' : (mScore <= 7 ? 'Medium Risk' : 'High Risk')
    };

    // Collect Health & Growth
    const vitA = document.querySelector('input[name="health_vitamin_a"]:checked');
    const dental = document.querySelector('input[name="health_dental"]:checked');
    const deworm = document.querySelector('input[name="health_deworming"]:checked');
    
    const illnessRows = [];
    document.querySelectorAll('#illnessTbody tr').forEach(tr => {
        const type = tr.querySelector('.illness-type') ? tr.querySelector('.illness-type').value : '';
        const dt = tr.querySelector('.illness-date') ? tr.querySelector('.illness-date').value : '';
        const interv = tr.querySelector('.illness-interv') ? tr.querySelector('.illness-interv').value : '';
        if (type || dt) illnessRows.push({ type, date: dt, intervention: interv });
    });

    const growth = {
        vitamin_a: vitA ? vitA.value : '',
        dental: dental ? dental.value : '',
        deworming: deworm ? deworm.value : '',
        illnesses: illnessRows
    };

    const dewormStat = document.querySelector('input[name="deworm_radio"]:checked');
    const health = {
        maternal_history: {
            goiter: document.getElementById('mat_goiter') ? document.getElementById('mat_goiter').checked : false,
            diabetes: document.getElementById('mat_diabetes') ? document.getElementById('mat_diabetes').checked : false,
            measles: document.getElementById('mat_measles') ? document.getElementById('mat_measles').checked : false,
            hepatitis: document.getElementById('mat_hepatitis') ? document.getElementById('mat_hepatitis').checked : false,
            heart: document.getElementById('mat_heart') ? document.getElementById('mat_heart').checked : false,
            other: document.getElementById('mat_other') ? document.getElementById('mat_other').value : ''
        },
        delivery_type: document.getElementById('del_type') ? document.getElementById('del_type').value : 'Normal',
        delivery_place: document.getElementById('del_place') ? document.getElementById('del_place').value : 'Hospital',
        complications: document.getElementById('del_complications') ? document.getElementById('del_complications').value : '',
        allergies: document.getElementById('del_allergies') ? document.getElementById('del_allergies').value : '',
        immunization: {
            dpt: document.getElementById('imm_dpt') ? document.getElementById('imm_dpt').value : '',
            polio: document.getElementById('imm_polio') ? document.getElementById('imm_polio').value : '',
            bcg: document.getElementById('imm_bcg') ? document.getElementById('imm_bcg').value : '',
            measles: document.getElementById('imm_measles') ? document.getElementById('imm_measles').value : '',
            tetanus: document.getElementById('imm_tetanus') ? document.getElementById('imm_tetanus').value : '',
            hepa_b: document.getElementById('imm_hepa_b') ? document.getElementById('imm_hepa_b').value : ''
        },
        deworming_status: dewormStat ? dewormStat.value : '',
        deworming_date: document.getElementById('deworm_date') ? document.getElementById('deworm_date').value : '',
        disabilities: {
            deformities: document.getElementById('dis_deformities') ? document.getElementById('dis_deformities').checked : false,
            deafness: document.getElementById('dis_deafness') ? document.getElementById('dis_deafness').checked : false,
            speech: document.getElementById('dis_speech') ? document.getElementById('dis_speech').checked : false,
            emotional: document.getElementById('dis_emotional') ? document.getElementById('dis_emotional').checked : false
        },
        physical_exam: {
            heent: document.getElementById('pe_heent') ? document.getElementById('pe_heent').value : 'Normal',
            abdomen: document.getElementById('pe_abdomen') ? document.getElementById('pe_abdomen').value : 'Normal',
            gut: document.getElementById('pe_gut') ? document.getElementById('pe_gut').value : 'Normal',
            muscular: document.getElementById('pe_muscular') ? document.getElementById('pe_muscular').value : 'Normal',
            neuro: document.getElementById('pe_neuro') ? document.getElementById('pe_neuro').value : 'Normal'
        },
        physician_sig_name: document.getElementById('physician_sig_name') ? document.getElementById('physician_sig_name').value : '',
        dental_sig_name: document.getElementById('dental_sig_name') ? document.getElementById('dental_sig_name').value : ''
    };

    // Eye Assessment
    const eyeSym = {};
    EYE_SYMPTOMS.forEach(s => {
        eyeSym[s.key] = {
            r: document.getElementById(`eye_r_${s.key}`) ? document.getElementById(`eye_r_${s.key}`).checked : false,
            l: document.getElementById(`eye_l_${s.key}`) ? document.getElementById(`eye_l_${s.key}`).checked : false,
            rem: document.getElementById(`eye_rem_${s.key}`) ? document.getElementById(`eye_rem_${s.key}`).value : ''
        };
    });
    const eye = {
        symptoms: eyeSym,
        visual_acuity: {
            aided_far: { r: document.getElementById('va_aided_far_r').value, l: document.getElementById('va_aided_far_l').value, rem: document.getElementById('va_aided_far_rem').value },
            aided_near: { r: document.getElementById('va_aided_near_r').value, l: document.getElementById('va_aided_near_l').value, rem: document.getElementById('va_aided_near_rem').value },
            unaided_far: { r: document.getElementById('va_unaided_far_r').value, l: document.getElementById('va_unaided_far_l').value, rem: document.getElementById('va_unaided_far_rem').value },
            unaided_near: { r: document.getElementById('va_unaided_near_r').value, l: document.getElementById('va_unaided_near_l').value, rem: document.getElementById('va_unaided_near_rem').value }
        },
        screener_name: document.getElementById('eye_screener_name') ? document.getElementById('eye_screener_name').value : '',
        exam_date: document.getElementById('eye_exam_date') ? document.getElementById('eye_exam_date').value : '',
        recommendations: document.getElementById('eye_recommendations') ? document.getElementById('eye_recommendations').value : '',
        practitioner_name: document.getElementById('eye_practitioner_name') ? document.getElementById('eye_practitioner_name').value : ''
    };

    // Intake & Family Composition
    const famRows = [];
    document.querySelectorAll('#familyCompTbody tr').forEach(tr => {
        const name = tr.querySelector('.fam-name') ? tr.querySelector('.fam-name').value : '';
        const age = tr.querySelector('.fam-age') ? tr.querySelector('.fam-age').value : '';
        const sex = tr.querySelector('.fam-sex') ? tr.querySelector('.fam-sex').value : '';
        const civil = tr.querySelector('.fam-civil') ? tr.querySelector('.fam-civil').value : '';
        const rel = tr.querySelector('.fam-rel') ? tr.querySelector('.fam-rel').value : '';
        const educ = tr.querySelector('.fam-educ') ? tr.querySelector('.fam-educ').value : '';
        const occ = tr.querySelector('.fam-occ') ? tr.querySelector('.fam-occ').value : '';
        const inc = tr.querySelector('.fam-inc') ? tr.querySelector('.fam-inc').value : '';
        if (name) famRows.push({ name, age, sex, civil, rel, educ, occ, inc });
    });

    const bCert = document.querySelector('input[name="intake_birth_cert"]:checked');
    const pExp = {};
    for (let i = 1; i <= 7; i++) {
        pExp[`q${i}`] = document.getElementById(`pexpect_${i}`) ? document.getElementById(`pexpect_${i}`).value : '';
    }

    const intake = {
        religion: document.getElementById('intake_religion') ? document.getElementById('intake_religion').value : '',
        birthplace: document.getElementById('intake_birthplace') ? document.getElementById('intake_birthplace').value : '',
        nutritional_status: document.getElementById('intake_nutritional_status') ? document.getElementById('intake_nutritional_status').value : '',
        handicap: document.getElementById('intake_handicap') ? document.getElementById('intake_handicap').value : '',
        birth_cert: bCert ? bCert.value : 'Available',
        family_members: famRows,
        dev_indicators: {
            motor: document.getElementById('dev_motor') ? document.getElementById('dev_motor').checked : false,
            personal_social: document.getElementById('dev_personal_social') ? document.getElementById('dev_personal_social').checked : false,
            cognitive: document.getElementById('dev_cognitive') ? document.getElementById('dev_cognitive').checked : false,
            language: document.getElementById('dev_language') ? document.getElementById('dev_language').checked : false,
            val_god: document.getElementById('dev_val_god') ? document.getElementById('dev_val_god').checked : false,
            val_self: document.getElementById('dev_val_self') ? document.getElementById('dev_val_self').checked : false,
            val_family: document.getElementById('dev_val_family') ? document.getElementById('dev_val_family').checked : false,
            val_nonrelatives: document.getElementById('dev_val_nonrelatives') ? document.getElementById('dev_val_nonrelatives').checked : false,
            val_community: document.getElementById('dev_val_community') ? document.getElementById('dev_val_community').checked : false
        },
        home_conditions: {
            detrimental_home: document.getElementById('home_detrimental_home') ? document.getElementById('home_detrimental_home').value : '',
            detrimental_neighborhood: document.getElementById('home_detrimental_neigh') ? document.getElementById('home_detrimental_neigh').value : '',
            distance: document.getElementById('home_distance') ? document.getElementById('home_distance').value : '',
            transpo: document.getElementById('home_transpo') ? document.getElementById('home_transpo').value : '',
            escort: document.getElementById('home_escort') ? document.getElementById('home_escort').value : '',
            receiver: document.getElementById('home_receiver') ? document.getElementById('home_receiver').value : ''
        },
        parental_expectations: pExp,
        evaluation: {
            eligibility: document.getElementById('eval_eligibility') ? document.getElementById('eval_eligibility').value : '',
            period: document.getElementById('eval_period') ? document.getElementById('eval_period').value : '',
            worker_name: document.getElementById('eval_worker_name') ? document.getElementById('eval_worker_name').value : '',
            social_worker_name: document.getElementById('eval_social_worker_name') ? document.getElementById('eval_social_worker_name').value : ''
        }
    };

    // Consent Form
    const consent = {
        father_name: document.getElementById('consent_father_name') ? document.getElementById('consent_father_name').value : '',
        mother_name: document.getElementById('consent_mother_name') ? document.getElementById('consent_mother_name').value : '',
        residence: document.getElementById('consent_residence') ? document.getElementById('consent_residence').value : '',
        birthdate: document.getElementById('consent_birthdate') ? document.getElementById('consent_birthdate').value : '',
        birthplace: document.getElementById('consent_birthplace') ? document.getElementById('consent_birthplace').value : '',
        referred_to: document.getElementById('consent_referred_to') ? document.getElementById('consent_referred_to').value : '',
        referred_by: document.getElementById('consent_referred_by') ? document.getElementById('consent_referred_by').value : '',
        period: document.getElementById('consent_period') ? document.getElementById('consent_period').value : '',
        issued_date: document.getElementById('consent_issued_date') ? document.getElementById('consent_issued_date').value : '',
        issued_place: document.getElementById('consent_issued_place') ? document.getElementById('consent_issued_place').value : '',
        witness_social: document.getElementById('consent_witness_social') ? document.getElementById('consent_witness_social').value : '',
        witness_worker: document.getElementById('consent_witness_worker') ? document.getElementById('consent_witness_worker').value : ''
    };

    // Behavior Records
    const behRows = [];
    document.querySelectorAll('#behaviorRecordsTbody tr').forEach(tr => {
        const dt = tr.querySelector('.beh-date') ? tr.querySelector('.beh-date').value : '';
        const obs = tr.querySelector('.beh-obs') ? tr.querySelector('.beh-obs').value : '';
        const disc = tr.querySelector('.beh-disc') ? tr.querySelector('.beh-disc').value : '';
        if (dt || obs) behRows.push({ date: dt, observation: obs, discussion: disc });
    });

    const payload = {
        sociodemographic: socio,
        examiner_notes: notes,
        mchat_r: mchat,
        growth_chart_data: growth,
        health_record: health,
        eye_vision: eye,
        intake_form: intake,
        consent_form: consent,
        behavior_records: behRows
    };

    try {
        const resp = await fetch(`/api/eccd-booklet/by-child/${childId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });
        const result = await resp.json();
        if (result.success) {
            showToastMessage("ECCD Booklet changes saved successfully!", "success");
        } else {
            alert("Failed to save changes. Please try again.");
        }
    } catch (e) {
        console.error(e);
        alert("Network error occurred while saving booklet.");
    }
};

/**
 * Toast Notification Helper
 */
function showToastMessage(msg, type = 'success') {
    const existing = document.getElementById('eccdToastBox');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'eccdToastBox';
    toast.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: ${type === 'success' ? '#15803d' : '#b91c1c'};
        color: white;
        padding: 14px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.2);
        font-weight: 700;
        font-size: 0.95rem;
        z-index: 99999;
        display: flex;
        align-items: center;
        gap: 10px;
        animation: fadeIn 0.3s ease;
    `;
    toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${msg}`;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.4s';
        setTimeout(() => toast.remove(), 400);
    }, 3200);
}

/**
 * Real-time M-CHAT-R Risk Calculator
 */
window.calculateMChatScore = function() {
    let score = 0;
    let answeredCount = 0;

    MCHAT_QUESTIONS.forEach(q => {
        const sel = document.querySelector(`input[name="mchat_q_${q.no}"]:checked`);
        if (sel) {
            answeredCount++;
            if (q.reverse) {
                if (sel.value === 'OO') score++;
            } else {
                if (sel.value === 'HINDI') score++;
            }
        }
    });

    const badge = document.getElementById('mchatTotalScoreBadge');
    const levelText = document.getElementById('mchatRiskLevel');
    const descText = document.getElementById('mchatRiskDesc');
    const alertBox = document.getElementById('mchatRiskAlert');
    const icon = document.getElementById('mchatRiskIcon');

    if (!badge) return;

    badge.innerText = `${score} / 20`;

    if (score <= 2) {
        // Low Risk
        badge.style.background = '#15803d';
        if (alertBox) { alertBox.style.background = '#f0fdf4'; alertBox.style.borderColor = '#bbf7d0'; }
        if (levelText) { levelText.innerText = 'Mababang Panganib (Low Risk)'; levelText.style.color = '#14532d'; }
        if (descText) descText.innerText = 'Kabuuang puntos 0-2: Karaniwang pag-unlad ang ipinapahiwatig. Ipagpatuloy ang pagsubaybay sa regular na pag-aaral.';
        if (icon) { icon.style.background = '#16a34a'; icon.innerHTML = '<i class="fa-solid fa-check"></i>'; }
    } else if (score <= 7) {
        // Medium Risk
        badge.style.background = '#d97706';
        if (alertBox) { alertBox.style.background = '#fffbeb'; alertBox.style.borderColor = '#fde68a'; }
        if (levelText) { levelText.innerText = 'Katamtamang Panganib (Medium Risk)'; levelText.style.color = '#92400e'; }
        if (descText) descText.innerText = 'Kabuuang puntos 3-7: Inirerekomenda ang follow-up screening o konsultasyon sa Child Development Specialist / Pediatrician.';
        if (icon) { icon.style.background = '#f59e0b'; icon.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>'; }
    } else {
        // High Risk
        badge.style.background = '#b91c1c';
        if (alertBox) { alertBox.style.background = '#fef2f2'; alertBox.style.borderColor = '#fecaca'; }
        if (levelText) { levelText.innerText = 'Mataas na Panganib (High Risk)'; levelText.style.color = '#991b1b'; }
        if (descText) descText.innerText = 'Kabuuang puntos 8-20: Agarang pagsangguni sa Developmental Pediatrician para sa komprehensibong clinical diagnostic assessment at early intervention.';
        if (icon) { icon.style.background = '#dc2626'; icon.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i>'; }
    }
};

/**
 * Sub-tab switchers
 */
window.switchGraphPage = function(pageNum) {
    const btn19 = document.getElementById('btnGraphPage19');
    const btn20 = document.getElementById('btnGraphPage20');
    const sec19 = document.getElementById('graphSectionPage19');
    const sec20 = document.getElementById('graphSectionPage20');

    if (pageNum === 19) {
        btn19.style.background = '#043263';
        btn19.style.color = 'white';
        btn20.style.background = 'transparent';
        btn20.style.color = '#64748b';
        sec19.style.display = 'block';
        sec20.style.display = 'none';
        renderPage19Graph();
    } else {
        btn20.style.background = '#043263';
        btn20.style.color = 'white';
        btn19.style.background = 'transparent';
        btn19.style.color = '#64748b';
        sec20.style.display = 'block';
        sec19.style.display = 'none';
        renderPage20Graph();
    }
};

window.switchHealthSubTab = function(sub) {
    ['Growth', 'Record', 'Eye'].forEach(k => {
        const btn = document.getElementById(`btnSubHealth${k}`);
        if (btn) {
            btn.style.background = 'transparent';
            btn.style.color = '#64748b';
        }
    });
    document.getElementById('healthSubSectionGrowth').style.display = 'none';
    document.getElementById('healthSubSectionRecord').style.display = 'none';
    document.getElementById('healthSubSectionEye').style.display = 'none';

    if (sub === 'growth') {
        document.getElementById('btnSubHealthGrowth').style.background = '#043263';
        document.getElementById('btnSubHealthGrowth').style.color = 'white';
        document.getElementById('healthSubSectionGrowth').style.display = 'block';
        renderGrowthChartSvg();
    } else if (sub === 'record') {
        document.getElementById('btnSubHealthRecord').style.background = '#043263';
        document.getElementById('btnSubHealthRecord').style.color = 'white';
        document.getElementById('healthSubSectionRecord').style.display = 'block';
    } else if (sub === 'eye') {
        document.getElementById('btnSubHealthEye').style.background = '#043263';
        document.getElementById('btnSubHealthEye').style.color = 'white';
        document.getElementById('healthSubSectionEye').style.display = 'block';
    }
};

window.switchIntakeSubTab = function(sub) {
    ['Form', 'Consent', 'Behavior'].forEach(k => {
        const btn = document.getElementById(`btnSubIntake${k}`);
        if (btn) {
            btn.style.background = 'transparent';
            btn.style.color = '#64748b';
        }
    });
    document.getElementById('intakeSubSectionIntake').style.display = 'none';
    document.getElementById('intakeSubSectionConsent').style.display = 'none';
    document.getElementById('intakeSubSectionBehavior').style.display = 'none';

    if (sub === 'intake') {
        document.getElementById('btnSubIntakeForm').style.background = '#043263';
        document.getElementById('btnSubIntakeForm').style.color = 'white';
        document.getElementById('intakeSubSectionIntake').style.display = 'block';
    } else if (sub === 'consent') {
        document.getElementById('btnSubConsent').style.background = '#043263';
        document.getElementById('btnSubConsent').style.color = 'white';
        document.getElementById('intakeSubSectionConsent').style.display = 'block';
    } else if (sub === 'behavior') {
        document.getElementById('btnSubBehavior').style.background = '#043263';
        document.getElementById('btnSubBehavior').style.color = 'white';
        document.getElementById('intakeSubSectionBehavior').style.display = 'block';
    }
};

/**
 * Dynamic Table Row Adders / Removers
 */
window.addFamilyMemberRow = function(data = {}) {
    const tbody = document.getElementById('familyCompTbody');
    if (!tbody) return;
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid #e2e8f0';
    tr.innerHTML = `
        <td style="padding:4px;"><input type="text" class="form-control fam-name" style="width:100%; padding:4px;" value="${data.name || ''}" placeholder="Full Name"></td>
        <td style="padding:4px;"><input type="number" class="form-control fam-age" style="width:100%; padding:4px; text-align:center;" value="${data.age || ''}"></td>
        <td style="padding:4px;">
            <select class="form-control fam-sex" style="width:100%; padding:4px;">
                <option value="M" ${data.sex === 'M' ? 'selected' : ''}>M</option>
                <option value="F" ${data.sex === 'F' ? 'selected' : ''}>F</option>
            </select>
        </td>
        <td style="padding:4px;"><input type="text" class="form-control fam-civil" style="width:100%; padding:4px; text-align:center;" value="${data.civil || 'Single'}"></td>
        <td style="padding:4px;"><input type="text" class="form-control fam-rel" style="width:100%; padding:4px;" value="${data.rel || ''}" placeholder="e.g. Sibling"></td>
        <td style="padding:4px;"><input type="text" class="form-control fam-educ" style="width:100%; padding:4px;" value="${data.educ || ''}" placeholder="Education"></td>
        <td style="padding:4px;"><input type="text" class="form-control fam-occ" style="width:100%; padding:4px;" value="${data.occ || ''}" placeholder="Occupation"></td>
        <td style="padding:4px;"><input type="text" class="form-control fam-inc" style="width:100%; padding:4px;" value="${data.inc || ''}" placeholder="Income"></td>
        <td align="center" style="padding:4px;"><button type="button" onclick="this.closest('tr').remove()" style="background:none; border:none; color:#ef4444; cursor:pointer;"><i class="fa-solid fa-trash"></i></button></td>
    `;
    tbody.appendChild(tr);
};

window.addIllnessRow = function(data = {}) {
    const tbody = document.getElementById('illnessTbody');
    if (!tbody) return;
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid #e2e8f0';
    tr.innerHTML = `
        <td style="padding:6px;"><input type="text" class="form-control illness-type" style="width:100%; padding:4px;" value="${data.type || ''}" placeholder="e.g. Bronchitis"></td>
        <td style="padding:6px;"><input type="date" class="form-control illness-date" style="width:100%; padding:4px;" value="${data.date || ''}"></td>
        <td style="padding:6px;"><input type="text" class="form-control illness-interv" style="width:100%; padding:4px;" value="${data.intervention || ''}" placeholder="Antibiotics / Doctor check"></td>
        <td align="center" style="padding:6px;"><button type="button" onclick="this.closest('tr').remove()" style="background:none; border:none; color:#ef4444; cursor:pointer;"><i class="fa-solid fa-trash"></i></button></td>
    `;
    tbody.appendChild(tr);
};

window.addBehaviorRow = function(data = {}) {
    const tbody = document.getElementById('behaviorRecordsTbody');
    if (!tbody) return;
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid #e2e8f0';
    tr.innerHTML = `
        <td style="padding:6px;"><input type="date" class="form-control beh-date" style="width:100%; padding:4px; text-align:center;" value="${data.date || ''}"></td>
        <td style="padding:6px;"><input type="text" class="form-control beh-obs" style="width:100%; padding:4px;" value="${data.observation || ''}" placeholder="Special need / observed behavior..."></td>
        <td style="padding:6px;"><input type="text" class="form-control beh-disc" style="width:100%; padding:4px;" value="${data.discussion || ''}" placeholder="Activity taken / parent discussion..."></td>
        <td align="center" style="padding:6px;"><button type="button" onclick="this.closest('tr').remove()" style="background:none; border:none; color:#ef4444; cursor:pointer;"><i class="fa-solid fa-trash"></i></button></td>
    `;
    tbody.appendChild(tr);
};

/**
 * Render Page 18 Evaluation Summary Table
 */
window.renderPage18Table = function() {
    const tbody = document.getElementById('page18Tbody');
    const tfoot = document.getElementById('page18Tfoot');
    if (!tbody || !window.currentChildReports) return;

    const r1 = window.currentChildReports['1st'] || {};
    const r2 = window.currentChildReports['2nd'] || {};
    const r3 = window.currentChildReports['3rd'] || {};
    const rOverall = window.currentChildReports['Overall'] || {};

    const a1 = (typeof currentAssessments !== 'undefined') ? currentAssessments.find(a => a.assessment_period === '1st') : null;
    const a2 = (typeof currentAssessments !== 'undefined') ? currentAssessments.find(a => a.assessment_period === '2nd') : null;
    const a3 = (typeof currentAssessments !== 'undefined') ? currentAssessments.find(a => a.assessment_period === '3rd') : null;

    if (document.getElementById('p18_date_1st')) document.getElementById('p18_date_1st').innerText = a1 ? (a1.assessment_date || '--') : '--';
    if (document.getElementById('p18_age_1st')) document.getElementById('p18_age_1st').innerText = r1.chronological_age || (r1.child_age ? `${r1.child_age}y` : '--');
    if (document.getElementById('p18_date_2nd')) document.getElementById('p18_date_2nd').innerText = a2 ? (a2.assessment_date || '--') : '--';
    if (document.getElementById('p18_age_2nd')) document.getElementById('p18_age_2nd').innerText = r2.chronological_age || (r2.child_age ? `${r2.child_age}y` : '--');
    if (document.getElementById('p18_date_3rd')) document.getElementById('p18_date_3rd').innerText = a3 ? (a3.assessment_date || '--') : '--';
    if (document.getElementById('p18_age_3rd')) document.getElementById('p18_age_3rd').innerText = r3.chronological_age || (r3.child_age ? `${r3.child_age}y` : '--');

    const domains = [
        'Gross Motor',
        'Fine Motor',
        'Self-Help',
        'Receptive Language',
        'Expressive Language',
        'Cognitive',
        'Social-Emotional'
    ];

    tbody.innerHTML = '';

    domains.forEach(d => {
        const d1 = (r1.domain_scores || []).find(x => x.domain_name.toLowerCase().includes(d.toLowerCase())) || {};
        const d2 = (r2.domain_scores || []).find(x => x.domain_name.toLowerCase().includes(d.toLowerCase())) || {};
        const d3 = (r3.domain_scores || []).find(x => x.domain_name.toLowerCase().includes(d.toLowerCase())) || {};

        tbody.innerHTML += `
            <tr style="border-bottom:1px solid #cbd5e1;">
                <td style="padding:10px 14px; font-weight:700; color:#1e293b; background:#f8fafc; border-right:1px solid #cbd5e1;">${d}</td>
                <td align="center" style="padding:8px; border-right:1px solid #cbd5e1; font-weight:600;">${d1.raw_score !== undefined ? d1.raw_score : '--'}</td>
                <td align="center" style="padding:8px; border-right:2px solid #cbd5e1; font-weight:800; color:#0369a1; background:#f0f9ff;">${d1.scaled_score !== undefined ? d1.scaled_score : '--'}</td>
                <td align="center" style="padding:8px; border-right:1px solid #cbd5e1; font-weight:600;">${d2.raw_score !== undefined ? d2.raw_score : '--'}</td>
                <td align="center" style="padding:8px; border-right:2px solid #cbd5e1; font-weight:800; color:#b45309; background:#fef3c7;">${d2.scaled_score !== undefined ? d2.scaled_score : '--'}</td>
                <td align="center" style="padding:8px; border-right:1px solid #cbd5e1; font-weight:600;">${d3.raw_score !== undefined ? d3.raw_score : '--'}</td>
                <td align="center" style="padding:8px; font-weight:800; color:#15803d; background:#f0fdf4;">${d3.scaled_score !== undefined ? d3.scaled_score : '--'}</td>
            </tr>
        `;
    });

    if (tfoot) {
        tfoot.innerHTML = `
            <tr style="background:#f1f5f9; border-top:2px solid #0f172a; border-bottom:1px solid #cbd5e1;">
                <td style="padding:10px 14px; font-weight:800; color:#0f172a; border-right:1px solid #cbd5e1;">Sum of Scaled Scores</td>
                <td colspan="2" align="center" style="padding:10px; font-size:1.05rem; font-weight:900; color:#0284c7; border-right:2px solid #cbd5e1;">${r1.sum_scaled_scores || '--'}</td>
                <td colspan="2" align="center" style="padding:10px; font-size:1.05rem; font-weight:900; color:#d97706; border-right:2px solid #cbd5e1;">${r2.sum_scaled_scores || '--'}</td>
                <td colspan="2" align="center" style="padding:10px; font-size:1.05rem; font-weight:900; color:#16a34a;">${r3.sum_scaled_scores || '--'}</td>
            </tr>
            <tr style="background:#e2e8f0; border-bottom:1px solid #cbd5e1;">
                <td style="padding:10px 14px; font-weight:800; color:#0f172a; border-right:1px solid #cbd5e1;">Standard Score</td>
                <td colspan="2" align="center" style="padding:10px; font-size:1.15rem; font-weight:900; color:#0284c7; border-right:2px solid #cbd5e1;">${r1.standard_score || '--'}</td>
                <td colspan="2" align="center" style="padding:10px; font-size:1.15rem; font-weight:900; color:#d97706; border-right:2px solid #cbd5e1;">${r2.standard_score || '--'}</td>
                <td colspan="2" align="center" style="padding:10px; font-size:1.15rem; font-weight:900; color:#16a34a;">${r3.standard_score || '--'}</td>
            </tr>
            <tr style="background:#f8fafc;">
                <td style="padding:10px 14px; font-weight:800; color:#0f172a; border-right:1px solid #cbd5e1;">Interpretation</td>
                <td colspan="2" align="center" style="padding:10px; font-size:0.82rem; font-weight:700; color:#0369a1; border-right:2px solid #cbd5e1;">${r1.interpretation || '--'}</td>
                <td colspan="2" align="center" style="padding:10px; font-size:0.82rem; font-weight:700; color:#b45309; border-right:2px solid #cbd5e1;">${r2.interpretation || '--'}</td>
                <td colspan="2" align="center" style="padding:10px; font-size:0.82rem; font-weight:700; color:#15803d;">${r3.interpretation || '--'}</td>
            </tr>
        `;
    }
};

/**
 * Render Page 19 Scaled Scores SVG Dot-Matrix Graphs
 */
window.renderPage19Graph = function() {
    if (!window.currentChildReports) return;

    const domains = [
        'Gross Motor',
        'Fine Motor',
        'Self-Help',
        'Receptive Language',
        'Expressive Language',
        'Cognitive',
        'Social-Emotional'
    ];

    ['1st', '2nd', '3rd'].forEach((p, idx) => {
        const periodIdx = idx + 1;
        const report = window.currentChildReports[p] || {};
        const container = document.getElementById(`p19_svg_container_${periodIdx}`);
        const ageEl = document.getElementById(`p19_age_${periodIdx}`);
        if (ageEl) ageEl.innerText = report.chronological_age || (report.child_age ? `${report.child_age}y` : '--');

        if (!container) return;

        // SVG parameters
        const w = 320;
        const h = 420;
        const padX = 40;
        const padY = 25;
        const cellW = (w - padX) / domains.length;
        const cellH = (h - padY * 2) / 19; // 19 score steps

        const domainScores = report.domain_scores || [];
        const points = [];

        domains.forEach((d, dIdx) => {
            const found = domainScores.find(x => x.domain_name.toLowerCase().includes(d.toLowerCase()));
            const sc = (found && found.scaled_score !== undefined) ? Number(found.scaled_score) : null;
            if (sc && sc >= 1 && sc <= 19) {
                const cx = padX + dIdx * cellW + cellW / 2;
                const cy = padY + (19 - sc) * cellH + cellH / 2;
                points.push({ x: cx, y: cy, score: sc, domain: d });
            }
        });

        // Generate SVG markup
        let svg = `<svg viewBox="0 0 ${w} ${h}" style="width:100%; height:auto; font-family:'Montserrat', sans-serif;">`;

        // Background color zones
        // 14-19 (Advanced): top 6 rows
        svg += `<rect x="${padX}" y="${padY}" width="${w - padX}" height="${cellH * 6}" fill="#fef3c7" opacity="0.6"/>`;
        // 7-13 (Average): next 7 rows
        svg += `<rect x="${padX}" y="${padY + cellH * 6}" width="${w - padX}" height="${cellH * 7}" fill="#fef9c3" opacity="0.7"/>`;
        // Midpoint 10 highlight
        svg += `<rect x="${padX}" y="${padY + cellH * 9}" width="${w - padX}" height="${cellH}" fill="#bfdbfe" opacity="0.5"/>`;
        // 1-6 (Re-test): bottom 6 rows
        svg += `<rect x="${padX}" y="${padY + cellH * 13}" width="${w - padX}" height="${cellH * 6}" fill="#fefce8" opacity="0.9"/>`;

        // Horizontal Grid lines & Score numbers 19 down to 1
        for (let s = 19; s >= 1; s--) {
            const y = padY + (19 - s) * cellH;
            svg += `<line x1="${padX}" y1="${y}" x2="${w}" y2="${y}" stroke="#e2e8f0" stroke-width="1"/>`;
            svg += `<text x="${padX - 8}" y="${y + cellH * 0.7}" font-size="10" font-weight="700" fill="#475569" text-anchor="end">${s}</text>`;
        }
        svg += `<line x1="${padX}" y1="${padY + cellH * 19}" x2="${w}" y2="${padY + cellH * 19}" stroke="#cbd5e1" stroke-width="1.5"/>`;

        // Vertical domain lines and labels
        domains.forEach((d, dIdx) => {
            const x = padX + dIdx * cellW;
            svg += `<line x1="${x}" y1="${padY}" x2="${x}" y2="${padY + cellH * 19}" stroke="#e2e8f0" stroke-width="1"/>`;
            // Dots at every integer level
            for (let s = 1; s <= 19; s++) {
                const cy = padY + (19 - s) * cellH + cellH / 2;
                const cx = x + cellW / 2;
                svg += `<circle cx="${cx}" cy="${cy}" r="1.5" fill="#cbd5e1"/>`;
            }
        });
        svg += `<line x1="${w}" y1="${padY}" x2="${w}" y2="${padY + cellH * 19}" stroke="#cbd5e1" stroke-width="1.5"/>`;

        // Polyline connecting plotted points
        if (points.length > 1) {
            const polyPoints = points.map(p => `${p.x},${p.y}`).join(' ');
            const strokeColor = periodIdx === 1 ? '#0284c7' : (periodIdx === 2 ? '#d97706' : '#16a34a');
            svg += `<polyline points="${polyPoints}" fill="none" stroke="${strokeColor}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>`;
        }

        // Draw points with cross / X marker
        points.forEach(p => {
            const ptColor = periodIdx === 1 ? '#0284c7' : (periodIdx === 2 ? '#d97706' : '#16a34a');
            svg += `<circle cx="${p.x}" cy="${p.y}" r="6" fill="${ptColor}"/>`;
            svg += `<text x="${p.x}" y="${p.y + 3}" font-size="10" font-weight="900" fill="white" text-anchor="middle">x</text>`;
        });

        svg += `</svg>`;
        container.innerHTML = svg;
    });
};

/**
 * Render Page 20 Standard Scores Trajectory Graph
 */
window.renderPage20Graph = function() {
    const container = document.getElementById('p20_svg_container');
    if (!container || !window.currentChildReports) return;

    const r1 = window.currentChildReports['1st'] || {};
    const r2 = window.currentChildReports['2nd'] || {};
    const r3 = window.currentChildReports['3rd'] || {};

    const a1 = (typeof currentAssessments !== 'undefined') ? currentAssessments.find(a => a.assessment_period === '1st') : null;
    const a2 = (typeof currentAssessments !== 'undefined') ? currentAssessments.find(a => a.assessment_period === '2nd') : null;
    const a3 = (typeof currentAssessments !== 'undefined') ? currentAssessments.find(a => a.assessment_period === '3rd') : null;

    if (document.getElementById('p20_date_1')) document.getElementById('p20_date_1').innerText = a1 ? (a1.assessment_date || '--') : '--';
    if (document.getElementById('p20_date_2')) document.getElementById('p20_date_2').innerText = a2 ? (a2.assessment_date || '--') : '--';
    if (document.getElementById('p20_date_3')) document.getElementById('p20_date_3').innerText = a3 ? (a3.assessment_date || '--') : '--';

    const w = 700;
    const h = 420;
    const padL = 70;
    const padR = 40;
    const padTop = 35;
    const padBottom = 25;

    const chartW = w - padL - padR;
    const chartH = h - padTop - padBottom;

    // Standard Score scale from 20 to 160 (range = 140)
    const minScore = 20;
    const maxScore = 160;
    const range = maxScore - minScore;

    const getY = (score) => {
        const clamped = Math.max(minScore, Math.min(maxScore, score));
        return padTop + chartH - ((clamped - minScore) / range) * chartH;
    };

    const colW = chartW / 3;
    const colXs = [padL + colW * 0.5, padL + colW * 1.5, padL + colW * 2.5];

    let svg = `<svg viewBox="0 0 ${w} ${h}" style="width:100%; height:auto; font-family:'Montserrat', sans-serif;">`;

    // Background color zones
    // 130-160: Suggests Advanced (Orange)
    const y130 = getY(130);
    svg += `<rect x="${padL}" y="${padTop}" width="${chartW}" height="${y130 - padTop}" fill="#fed7aa" opacity="0.6"/>`;
    // 70-129: Average (Yellow)
    const y70 = getY(70);
    svg += `<rect x="${padL}" y="${y130}" width="${chartW}" height="${y70 - y130}" fill="#fef08a" opacity="0.7"/>`;
    // 20-69: Re-test (Pale yellow)
    svg += `<rect x="${padL}" y="${y70}" width="${chartW}" height="${padTop + chartH - y70}" fill="#fefce8" opacity="0.9"/>`;

    // Horizontal grid lines every 10 points
    for (let s = minScore; s <= maxScore; s += 10) {
        const y = getY(s);
        svg += `<line x1="${padL}" y1="${y}" x2="${w - padR}" y2="${y}" stroke="#cbd5e1" stroke-width="${s % 20 === 0 ? 1.5 : 0.8}"/>`;
        svg += `<text x="${padL - 10}" y="${y + 4}" font-size="11" font-weight="${s % 20 === 0 ? '800' : '600'}" fill="#334155" text-anchor="end">${s}</text>`;
    }

    // Zone labels on the left border
    svg += `<text x="${padL + 8}" y="${padTop + 20}" font-size="10" font-weight="800" fill="#c2410c">Suggests advanced development</text>`;
    svg += `<text x="${padL + 8}" y="${y130 + 25}" font-size="10" font-weight="800" fill="#854d0e">Average development</text>`;
    svg += `<text x="${padL + 8}" y="${y70 + 25}" font-size="10" font-weight="800" fill="#a16207">Re-test after 3 to 6 months</text>`;

    // Vertical Column lines and tick rulers
    const headers = ["3 years & 1 month", "4 years", "5 years"];
    colXs.forEach((cx, i) => {
        // Vertical axis line
        svg += `<line x1="${cx}" y1="${padTop}" x2="${cx}" y2="${padTop + chartH}" stroke="#0f172a" stroke-width="2"/>`;
        // Top column title
        svg += `<rect x="${cx - colW * 0.45}" y="${padTop - 25}" width="${colW * 0.9}" height="22" fill="#0f172a" rx="4"/>`;
        svg += `<text x="${cx}" y="${padTop - 10}" font-size="11" font-weight="800" fill="white" text-anchor="middle">${headers[i]}</text>`;

        // Ruler ticks every 5 units
        for (let s = minScore; s <= maxScore; s += 5) {
            const y = getY(s);
            const tickSize = s % 10 === 0 ? 8 : 4;
            svg += `<line x1="${cx - tickSize}" y1="${y}" x2="${cx + tickSize}" y2="${y}" stroke="#0f172a" stroke-width="1"/>`;
        }
    });

    // Plot child standard scores
    const scores = [
        r1.standard_score ? Number(r1.standard_score) : null,
        r2.standard_score ? Number(r2.standard_score) : null,
        r3.standard_score ? Number(r3.standard_score) : null
    ];

    const plotPts = [];
    scores.forEach((sc, i) => {
        if (sc !== null && !isNaN(sc)) {
            plotPts.push({ x: colXs[i], y: getY(sc), score: sc, idx: i });
        }
    });

    // Connecting line
    if (plotPts.length > 1) {
        const polyline = plotPts.map(p => `${p.x},${p.y}`).join(' ');
        svg += `<polyline points="${polyline}" fill="none" stroke="#2563eb" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`;
    }

    // Points with 'X' markers
    plotPts.forEach(p => {
        svg += `<circle cx="${p.x}" cy="${p.y}" r="9" fill="#1e40af"/>`;
        svg += `<text x="${p.x}" y="${p.y + 4}" font-size="13" font-weight="900" fill="white" text-anchor="middle">x</text>`;
        svg += `<text x="${p.x + 15}" y="${p.y + 4}" font-size="12" font-weight="800" fill="#1e3a8a">${p.score}</text>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
};

/**
 * Render Child Weight Growth Curve SVG
 */
window.renderGrowthChartSvg = function() {
    const container = document.getElementById('growthChartSvgContainer');
    if (!container) return;

    const w = 700;
    const h = 320;
    const padL = 50;
    const padR = 30;
    const padT = 20;
    const padB = 30;

    let svg = `<svg viewBox="0 0 ${w} ${h}" style="width:100%; height:auto; font-family:'Montserrat', sans-serif;">`;
    svg += `<rect x="${padL}" y="${padT}" width="${w - padL - padR}" height="${h - padT - padB}" fill="#f8fafc" stroke="#cbd5e1"/>`;

    // Reference curve bounds (+2SD, 0, -2SD)
    // Age 3-4 (37-48m), 4-5 (49-60m), 5-6 (61-72m)
    svg += `<path d="M ${padL} 220 Q 300 160 ${w - padR} 80" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-dasharray="4,2"/>`;
    svg += `<text x="${w - padR - 5}" y="75" font-size="10" font-weight="800" fill="#2563eb" text-anchor="end">+2SD Curve (Normal High)</text>`;

    svg += `<path d="M ${padL} 260 Q 300 200 ${w - padR} 130" fill="none" stroke="#10b981" stroke-width="3"/>`;
    svg += `<text x="${w - padR - 5}" y="125" font-size="10" font-weight="800" fill="#10b981" text-anchor="end">Median Standard Curve</text>`;

    svg += `<path d="M ${padL} 280 Q 300 230 ${w - padR} 180" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="4,2"/>`;
    svg += `<text x="${w - padR - 5}" y="175" font-size="10" font-weight="800" fill="#ef4444" text-anchor="end">-2SD Curve (Underweight Warning)</text>`;

    // Months markers along bottom
    const months = [37, 42, 48, 54, 60, 66, 72];
    months.forEach((m, i) => {
        const x = padL + (i / (months.length - 1)) * (w - padL - padR);
        svg += `<line x1="${x}" y1="${padT}" x2="${x}" y2="${h - padB}" stroke="#e2e8f0" stroke-width="1"/>`;
        svg += `<text x="${x}" y="${h - 10}" font-size="10" font-weight="700" fill="#64748b" text-anchor="middle">${m} mos</text>`;
    });

    svg += `</svg>`;
    container.innerHTML = svg;
};

/**
 * Print Complete Physical ECCD Booklet
 */
window.printCompleteBooklet = function() {
    window.print();
};
