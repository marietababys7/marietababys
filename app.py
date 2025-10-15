from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///marietababys.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    descripcion = db.Column(db.String(300))
    imagen = db.Column(db.String(300))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rutas
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/productos")
def productos():
    productos = Producto.query.all()
    return render_template("productos.html", productos=productos)

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for("admin"))
        else:
            flash("Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/admin")
@login_required
def admin():
    productos = Producto.query.all()
    return render_template("admin.html", productos=productos)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/add_producto", methods=["POST"])
@login_required
def add_producto():
    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    imagen = request.form.get("imagen")
    nuevo = Producto(nombre=nombre, descripcion=descripcion, imagen=imagen)
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
