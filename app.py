from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'your_super_secret_secure_key_here' # مفتاح تشفير الجلسات لتأمين النظام

# قاعدة بيانات مؤقتة ومحاكاة للمواعيد والأقسام الأربعة للمشروع
DEPARTMENTS = ['Computer', 'Communications', 'Electronics', 'General Subjects']
appointments_db = []

@app.route('/')
def home():
    # عرض الصفحة الرئيسية النظيفة بدون زر الإدارة
    return render_template('index.html')

@app.route('/department/<dept_name>')
def show_department(dept_name):
    # مسار حجز المواعيد للأقسام والمتدربين
    return f"صفحة الحجز المخصصة لقسم أو جهة: {dept_name}"

# 🔒 مسار لوحة التحكم - لا يظهر له أي زر في الموقع ويتم كتابته يدوياً في المتصفح
@app.route('/admin')
def admin_dashboard():
    # التحقق البرمجي: إذا لم يكن المستخدم الحالي آدمن، يتم طرده فوراً وتحويله للرئيسية
    if not session.get('is_admin'):
        # خيار إضافي: يمكنك تحويله لصفحة تسجيل دخول مخصصة للآدمن، أو إرجاعه للرئيسية كالتالي
        return redirect(url_for('home'))
    
    # إذا كانت الهوية صحيحة ومسجل دخوله، يفتح له لوحة التحكم بنجاح
    return render_template('admin.html', appointments=appointments_db)

# مسار محاكاة لتسجيل دخول الإدارة (تستخدمه أنت لتفعيل الجلسة)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # تحقق بسيط من بيانات الآدمن (يمكنك ربطها بقاعدة بيانات لاحقاً)
        if username == 'admin' and password == 'password123':
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "بيانات الدخول خاطئة!"
            
    return '''
        <form method="post" style="direction: rtl; text-align: center; margin-top: 50px;">
            <h2>تسجيل دخول الإدارة السرّي</h2>
            اسم المستخدم: <input type="text" name="username"><br><br>
            كلمة المرور: <input type="password" name="password"><br><br>
            <input type="submit" value="دخول">
        </form>
    '''

# مسار تسجيل الخروج للإدارة لإنهاء الجلسة وتأمين اللوحة مجدداً
@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
