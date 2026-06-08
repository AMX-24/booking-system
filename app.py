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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_name TEXT NOT NULL,
            trainee_id TEXT NOT NULL,
            department TEXT NOT NULL,
            target_entity TEXT NOT NULL,
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

TARGET_ENTITIES = {
    'affairs': 'شؤون المتدربين',
    'chairman': 'رئيس القسم',
    'faculty': 'عضو هيئة تدريس'
}

@app.route('/')
def home():
    return render_template('index.html', entities=TARGET_ENTITIES)

@app.route('/select_time/<entity_id>')
def select_time(entity_id):
    if entity_id not in TARGET_ENTITIES:
        return redirect(url_for('home'))
    
    entity_name = TARGET_ENTITIES[entity_id]
    return render_template('select_time.html', entity_id=entity_id, entity_name=entity_name, departments=DEPARTMENTS)

@app.route('/get_available_slots', methods=['POST'])
def get_available_slots():
    entity_id = request.form.get('entity_id')
    department = request.form.get('department')
    booking_date = request.form.get('booking_date')
    
    if not entity_id or not department or not booking_date:
        return "بيانات غير مكتملة", 400

    conn = get_db_connection()
    cursor = conn.cursor()
    # الفرز الذكي: يبحث عن الأوقات المحجوزة لنفس الجهة والقسم والتاريخ المختار بالتحديد
    cursor.execute('''
        SELECT booking_time FROM bookings 
        WHERE target_entity = ? AND department = ? AND booking_date = ?
    ''', (entity_id, department, booking_date))
    
    booked_rows = cursor.fetchall()
    conn.close()
    
    booked_times = [row['booking_time'] for row in booked_rows]
    free_times = [t for t in AVAILABLE_TIMES if t not in booked_times]
    
    if not free_times:
        return '<p class="text-danger text-center fw-bold">عذراً، جميع المواعيد لهذا اليوم محجوزة بالكامل.</p>'
        
    html_buttons = ""
    for t in free_times:
        html_buttons += f'<button type="button" class="btn btn-outline-success slot-btn m-1" onclick="selectSlot(\'{t}\')">{t}</button>'
    return html_buttons

@app.route('/book', methods=['POST'])
def book():
    trainee_name = request.form.get('trainee_name')
    trainee_id = request.form.get('trainee_id')
    department = request.form.get('department')
    entity_id = request.form.get('entity_id')
    booking_date = request.form.get('booking_date')
    booking_time = request.form.get('booking_time')
    
    if not (trainee_name and trainee_id and department and entity_id and booking_date and booking_time):
        flash('فضلاً املأ جميع الحقول المطلوبة واختر موعداً متاحاً.', 'danger')
        return redirect(url_for('select_time', entity_id=entity_id))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id FROM bookings 
        WHERE target_entity = ? AND department = ? AND booking_date = ? AND booking_time = ?
    ''', (entity_id, department, booking_date, booking_time))
    
    if cursor.fetchone():
        conn.close()
        flash('عذراً، هذا الوقت تم حشزه للتو! يرجى اختيار وقت آخر.', 'danger')
        return redirect(url_for('select_time', entity_id=entity_id))
        
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO bookings (trainee_name, trainee_id, department, target_entity, booking_date, booking_time, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (trainee_name, trainee_id, department, entity_id, booking_date, booking_time, timestamp))
    
    conn.commit()
    conn.close()
    
    session['success_info'] = {
        'name': trainee_name,
        'id': trainee_id,
        'dept': DEPARTMENTS[department],
        'entity': TARGET_ENTITIES[entity_id],
        'date': booking_date,
        'time': booking_time
    }
    
    return redirect(url_for('success'))

@app.route('/success')
def success():
    info = session.get('success_info')
    if not info:
        return redirect(url_for('home'))
    return render_template('success.html', info=info)

# --- نظام لوحة تحكم الإدارة ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
            
    return render_template('admin.html', login_mode=True)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
    all_bookings = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', login_mode=False, bookings=all_bookings, depts=DEPARTMENTS, entities=TARGET_ENTITIES)

@app.route('/admin/delete/<int:booking_id>')
def delete_booking(booking_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    flash('تم إلغاء الحجز بنجاح.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

init_db()

if __name__ == '__main__':
    app.run(debug=True)
