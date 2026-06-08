import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
# مفتاح تشفير عشوائي وآمن للجلسات لضمان حماية المنظومة
app.secret_key = os.environ.get('SECRET_KEY', 'cti_booking_secure_key_2026')

# محاكاة لقاعدة بيانات المواعيد للأقسام الأربعة في الكلية
# (الحاسب الآلي، الاتصالات، الإلكترونيات، المواد العامة، بالإضافة لشؤون المتدربين)
DEPARTMENTS = {
    'computer': 'قسم تقنية الحاسب الآلي',
    'telecom': 'قسم تقنية الاتصالات',
    'electronics': 'قسم تقنية الإلكترونيات',
    'general': 'قسم المواد العامة',
    'trainee_affairs': 'إدارة شؤون المتدربين'
}

@app.route('/')
def home():
    # يعرض الصفحة الرئيسية النظيفة (بدون زر الإدارة السفلي)
    return render_template('index.html')

@app.route('/department/<dept_id>')
def show_department(dept_id):
    # التحقق من وجود القسم المطلوب
    if dept_id in DEPARTMENTS:
        dept_name = DEPARTMENTS[dept_id]
        return f"<h1>بوابة الحجز المخصصة لـ: {dept_name}</h1><p>سيتم عرض المواعيد المتاحة هنا ديناميكياً.</p><a href='/'>العودة للرئيسية</a>"
    return redirect(url_for('home'))

# 🔒 مسار لوحة التحكم السرّي - تكتبه بيدك في المتصفح للدخول
@app.route('/admin')
def admin_dashboard():
    # نظام الحماية: إذا حاول مستخدم عادي تخمين الرابط، يطرده النظام فوراً ويعيده للرئيسية
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    # إذا كان المسؤول مسجلاً لدخوله، تفتح له اللوحة
    return """
    <div style="direction: rtl; text-align: center; font-family: sans-serif; padding-top: 50px;">
        <h1>🔒 لوحة التحكم الإدارية المركزية</h1>
        <p>مرحباً بك يا مسؤول النظام. هنا يمكنك رصد الحجوزات اليومية للأقسام.</p>
        <a href="/admin/logout" style="color: red;">تسجيل الخروج</a>
    </div>
    """

# مسار تسجيل الدخول المخصص لك (الآدمن) لتفعيل الصلاحية
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # بيانات الدخول الافتراضية (يمكنك تغييرها لاحقاً)
        if username == 'admin' and password == '123456':
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "<p style='color:red; text-align:center;'>بيانات الدخول غير صحيحة!</p>"
            
    return '''
    <div style="direction: rtl; text-align: center; font-family: sans-serif; margin-top: 100px;">
        <h2>تسجيل دخول الإدارة</h2>
        <form method="post">
            اسم المستخدم: <input type="text" name="username" required><br><br>
            كلمة المرور: <input type="password" name="password" required><br><br>
            <input type="submit" value="تسجيل الدخول">
        </form>
    </div>
    '''

# مسار تسجيل الخروج لإلغاء صلاحية الآدمن وتأمين اللوحة مجدداً
@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
