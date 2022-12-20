from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db=SQLAlchemy(app)

# Datos globales a validar 
categorias_validas_ingreso = ['salario', 'extras']
categorias_validas_egreso = ['vivienda', 'deudas', 'servicios', 'supermercado', 'movilidad', 'entretenimiento']

# Crear modelo de base de datos de usuario
class Users (db.Model):
    id=db.Column(db.Integer, primary_key=True)
    telefono=db.Column(db.Integer, nullable=False)
    nombre=db.Column(db.String(100), nullable=False)
    contrasenha=db.Column(db.String(50), nullable=False)

    def __init__(self, nombre, telefono, contrasenha, saldo ):
        self.nombre=nombre
        self.telefono=telefono
        self.contrasenha=contrasenha 

# Crear modelo de base de datos de transacciones 
class Transactions (db.Model):
    id=db.Column(db.Integer, primary_key=True)
    transaccion=db.Column(db.String(20), nullable=False)
    monto=db.Column(db.Integer, nullable=False)
    categoria=db.Column(db.String(20), nullable=False)
    telefono=db.Column(db.Integer, nullable=False)

    def __init__(self, transaccion, monto, categoria, telefono):
        self.transaccion = transaccion
        self.monto = monto
        self.categoria = categoria
        self.telefono = telefono
       
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
    print('Los args de la pagina principal son', args)
    
    # Consultamos el saldo del usuario
    saldo = consultar_saldo(datos[1])

    return render_template('pagina_principal.html', nombre=datos[0], telefono=datos[1], saldo=saldo)

# Funcion para calcular el saldo de un usuario y actualizar la base de datos del usuario 
def consultar_saldo(telefono): 
    # Se obtienen las transacciones de egreso y se suman
    transacciones_egreso = db.session.query(Transactions).filter_by(telefono=telefono).filter_by(transaccion='egreso').all()
    total = 0
    for transaction in transacciones_egreso: 
        total = total - transaction.monto

    # Se obtienen las transacciones de ingreso y se suman 
    transacciones_ingreso = db.session.query(Transactions).filter_by(telefono=telefono).filter_by(transaccion='ingreso').all()
    for transaction in transacciones_ingreso: 
        total = total + transaction.monto
    print('El saldo del usuario es', total)
    return total 


# Ruta para la pagina de ingresar datos 
@app.route('/ingresar_datos', methods=['GET', 'POST'])
def ingresar_datos():
    if request.method=='POST':
        # Verificamos los argumentos recibidos de la pagina de sign_up o login
        args = request.args 
        try: 
            nombre = args['nombre']
            telefono = args['telefono'] 
        except: 
            # Si intenta ingresar a la pagina principal sin iniciar sesion, le redireccionamos 
            print('No iniciaste sesion, master. ')
            return redirect(url_for('login'))

        # Validamos que los datos de ingreso y egreso se procesen solo si ya se inicio sesion
        opcion=request.form['opcion']
        monto=request.form['monto']
        categoria=request.form['categoria']
        telefono=request.args['telefono']
        
        print ('Se recibio la transaccion de',opcion, monto, categoria, telefono)

        # Realizamos las operaciones necesarias segun sea ingreso o egreso
        if (opcion == 'ingreso') and (categoria in categorias_validas_ingreso):
            print('EL REQUEST METHOD ES', request.method)

            transaccion = Transactions(opcion, monto, categoria, telefono)
            db.session.add(transaccion)
            db.session.commit()
        elif (opcion == 'egreso') and (categoria in categorias_validas_egreso): 
            transaccion = Transactions(opcion, monto, categoria, telefono)
            db.session.add(transaccion)
            db.session.commit()
        else: 
            print('La transaccion no corresponde con la categoria. ')
    

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
                
                return redirect(url_for('pagina_principal', nombre=nombre, telefono=telefono, saldo=consultar_saldo(telefono)))

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
                return redirect(url_for('pagina_principal',  nombre=dict_usuario['nombre'], telefono=telefono, saldo=consultar_saldo(telefono)))

            else: 
                print ('Te equivocaste de contrasenha master ')
    return render_template('login.html')    

@app.route('/borrar/<int:id>')
def borrar(id):
    usuario_a_eliminar = Users.query.get(id)
    db.session.delete(usuario_a_eliminar)
    db.session.commit()
    return redirect(url_for('pagina_principal',nombre='', telefono='', saldo=0))


# Definimos la ruta principal
@app.route('/')
def index ():
    return render_template('index.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=8080) 