import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
# مفتاح أمان لتشفير الجلسات وحماية المنظومة
app.secret_key = os.environ.get('SECRET_KEY', 'cti_booking_secure_key_2026')

@app.route('/')
def home():
    # استدعاء الصفحة الرئيسية النظيفة المضاف لها الخلفية
    return render_template('index.html')

@app.route('/department/<dept_name>')
def show_department(dept_name):
    return f"<div style='text-align:center; padding-top:50px; font-family:sans-serif;'><h1>بوابة الحجز لـ: {dept_name}</h1><a href='/'>العودة للرئيسية</a></div>"

# 🔒 مسار لوحة التحكم السرّي - تكتبه بيدك في المتصفح للدخول
@app.route('/admin')
def admin_dashboard():
    # إذا حاول أي مستخدم عادي الدخول، يطرده النظام تلقائياً للرئيسية
    if not session.get('is_admin'):
        return redirect(url_for('home'))
    
    return """
    <div style="direction: rtl; text-align: center; font-family: sans-serif; padding-top: 50px;">
        <h1>🔒 لوحة التحكم الإدارية</h1>
        <p style="color: green;">مرحباً بك يا مسؤول النظام، تم الدخول بأمان.</p>
        <a href="/admin/logout" style="color: red; text-decoration: none; font-weight: bold;">تسجيل الخروج</a>
    </div>
    """

# مسار تسجيل دخول الإدارة لتفعيل الصلاحية ودخول الـ Admin
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # بيانات الدخول السرية الخاصة بك
        if username == 'admin' and password == 'password123':
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "<p style='color:red; text-align:center;'>بيانات الدخول خاطئة!</p>"
            
    return '''
    <div style="direction: rtl; text-align: center; font-family: sans-serif; margin-top: 100px;">
        <h2>تسجيل دخول الإدارة السرّي</h2>
        <form method="post">
            اسم المستخدم: <input type="text" name="username" required><br><br>
            كلمة المرور: <input type="password" name="password" required><br><br>
            <input type="submit" value="دخول">
        </form>
    </div>
    '''

# تسجيل الخروج لحماية لوحة التحكم بعد انتهائك
@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
