from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from functools import wraps

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_anda_yang_sangat_aman'

db_config = { 'host': 'localhost', 'user': 'root', 'password': '', 'database': 'db_onderdil' }

def get_db_connection():
    return mysql.connector.connect(**db_config)

# --- DECORATOR (Tidak Berubah) ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Anda harus login untuk mengakses halaman ini.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'admin':
            flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Rute Login/Register/Index/Dashboard (Tidak Berubah) ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and user['password'] == password:
            session['user_id'] = user['id_user']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('Password dan Konfirmasi Password tidak cocok!', 'danger')
            return render_template('register.html') 
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'pelanggan')", (username, password))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error:
            flash('Username sudah terdaftar!', 'danger')
            return render_template('register.html')
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(id_kendaraan) AS jumlah FROM kendaraan WHERE id_jenis = 1")
    jumlah_motor = cursor.fetchone()['jumlah']
    cursor.execute("SELECT COUNT(id_kendaraan) AS jumlah FROM kendaraan WHERE id_jenis = 2")
    jumlah_sepeda = cursor.fetchone()['jumlah']
    cursor.close()
    conn.close()
    return render_template('dashboard.html', 
                           jumlah_motor=jumlah_motor, 
                           jumlah_sepeda=jumlah_sepeda, 
                           username=session['username'], 
                           role=session['role'])

# --- Rute Pilih Kendaraan (Tidak Berubah) ---
@app.route('/pilih/<int:id_jenis>')
@login_required
def pilih_kendaraan(id_jenis):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM kendaraan WHERE id_jenis = %s", (id_jenis,))
    kendaraan_list = cursor.fetchall()
    
    if not kendaraan_list:
        systems_by_vehicle = {}
    else:
        kendaraan_ids = tuple(k['id_kendaraan'] for k in kendaraan_list)
        if len(kendaraan_ids) == 1:
            query_sistem = f"SELECT * FROM sistem WHERE id_kendaraan = {kendaraan_ids[0]}"
            cursor.execute(query_sistem)
        else:
            query_sistem = f"SELECT * FROM sistem WHERE id_kendaraan IN {kendaraan_ids}"
            cursor.execute(query_sistem)
        all_systems = cursor.fetchall()
        systems_by_vehicle = {}
        for s in all_systems:
            v_id = s['id_kendaraan']
            if v_id not in systems_by_vehicle: systems_by_vehicle[v_id] = []
            systems_by_vehicle[v_id].append(s)

    favorit_ids = []
    if 'user_id' in session:
        cursor.execute("SELECT id_kendaraan FROM garasi WHERE id_user = %s", (session['user_id'],))
        results = cursor.fetchall()
        favorit_ids = [item['id_kendaraan'] for item in results]
        
    cursor.close()
    conn.close()
    return render_template('pilih_kendaraan.html', 
                           kendaraan_list=kendaraan_list, 
                           systems_by_vehicle=systems_by_vehicle,
                           favorit_ids=favorit_ids)

# --- Rute Detail Onderdil (Tidak Berubah) ---
@app.route('/onderdil/<int:id_kendaraan>/<int:id_sistem>')
@login_required
def detail_onderdil(id_kendaraan, id_sistem):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM onderdil WHERE id_kendaraan = %s AND id_sistem = %s", (id_kendaraan, id_sistem))
    onderdil_list = cursor.fetchall()
    cursor.execute("SELECT nama_kendaraan FROM kendaraan WHERE id_kendaraan = %s", (id_kendaraan,))
    kendaraan = cursor.fetchone()
    cursor.execute("SELECT nama_sistem FROM sistem WHERE id_sistem = %s", (id_sistem,))
    sistem = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('detail_onderdil.html', onderdil_list=onderdil_list, kendaraan=kendaraan, sistem=sistem)

