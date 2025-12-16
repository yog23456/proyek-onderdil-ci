// Menunggu semua elemen HTML dimuat sebelum menjalankan script
document.addEventListener('DOMContentLoaded', function() {

    // --- LOGIKA UNTUK SIDEBAR BUKA-TUTUP ---
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const appLayout = document.getElementById('app-layout');
    if (sidebarToggle && appLayout) {
        sidebarToggle.addEventListener('click', function() {
            appLayout.classList.toggle('sidebar-hidden');
        });
    }

    // --- LOGIKA UNTUK MENU ACCORDION (INI YANG MEMPERBAIKI BUG ANDA) ---
    const jenisKendaraanMenu = document.getElementById('jenis-kendaraan-menu');
    if (jenisKendaraanMenu) {
        // Tambahkan event listener ke link utamanya (tag <a>)
        jenisKendaraanMenu.querySelector('a').addEventListener('click', function(e) {
            // Mencegah link pindah halaman
            e.preventDefault();
            // Toggle class 'open' pada elemen 'li' induknya
            jenisKendaraanMenu.classList.toggle('open');
        });
    }

    // --- LOGIKA UNTUK POP-UP LOGOUT ---
    const showLogoutBtn = document.getElementById('show-logout-modal');
    const cancelLogoutBtn = document.getElementById('cancel-logout-btn');
    const logoutModal = document.getElementById('logout-modal');
    if (showLogoutBtn) {
        showLogoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (logoutModal) logoutModal.classList.add('active');
        });
    }
    if (cancelLogoutBtn) {
        cancelLogoutBtn.addEventListener('click', function() {
            if (logoutModal) logoutModal.classList.remove('active');
        });
    }
    if (logoutModal) {
        logoutModal.addEventListener('click', function(e) {
            if (e.target === logoutModal) {
                logoutModal.classList.remove('active');
            }
        });
    }

    // --- LOGIKA UNTUK SHOW/HIDE PASSWORD ---
    const toggleButtons = document.querySelectorAll('.password-toggle');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const passwordInput = this.parentElement.querySelector('input');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.textContent = '🙈';
            } else {
                passwordInput.type = 'password';
                this.textContent = '👁️';
            }
        });
    });

    // --- LOGIKA UNTUK 3-LEVEL CHAINED DROPDOWN (DI FORM) ---
    const selectJenis = document.getElementById('select-jenis');
    const selectKendaraan = document.getElementById('select-kendaraan');
    const selectSistem = document.getElementById('select-sistem');

    // Pastikan kita berada di halaman 'tambah_onderdil'
    if (selectJenis && selectKendaraan && selectSistem) {
        
        // 1. Saat dropdown JENIS berubah
        selectJenis.addEventListener('change', function() {
            const idJenis = this.value;
            selectKendaraan.disabled = true;
            selectKendaraan.innerHTML = '<option value="">-- Memuat Kendaraan... --</option>';
            selectSistem.disabled = true;
            selectSistem.innerHTML = '<option value="">-- Pilih Kendaraan Dulu --</option>';
            if (!idJenis) return;

            // Panggil API #1 untuk mengambil data KENDARAAN
            fetch(`/api/get_kendaraan/${idJenis}`)
                .then(response => response.json())
                .then(data => {
                    selectKendaraan.disabled = false;
                    selectKendaraan.innerHTML = '<option value="" disabled selected>-- Pilih Kendaraan --</option>';
                    data.forEach(kendaraan => {
                        const option = document.createElement('option');
                        option.value = kendaraan.id_kendaraan;
                        option.textContent = kendaraan.nama_kendaraan;
                        selectKendaraan.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching kendaraan:', error);
                    selectKendaraan.innerHTML = '<option value="">-- Gagal memuat --</option>';
                });
        });

        // 2. Saat dropdown KENDARAAN berubah
        selectKendaraan.addEventListener('change', function() {
            const idKendaraan = this.value;
            selectSistem.disabled = true;
            selectSistem.innerHTML = '<option value="">-- Memuat Sistem... --</option>';
            if (!idKendaraan) return;

            // Panggil API #2 untuk mengambil data SISTEM
            fetch(`/api/get_sistem/${idKendaraan}`)
                .then(response => response.json())
                .then(data => {
                    selectSistem.disabled = false;
                    selectSistem.innerHTML = '<option value="" disabled selected>-- Pilih Sistem --</option>';
                    data.forEach(sistem => {
                        const option = document.createElement('option');
                        option.value = sistem.id_sistem;
                        option.textContent = sistem.nama_sistem;
                        selectSistem.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error fetching sistem:', error);
                    selectSistem.innerHTML = '<option value="">-- Gagal memuat --</option>';
                });
        });
    }

});
// --- AKHIR DARI 'DOMContentLoaded' ---


// --- FUNGSI GLOBAL (DI LUAR LISTENER) ---

function pilihKendaraan(element, id) {
    const wrapper = document.getElementById('kendaraan-wrapper');
    if (!wrapper) return;
    if (element.classList.contains('terpilih')) {
        element.classList.remove('terpilih');
        wrapper.classList.remove('selection-active');
    } else {
        document.querySelectorAll('.kendaraan-item').forEach(item => {
            item.classList.remove('terpilih');
        });
        element.classList.add('terpilih');
        wrapper.classList.add('selection-active');
    }
}

const onderdilWrapper = document.getElementById('onderdil-page-wrapper');
function tampilDetail(element) {
    if (!onderdilWrapper) return;
    onderdilWrapper.classList.add('detail-aktif');
    const nama = element.dataset.nama;
    const fungsi = element.dataset.fungsi;
    const kerusakan = element.dataset.kerusakan;
    const rekomendasi = element.dataset.rekomendasi;
    const gambar = element.dataset.gambar;
    document.getElementById('detail-nama').textContent = nama;
    document.getElementById('detail-fungsi').textContent = fungsi;
    document.getElementById('detail-kerusakan').textContent = kerusakan;
    document.getElementById('detail-rekomendasi').textContent = rekomendasi;
    document.getElementById('detail-gambar').src = gambar;
}

function tutupDetail() {
    if (onderdilWrapper) onderdilWrapper.classList.remove('detail-aktif');
}