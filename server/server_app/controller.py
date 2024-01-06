from flask import render_template, url_for, redirect, request, session, jsonify
from server_app import app, dao, login, utils, admin
from flask_login import login_user, logout_user, login_required, current_user
from server_app.models import Role
from datetime import datetime
import cloudinary
import cloudinary.uploader
import math

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
                dao.add_user(name=name, 
                             username=username, 
                             password=password)
                return redirect(url_for('user_login'))
            else:
                err_msg = 'Mật khẩu không khớp'
        except Exception as ex:
            err_msg = 'Hệ thống đang có lỗi' +str(ex)

    return render_template("register_page.html", 
                           err_msg=err_msg)

@app.route("/login", methods=['get', 'post'])
def user_login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        userRole = request.form.get('userRole')

        user = dao.check_login(username=username, 
                               password=password, 
                               userRole=userRole)

        if user:
            login_user(user=user) #current_user

            return redirect(url_for('home_page'))
        else:
            err_msg = 'Username hoặc password không chính xác'

    return render_template("login_page.html", 
                           err_msg=err_msg)

@app.route('/logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_login'))

@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id=user_id)

# @app.context_processor
# def common_response():
#     return dict(Role=Role)

@app.context_processor
def common_responses():
    return {
        'medicine_state': utils.counter_medicine(session.get('medicine')),
        'Role': Role
    }

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

        dao.update_patient(user_id=user_id, 
                           name=name, 
                           sex=sex, 
                           birth=birth, 
                           email=email, 
                           avatar=avatar_path, 
                           address=address, 
                           phone=phone)
        return redirect(url_for('home_page'))

@app.route('/register_medical', methods=['get', 'post'])
def medical_register():
    msg = ''
    if not current_user.is_authenticated:
        return redirect('/login')
    elif current_user.loaiNguoiDung == Role.Patient: 
        if request.method.__eq__('POST'):
            date = request.form.get('date')
            time = request.form.get('time')

            date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')
            count = dao.count_register_medical(date = date)
            if count > 0 and count < 5:
                dao.register_medical(patient_id=current_user.id, 
                                     date_time=date_time)
            else: 
                msg = 'Đã đủ số lượng đăng ký'

            if not msg:
                return redirect(url_for('home_page'))
            
    elif current_user.loaiNguoiDung == Role.Nurse: 
        if request.method.__eq__('POST'):
            phone = request.form.get('phone')
            date = request.form.get('date')
            time = request.form.get('time')

            date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')           
            count = dao.count_register_medical(date = date)

            if count > 0 and count < 5:
                dao.register_medical(phone=phone, 
                                     date_time=date_time)
            else: 
                msg = 'Đã đủ số lượng đăng ký'
            
            if not msg:
                return redirect(url_for('home_page'))
    return render_template('medical_register_page.html', 
                           msg=msg)
    
@app.route("/medical_list", methods=['get'])
def medical_list():
    date = request.args.get('date')
    medical_list = dao.get_register_medical_by_date(date=date)

    return render_template('medical_examination_list_page.html', 
                           medical_list=medical_list)

@app.route("/medicine")
def medicine_list():
    kw = request.args.get("keywordthuoc")
    counter = dao.count_medicine()
    page = request.args.get("page", 1)
    drugs = dao.load_medicine(kw=kw, page=int(page))
    return render_template('medicine.html',
                           drugs=drugs,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))

@app.route('/login_admin',methods=['post', 'get'])
def login_admin():
    if request.method == 'POST':
        username = request.form.get('usernameAd')
        password = request.form.get('passwordAd')

        user = dao.check_login(username=username, password=password,userRole=Role.Admin)

        if user:
            login_user(user=user)

    return redirect('/admin')

@app.route('/prescription')
def prescription_medicine():
    return render_template("prescription.html",
                           stats=utils.counter_medicine(session.get('medicine')))


# @app.context_processor
# def common_responses():
#     return {
#         'medicine_state': utils.counter_medicine(session.get('medicine'))
#     }

@app.route("/api/add-medicine",methods=['post'])
def add_to_medicine(): #add_prescription
    data= request.get_json()
    id=str(data.get('id'))
    tenThuoc=data.get('tenThuoc')
    donGia=data.get('donGia')
    medicine =session.get('medicine')
    if not medicine:
        medicine={}

    if id in medicine:
        medicine[id]['quantity']= medicine[id]['quantity']+1
    else:
        medicine[id]={
             'id':id,
            'tenThuoc':tenThuoc,
            'donGia':donGia,
            'quantity': 1
        }
    session['medicine']= medicine

    return jsonify(utils.counter_medicine(medicine))

if __name__ == '__main__':
    app.run(debug=True)