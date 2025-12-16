import pytest
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- KONFIGURASI ---
BASE_URL = "http://127.0.0.1:5000"
SCREENSHOT_DIR = "screenshots_laporan"

# Buat folder screenshot otomatis jika belum ada
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)

class TestSistemLogin:
    
    def setup_method(self):
        """Persiapan sebelum setiap test case dijalankan."""
        chrome_options = Options()
        # Aktifkan mode headless sesuai permintaan tugas slide
        # Hapus tanda komentar (#) di bawah jika ingin browser berjalan tanpa UI (background)
        # chrome_options.add_argument("--headless") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless") # Pastikan baris ini TIDAK dikomentari (#)
        chrome_options.add_argument("--window-size=1366,768") # Ukuran layar standar laptop
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10) # Waktu tunggu standar
    
    def teardown_method(self):
        """Membersihkan browser setelah test case selesai."""
        self.driver.quit()

    def ambil_screenshot(self, nama_kasus):
        """Fungsi pembantu untuk dokumentasi hasil screenshot jika gagal."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        nama_file = f"{SCREENSHOT_DIR}/{nama_kasus}_{timestamp}.png"
        self.driver.save_screenshot(nama_file)
        print(f"\n[FOTO] Screenshot error tersimpan di: {nama_file}")

    def login_sebagai_user(self):
        """Helper untuk login cepat agar tidak mengulang kodingan."""
        driver = self.driver
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "username").send_keys("yogi_tes")
        driver.find_element(By.NAME, "password").send_keys("12345")
        driver.find_element(By.TAG_NAME, "button").click()
        # Tunggu sampai masuk dashboard
        WebDriverWait(driver, 5).until(EC.url_contains("/dashboard"))

    # ==========================================
    # 6 TEST CASE LENGKAP
    # ==========================================

    # 1. LOGIN VALID
    def test_01_login_valid(self):
        driver = self.driver
        print("\n[TEST 1] Menguji Login Valid...")
        try:
            driver.get(f"{BASE_URL}/login")
            driver.find_element(By.NAME, "username").send_keys("yogi_tes")
            driver.find_element(By.NAME, "password").send_keys("12345")
            driver.find_element(By.TAG_NAME, "button").click()
            
            WebDriverWait(driver, 5).until(EC.url_contains("/dashboard"))
            assert "/dashboard" in driver.current_url
        except Exception as e:
            self.ambil_screenshot("Error_Login_Valid")
            raise e

    # 2. LOGIN GAGAL (Password Salah)
    def test_02_login_gagal(self):
        driver = self.driver
        print("\n[TEST 2] Menguji Login Gagal...")
        try:
            driver.get(f"{BASE_URL}/login")
            driver.find_element(By.NAME, "username").send_keys("yogi_tes")
            driver.find_element(By.NAME, "password").send_keys("salah123")
            driver.find_element(By.TAG_NAME, "button").click()
            
            assert "/login" in driver.current_url
            error_msg = driver.find_element(By.CSS_SELECTOR, ".alert").text
            assert "Username atau password salah" in error_msg
        except Exception as e:
            self.ambil_screenshot("Error_Login_Gagal")
            raise e

    # 3. FIELD KOSONG
    def test_03_field_kosong(self):
        driver = self.driver
        print("\n[TEST 3] Menguji Field Kosong...")
        try:
            driver.get(f"{BASE_URL}/login")
            driver.find_element(By.TAG_NAME, "button").click()
            
            assert "/dashboard" not in driver.current_url
            driver.find_element(By.NAME, "username") 
        except Exception as e:
            self.ambil_screenshot("Error_Field_Kosong")
            raise e

    # 5. LOGOUT - BATAL (Test Tombol Abu-abu)
    def test_04_logout_batal(self):
        driver = self.driver
        print("\n[TEST 5] Menguji Logout -> Klik Batal (Modal HTML)...")
        try:
            self.login_sebagai_user()

            # 1. Klik menu Logout di sidebar
            # Mencari elemen yang punya tulisan 'Logout' atau 'Keluar'
            tombol_menu = driver.find_element(By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), 'Keluar')]")
            tombol_menu.click()

            # 2. Tunggu Modal Muncul & Klik tombol 'Batal'
            # Kita gunakan teks 'Batal' sesuai screenshot Anda
            tombol_batal = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Batal')]"))
            )
            tombol_batal.click()

            # 3. Validasi: Harus tetap di dashboard (URL tidak berubah)
            time.sleep(1) # Jeda sedikit untuk animasi tutup modal
            assert "/dashboard" in driver.current_url
            
        except Exception as e:
            self.ambil_screenshot("Error_Logout_Batal")
            raise e

    # 6. LOGOUT - JADI (Test Tombol Merah)
    # 6. LOGOUT - JADI (REVISI FINAL)
    def test_05_logout_jadi(self):
        driver = self.driver
        print("\n[TEST 6] Menguji Logout -> Klik Ya, Logout (Revisi)...")
        try:
            self.login_sebagai_user()

            # 1. Klik menu Logout di sidebar
            # Kita tunggu sampai menu benar-benar bisa diklik
            tombol_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Logout') or contains(text(), 'Keluar')]"))
            )
            tombol_menu.click()

            # 2. Tunggu Modal Muncul
            print("   -> Menunggu modal logout muncul...")
            # REVISI PENTING:
            # Menggunakan "//*[...]" agar bisa mendeteksi tag <a>, <button>, atau <div>
            # Waktu tunggu diperpanjang jadi 10 detik
            tombol_ya = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Ya, Logout')]"))
            )
            
            # 3. KLIK PAKSA (JavaScript Click)
            # Ini adalah solusi anti-gagal jika tombol tertutup animasi
            driver.execute_script("arguments[0].click();", tombol_ya)
            print("   -> Tombol 'Ya, Logout' berhasil diklik.")

            # 4. Validasi: Harus pindah ke halaman Login
            WebDriverWait(driver, 10).until(EC.url_contains("/login"))
            assert "/login" in driver.current_url
            print("   -> Sukses: User berhasil logout.")

        except Exception as e:
            self.ambil_screenshot("Error_Logout_Jadi_Revisi")
            print(f"   -> GAGAL: {str(e)}")
            raise e