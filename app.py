from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False
db=SQLAlchemy(app)

# Crear modelo de base de datos de usuario
class Users (db.Model):
    id=db.Column(db.Integer, primary_key=True)
    telefono=db.Column(db.Integer, nullable=False)
    nombre=db.Column(db.String(100), nullable=False)
    contrasenha1=db.Column(db.String(100), nullable=False)
    contrasenha2=db.Column(db.String(100), nullable=False)

    def __init__(self, nombre, telefono, contrasenha1, contrasenha2):
        self.nombre=nombre
        self.telefono=telefono
        self.contrasenha1=contrasenha1
        self.contrasenha2=contrasenha2

# Ruta para el sign up de un usuario nuevo 
@app.route('/sign_up', methods=['GET','POST'])
def sign_up():
    if request.method=='POST':
        nombre=request.form['nombre']
        telefono=request.form['telefono']
        contrasenha1=request.form['contrasenha1']
        contrasenha2=request.form['contrasenha2']

        print('Sign up con los datos...', nombre, telefono, contrasenha1, contrasenha2)

        # Verificar que no exista ya ese usuario en la base de datos 
        try:
            existe_el_usuario = db.session.execute(db.select(Users).filter_by(telefono=telefono)).one()
        except: 
            existe_el_usuario = None 

        # Si no existe el usuario en la base de datos, lo registramos 
        if existe_el_usuario == None: 
            # Verificar si las contrasenhas coinciden
            if contrasenha1 == contrasenha2: 
                # Agregar a la base de datos. 
                print ('Agregar a la base de datos uwu')
                usuario = Users(nombre, telefono, contrasenha1, contrasenha2)
                db.session.add(usuario)
                db.session.commit()
            else:
                print ('Te equivocaste de contrasenha master ')

    return render_template('sign_up.html')

# Ruta para el login -- iniciar sesion de un usuario que ya existe
@app.route('/login', methods=['GET','POST'])
def login ():
    if request.method=='POST':
        telefono=request.form['telefono']
        contrasenha=request.form['contrasenha']

        print ('Login con los datos... ', telefono, contrasenha)

        # Verificamos de que exista el usuario en nuestra base de datos 
        try:
            usuario = Users.query.filter_by(telefono=telefono).first()
        except:  
            usuario = None 

        # Si el usuario existe, debemos validar la contrasenha 
        
        print(usuario.__str__(), usuario)

    return render_template('login.html')

# Definimos la ruta principal
@app.route('/')
def index ():
    return render_template('index.html')



if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=8080)


   