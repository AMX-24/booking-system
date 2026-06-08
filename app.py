import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cti_booking_secret_key_2026')

DB_NAME = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # جدول الحجوزات مع حقل اسم الدكتور المستقل
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_name TEXT NOT NULL,
            trainee_id TEXT NOT NULL,
            department TEXT NOT NULL,
            target_entity TEXT NOT NULL,
            doctor_name TEXT,
            booking_date TEXT NOT NULL,
            booking_time TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin123'))
    except sqlite3.IntegrityError:
        pass
        
    conn.commit()
    conn.close()

AVAILABLE_TIMES = [
    "08:00 ص", "08:30 ص", "09:00 ص", "09:30 ص",
    "10:00 ص", "10:30 ص", "11:00 ص", "11:30 ص",
    "12:00 م", "12:30 م", "01:00 م", "01:30 م"
]

DEPARTMENTS = {
    'computer': 'قسم الحاسب الآلي',
    'communications': 'قسم الاتصالات',
    'electronics': 'قسم الإلكترونيات',
    'general': 'قسم المواد العامة'
}

# المكتبة الكاملة والمقفلة لأسماء أعضاء هيئة التدريس لكل الأقسام الأربعة
DOCTORS_BY_DEPT = {
    'computer': [
        'إبراهيم العديني', 'أحمد كليبي', 'احمد العمري', 'أحمد رشاد', 'احمد عنقاوي',
        'أيمن العبيدي', 'بندر الثقفي', 'بندر محمد العويضي', 'ثامر عطيه الغامدي', 'جمعان الزهراني',
        'جميل الخليفي', 'حسن المالكي', 'حسين احمد باداود', 'حمد الشهابي', 'حامد الشيخ',
        'حامد الشمراني', 'خالد الغامدي', 'خليل ال صمع', 'سالم الزهراني', 'سلطان ال مغلف',
        'سلمان الشهري', 'صالح الغامدي', 'عادل الغامدي', 'عبدالرحمن المنتشري', 'عبدالرحمن الحربي',
        'عبدالله الحازمي', 'عبدالله السهيمي', 'عبدالله الشهري', 'عبدالله ناصر', 'عبدالهادي المالكي',
        'عبيد الحربي', 'فايز شافعي', 'فهد السميري', 'محمد العرياني', 'محمد الشريف',
        'منصور الزهراني', 'موسى المحمادي', 'وليد الغامدي', 'ياسر الحبشان'
    ],
    'communications': [
        'أحمد البار', 'امين مشدق', 'إيمن صائغ', 'بدر الجهني', 'رضا الجهني',
        'سعيد ظافر', 'سامي قرامي', 'سعيد عبدالرحيم', 'عمر الصايغ', 'عيد الحربي',
        'عيسى السقاف', 'ماجد السريحي', 'ماهر نحاس', 'محمد العلياني', 'محمد سلامي',
        'منصور الحازمي', 'وليد جمعة', 'ياسر مياجي'
    ],
    'electronics': [
        'إسماعيل فاضل', 'أنس كرسوم', 'أيمن كيفي', 'أيمن بنجر', 'جابر يماني',
        'جميل الجهني', 'حاتم الردادي', 'حاتم الزهراني', 'حسن بادويل', 'حسين المكرمي',
        'خالد حجازي', 'رمزي مهدي', 'سعود المطيري', 'سعود الغامدي', 'سعود خوتنلي',
        'سعيد ابو عسيس', 'سلطان العتيبي', 'صالح الشهري', 'طارق الغامدي', 'ظافر الشهري',
        'عبدالرحمن الغامدي', 'عبدالله غرسان', 'عواض الشهري', 'فايز الشهري', 'فهد العامودي',
        'فوزي جلالة', 'محمد صباغ', 'محمد الرفاعي', 'محمد عشري', 'هيثم نايته', 'يزيد الغامدي'
    ],
    'general': [
        'بندر العمودي', 'تركي الغامدي', 'تركي العتيبي', 'خالد السلمي', 'خالد الزهراني',
        'رامي حكمي', 'سامر فطاني', 'عبدالعزيز السلمي', 'عبدالله القحطاني', 'عبدالله البشري',
        'عبدالله الرفاعي', 'علي الغامدي', 'علي الشهري', 'عمر رزق الله', 'فهيد المطيري',
        'فواز الحربي', 'فيصل الحارثي', 'محمد ناجي', 'منصور الشهراني', 'هشام ابو الجدايل'
    ]
}
