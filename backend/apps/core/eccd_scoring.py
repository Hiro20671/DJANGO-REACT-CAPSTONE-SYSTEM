from datetime import date

# Map raw scores to scaled scores for each domain and age group
# Format: (min_raw, max_raw, scaled_score)
SCALED_SCORE_TABLES = {
    '3.1-4.0': {
        'Gross Motor': [(0,3,1), (4,4,2), (5,5,3), (6,6,5), (7,7,6), (8,8,7), (9,9,8), (10,10,10), (11,11,11), (12,12,12), (13,13,14)],
        'Fine Motor': [(0,3,2), (4,4,4), (5,5,5), (6,6,7), (7,7,9), (8,8,10), (9,9,12), (10,10,14), (11,11,15)],
        'Self-Help': [(0,9,1), (10,10,2), (11,11,3), (12,12,4), (13,14,5), (15,15,6), (16,16,7), (17,17,8), (18,19,9), (20,20,10), (21,21,11), (22,22,12), (23,24,13), (25,25,14), (26,26,15), (27,27,16)],
        'Receptive Language': [(0,1,3), (2,2,5), (3,3,7), (4,4,10), (5,5,12)],
        'Expressive Language': [(0,2,1), (3,3,3), (4,4,4), (5,5,5), (6,6,8), (7,7,10), (8,8,12)],
        'Cognitive': [(0,0,3), (1,1,4), (2,3,5), (4,4,6), (5,5,7), (6,6,8), (7,7,9), (8,9,10), (10,10,11), (11,11,12), (12,12,13), (13,14,14), (15,15,15), (16,16,16), (17,17,17), (18,18,18), (19,21,19)],
        'Social-Emotional': [(0,9,1), (10,11,2), (12,12,3), (13,13,4), (14,14,5), (15,15,6), (16,16,7), (17,18,8), (19,19,9), (20,20,10), (21,21,11), (22,22,12), (23,23,13), (24,24,14)],
    },
    '4.1-5.0': {
        'Gross Motor': [(0,5,1), (6,6,2), (7,7,4), (8,8,5), (9,9,7), (10,10,8), (11,11,10), (12,12,11), (13,13,13)],
        'Fine Motor': [(0,3,1), (4,4,2), (5,5,4), (6,6,5), (7,7,7), (8,8,9), (9,9,10), (10,10,12), (11,11,14)],
        'Self-Help': [(0,15,1), (16,16,2), (17,17,3), (18,18,4), (19,19,5), (20,20,6), (21,21,8), (22,22,9), (23,23,10), (24,24,11), (25,25,12), (26,26,13), (27,27,14)],
        'Receptive Language': [(0,1,1), (2,2,3), (3,3,5), (4,4,9), (5,5,11)],
        'Expressive Language': [(0,5,2), (6,6,5), (7,7,8), (8,8,11)],
        'Cognitive': [(0,0,1), (1,1,2), (2,3,3), (4,4,4), (5,5,5), (6,7,6), (8,8,7), (9,10,8), (11,11,9), (12,12,10), (13,14,11), (15,15,12), (16,17,13), (18,18,14), (19,20,15), (21,21,16)],
        'Social-Emotional': [(0,13,1), (14,14,2), (15,15,3), (16,16,4), (17,17,5), (18,18,7), (19,19,8), (20,20,9), (21,21,10), (22,22,11), (23,23,12), (24,24,13)],
    },
    '5.1-5.11': {
        'Gross Motor': [(0,10,1), (11,11,4), (12,12,7), (13,13,11)],
        'Fine Motor': [(0,5,1), (6,6,3), (7,7,5), (8,8,7), (9,9,8), (10,10,10), (11,11,12)],
        'Self-Help': [(0,19,2), (20,20,3), (21,21,4), (22,22,6), (23,23,7), (24,24,9), (25,25,10), (26,26,12), (27,27,13)],
        'Receptive Language': [(0,2,1), (3,3,4), (4,4,8), (5,5,11)],
        'Expressive Language': [(0,7,5), (8,8,11)],
        'Cognitive': [(0,9,1), (10,10,2), (11,11,3), (12,12,4), (13,13,5), (14,14,6), (15,15,7), (16,16,8), (17,17,9), (18,18,10), (19,19,11), (20,20,12), (21,21,13)],
        'Social-Emotional': [(0,15,1), (16,16,2), (17,17,3), (18,18,5), (19,19,6), (20,20,7), (21,21,9), (22,22,10), (23,23,11), (24,24,13)],
    }
}

