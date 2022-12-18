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
def registro():
    if request.method=='POST':
        nombre=request.form['nombre']
        telefono=request.form['telefono']
        contrasenha1=request.form['contrasenha1']
        contrasenha2=request.form['contrasenha2']

        print('Sign up con los datos...', nombre, telefono, contrasenha1, contrasenha2)

        # Verificar que no exista ese usuario en la base de datos 
        

        # Si las contrasenhas coinciden, mandar a la base de datos 
        if contrasenha1 == contrasenha2: 
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
    return render_template('login.html')






if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)