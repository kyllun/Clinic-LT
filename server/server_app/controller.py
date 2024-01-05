from flask import render_template, url_for, redirect, request
from server_app import app, dao, login
from flask_login import login_user, logout_user, login_required, current_user
from server_app.models import Role
from datetime import datetime
import cloudinary
import cloudinary.uploader

@app.route("/")
def home_page():
    return render_template("home_page.html")

@app.route("/register", methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        try:
            if(password.strip().__eq__(confirm.strip())):
                dao.add_user(name=name, username=username, password=password)
                return redirect(url_for('user_login'))
            else:
                err_msg = 'Mật khẩu không khớp'
        except Exception as ex:
            err_msg = 'Hệ thống đang có lỗi' +str(ex)

    return render_template("register_page.html", err_msg=err_msg)

@app.route("/login", methods=['get', 'post'])
def user_login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        userRole = request.form.get('userRole')

        user = dao.check_login(username=username, password=password, userRole=userRole)

        if user:
            login_user(user=user) #current_user

            return redirect(url_for('home_page'))
        else:
            err_msg = 'Username hoặc password không chính xác'

    return render_template("login_page.html", err_msg=err_msg)

@app.route('/logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_login'))

@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.context_processor
def common_response():
    return dict(Role=Role)

@app.route("/patient_information")
def patient_information():    
    return render_template("patient_infomation_page.html")

@app.route("/patient_information/<int:user_id>", methods=['get', 'post'])
def update_patient_infor(user_id):
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        sex = request.form.get('sex')
        birth = request.form.get('birth')
        email = request.form.get('email')
        avatar = request.files.get('avatar')
        avatar_path = None
        if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']
        address = request.form.get('address')
        phone = request.form.get('phone')

        dao.update_patient(user_id=user_id, name=name, sex=sex, birth=birth, email=email, avatar=avatar_path, address=address, phone=phone)
        return redirect(url_for('home_page'))

@app.route('/medical_register', methods=['get', 'post'])
def medical_register():
    if not current_user.is_authenticated:
        return redirect('/login')
    elif current_user.loaiNguoiDung == Role.Patient: 
        if request.method.__eq__('POST'):
            date = request.form.get('date')
            time = request.form.get('time')

            date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')

            count = dao.count_register_medical(date)
            if count < 40:
                dao.register_medical(user_id=current_user.id, date_time=date_time)
            else: 
                msg = 'Đã đủ số lượng đăng ký'
            return redirect(url_for('home_page'))
    elif current_user.loaiNguoiDung == Role.Nurse: 
        if request.method.__eq__('POST'):
            phone = request.form.get('phone')
            date = request.form.get('date')
            time = request.form.get('time')

            date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')

            count = dao.count_register_medical(date)
            if count < 40:
                dao.register_medical(phone=phone, date_time=date_time)
            else: 
                msg = 'Đã đủ số lượng đăng ký'
            return redirect(url_for('home_page'))
    return render_template('medical_register_page.html', msg=msg)
    
@app.route("/medical_list")
def medical_list():
    
    return render_template('medical_examination_list_page.html')

if __name__ == '__main__':
    app.run(debug=True)