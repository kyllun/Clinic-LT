from server_app import app, db
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from server_app.models import Thuoc, DonViThuoc, Role
from flask_login import current_user, logout_user, login_user
from flask import redirect
from flask_admin import Admin, expose ,AdminIndexView
from server_app import utils

class MyAdmin(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/admin_page.html', 
                           stats=utils.sales_report(),
                           sales_data=utils.total_amount_by_month())

class AuthenticatedAdmin(ModelView):
     def is_accessible(self):
         return current_user.is_authenticated and current_user.loaiNguoiDung.__eq__(Role.Admin)

class DrugsView(AuthenticatedAdmin):
    column_list = ['tenThuoc', 'ngaySX', 'hanSD', 'donGia', 'donViThuoc']
    column_searchable_list = ['tenThuoc', 'donGia']
    column_filters = ['tenThuoc', 'donGia']
    can_view_details = True
    can_export = True

class DonViThuocView(AuthenticatedAdmin):
    column_list = ['donVi', 'thuoc']

class MedicineView(DrugsView):
    can_view_details = True
    can_export = True
    column_searchable_list = ['tenThuoc', 'donGia']
    column_labels = {
        'tenThuoc': 'Ten Thuoc',
        'ngaySX': 'Ngay san xuat',
        'hanSD': 'Han su dung',
        'donGia': 'Don gia'
    }
    column_filters = ['tenThuoc', 'donGia']

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated

admin = Admin(app=app, name='Quản trị thuốc', template_mode='bootstrap4', index_view=MyAdmin())
admin.add_view(DonViThuocView(DonViThuoc,db.session))
admin.add_view(DrugsView(Thuoc,db.session))
admin.add_view(LogoutView(name='Logout'))
