/**
 * BMV3 System-Wide Language Translator Engine
 * Supports full portal-wide translation between English and Tagalog (Filipino)
 * for both Parents and Teachers portals.
 */

(function () {
    'use strict';

    // Comprehensive Dictionary for BMV3 System Interface
    const TRANSLATIONS = {
        // Navigation & Menus
        'Home': 'Tahanan',
        'Dashboard': 'Talaan (Dashboard)',
        'Analytics & AI Insights': 'Pagsusuri at AI Pananaw',
        'Drop-Off/Pick-Up': 'Paghatid at Pagsundo',
        'Drop-Off / Pick-Up': 'Paghatid at Pagsundo',
        'Attendance': 'Talaan ng Pagdalo',
        'Milestones': 'Mga Antas ng Pag-unlad',
        'ECCD Booklet': 'ECCD Booklet',
        'Daily Activities': 'Pang-araw-araw na Gawain',
        'Parent Engagement': 'Ugnayan ng Magulang',
        'Messages': 'Mga Mensahe',
        'Nutrition': 'Nutrisyon at Kalusugan',
        'Children': 'Mga Bata',
        'Pupils': 'Mga Mag-aaral',
        'Announcements': 'Mga Anunsyo',
        'Student House Map': 'Mapa ng Tirahan ng Bata',
        'Textblast Broadcast': 'Pangkalahatang Textblast',
        'Settings': 'Mga Setting / Kaayusan',
        'Logout': 'Mag-logout',
        'Check-In': 'Pag-check-in',
        'Stats': 'Estadistika',
        'MENU': 'MENU / MGA OPSYON',

        // Action Buttons & Controls
        'Generate Parent Account': 'Gumawa ng Account ng Magulang',
        'Generate & Send Account': 'Gawin at Ipadala ang Account',
        'Generate Another': 'Gumawa Pa ng Isa',
        'Done': 'Tapos Na',
        'Cancel': 'Kanselahin',
        'Save': 'I-save',
        'Save Changes': 'I-save ang mga Pagbabago',
        'Submit': 'Isumite',
        'Send Broadcast': 'Ipadala ang Broadcast',
        'Broadcasting...': 'Ipinapadala...',
        'Broadcasting via Brevo Relay...': 'Ipinapadala sa pamamagitan ng Brevo Relay...',
        'View': 'Tingnan',
        'Edit': 'I-edit',
        'Delete': 'Burahin',
        'Withdraw': 'I-withdraw',
        'Confirm Withdrawal': 'Kumpirmahin ang Pag-withdraw',
        'Profile': 'Profile',
        'Parent Account': 'Account ng Magulang',
        'Credentials': 'Mga Kredensyal',
        'Export': 'I-export',
        'Filter': 'I-filter',
        'Search': 'Maghanap',
        'Download': 'I-download',
        'Print': 'I-print',
        'Refresh': 'I-refresh',
        'Clear Text': 'Burahin ang Teksto',
        'Translate Text': 'Isalin ang Teksto',
        'Swap': 'Pagpalitin',
        'Copy': 'Kopyahin',
        'Copy Translation': 'Kopyahin ang Salin',
        'Copy Username': 'Kopyahin ang Username',
        'Copy Password': 'Kopyahin ang Password',
        'Ask AI Insights': 'Magtanong sa AI',
        'Generate Dossier': 'Gumawa ng Dossier',
        'Live Session Sync': 'Kasalukuyang Sesyon',
        'Exit Archive Mode': 'Umalis sa Archive Mode',
        'Install': 'I-install',
        'Translate': 'Isalin',

        // User Roles & Stakeholders
        'Teacher': 'Guro',
        'Parent': 'Magulang',
        'Guardian': 'Tagapag-alaga',
        'Mother': 'Ina',
        'Father': 'Ama',
        'Other Guardian': 'Ibang Tagapag-alaga',
        'Teacher User': 'Guro',
        'Parent User': 'Magulang',

        // Section Headers & Titles
        'Pupil Management & Shift Allocation': 'Pamamahala ng Mag-aaral at Iskedyul ng Shift',
        'Pupil Profile & Shift Details': 'Profile ng Mag-aaral at Detalye ng Shift',
        'Total Active Cohort': 'Kabuuang Aktibong Mag-aaral',
        'Enrolled Pupils': 'Naka-enroll na mga Bata',
        'Pending Applications': 'Mga Nakabinbing Aplikasyon',
        'Withdrawn Pupil Records & Archives': 'Nai-withdraw na Talaan at Archive',
        'Awaiting Teacher Review': 'Naghihintay sa Pagsusuri ng Guro',
        'Historical attendance, milestones, and ECCD records are securely preserved. Re-enrollment restores active status.': 'Ang mga nakaraang pagdalo, milestones, at talaan ng ECCD ay ligtas na napanatili. Ang muling pag-enroll ay magbabalik sa aktibong katayuan.',
        'Withdraw Student Confirmation': 'Kumpirmasyon sa Pag-withdraw ng Mag-aaral',

        // School Years & Shifts
        'School Year:': 'Taong Panuruan:',
        'School Year': 'Taong Panuruan',
        'Current Active School Year': 'Kasalukuyang Aktibong Taon',
        'Active Current': 'Kasalukuyang Aktibo',
        'Past Batch': 'Nakaraang Taon',
        'Morning Shift (AM)': 'Pang-umagang Shift (AM)',
        'Afternoon Shift (PM)': 'Panghapon na Shift (PM)',
        'All Shifts (AM & PM)': 'Lahat ng Shift (AM at PM)',
        'Morning (AM)': 'Pang-umaga (AM)',
        'Afternoon (PM)': 'Panghapon (PM)',
        'Shift': 'Shift',

        // Tables & Fields
        'Pupil Name': 'Pangalan ng Bata',
        'Withdrawal Date': 'Petsa ng Pag-withdraw',
        'Withdrawal Date *': 'Petsa ng Pag-withdraw *',
        'Withdrawal Reason': 'Dahilan ng Pag-withdraw',
        'Withdrawal Reason (Optional)': 'Dahilan ng Pag-withdraw (Opsyonal)',
        'Recorded Reason': 'Nai-record na Dahilan',
        'Age & Gender': 'Edad at Kasarian',
        'Guardian Details': 'Detalye ng Magulang/Tagapag-alaga',
        'Parent / Guardian Full Name': 'Buong Pangalan ng Magulang / Tagapag-alaga',
        'Parent / Guardian Full Name *': 'Buong Pangalan ng Magulang / Tagapag-alaga *',
        'Parent Email Address': 'Email Address ng Magulang',
        'Parent Email Address *': 'Email Address ng Magulang *',
        'Link to Enrolled Pupil': 'Iugnay sa Naka-enroll na Bata',
        'Link to Enrolled Pupil (Optional)': 'Iugnay sa Naka-enroll na Bata (Opsyonal)',
        'Temporary Password:': 'Pansamantalang Password:',
        'Temporary Password': 'Pansamantalang Password',
        'Recipient Email:': 'Email ng Tatanggap:',
        'Recipient Email': 'Email ng Tatanggap',
        'Full Name:': 'Buong Pangalan:',
        'Full Name': 'Buong Pangalan',
        'Username:': 'Username:',
        'Username': 'Username',
        'Linked Pupil:': 'Naka-link na Bata:',
        'Linked Pupil': 'Naka-link na Bata',
        'Account Created Successfully!': 'Matagumpay na Nagawa ang Account!',
        'Credentials have been generated and dispatched via Brevo.': 'Nagawa ang mga kredensyal at matagumpay na naipadala sa pamamagitan ng Brevo.',

        // Broadcast & Textblast
        'Notice Title': 'Pamagat ng Paunawa',
        'Category': 'Kategorya',
        'Channels:': 'Mga Channel:',
        'Channels': 'Mga Channel',
        'Send Email (Brevo SMTP)': 'Magpadala ng Email (Brevo SMTP)',
        'Send SMS (Mobile Textblast)': 'Magpadala ng SMS (Mobile Textblast)',
        'Target Cohort Scope': 'Saklaw ng mga Tatanggap',
        'All Registered Parents & Guardians (All Batches)': 'Lahat ng Magulang at Tagapag-alaga (Lahat ng Taon)',
        'Active Current School Year Cohort': 'Kasalukuyang Aktibong Taon Lamang',
        'Send Test Copy to Email (Optional)': 'Magpadala ng Test Copy sa Email (Opsyonal)',
        'Message Content': 'Nilalaman ng Mensahe',
        'Broadcast History': 'Kasaysayan ng Broadcast',
        'Compose Broadcast': 'Sumulat ng Broadcast',
        'Delivered': 'Naipadala',
        'Active': 'Aktibo',
        'Direct Mobile Gateway': 'Direktang Mobile Gateway',
        'Target: All Registered Parents & Guardians': 'Target: Lahat ng Rehistradong Magulang at Tagapag-alaga',

        // Analytics & KPIs
        'Development Readiness (DRI)': 'Kahandaan sa Pag-unlad (DRI)',
        'Smart Attendance Rate': 'Antas ng Pagdalo',
        'Nutrition Health Index': 'Indeks ng Kalusugan at Nutrisyon',
        'Learning Task Completion': 'Pagtapos sa mga Gawain',
        'Risk Watchlist Flags': 'Mga Babala sa Panganib',
        'Normal BMI': 'Normal na BMI',
        'Underweight': 'Kulang sa Timbang',
        'Overweight': 'Sobra sa Timbang',
        'Severely Underweight': 'Masyadong Mababa ang Timbang',
        'Severely Wasted': 'Masyadong Payat',
        'Wasted': 'Payat',
        'High Risk': 'Mataas ang Panganib',
        'Low Risk': 'Mababang Panganib',
        'Moderate Risk': 'Katamtamang Panganib',
        'School Ready': 'Handa na sa Paaralan',
        'Projected:': 'Inaasahan:',
        'warnings active': 'aktibong babala',

        // Attendance Statuses
        'Present': 'Pumasok (Present)',
        'Absent': 'Lumiban (Absent)',
        'Late': 'Nahuli (Late)',
        'Excused': 'May Paalam (Excused)',
        'Time In': 'Oras ng Pagpasok',
        'Time Out': 'Oras ng Pag-uwi',
        'Date': 'Petsa',
        'Status': 'Katayuan',
        'Sender': 'Nagpadala',
        'Emails': 'Mga Email',
        'SMS': 'Mga SMS',

        // Student Data & Status
        'Enrolled': 'Naka-enroll',
        'Pending': 'Nakabinbin',
        'Withdrawn': 'Nai-withdraw',
        'Male': 'Lalaki',
        'Female': 'Babae',
        'yrs': 'taon',
        'Address': 'Tirahan',
        'Birthdate': 'Kaarawan',
        'Age': 'Edad',
        'Gender': 'Kasarian',

        // Language & Translator
        'Language Translator': 'Pagsasalin ng Wika (Language Translator)',
        'Original Text': 'Orihinal na Teksto',
        'Translated Output': 'Kinalabasang Salin',
        'Source:': 'Pinagmulan:',
        'Target:': 'Target:',
        'English (English)': 'Ingles (English)',
        'Tagalog (Filipino)': 'Tagalog (Filipino)',
        'English': 'Ingles',
        'Tagalog': 'Tagalog',
        'Clear Text': 'Burahin ang Teksto',
        'Translate Text': 'Isalin ang Teksto',

        // Settings Tabs & Sections
        'Account': 'Account',
        'School Branding': 'Pangalan at Tatak ng Daycare',
        'School Settings': 'Mga Setting ng Paaralan',
        'Active School Year Config': 'Aktibong Taong Panuruan',
        'Notifications': 'Mga Abiso / Notifications',
        'Appearance': 'Hitsura at Tema',
        'Privacy & Security': 'Seguridad at Privacy',
        'About System': 'Tungkol sa Sistema',

        // Informational Messages & Alerts
        'No enrolled students found in this school year.': 'Walang nahanap na naka-enroll na mag-aaral sa taong panuruang ito.',
        'No withdrawn students.': 'Walang mag-aaral na nai-withdraw.',
        'No broadcasts sent yet.': 'Wala pang naipapadalang broadcast.',
        'Loading broadcast history...': 'Ikinakarga ang kasaysayan ng broadcast...',
        'Manage student profiles, assign class shifts (Morning AM / Afternoon PM), and review enrollment applications': 'Pamahalaan ang mga profile ng bata, magtalaga ng shifts (Umaga AM / Hapon PM), at suriin ang mga enrollment application',
        '10-Pillar Smart Monitoring, Risk Scoring Engine, Development Readiness Index (DRI), & Automated Early-Warnings': '10-Pillar Matalinong Pagsubaybay, Pagsusuri ng Panganib, Indeks ng Kahandaan (DRI), at Awtomatikong Babala',
        'BMV3 Daycare AI Analytics & Intelligence': 'BMV3 Daycare AI Analytics at Matalinong Pagsusuri',
        'Manage account preferences, alerts, and system lifecycle': 'Pamahalaan ang mga kagustuhan sa account, mga alerto, at sistema',
        'BMV3 Child Care Management System': 'Sistema ng Pamamahala ng Daycare sa BMV3',
        'Install the BMV3 Child Care Web App for a faster mobile experience!': 'I-install ang BMV3 Child Care Web App para sa mas mabilis na mobile experience!',

        // ECCD Booklet & Developmental Domains
        'Gross Motor': 'Gross Motor (Malalaking Kalamnan)',
        'Fine Motor': 'Fine Motor (Maliliit na Kalamnan)',
        'Self-Help': 'Self-Help (Pangangalaga sa Sarili)',
        'Receptive Language': 'Receptive Language (Kakayahang Umunawa ng Wika)',
        'Expressive Language': 'Expressive Language (Kakayahang Magpahayag ng Wika)',
        'Cognitive': 'Cognitive (Pangkaisipan at Pag-unawa)',
        'Social-Emotional': 'Social-Emotional (Sosyo-Emosyonal / Pakikipagkapwa)',
        'Developmental Domains': 'Mga Larangan ng Pag-unlad',
        'Domain': 'Larangan ng Pag-unlad (Domain)',
        'Sum of Scaled Scores': 'Kabuuan ng Scaled Scores',
        'Standard Score': 'Pamantayang Iskor (Standard Score)',
        'Raw Score': 'Hilaw na Iskor (Raw Score)',
        'Scaled Score': 'Scaled Score',
        'Interpretation': 'Pagpapakahulugan (Interpretasyon)',
        '1st Evaluation': 'Unang Pagsusuri',
        '2nd Evaluation': 'Ikalawang Pagsusuri',
        '3rd Evaluation': 'Ikatlong Pagsusuri',
        'Age & Evaluation Periods': 'Edad at Panahon ng Pagsusuri',
        'Demonstrated Progress': 'Naipakitang Pag-unlad',
        'Observed Milestones': 'Naobserbahang Milestones',
        'Completed': 'Tapos Na',
        'In Progress': 'Kasalukuyang Ginagawa',
        'Not Started': 'Hindi Pa Nasimulan',
        'ECCD Domains Scale Scoring & Summary Table': 'Talaan ng Pagmamarka sa ECCD Domains',
        'Evaluation Summary & Score Conversion (Page 18)': 'Buod ng Pagsusuri at Pagpalit ng Iskor (Pahina 18)',
        'Interpretation of Scaled Score:': 'Kahulugan ng Scaled Score:',
        'Interpretation of Standard Score:': 'Kahulugan ng Standard Score:',
        'Development in the domain must be monitored after 3 months': 'Kailangang subaybayan ang pag-unlad pagkalipas ng 3 buwan',
        'Development in the domain must be monitored after 6 months': 'Kailangang subaybayan ang pag-unlad pagkalipas ng 6 na buwan',
        'Average overall development in the domain': 'Normal / Katamtamang pag-unlad sa larangang ito',
        'Suggests slightly advanced development in the domain': 'Bahagyang mas maunlad kaysa karaniwan',
        'Suggests highly advanced development in the domain': 'Napakataas na antas ng pag-unlad',
        '69 and below': '69 pababa',
        'Overall development must be monitored after 3 months': 'Kailangang subaybayan ang kabuuang pag-unlad pagkaraan ng 3 buwan',
        'Overall development must be monitored after 6 months': 'Kailangang subaybayan ang kabuuang pag-unlad pagkaraan ng 6 na buwan',
        'Average overall development': 'Normal / Katamtamang kabuuang pag-unlad',
        'Slightly advanced overall development': 'Bahagyang mas maunlad na kabuuang pag-unlad',
        'Highly advanced overall development': 'Napakataas na kabuuang pag-unlad',
        '130 and above': '130 pataas',
        'Print Summary': 'I-print ang Buod',
        'Audit History': 'Kasaysayan ng Pagbabago',
        'Save Profile': 'I-save ang Profile',
        'Save Form': 'I-save ang Form',
        'Save Health': 'I-save ang Kalusugan',
        'Save All Booklet Answers': 'I-save ang Lahat ng Sagot sa Booklet',
        'Select Child\'s Booklet': 'Piliin ang Booklet ng Bata',
        '1. Sociodemographic Profile': '1. Profile ng Bata at Magulang',
        '2. M-CHAT-R Autism Checklist': '2. M-CHAT-R Checklist',
        '3. Health & Growth Records': '3. Talaan ng Kalusugan at Paglaki',
        '4. Intake & Consent Form': '4. Intake at Pahintulot (Consent)',
        '5. Teacher Score Summary & Graphs': '5. Buod ng Iskor ng Guro at Graph',
        'Sociodemographics': 'Profile ng Bata',
        'M-CHAT-R Screening': 'M-CHAT-R Pagsusuri',
        'Health & Growth': 'Kalusugan at Paglaki',
        'Intake & Consent': 'Intake at Pahintulot',
        'Early Childhood Care and Development (ECCD) Booklet': 'ECCD Booklet (Pangangalaga at Pag-unlad ng Bata)',
        'Official Child\'s Record 2 (Age 3y 1m to 5y) — Complete parent forms, update health & growth history, and view teacher evaluations': 'Opisyal na Rekord ng Bata 2 (Edad 3 taon 1 buwan hanggang 5 taon) — Sagutan ang mga form ng magulang, i-update ang kalusugan, at tingnan ang pagsusuri ng guro',
        'Parent has no email address': 'Walang email address ang magulang',
        'Check this box if the parent does not own an email address. The system will create an offline account and show the credentials on-screen.': 'Lagyan ng tsek kung walang email ang magulang. Gagawa ang system ng account at ipapakita ang username at password sa screen upang makuhanan ng litrato.',
        'Tip: The parent can take a picture of this screen with their mobile phone to keep a copy of their login credentials.': 'Payo: Maaaring picturan ng magulang ang screen na ito gamit ang cellphone para may kopya sila ng kanilang username at password.',
        'Official Child\'s Record 2': 'Opisyal na Rekord ng Bata 2',
        'Early Childhood Care and Development (ECCD) Checklist': 'Checklist sa Pangangalaga at Pag-unlad ng Bata (ECCD)',
        'Age 3 years 1 month to 5 years': 'Edad 3 taon 1 buwan hanggang 5 taon',
        'PROVINCE OF QUEZON • OFFICIAL RECORD': 'LALAWIGAN NG QUEZON • OPISYAL NA TALAAN',
        'Child Basic Identification': 'Pangunahing Pagkakakilanlan ng Bata',
        'Child\'s Full Name:': 'Buong Pangalan ng Bata:',
        'Child\'s Full Name': 'Buong Pangalan ng Bata',
        'Select Sex': 'Piliin ang Kasarian',
        'Date of Birth (Month / Day / Year):': 'Petsa ng Kapanganakan (Buwan / Araw / Taon):',
        'Residential Address:': 'Tirahan ng Pamilya:',
        'Residential Address': 'Tirahan ng Pamilya',
        'Child\'s Handedness': 'Ginagamit na Kamay ng Bata',
        'Right': 'Kanan',
        'Left': 'Kaliwa',
        'Both': 'Pareho',
        'Not yet established': 'Hindi pa tiyak / Nagsasanay pa',
        'Is the child presently studying?': 'Kasalukuyan bang nag-aaral ang bata?',
        'Parental Background & Family Structure': 'Impormasyon ng Magulang at Pamilya',
        'Father\'s Information': 'Impormasyon ng Ama',
        'Father\'s Name:': 'Pangalan ng Ama:',
        'Father\'s Age:': 'Edad ng Ama:',
        'Father\'s Occupation:': 'Hanapbuhay ng Ama:',
        'Father\'s Educational Attainment:': 'Naabot na Pag-aaral ng Ama:',
        'Mother\'s Information': 'Impormasyon ng Ina',
        'Mother\'s Name:': 'Pangalan ng Ina:',
        'Mother\'s Age:': 'Edad ng Ina:',
        'Mother\'s Occupation:': 'Hanapbuhay ng Ina:',
        'Mother\'s Educational Attainment:': 'Naabot na Pag-aaral ng Ina:',
        'Child\'s Number of Siblings:': 'Bilang ng Kapatid ng Bata:',
        'Child\'s Birth Order (1st, 2nd, 3rd, etc.):': 'Pang-ilan sa Magkakapatid:',
        'I. PERSONAL DATA:': 'I. PANSARILING IMPORMASYON:',
        'Religion:': 'Relihiyon:',
        'Place of Birth:': 'Lugar ng Kapanganakan:',
        'Nutritional Status:': 'Kalagayan sa Nutrisyon:',
        'Physical Handicap/Impairment:': 'Pisikal na Kapansanan o Kondisyon:',
        'II. FAMILY COMPOSITION': 'II. KOMPOSISYON NG PAMILYA',
        'Add Member': 'Magdagdag ng Kasama sa Bahay',
        'III. DEVELOPMENT INFORMATION:': 'III. IMPORMASYON SA PAGLAKI AT PAG-UNLAD:',
        '1. Birth Certificate:': '1. Sertipiko ng Kapanganakan:',
        'Available': 'Mayroon',
        'Not Available': 'Wala',
        'IV. HOME CONDITIONS:': 'IV. KALAGAYAN SA TAHANAN AT PAMAYANAN:',
        'V. PARENTAL EXPECTATIONS': 'V. MGA INAASAHAN NG MAGULANG',
        '1. What do parents expect to learn from attendance at the day care center?': '1. Ano ang inaasahang matututuhan ng magulang mula sa pagpasok ng bata sa day care?',
        '2. What are the parents perceived role in instilling values to the child at home?': '2. Ano ang pananaw ng magulang sa kanilang tungkulin sa pagtuturo ng magagandang asal sa tahanan?',
        '3. What do the parents perceive as their role in relation to the Day Care Worker?': '3. Ano ang tingin ng magulang sa kanilang pakikipagtulungan sa Day Care Worker (Guro)?',
        '4. What do they expect of the Day Care Worker?': '4. Ano ang inaasahan ng mga magulang mula sa Day Care Worker (Guro)?',
        '5. What do the parents perceive as their role in contributing to the success of the Day Care Center?': '5. Ano ang maitutulong ng magulang para maging matagumpay ang Day Care Center?',
        '6. What do the parents expect of their children at the Day Care Center?': '6. Ano ang inaasahan ng magulang na marating o matutuhan ng kanilang anak sa Day Care Center?',
        '7. Other Expectations:': '7. Iba pang Inaasahan:',
        'Health, Growth & Vision Records': 'Talaan ng Kalusugan, Paglaki, at Paningin',
        'Growth & Nutrition': 'Paglaki at Nutrisyon',
        'Physician\'s Health Record': 'Pagsusuri ng Doktor',
        'Eye & Vision Assessment': 'Pagsusuri sa Mata at Paningin',
        'Child Weight Growth Curve & Clinical Nutrition Checklist': 'Kurba ng Paglaki at Timbang ng Bata at Checklist sa Nutrisyon',
        'Health / Nutrition Periodic Checklist': 'Pana-panahong Talaan ng Kalusugan at Nutrisyon',
        '1. Vitamin A supplementation every six months': '1. Pagbibigay ng Bitamina A tuwing 6 na buwan',
        '2. First dental check-up at 2-3 years old': '2. Unang pagsusuri ng ngipin sa edad 2-3 taon',
        '3. Deworming': '3. Pagpurga tuwing 6 na buwan',
        '4. History of Major Illness': '4. Kasaysayan ng Pagkakasakit',
        'Type of Illness': 'Uri ng Sakit',
        'Intervention Given': 'Gamot o Lunas',
        'Add Entry': 'Magdagdag ng Tala',
        'CONSENT OF THE PROVISION OF DAY CARE SERVICE': 'PAHINTULOT PARA SA PAGBIBIGAY NG SERBISYO SA DAY CARE',
        'Official Assessment Summary:': 'Opisyal na Buod ng Pagsusuri:'
    };

    // Build reverse map for restoring original English text
    const REVERSE_TRANSLATIONS = {};
    for (const [en, tl] of Object.entries(TRANSLATIONS)) {
        REVERSE_TRANSLATIONS[tl] = en;
    }

    let currentLanguage = localStorage.getItem('bmv3_language') || 'en';
    let isTranslating = false;

    /**
     * Translate single text string
     */
    function translateString(str, lang) {
        if (!str || typeof str !== 'string') return str;
        const trimmed = str.trim();
        if (!trimmed) return str;

        if (lang === 'tl') {
            if (TRANSLATIONS[trimmed]) {
                return str.replace(trimmed, TRANSLATIONS[trimmed]);
            }
        } else {
            if (REVERSE_TRANSLATIONS[trimmed]) {
                return str.replace(trimmed, REVERSE_TRANSLATIONS[trimmed]);
            }
        }
        return str;
    }

    /**
     * Walk through DOM nodes and translate text
     */
    function translateNode(node, lang) {
        if (!node) return;

        // Skip scripts, styles, textareas where user inputs text, etc.
        const tagName = node.tagName ? node.tagName.toUpperCase() : '';
        if (['SCRIPT', 'STYLE', 'CODE', 'PRE', 'NOSCRIPT'].includes(tagName)) return;

        // Skip inputs unless translating placeholder
        if (tagName === 'INPUT' || tagName === 'TEXTAREA') {
            const ph = node.getAttribute('placeholder');
            if (ph) {
                if (!node.dataset.origPlaceholder) {
                    node.dataset.origPlaceholder = ph;
                }
                const translatedPh = (lang === 'tl') 
                    ? (TRANSLATIONS[node.dataset.origPlaceholder.trim()] || node.dataset.origPlaceholder)
                    : node.dataset.origPlaceholder;
                node.setAttribute('placeholder', translatedPh);
            }
            return;
        }

        // Translate Text Nodes
        if (node.nodeType === Node.TEXT_NODE) {
            const txt = node.nodeValue;
            const trimmed = txt.trim();
            if (trimmed && trimmed.length > 1) {
                if (!node._bmv3_orig) {
                    node._bmv3_orig = txt;
                }
                if (lang === 'tl') {
                    if (TRANSLATIONS[trimmed]) {
                        node.nodeValue = txt.replace(trimmed, TRANSLATIONS[trimmed]);
                    }
                } else {
                    if (node._bmv3_orig) {
                        node.nodeValue = node._bmv3_orig;
                    }
                }
            }
            return;
        }

        // Translate element attributes like title / aria-label
        if (node.nodeType === Node.ELEMENT_NODE) {
            const title = node.getAttribute('title');
            if (title && title.trim()) {
                if (!node.dataset.origTitle) node.dataset.origTitle = title;
                if (lang === 'tl' && TRANSLATIONS[node.dataset.origTitle.trim()]) {
                    node.setAttribute('title', TRANSLATIONS[node.dataset.origTitle.trim()]);
                } else if (lang === 'en' && node.dataset.origTitle) {
                    node.setAttribute('title', node.dataset.origTitle);
                }
            }

            // Recurse children
            for (let i = 0; i < node.childNodes.length; i++) {
                translateNode(node.childNodes[i], lang);
            }
        }
    }

    /**
     * Apply translation to the entire page
     */
    function applyPageTranslation(lang) {
        if (isTranslating) return;
        isTranslating = true;

        try {
            document.documentElement.lang = lang;
            translateNode(document.body, lang);
            updateToggleButtons(lang);
            updateSettingsLanguageCard(lang);
        } catch (e) {
            console.error('BMV3 Translation Error:', e);
        } finally {
            isTranslating = false;
        }
    }

    /**
     * Update the visual state of the navbar toggle buttons
     */
    function updateToggleButtons(lang) {
        const btnEn = document.getElementById('sysLangBtnEn');
        const btnTl = document.getElementById('sysLangBtnTl');

        if (btnEn && btnTl) {
            if (lang === 'tl') {
                btnTl.style.background = '#2563eb';
                btnTl.style.color = '#ffffff';
                btnTl.style.boxShadow = '0 2px 6px rgba(37,99,235,0.3)';
                btnEn.style.background = 'transparent';
                btnEn.style.color = 'var(--text-secondary, #64748b)';
                btnEn.style.boxShadow = 'none';
            } else {
                btnEn.style.background = '#2563eb';
                btnEn.style.color = '#ffffff';
                btnEn.style.boxShadow = '0 2px 6px rgba(37,99,235,0.3)';
                btnTl.style.background = 'transparent';
                btnTl.style.color = 'var(--text-secondary, #64748b)';
                btnTl.style.boxShadow = 'none';
            }
        }
    }

    /**
     * Update settings page language cards if present
     */
    function updateSettingsLanguageCard(lang) {
        const radioEn = document.getElementById('systemLangRadioEn');
        const radioTl = document.getElementById('systemLangRadioTl');
        const cardEn = document.getElementById('langOptionCardEn');
        const cardTl = document.getElementById('langOptionCardTl');

        if (radioEn && radioTl) {
            radioEn.checked = (lang === 'en');
            radioTl.checked = (lang === 'tl');
        }
        if (cardEn && cardTl) {
            if (lang === 'tl') {
                cardTl.style.borderColor = '#2563eb';
                cardTl.style.background = '#eff6ff';
                cardEn.style.borderColor = '#e2e8f0';
                cardEn.style.background = 'transparent';
            } else {
                cardEn.style.borderColor = '#2563eb';
                cardEn.style.background = '#eff6ff';
                cardTl.style.borderColor = '#e2e8f0';
                cardTl.style.background = 'transparent';
            }
        }
    }

    /**
     * Public API: set language and persist
     */
    window.setSystemLanguage = function (lang) {
        currentLanguage = (lang === 'tl') ? 'tl' : 'en';
        localStorage.setItem('bmv3_language', currentLanguage);
        applyPageTranslation(currentLanguage);

        window.dispatchEvent(new CustomEvent('bmv3LanguageChanged', { detail: { language: currentLanguage } }));
    };

    /**
     * Public API: get current language
     */
    window.getSystemLanguage = function () {
        return currentLanguage;
    };

    /**
     * Initialize on DOM Ready
     */
    document.addEventListener('DOMContentLoaded', function () {
        currentLanguage = localStorage.getItem('bmv3_language') || 'en';
        if (currentLanguage === 'tl') {
            applyPageTranslation('tl');
        } else {
            updateToggleButtons('en');
            updateSettingsLanguageCard('en');
        }

        // Set up MutationObserver to translate dynamically rendered elements (tables, charts, modals)
        const observer = new MutationObserver(function (mutations) {
            if (currentLanguage !== 'tl' || isTranslating) return;

            for (const mutation of mutations) {
                for (const addedNode of mutation.addedNodes) {
                    if (addedNode.nodeType === Node.ELEMENT_NODE || addedNode.nodeType === Node.TEXT_NODE) {
                        translateNode(addedNode, 'tl');
                    }
                }
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });

})();
