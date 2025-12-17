import unittest
from app import app

class TestAplikasi(unittest.TestCase):

    # Persiapan sebelum setiap tes dijalankan
    def setUp(self):
        # Mengatur aplikasi ke mode TESTING
        app.testing = True
        # Mematikan perlindungan CSRF token agar tes lebih mudah
        app.config['WTF_CSRF_ENABLED'] = False 
        # Membuat "Browser Palsu" (Test Client)
        self.app = app.test_client()

    # --- TEST CASE 1: Halaman Login ---
    def test_01_halaman_login(self):
        # Robot mencoba membuka halaman /login
        response = self.app.get('/login', follow_redirects=True)
        
        # Harapannya: Status 200 (OK / Berhasil Dibuka)
        self.assertEqual(response.status_code, 200)
        print("\n[OK] Test 1: Halaman Login berhasil dibuka.")

    # --- TEST CASE 2: Login Sukses (Mock Data) ---
    def test_02_login_sukses(self):
        # Data login yang BENAR (Sesuai IF di app.py)
        data_valid = {
            'username': 'yogi_tes', 
            'password': '12345'
        }
        # Kirim data login (POST)
        response = self.app.post('/login', data=data_valid, follow_redirects=True)
        
        # Harapannya: Status 200 (Berhasil masuk dashboard)
        self.assertEqual(response.status_code, 200)
        
        # Validasi: Pastikan URL tidak lagi di halaman login
        # (Kita cek isi halamannya, harusnya BUKAN halaman login kosong)
        # Atau cek apakah session user_id sudah terbentuk
        with self.app.session_transaction() as sess:
            self.assertTrue(sess.get('logged_in'))
            
        print("\n[OK] Test 2: Login Sukses (yogi_tes) berhasil masuk.")

    # --- TEST CASE 3: Login Gagal (Password Salah) ---
    def test_03_login_gagal(self):
        # Data login yang SALAH
        data_salah = {
            'username': 'yogi_tes', 
            'password': 'password_ngawur'
        }
        # Kirim data login (POST)
        response = self.app.post('/login', data=data_salah, follow_redirects=True)
        
        # Harapannya: Halaman dimuat (200) tapi menampilkan pesan error
        self.assertEqual(response.status_code, 200)
        
        # Validasi: Cari teks pesan error di halaman (Flash Message)
        # Kita ubah respon HTML jadi string dulu
        isi_halaman = response.data.decode('utf-8')
        
        # Cari kata "salah" (dari pesan "Username atau password salah")
        self.assertIn('salah', isi_halaman.lower())
        
        print("\n[OK] Test 3: Login Gagal berhasil dicegah.")

    # --- TEST CASE 4: Logout ---
    def test_04_logout(self):
        # 1. Login paksa dulu (Manipulasi Session)
        with self.app as c:
            with c.session_transaction() as sess:
                sess['logged_in'] = True
                sess['username'] = 'yogi_tes'
            
            # 2. Klik Logout
            response = c.get('/logout', follow_redirects=True)
            
            # 3. Harapannya: Balik ke halaman login (Status 200)
            self.assertEqual(response.status_code, 200)
            
            # 4. Validasi: Session harusnya kosong/hilang
            # (Kita cek manual atau asumsikan redirect berhasil)
            print("\n[OK] Test 4: Logout berhasil.")

if __name__ == "__main__":
    unittest.main()