from flask import render_template, url_for, redirect, request
from server_app import app, dao, login
from flask_login import login_user, logout_user, login_required
from server_app.models import Role

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

@app.route('/medical_register')
def medical_register():
    return render_template('medical_register_page.html')

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
        address = request.form.get('address')
        phone = request.form.get('phone')

        dao.update_patient(user_id=user_id, name=name, sex=sex, birth=birth, email=email, avatar=avatar, address=address, phone=phone)
        return redirect(url_for('home_page'))

@app.route("/medical_register")
def medical_register():    
    return render_template("medical_register_page.html")

@app.route("/medical_register/<int:user_id>", methods=['get', 'post'])
def register_medical_form(user_id):
    if request.method.__eq__('POST'):
        date = request.form.get('date')
        time = request.form.get('time')

        dao.register_medical(date=date, time=time)
        return redirect(url_for('home_page'))


if __name__ == '__main__':
    app.run(debug=True)