STANDARD_SCORE_TABLE = {
    21: 39, 22: 40, 23: 42, 24: 43, 25: 44, 26: 45, 27: 46, 28: 48, 29: 49, 30: 50,
    31: 51, 32: 53, 33: 54, 34: 55, 35: 56, 36: 57, 37: 59, 38: 60, 39: 61, 40: 62,
    41: 64, 42: 65, 43: 66, 44: 67, 45: 68, 46: 70, 47: 71, 48: 72, 49: 73, 50: 75,
    51: 76, 52: 77, 53: 78, 54: 79, 55: 81, 56: 82, 57: 83, 58: 84, 59: 86, 60: 87,
    61: 88, 62: 89, 63: 90, 64: 92, 65: 93, 66: 94, 67: 95, 68: 96, 69: 98, 70: 100,
    71: 101, 72: 103, 73: 104, 74: 105, 75: 106, 76: 107, 77: 109, 78: 110, 79: 111, 80: 112,
    81: 114, 82: 115, 83: 116, 84: 117, 85: 118, 86: 120, 87: 121, 88: 122, 89: 123, 90: 125,
    91: 126, 92: 127, 93: 128, 94: 129, 95: 131, 96: 132, 97: 133, 98: 134, 99: 135, 100: 137,
    101: 138, 102: 139, 103: 140, 104: 142, 105: 143, 106: 144, 107: 145, 108: 146, 109: 148, 110: 149, 
    111: 150, # Interpolated
    112: 151
}

def compute_age(date_tested, date_of_birth):
    """
    Computes exact age based on ECCD formula:
    Each month is composed of 30 days.
    """
    if not date_of_birth:
        return 0, 0, 0
        
    if isinstance(date_of_birth, str):
        from datetime import datetime
        try:
            date_of_birth = datetime.strptime(date_of_birth.split('T')[0], '%Y-%m-%d').date()
        except:
            return 0, 0, 0
            
    if isinstance(date_tested, str):
        from datetime import datetime
        try:
            date_tested = datetime.strptime(date_tested.split('T')[0], '%Y-%m-%d').date()
        except:
            date_tested = date.today()

    try:
        days = getattr(date_tested, 'day', date.today().day) - getattr(date_of_birth, 'day', 1)
        months = getattr(date_tested, 'month', date.today().month) - getattr(date_of_birth, 'month', 1)
        years = getattr(date_tested, 'year', date.today().year) - getattr(date_of_birth, 'year', 2020)

        if days < 0:
            days += 30
            months -= 1

        if months < 0:
            months += 12
            years -= 1

        return years, months, days
    except Exception:
        return 0, 0, 0

def get_age_group(years, months):
    if years == 3 and 1 <= months <= 11:
        return '3.1-4.0'
    elif years == 4 and months == 0:
        return '3.1-4.0'
    elif years == 4 and 1 <= months <= 11:
        return '4.1-5.0'
    elif years == 5 and months == 0:
        return '4.1-5.0'
    elif years == 5 and 1 <= months <= 11:
        return '5.1-5.11'
    
    # If they fall exactly outside but very close, return the closest group
    if years < 3 or (years == 3 and months == 0):
        return '3.1-4.0'
    if years >= 6:
        return '5.1-5.11'
        
    return None

def get_scaled_score(age_group, domain_name, raw_score):
    if age_group not in SCALED_SCORE_TABLES:
        return None
    
    # Clean the domain name for mapping
    # e.g., "Gross Motor Domain" -> "Gross Motor"
    domain_mapping = {
        'Gross Motor Domain': 'Gross Motor',
        'Fine Motor': 'Fine Motor',
        'Self-Help': 'Self-Help',
        'Receptive Language': 'Receptive Language',
        'Expressive Language': 'Expressive Language',
        'Cognitive': 'Cognitive',
        'Social-Emotional': 'Social-Emotional',
        'Gross Motor': 'Gross Motor'
    }
    
    table_domain = None
    for k, v in domain_mapping.items():
        if k.lower() in domain_name.lower():
            table_domain = v
            break
            
    if not table_domain:
        table_domain = domain_name
    
    if table_domain not in SCALED_SCORE_TABLES[age_group]:
        return None
        
    ranges = SCALED_SCORE_TABLES[age_group][table_domain]
    for min_r, max_r, ss in ranges:
        if min_r <= raw_score <= max_r:
            return ss
            
    # Fallback to highest if max exceeded
    if raw_score > ranges[-1][1]:
        return ranges[-1][2]
    return 1

def get_standard_score(sum_scaled):
    if sum_scaled < 21:
        return STANDARD_SCORE_TABLE[21]
    if sum_scaled > 112:
        return STANDARD_SCORE_TABLE[112]
    return STANDARD_SCORE_TABLE.get(sum_scaled, None)

def get_standard_score_interpretation(score):
    if score is None:
        return 'N/A'
    if score <= 69:
        return "Suggests Significant Delay"
    elif 70 <= score <= 79:
        return "Suggests Slight Delay"
    elif 80 <= score <= 119:
        return "Average Development"
    elif 120 <= score <= 129:
        return "Slightly Advanced"
    else:
        return "Highly Advanced"

