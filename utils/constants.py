# ==================================================
# MONTHS MAPPING
# ==================================================
months_map = {
    # Thai Short
    "ม.ค.": 1, "ก.พ.": 2, "มี.ค.": 3, "เม.ย.": 4, "พ.ค.": 5, "มิ.ย.": 6,
    "ก.ค.": 7, "ส.ค.": 8, "ก.ย.": 9, "ต.ค.": 10, "พ.ย.": 11, "ธ.ค.": 12,
    # Thai Full
    "มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4, "พฤษภาคม": 5, "มิถุนายน": 6,
    "กรกฎาคม": 7, "สิงหาคม": 8, "กันยายน": 9, "ตุลาคม": 10, "พฤศจิกายน": 11, "ธันวาคม": 12,
    # English Short
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
    # English Full
    "JANUARY": 1, "FEBRUARY": 2, "MARCH": 3, "APRIL": 4, "MAY": 5, "JUNE": 6,
    "JULY": 7, "AUGUST": 8, "SEPTEMBER": 9, "OCTOBER": 10, "NOVEMBER": 11, "DECEMBER": 12
}

# ==================================================
# SPECIAL CITIES & TOURIST SPOTS (Aliases)
# ==================================================
# Key = Lowercase Search Term | Value = The name you want to save
special_places_map = {
    # --- East ---
    "pattaya": "Chon Buri",
    "pataya": "Chon Buri",
    "bangsaen": "Chon Buri",
    "koh larn": "Chon Buri",
    "sattahip": "Chon Buri",
    "koh chang": "Trat",
    "ko chang": "Trat",
    "koh samet": "Rayong",
    
    # --- South ---
    "hat yai": "Songkhla",
    "hatyai": "Songkhla",
    "samui": "Surat Thani",
    "koh samui": "Surat Thani",
    "ko samui": "Surat Thani",
    "koh phangan": "Surat Thani",
    "koh tao": "Surat Thani",
    "krabi town": "Krabi",
    "koh lanta": "Krabi",
    "phi phi": "Krabi",
    "patong": "Phuket",
    "khaolak": "Phang-nga",
    "khao lak": "Phang-nga",
    "betong": "Yala",

    # --- West / Central ---
    "hua hin": "Prachuap Khiri Khan",
    "huahin": "Prachuap Khiri Khan",
    "cha-am": "Phetchaburi",
    "cha am": "Phetchaburi",
    "suan phueng": "Ratchaburi",
    "amphawa": "Samut Songkhram",

    # --- North / Northeast ---
    "khao yai": "Nakhon Ratchasima",
    "khaoyai": "Nakhon Ratchasima",
    "pak chong": "Nakhon Ratchasima",
    "korat": "Nakhon Ratchasima",
    "pai": "Mae Hong Son",
    "chiang khan": "Loei",
    "khao kho": "Phetchabun",

    # --- Bangkok Area ---
    "bkk": "Bangkok",
    "krung thep": "Bangkok",
    "muang thong": "Nonthaburi",
    "impact arena": "Nonthaburi",
    "thunder dome": "Nonthaburi",
    "rangsit": "Pathum Thani",
    "salaya": "Nakhon Pathom",
    
    # --- Common Typos ---
    "chang mai": "Chiang Mai",
    "chiangmai": "Chiang Mai",
    "ayutthaya": "Phra Nakhon Si Ayutthaya"
}

# ==================================================
# YOUR STANDARD PROVINCES LIST
# ==================================================
valid_provinces = [
    # ภาคกลาง & ตะวันออก & ตะวันตก
    "กรุงเทพมหานคร", "Bangkok", "กาญจนบุรี", "Kanchanaburi", "จันทบุรี", "Chanthaburi", 
    "ฉะเชิงเทรา", "Chachoengsao", "ชลบุรี", "Chon Buri", "ชัยนาท", "Chai Nat", 
    "ตราด", "Trat", "นครนายก", "Nakhon Nayok", "นครปฐม", "Nakhon Pathom", 
    "นครสวรรค์", "Nakhon Sawan", "นนทบุรี", "Nonthaburi", "ปทุมธานี", "Pathum Thani", 
    "ประจวบคีรีขันธ์", "Prachuap Khiri Khan", "ปราจีนบุรี", "Prachin Buri", 
    "พระนครศรีอยุธยา", "Phra Nakhon Si Ayutthaya", "เพชรบุรี", "Phetchaburi", 
    "ราชบุรี", "Ratchaburi", "ระยอง", "Rayong", "ลพบุรี", "Lop Buri", 
    "สมุทรปราการ", "Samut Prakan", "สมุทรสงคราม", "Samut Songkhram", 
    "สมุทรสาคร", "Samut Sakhon", "สระแก้ว", "Sa Kaeo", "สระบุรี", "Saraburi", 
    "สิงห์บุรี", "Sing Buri", "สุพรรณบุรี", "Suphan Buri", "อ่างทอง", "Ang Thong", 
    "อุทัยธานี", "Uthai Thani",
    
    # ภาคเหนือ
    "กำแพงเพชร", "Kamphaeng Phet", "เชียงราย", "Chiang Rai", "เชียงใหม่", "Chiang Mai", 
    "ตาก", "Tak", "น่าน", "Nan", "พะเยา", "Phayao", "พิจิตร", "Phichit", 
    "พิษณุโลก", "Phitsanulok", "เพชรบูรณ์", "Phetchabun", "แพร่", "Phrae", 
    "แม่ฮ่องสอน", "Mae Hong Son", "ลำปาง", "Lampang", "ลำพูน", "Lamphun", 
    "สุโขทัย", "Sukhothai", "อุตรดิตถ์", "Uttaradit",
    
    # ภาคอีสาน
    "กาฬสินธุ์", "Kalasin", "ขอนแก่น", "Khon Kaen", "ชัยภูมิ", "Chaiyaphum", 
    "นครพนม", "Nakhon Phanom", "นครราชสีมา", "Nakhon Ratchasima", "บึงกาฬ", "Bueng Kan", 
    "บุรีรัมย์", "Buri Ram", "มหาสารคาม", "Maha Sarakham", "มุกดาหาร", "Mukdahan", 
    "ยโสธร", "Yasothon", "ร้อยเอ็ด", "Roi Et", "เลย", "Loei", 
    "ศรีสะเกษ", "Si Sa Ket", "สกลนคร", "Sakon Nakhon", "สุรินทร์", "Surin", 
    "หนองคาย", "Nong Khai", "หนองบัวลำภู", "Nong Bua Lam Phu", 
    "อำนาจเจริญ", "Amnat Charoen", "อุดรธานี", "Udon Thani", "อุบลราชธานี", "Ubon Ratchathani",
    
    # ภาคใต้
    "กระบี่", "Krabi", "ชุมพร", "Chumphon", "ตรัง", "Trang", 
    "นครศรีธรรมราช", "Nakhon Si Thammarat", "นราธิวาส", "Narathiwat", "ปัตตานี", "Pattani", 
    "พังงา", "Phang-nga", "พัทลุง", "Phatthalung", "ภูเก็ต", "Phuket", "ยะลา", "Yala", 
    "ระนอง", "Ranong", "สงขลา", "Songkhla", "สตูล", "Satun", "สุราษฎร์ธานี", "Surat Thani"
]

# ==================================================
# FINAL MERGE
# ==================================================
# Start with the aliases
province_map = special_places_map.copy()

# Add your standard provinces to the map
# This maps the lowercase version to the original capitalization
for p in valid_provinces:
    key = p.lower()
    if key not in province_map:
        province_map[key] = p