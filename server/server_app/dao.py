from server_app import app, db
from server_app.models import BenhNhan, YTa, BacSi, ThuNgan, NguoiDung, Role
from sqlalchemy.orm.exc import NoResultFound
import hashlib

def add_user(name, username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = NguoiDung(hoTen=name.strip(),
                     username=username.strip(),
                     password=password,
                     loaiNguoiDung=Role.Patient)
    db.session.add(user)
    db.session.commit()

def check_login(username, password):
    if username and password: 
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())   
        # Tìm kiếm người dùng dựa trên tên đăng nhập
        try:
            user = NguoiDung.query.filter_by(username=username.strip()).one()
        except NoResultFound:
            return None  # Trả về None nếu không tìm thấy người dùng
        
        # Kiểm tra mật khẩu
        if user.password == password:
            return user  # Trả về đối tượng người dùng nếu thông tin đăng nhập hợp lệ
        return None  # Trả về None nếu mật khẩu không khớp
    
def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)