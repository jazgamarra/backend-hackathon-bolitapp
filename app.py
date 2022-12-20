from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_NOTIFICATIO    NS'] = False
db=SQLAlchemy(app)

# Datos globales a validar 
categorias_validas_ingreso = ['salario', 'extras']
categorias_validas_egreso = ['vivienda', 'deudas', 'servicios', 'supermercado', 'movilidad', 'entretenimiento']

# Crear modelo de base de datos de usuario
class Users (db.Model):
    id=db.Column(db.Integer, primary_key=True)
    telefono=db.Column(db.Integer, nullable=False)
    nombre=db.Column(db.String(100), nullable=False)
    contrasenha=db.Column(db.String(100), nullable=False)
    saldo=db.Column(db.Integer, nullable=False)

    def __init__(self, nombre, telefono, contrasenha, saldo ):
        self.nombre=nombre
        self.telefono=telefono
        self.contrasenha=contrasenha 
        self.saldo = saldo

# Ruta de la pagina principal 
@app.route('/pagina_principal')
def pagina_principal ():
    # Verificamos si inicio sesion revisando los argumentos 
    args = request.args 
    try: 
        datos = [ args['nombre'], args['telefono'] ]
    except: 
        # Si intenta ingresar a la pagina principal sin iniciar sesion, le redireccionamos 
        print('No iniciaste sesion, master. ')
        return redirect(url_for('login'))
    return render_template('pagina_principal.html', nombre=datos[0], telefono=datos[1])

# Ruta para la pagina de ingresar datos 
@app.route('/ingresar_datos', methods=['GET', 'POST'])
def ingresar_datos():
    # Verificamos los argumentos recibidos de la pagina de sign_up o login
    args = request.args 
    try: 
        datos = [ args['nombre'], args['telefono'] ]
    except: 
        # Si intenta ingresar a la pagina principal sin iniciar sesion, le redireccionamos 
        print('No iniciaste sesion, master. ')
        return redirect(url_for('login'))

    # Validamos que los datos de ingreso y egreso se procesen solo si ya se inicio sesion
    if ((datos[0] != None) and (datos[1] != None)):
        if request.method=='POST':
            opcion=request.form['opcion']
            monto=request.form['monto']
            categoria=request.form['categoria']
            telefono=request.args['telefono']
            
        # Realizamos las operaciones necesarias segun sea ingreso o egreso
            if opcion == 'ingreso': 
                # Validamos si es una categoria valida para las areas de ingreso 
                if categoria in categorias_validas_ingreso: 
                    print('Se registro el ingreso de', monto, categoria)
                else: 
                    print('No es una categoria valida de ingreso ')

            elif opcion == 'egreso': 
                if categoria in categorias_validas_egreso: 
                    print('Se registro el egreso de', monto, categoria)
                else: 
                    print('No es una categoria valida de egreso')

    return render_template('ingresar_datos.html')

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
                usuario = Users(nombre, telefono, contrasenha1, 0)
                db.session.add(usuario)
                db.session.commit()
                # Direccionarle a la pagina principal mandando como parametro el nombre y telefono 
                return redirect(url_for('pagina_principal', nombre=nombre, telefono=telefono))

            else:
                print ('Te equivocaste de contrasenha master ')

    return render_template('sign_up.html')

# Ruta para el login -- iniciar sesion de un usuario que ya existe
@app.route('/login', methods=['GET','POST'])
def login ():
    if request.method=='POST':
        telefono=request.form['telefono']
        contrasenha_ingresada=request.form['contrasenha']

        print ('Login con los datos... ', telefono, contrasenha_ingresada)

        # Verificamos de que exista el usuario en nuestra base de datos 
        try:
            usuario = Users.query.filter_by(telefono=telefono).first()
        except:  
            usuario = None 

        # Validamos que el usuario exista
        # Si el usuario no existe, usuario es None 
        if usuario != None: 
            # Convertir lo que viene de la base de datos a un diccionario 
            dict_usuario = usuario.__dict__
            contrasenha_correcta = dict_usuario['contrasenha']

            # Verificar si la contrasenha ingresada es correcta 
            if contrasenha_correcta == contrasenha_ingresada: 
                print('La contrasenha es correcta uwu')
                return redirect(url_for('pagina_principal',  nombre=dict_usuario['nombre'], telefono=telefono))

            else: 
                print ('Te equivocaste de contrasenha master ')
    return render_template('login.html')    

@app.route('/borrar/<int:id>')
def borrar(id):
    usuario_a_eliminar = Users.query.get(id)
    db.session.delete(usuario_a_eliminar)
    db.session.commit()
    return redirect(url_for('pagina_principal',nombre='', telefono=''))


# Definimos la ruta principal
@app.route('/')
def index ():
    return render_template('index.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=8080)


   


   