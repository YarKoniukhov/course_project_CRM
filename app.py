from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost:5432/crm_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Модели БД
class Departments(db.Model):
    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(40), unique=True)


class Employees(db.Model):
    employees_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fio = db.Column(db.String(100))
    position = db.Column(db.String(25))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.department_id'), nullable=False)


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_dt = db.Column(db.DateTime, nullable=False, default=datetime.strftime(datetime.today(), "%b %d %Y"))
    updated_dt = db.Column(db.DateTime, nullable=True, default=datetime.now().strftime("%Y-%m-%d"))
    order_type = db.Column(db.String(20))
    description = db.Column(db.String(100))
    status = db.Column(db.String(25))
    serial_no = db.Column(db.Integer)
    creator_id = db.Column(db.Integer, db.ForeignKey('employees.employees_id'))

    def __str__(self):
        return f'Order_id: {self.order_id}\n' \
               f'Created_dt: {self.created_dt}\n' \
               f'Update_dt: {self.updated_dt}\n' \
               f'Order_type: {self.order_type}\n' \
               f'Description: {self.description}\n' \
               f'Status: {self.status}\n' \
               f'Serial_no: {self.serial_no}\n' \
               f'Creator_id: {self.creator_id}\n'


class Customers(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fio = db.Column(db.String(100))
    number_phone = db.Column(db.Integer)
    email = db.Column(db.String(100))
    is_subscribed = db.Column(db.Boolean, default=False)


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String)
    create_dt = db.Column(db.DateTime, default=datetime.utcnow())


db.create_all()


# Главная страница
@app.route('/')
def home():
    return render_template('base.html')


# Вывод тех. задания на экран
@app.route('/tech_task')
def view_task():
    return render_template('technical_task.html')


# Модель 'Departments' - вывод информации, добавление, редактирование, удаление
@app.route('/view_departments')
def view_departments():
    print(Departments.query.all())
    return render_template('view_departments.html', params=Departments.query.all())


@app.route('/create_departments', methods=['POST', 'GET'])
def create_departments():
    if request.method == 'POST':
        data_departments = request.form.get('departments')
        depart = Departments.query.filter_by(department_name=data_departments).first()
        if depart:
            return render_template('base.html', content='Такой департамент уже существует!')
        elif data_departments == '':
            return render_template('base.html', content='Ошибка! Вы ничего не ввели!')
        department_profile = Departments(department_name=data_departments)
        try:
            db.session.add(department_profile)
            db.session.flush()
            db.session.commit()
            return redirect('/view_departments')
        except:
            return render_template('base.html', content='Что-то пошло не так!')
    else:
        return render_template('create_departments.html')


@app.route('/change_departments', methods=['POST', 'GET'])
def change_departments():
    if request.method == 'POST':
        dep = request.form.get('dep')
        if dep == '':
            return render_template('base.html', content='Ошибка! Вы ничего не ввели!')
        elif dep:
            return redirect(url_for('change_dep', dep=int(dep)))
    return render_template('change_departments.html')


@app.route('/change_dep', methods=['POST', 'GET'])
def change_dep():
    data = request.args.get('dep')
    departments = Departments.query.get(data)
    if request.method == 'POST':
        departments.department_name = request.form['department_name']
        try:
            db.session.commit()
            return redirect('/view_departments')
        except:
            return 'При редактировании произошла ошибка'
    else:
        return render_template('change_dep.html', departments=departments)


@app.route('/delete_departments')
def delete_departments():
    dep = request.args.get('dep')
    if dep:
        return redirect(url_for('del_departments', dep=int(dep)))
    return render_template('delete_departments.html')


@app.route('/del_departments')
def del_departments():
    data = request.args.get('dep')
    departments = Departments.query.get_or_404(data)
    try:
        db.session.delete(departments)
        db.session.flush()
        db.session.commit()
        return redirect('/view_departments')
    except:
        return render_template('base.html', content='Что-то пошло не так!')

# Модель 'Employees' - вывод информации, добавление, редактирование, удаление
@app.route('/view_employees')
def view_employees():
    return render_template('view_employees.html', params=Employees.query.all())


@app.route('/create_employee', methods=['POST', 'GET'])
def create_employee():
    if request.method == 'POST':
        fio = request.form.get('fio')
        position = request.form.get('position')
        department_id = request.form.get('department_id')
        employee_profile = Employees(fio=fio, position=position, department_id=department_id)
        try:
            db.session.add(employee_profile)
            db.session.flush()
            db.session.commit()
            return redirect('/view_employees')
        except:
            return render_template('base.html', content='Что-то пошло не так!')
    else:
        return render_template('create_employees.html')


