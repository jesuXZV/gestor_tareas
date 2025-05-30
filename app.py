from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'
DATABASE = 'usuarios.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            nombre_usuario TEXT UNIQUE NOT NULL,
            curso TEXT NOT NULL,
            documento TEXT UNIQUE NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL,
            rol TEXT DEFAULT 'rol_usuario',
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
            activo INTEGER DEFAULT 1
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            fecha_inicio DATE,
            fecha_fin DATE,
            estado TEXT DEFAULT 'activo',
            id_usuario_creador INTEGER,
            FOREIGN KEY (id_usuario_creador) REFERENCES usuarios(id) ON DELETE SET NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            fecha_vencimiento DATE,
            prioridad TEXT,
            estado TEXT DEFAULT 'pendiente',
            id_proyecto INTEGER,
            id_usuario_asignado INTEGER,
            ruta_archivo TEXT,
            FOREIGN KEY (id_proyecto) REFERENCES proyectos(id) ON DELETE CASCADE,
            FOREIGN KEY (id_usuario_asignado) REFERENCES usuarios(id) ON DELETE SET NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mensaje TEXT NOT NULL,
            leido INTEGER DEFAULT 0,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            id_usuario INTEGER,
            FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
        );
    ''')

    # Índices para optimizar búsquedas
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_nombre_usuario ON usuarios(nombre_usuario);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_documento ON usuarios(documento);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_correo ON usuarios(correo);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tareas_id_usuario_asignado ON tareas(id_usuario_asignado);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_proyectos_id_usuario_creador ON proyectos(id_usuario_creador);')

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN tema TEXT DEFAULT 'claro';")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN idioma TEXT DEFAULT 'es';")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN notificaciones INTEGER DEFAULT 1;")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(UserMixin):
    def __init__(self, id, nombre, nombre_usuario, curso, documento, correo, contrasena, rol, fecha_registro, activo):
        self.id = id
        self.nombre = nombre
        self.nombre_usuario = nombre_usuario
        self.curso = curso
        self.documento = documento
        self.correo = correo
        self.contrasena = contrasena
        self.rol = rol
        self.fecha_registro = fecha_registro
        self.activo = activo

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    fila = conn.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if fila:
        return Usuario(
            id=fila['id'],
            nombre=fila['nombre'],
            nombre_usuario=fila['nombre_usuario'],
            curso=fila['curso'],
            documento=fila['documento'],
            correo=fila['correo'],
            contrasena=fila['contrasena'],
            rol=fila['rol'],
            fecha_registro=fila['fecha_registro'],
            activo=fila['activo']
        )
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['nombre_usuario']
        contrasena = request.form['contrasena']
        conn = get_db_connection()
        fila = conn.execute('SELECT * FROM usuarios WHERE nombre_usuario = ?', (usuario,)).fetchone()
        conn.close()
        if fila and check_password_hash(fila['contrasena'], contrasena) and fila['activo']:
            user = Usuario(
                id=fila['id'],
                nombre=fila['nombre'],
                nombre_usuario=fila['nombre_usuario'],
                curso=fila['curso'],
                documento=fila['documento'],
                correo=fila['correo'],
                contrasena=fila['contrasena'],
                rol=fila['rol'],
                fecha_registro=fila['fecha_registro'],
                activo=fila['activo']
            )
            login_user(user)
            return redirect(url_for('admin' if user.rol == 'rol_administrador' else 'persona'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        nombre_usuario = request.form['nombre_usuario']
        curso = request.form['curso']
        documento = request.form['documento']
        correo = request.form['correo']
        contrasena = generate_password_hash(request.form['contrasena'])
        rol = request.form.get('rol', 'rol_usuario')
        conn = get_db_connection()
        try:
            # Ejecutar inserción
            conn.execute('''
                INSERT INTO usuarios (nombre, nombre_usuario, curso, documento, correo, contrasena, rol)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, nombre_usuario, curso, documento, correo, contrasena, rol))

            conn.commit()
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash('El nombre de usuario, documento o correo ya existe')
        finally:
            conn.close()
    return render_template('crear_usuario.html')


@app.route('/admin')
@login_required
def admin():
    if current_user.rol != 'rol_administrador':
        return redirect(url_for('persona'))
    conn = get_db_connection()
    usuarios = conn.execute('SELECT * FROM usuarios WHERE activo = 1').fetchall()
    conn.close()
    return render_template('admin.html', usuarios=usuarios)

@app.route('/persona')
@login_required
def persona():
    conn = get_db_connection()
    usuarios = conn.execute('SELECT * FROM usuarios WHERE activo = 1').fetchall()
    conn.close()
    return render_template('persona.html', usuarios=usuarios)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/ajustes', methods=['POST'])
@login_required
def ajustes():
    tema = request.form.get('tema')
    idioma = request.form.get('idioma')
    notificaciones = 1 if request.form.get('notificaciones') == 'on' else 0

    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE usuarios
            SET tema = ?, idioma = ?, notificaciones = ?
            WHERE id = ?
        ''', (tema, idioma, notificaciones, current_user.id))
        conn.commit()
        conn.close()
        return 'OK'
    except Exception as e:
        print("Error al guardar ajustes:", e)
        return 'Error al guardar ajustes', 500
    

@app.route('/ajustes', methods=['POST'])
@login_required
def guardar_ajustes():
    tema = request.form.get('tema')
    idioma = request.form.get('idioma')
    notificaciones = request.form.get('notificaciones')

    try:
        conn = get_db_connection()
        conn.execute(
            'UPDATE usuarios SET tema = ?, idioma = ?, notificaciones = ? WHERE id = ?',
            (tema, idioma, int(notificaciones == "on"), current_user.id)
        )
        conn.commit()
        conn.close()
        return "Ajustes guardados correctamente", 200
    except Exception as e:
        print("Error al guardar ajustes:", e)
        return "Error al guardar ajustes", 500




if __name__ == '__main__':
    init_db()
    app.run(debug=True)