from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, FileField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
import stripe

# -------------------- CONFIGURACIÓN --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

stripe.api_key = "sk_test_TU_CLAVE_DE_PRUEBA"

# -------------------- MODELOS --------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.String(500))
    price = db.Column(db.Float)
    image = db.Column(db.String(300))

# -------------------- FORMULARIOS --------------------
class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class ProductForm(FlaskForm):
    name = StringField('Nombre del producto', validators=[DataRequired()])
    description = StringField('Descripción', validators=[DataRequired()])
    price = FloatField('Precio', validators=[DataRequired()])
    image = FileField('Imagen del producto')
    submit = SubmitField('Agregar Producto')

# -------------------- LOGIN MANAGER --------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- RUTAS --------------------
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash("Usuario o contraseña incorrectos")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    form = ProductForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image=filename
        )
        db.session.add(new_product)
        db.session.commit()
        flash("Producto agregado correctamente")
        return redirect(url_for('admin'))
    return render_template('admin.html', form=form)

@app.route('/buy/<int:product_id>', methods=['POST'])
def buy(product_id):
    product = Product.query.get_or_404(product_id)
    flash(f"Simulación de compra para {product.name}")
    return redirect(url_for('index'))

# -------------------- CREAR BASE DE DATOS --------------------
with app.app_context():
    db.create_all()
    # Crear usuario admin solo si no existe
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', password='admin123')
        db.session.add(admin_user)
        db.session.commit()

# -------------------- EJECUTAR APP --------------------
if __name__ == '__main__':
    app.run(debug=True)