@app.route('/change_employees', methods=['POST', 'GET'])
def change_employees():
    if request.method == 'POST':
        empl = request.form.get('empl')
        if empl == '':
            return render_template('base.html', content='Ошибка! Вы ничего не ввели!')
        elif empl:
            return redirect(url_for('change_empl', empl=int(empl)))
    return render_template('change_employees.html')


@app.route('/change_empl', methods=['POST', 'GET'])
def change_empl():
    data = request.args.get('empl')
    employees = Employees.query.get(data)
    if request.method == 'POST':
        employees.fio = request.form['fio']
        employees.position = request.form['position']
        employees.department_id = request.form['department_id']
        try:
            db.session.commit()
            return redirect('/view_employees')
        except:
            return 'При редактировании произошла ошибка'
    else:
        return render_template('change_empl.html', employees=employees)


@app.route('/delete_employees')
def delete_employees():
    empl = request.args.get('empl')
    if empl:
        return redirect(url_for('del_employees', empl=int(empl)))
    return render_template('delete_employees.html')


@app.route('/del_employees')
def del_employees():
    data = request.args.get('empl')
    empl = Employees.query.get_or_404(data)
    try:
        db.session.delete(empl)
        db.session.flush()
        db.session.commit()
        return redirect('/view_employees')
    except:
        return render_template('base.html', content='Что-то пошло не так!')


# Модель 'Orders' - вывод информации, добавление, редактирование, удаление
@app.route('/view_orders')
def view_orders():
    order_list = Orders.query.join(Employees, Orders.creator_id == Employees.employees_id)\
        .add_columns(Orders.order_id, Orders.created_dt, Orders.updated_dt, Orders.order_type,
                     Orders.description, Orders.status, Orders.serial_no, Employees.fio)
    return render_template('view_orders.html', params=order_list)


@app.route('/create_orders', methods=['POST', 'GET'])
def create_orders():
    if request.method == 'POST':
        order_type = request.form.get('order_type')
        status = request.form.get('status')
        description = request.form.get('description')
        serial_no = request.form.get('serial_no')
        creator_id = request.form.get('creator_id')
        order_profile = Orders(order_type=order_type, status=status, description=description, serial_no=serial_no,
                               creator_id=creator_id)
        try:
            db.session.add(order_profile)
            db.session.flush()
            db.session.commit()
            return redirect('/view_orders')
        except:
            return render_template('base.html', content='Что-то пошло не так')
    else:
        return render_template('create_orders.html')


@app.route('/change_orders', methods=['POST', 'GET'])
def change_orders():
    if request.method == 'POST':
        order = request.form.get('order')
        if order == '':
            return render_template('base.html', content='Ошибка! Вы ничего не ввели!')
        elif order:
            return redirect(url_for('change_ord', order=int(order)))
    return render_template('change_orders.html')


@app.route('/change_ord', methods=['POST', 'GET'])
def change_ord():
    data = request.args.get('order')
    orders = Orders.query.get(data)
    if request.method == 'POST':
        orders.order_type = request.form['order_type']
        orders.description = request.form['description']
        orders.status = request.form['status']
        orders.serial_no = request.form['serial_no']
        orders.creator_id = request.form['creator_id']
        orders.updated_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            db.session.commit()
            return redirect('/view_orders')
        except:
            return 'При редактировании произошла ошибка'
    else:
        return render_template('change_ord.html', orders=orders)


@app.route('/delete_orders')
def delete_orders():
    order = request.args.get('order')
    if order:
        return redirect(url_for('del_orders', order=int(order)))
    return render_template('delete_orders.html')


@app.route('/del_orders')
def del_orders():
    data = request.args.get('order')
    order = Orders.query.get_or_404(data)
    print(order)
    try:
        db.session.delete(order)
        db.session.flush()
        db.session.commit()
        return redirect('/view_orders')
    except:
        return render_template('base.html', content='Что-то пошло не так!')


# Модель 'Customers' - вывод информации, добавление, редактирование, удаление
@app.route('/view_customers')
def view_customers():
    return render_template('view_customers.html', params=Customers.query.all())


@app.route('/create_customers', methods=['POST', 'GET'])
def create_customers():
    if request.method == 'POST':
        fio = request.form.get('fio')
        number_phone = request.form.get('number_phone')
        email = request.form.get('email')
        customers_profile = Customers(fio=fio, number_phone=number_phone, email=email)
        try:
            db.session.add(customers_profile)
            db.session.flush()
            db.session.commit()
            return redirect('/view_customers')
        except:
            return render_template('base.html', content='Что-то пошло не так!')
    else:
        return render_template('create_customers.html')


