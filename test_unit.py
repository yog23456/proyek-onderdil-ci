import pytest
from app import app


# --- FIXTURE ---
# Pengganti setUp() di unittest. Fixture ini otomatis "disuntik"
# ke setiap function test yang punya parameter bernama "client".
@pytest.fixture
def client():
    # Mengatur aplikasi ke mode TESTING
    app.testing = True
    # Mematikan perlindungan CSRF token agar tes lebih mudah
    app.config['WTF_CSRF_ENABLED'] = False
    # Membuat "Browser Palsu" (Test Client) dan kirim ke function test
    with app.test_client() as test_client:
        yield test_client


# --- TEST CASE 1: Halaman Login ---
def test_01_halaman_login(client):
    # Robot mencoba membuka halaman /login
    response = client.get('/login', follow_redirects=True)

    # Harapannya: Status 200 (OK / Berhasil Dibuka)
    assert response.status_code == 200
    print("\n[OK] Test 1: Halaman Login berhasil dibuka.")


# --- TEST CASE 2: Login Sukses (Mock Data) ---
def test_02_login_sukses(client):
    # Data login yang BENAR (Sesuai IF di app.py)
    data_valid = {
        'username': 'yogi_tes',
        'password': '12345'
    }
    # Kirim data login (POST)
    response = client.post('/login', data=data_valid, follow_redirects=True)

    # Harapannya: Status 200 (Berhasil masuk dashboard)
    assert response.status_code == 200

    # Validasi: Pastikan session user_id sudah terbentuk
    with client.session_transaction() as sess:
        assert sess.get('logged_in') is True

    print("\n[OK] Test 2: Login Sukses (yogi_tes) berhasil masuk.")


# --- TEST CASE 3: Login Gagal (Password Salah) ---
def test_03_login_gagal(client):
    # Data login yang SALAH
    data_salah = {
        'username': 'yogi_tes',
        'password': 'password_ngawur'
    }
    # Kirim data login (POST)
    response = client.post('/login', data=data_salah, follow_redirects=True)

    # Harapannya: Halaman dimuat (200) tapi menampilkan pesan error
    assert response.status_code == 200

    # Validasi: Cari teks pesan error di halaman (Flash Message)
    isi_halaman = response.data.decode('utf-8')

    # Cari kata "salah" (dari pesan "Username atau password salah")
    assert 'salah' in isi_halaman.lower()

    print("\n[OK] Test 3: Login Gagal berhasil dicegah.")


# --- TEST CASE 4: Logout ---
def test_04_logout(client):
    # 1. Login paksa dulu (Manipulasi Session)
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['username'] = 'yogi_tes'

    # 2. Klik Logout
    response = client.get('/logout', follow_redirects=True)

    # 3. Harapannya: Balik ke halaman login (Status 200)
    assert response.status_code == 200

    # 4. Validasi: Session harusnya kosong/hilang setelah logout
    with client.session_transaction() as sess:
        assert sess.get('logged_in') is None

    print("\n[OK] Test 4: Logout berhasil.")
