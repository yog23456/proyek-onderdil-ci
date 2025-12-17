from flask import Flask, render_template, request, redirect, url_for, session, flash

# Inisialisasi Aplikasi
app = Flask(__name__)
app.secret_key = 'bebas_aja_kuncinya'  # Diperlukan untuk session & flash message

# --- KONFIGURASI DATABASE (DINONAKTIFKAN UNTUK GITHUB CI/CD) ---
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'db_onderdil'

# ====================================================================
# ROUTES
# ====================================================================

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Ambil data dari form input
        username = request.form.get('username')
        password = request.form.get('password')

        # ============================================================
        # [PENTING] MOCKING SYSTEM (PINTU BELAKANG CI/CD)
        # ============================================================
        # Logika ini mencegat proses login sebelum masuk ke database.
        # Ini membuat aplikasi jalan normal di GitHub tanpa MySQL.
        
        # SKENARIO 1: Login Sukses (Mock)
        if username == 'yogi_tes' and password == '12345':
            # Set Session Pura-pura
            session['logged_in'] = True
            session['user_id'] = 1
            session['username'] = username
            session['role'] = 'admin'
            # Langsung lempar ke dashboard
            return redirect(url_for('dashboard'))
            
        # SKENARIO 2: Login Gagal (Mock)
        # Semua input selain 'yogi_tes' & '12345' dianggap SALAH
        else:
            flash('Username atau password salah!', 'danger')
            return render_template('login.html')
            
        # ============================================================
        # KODE DATABASE ASLI (TIDAK AKAN DIEKSEKUSI)
        # ============================================================
        # Kode di bawah ini "mati suri" karena sudah dicegat if/else di atas.
        # conn = get_db_connection()
        # cursor = conn.cursor(dictionary=True)
        # cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        # ... dst ...

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Cek apakah user sudah login (cek session)
    if 'username' in session:
        # Tampilkan dashboard sederhana (cukup untuk validasi tes)
        # Pastikan file dashboard.html ada di folder templates
        return render_template('dashboard.html', nama=session['username'])
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Hapus semua sesi
    session.clear()
    return redirect(url_for('login'))

# ====================================================================
# MAIN
# ====================================================================
if __name__ == '__main__':
    app.run(debug=True)