@app.route('/change_customers', methods=['POST', 'GET'])
def change_customers():
    if request.method == 'POST':
        cus = request.form.get('cus')
        if cus == '':
            return render_template('base.html', content='Ошибка! Вы ничего не ввели!')
        elif cus:
            return redirect(url_for('change_cus', cus=int(cus)))
    return render_template('change_customers.html')


@app.route('/change_cus', methods=['POST', 'GET'])
def change_cus():
    data = request.args.get('cus')
    customers = Customers.query.get(data)
    if request.method == 'POST':
        customers.fio = request.form['fio']
        customers.number_phone = request.form['number_phone']
        customers.email = request.form['email']
        try:
            db.session.commit()
            return redirect('/view_customers')
        except:
            return 'При редактировании произошла ошибка'
    else:
        return render_template('change_cus.html', customers=customers)


@app.route('/delete_customers')
def delete_customers():
    cus = request.args.get('cus')
    if cus:
        return redirect(url_for('del_customers', cus=int(cus)))
    return render_template('delete_customers.html')


@app.route('/del_customers')
def del_customers():
    data = request.args.get('cus')
    customers = Customers.query.get_or_404(data)
    try:
        db.session.delete(customers)
        db.session.flush()
        db.session.commit()
        return redirect('/view_customers')
    except:
        return render_template('base.html', content='Что-то пошло не так!')


# Модель 'Users' - вывод информации, редактирование, удаление
@app.route('/view_users')
def view_users():
    return render_template('view_users.html', params=Users.query.all())


@app.route('/change_users', methods=['POST', 'GET'])
def change_users():
    if request.method == 'POST':
        users = request.form.get('users')
        if users == '':
            return render_template('base.html', content='Ошибка! Вы ничего не ввели!')
        elif users:
            return redirect(url_for('change_user', users=int(users)))
    return render_template('change_users.html')


@app.route('/change_user', methods=['POST', 'GET'])
def change_user():
    data = request.args.get('users')
    users = Users.query.get(data)
    if request.method == 'POST':
        users.user_name = request.form['user_name']
        users.chat_id = request.form['chat_id']
        users.message = request.form['message']
        try:
            db.session.commit()
            return redirect('/view_users')
        except:
            return 'При редактировании произошла ошибка'
    else:
        return render_template('change_user.html', users=users)


@app.route('/delete_users')
def delete_users():
    users = request.args.get('users')
    if users:
        return redirect(url_for('del_users', users=int(users)))
    return render_template('delete_users.html')


@app.route('/del_users')
def del_users():
    data = request.args.get('users')
    users = Users.query.get_or_404(data)
    try:
        db.session.delete(users)
        db.session.flush()
        db.session.commit()
        return redirect('/view_users')
    except:
        return render_template('base.html', content='Что-то пошло не так!')


# Фильтрация заявок по датам создания.
@app.route('/get_orders_by_date', methods=['POST', 'GET'])
def get_orders_by_date():
    if request.method == 'POST':
        date_start = request.form.get('date_start')
        date_end = request.form.get('date_end')
        if date_start and date_end == '':
            return render_template('base.html', content='Ошибка! Вы ничего не ввели!')
        elif date_start and date_end:
            return redirect(url_for('get_order_date', date_start=date_start, date_end=date_end))
    return render_template('filter_by_date.html')


@app.route('/get_order_date')
def get_order_date():
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')
    dates = Orders.query.filter(Orders.created_dt >= date_start, Orders.created_dt <= date_end).all()
    return render_template('filter_date.html', params=dates)


# Фильтрация заявок по статусам.
@app.route('/search_order_status', methods=['POST', 'GET'])
def search_order_status():
    if request.method == 'POST':
        status = request.form.get('status')
        if status == '':
            return render_template('base.html', content='Ошибка! Вы ничего не ввели!')
        elif status:
            return redirect(url_for('search_status', status=status))
    return render_template('search_order_status.html')


@app.route('/search_status')
def search_status():
    data = request.args.get('status')
    dates = Orders.query.filter_by(status=data).all()
    return render_template('filter_date.html', params=dates)


# Фильтрация заявок по ответственным сотрудникам.
@app.route('/search_order_creator_id', methods=['POST', 'GET'])
def search_order_creator_id():
    if request.method == 'POST':
        creator_id = request.form.get('creator_id')
        if creator_id == '':
            return render_template('base.html', content='Ошибка! Вы ничего не ввели!')
        elif creator_id:
            return redirect(url_for('search_creator_id', creator_id=creator_id))
    return render_template('search_creator_id.html')


@app.route('/search_creator_id')
def search_creator_id():
    data = request.args.get('creator_id')
    dates = Orders.query.filter_by(creator_id=data).all()
    return render_template('filter_date.html', params=dates)


if __name__ == '__main__':
    app.run(debug=True)