# --- Rute Favorit (Tidak Berubah) ---
@app.route('/favorit')
@login_required
def favorit():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT k.id_kendaraan, k.nama_kendaraan, k.gambar_kendaraan, j.nama_jenis
        FROM garasi g JOIN kendaraan k ON g.id_kendaraan = k.id_kendaraan
        JOIN jenis_kendaraan j ON k.id_jenis = j.id_jenis WHERE g.id_user = %s
    """
    cursor.execute(query, (session['user_id'],))
    favorit_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('favorit.html', favorit_items=favorit_items)

@app.route('/toggle_favorit/<int:id_kendaraan>')
@login_required
def toggle_favorit(id_kendaraan):
    id_user = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_garasi FROM garasi WHERE id_user = %s AND id_kendaraan = %s", (id_user, id_kendaraan))
    ada = cursor.fetchone()
    if ada:
        cursor.execute("DELETE FROM garasi WHERE id_user = %s AND id_kendaraan = %s", (id_user, id_kendaraan))
    else:
        cursor.execute("INSERT INTO garasi (id_user, id_kendaraan) VALUES (%s, %s)", (id_user, id_kendaraan))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(request.referrer or url_for('index'))
    
# --- Rute Tambah Onderdil (DIPERBARUI UNTUK 3 TINGKAT) ---
@app.route('/tambah_onderdil', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah_onderdil():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Ambil data dari form
        id_kendaraan = request.form['id_kendaraan']
        id_sistem = request.form['id_sistem']
        nama_onderdil = request.form['nama_onderdil']
        fungsi = request.form['fungsi']
        kerusakan = request.form['kerusakan']
        rekomendasi = request.form['rekomendasi']
        gambar = request.form['gambar']
        
        # Query insert
        query = "INSERT INTO onderdil (id_kendaraan, id_sistem, nama_onderdil, fungsi, ciri_kerusakan, rekomendasi, gambar_onderdil) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (id_kendaraan, id_sistem, nama_onderdil, fungsi, kerusakan, rekomendasi, gambar))
        conn.commit()
        
        flash('Data onderdil baru berhasil ditambahkan!', 'success')
        return redirect(url_for('tambah_onderdil'))

    # **INI BAGIAN PENTING YANG MEMPERBAIKI BUG ANDA**
    # Untuk method GET, kita HANYA perlu mengirim daftar JENIS kendaraan
    cursor.execute("SELECT * FROM jenis_kendaraan ORDER BY nama_jenis")
    jenis_list = cursor.fetchall()
    cursor.close()
    conn.close()
    # Mengirim 'jenis_list' ke template
    return render_template('tambah_onderdil.html', jenis_list=jenis_list) 

# --- Rute Tambah Kendaraan (Tidak Berubah) ---
@app.route('/tambah_kendaraan', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah_kendaraan():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        nama_kendaraan = request.form['nama_kendaraan']
        id_jenis = request.form['id_jenis']
        gambar_kendaraan = request.form['gambar_kendaraan']
        sistem_string = request.form['sistem_list']
        query_kendaraan = "INSERT INTO kendaraan (nama_kendaraan, id_jenis, gambar_kendaraan) VALUES (%s, %s, %s)"
        cursor.execute(query_kendaraan, (nama_kendaraan, id_jenis, gambar_kendaraan))
        new_vehicle_id = cursor.lastrowid 
        if sistem_string:
            sistem_list = [s.strip() for s in sistem_string.split(',') if s.strip()]
            if sistem_list:
                query_sistem = "INSERT INTO sistem (id_kendaraan, nama_sistem) VALUES (%s, %s)"
                sistem_data_tuples = [(new_vehicle_id, nama_sistem) for nama_sistem in sistem_list]
                cursor.executemany(query_sistem, sistem_data_tuples)
        conn.commit()
        flash('Data kendaraan baru dan sistemnya berhasil ditambahkan!', 'success')
        return redirect(url_for('tambah_kendaraan'))
    cursor.execute("SELECT * FROM jenis_kendaraan")
    jenis_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tambah_kendaraan.html', jenis_list=jenis_list)

# --- Rute Logout (Tidak Berubah) ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- RUTE API (Tidak Berubah) ---
@app.route('/api/get_kendaraan/<int:id_jenis>')
@login_required
@admin_required
def get_kendaraan(id_jenis):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_kendaraan, nama_kendaraan FROM kendaraan WHERE id_jenis = %s ORDER BY nama_kendaraan", (id_jenis,))
    kendaraan_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(kendaraan_list)

@app.route('/api/get_sistem/<int:id_kendaraan>')
@login_required
@admin_required
def get_sistem(id_kendaraan):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_sistem, nama_sistem FROM sistem WHERE id_kendaraan = %s ORDER BY nama_sistem", (id_kendaraan,))
    sistem_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(sistem_list)

if __name__ == '__main__':
    app.run(debug=True)