# 🤖 AI Auto Tunneler

**Termux Free Internet with AI Detection** - Sistem AI yang secara otomatis mencari dan menguji kombinasi SNI domain + SSH server untuk bypass internet gratis di Termux.

## ✨ Fitur Utama

### 🧠 ALL-IN-ONE BYPASS ENGINE
- ✅ **Auto SNI Scraper** - Otomatis cari SNI domain aktif
- ✅ **Auto SSH Scraper** - Otomatis cari SSH server gratis dari berbagai sumber
- ✅ **Bypass Tester** - Tes celah operator secara otomatis
- ✅ **Config Persistence** - Simpan dan load kombinasi yang berhasil
- ✅ **Web UI** - Interface user-friendly dengan real-time monitoring
- ✅ **SOCKS Proxy** - Proxy SOCKS5 otomatis untuk aplikasi

### 🌐 Web Interface
- **Real-time Status** - Monitor status koneksi secara langsung
- **Live Logs** - Log aktivitas real-time
- **Auto Discovery** - Scan otomatis domain dan server
- **One-Click Connect** - Gunakan konfigurasi terbaik dengan satu klik
- **Mobile Friendly** - Optimized untuk HP Android

## 🚀 Quick Start

### 1. Persiapan Termux
```bash
# Update Termux
pkg update && pkg upgrade

# Install dependencies
pkg install python openssh curl stunnel tsu nmap git

# Install sshpass (optional tapi recommended)
pkg install sshpass

# Setup storage access
termux-setup-storage
```

### 2. Download & Install
```bash
# Clone repository
git clone https://github.com/dhackerxyz/Tunnel_Free_Internet_Termux.git
cd Tunnel_Free_Internet_Termux

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Jalankan AI Auto Tunneler
```bash
# Method 1: Auto run script (recommended)
chmod +x autorun.sh
./autorun.sh

# Method 2: Manual start
python main.py
```

### 4. Akses Web UI
- **Local**: http://localhost:8080
- **Network**: http://[IP_ANDA]:8080 (untuk akses dari HP lain)

## 📱 Cara Penggunaan

### 🔍 Auto Discovery
1. **Scan SNI Domains** - Klik untuk mencari domain SNI yang bisa bypass
2. **Scan SSH Servers** - Klik untuk mencari SSH server gratis aktif
3. **Test Bypass** - Otomatis tes kombinasi SNI + SSH yang berhasil

### ⚡ Quick Connect
1. **Use Best Config** - Gunakan kombinasi terbaik yang pernah berhasil
2. **Start Tunnel** - Mulai koneksi dengan config yang dipilih
3. **Test Connection** - Tes apakah koneksi berjalan dengan baik

### 🛠️ Manual Configuration
Jika ingin setting manual:
- **SNI Domain**: Masukkan domain SNI (contoh: free.facebook.com)
- **SSH Server**: Masukkan detail SSH server
- **Credentials**: Username dan password SSH

## 🔧 Konfigurasi Browser

Setelah tunnel aktif, setting browser untuk menggunakan SOCKS proxy:

### Chrome/Firefox Mobile
1. Install app **ProxyDroid** atau **Orbot**
2. Setting SOCKS5 proxy: `127.0.0.1:9092`
3. Enable proxy dan browsing gratis!

### Firefox Desktop
1. Settings → Network Settings → Manual proxy configuration
2. SOCKS Host: `127.0.0.1` Port: `9092`
3. SOCKS v5: ✅

## 📂 Struktur Project

```
auto_tunnel_ai/
├── assets/                 # Web UI files
│   ├── index.html         # Main UI
│   ├── style.css          # Styling
│   └── script.js          # Frontend logic
├── core/                  # Core modules
│   ├── sni_scraper.py     # SNI domain scraper
│   ├── ssh_scraper.py     # SSH server scraper
│   ├── test_bypass.py     # Bypass tester
│   ├── inject_engine.sh   # Tunnel injector
│   └── checker.py         # Connection checker
├── config.json            # Working combinations
├── db.json                # Scan results history
├── main.py                # FastAPI backend
├── autorun.sh             # Auto startup script
└── requirements.txt       # Python dependencies
```

## 🎯 Target SNI Domains

AI akan otomatis scan domain-domain ini dan banyak lagi:

### Facebook/Meta CDNs
- `free.facebook.com`
- `www.facebook.com`
- `connect.facebook.net`
- `static.xx.fbcdn.net`

### WhatsApp CDNs
- `cdn.whatsapp.net`
- `web.whatsapp.com`
- `media.wa.me`

### Google CDNs
- `ssl.gstatic.com`
- `fonts.googleapis.com`
- `ajax.googleapis.com`

### CloudFlare & Others
- `cdnjs.cloudflare.com`
- `cdn.jsdelivr.net`
- `unpkg.com`

## 🔐 SSH Sources

AI akan otomatis scrape dari sumber-sumber ini:

- **FastSSH** - fastssh.com
- **SSHKit** - sshkit.com  
- **TCPVPN** - tcpvpn.com
- **SpeedSSH** - speedssh.com
- **VPNJantit** - vpnjantit.com

## 🚀 Advanced Usage

### Auto Scan Mode
```bash
# Start dengan auto scan
./autorun.sh --auto-scan
```

### Custom Port
```bash
# Gunakan port lain
./autorun.sh --port 8090
```

### Background Mode
```bash
# Jalankan di background
nohup python main.py &
```

### Monitor Logs
```bash
# Real-time logs
tail -f tunnel.log
```

## 🔧 API Endpoints

AI Auto Tunneler menyediakan REST API:

- `GET /api/status` - Status tunnel
- `POST /api/scan` - Start scanning
- `GET /api/results` - Hasil scan
- `POST /api/tunnel/start` - Start tunnel
- `POST /api/tunnel/stop` - Stop tunnel
- `GET /api/tunnel/test` - Test connection

## 🆘 Troubleshooting

### Tunnel Gagal Start
```bash
# Check processes
ps aux | grep -E "(stunnel|ssh)"

# Kill stuck processes
pkill -f stunnel
pkill -f "ssh.*-D"

# Restart
./autorun.sh
```

### Port Conflict
```bash
# Cek port yang dipakai
netstat -tlnp | grep :8080

# Ganti port
./autorun.sh --port 8090
```

### Permission Denied
```bash
# Fix permissions
chmod +x autorun.sh
chmod +x core/inject_engine.sh
```

## 🎯 Tips & Tricks

### 🔥 Pro Tips
1. **Coba berbagai operator** - Hasil bisa beda per provider
2. **Test di waktu off-peak** - Malam hari biasanya lebih stabil
3. **Save working configs** - AI akan otomatis save yang berhasil
4. **Monitor connection** - Use built-in connection tester
5. **Update reguler** - Sumber SSH berubah-ubah

### 🎯 Operator Specific
- **Telkomsel**: Coba `free.facebook.com` + SSH port 443
- **Indosat**: `ssl.gstatic.com` biasanya work
- **XL**: CloudFlare CDNs sering berhasil
- **Axis**: Discord CDNs kadang work
- **3**: Google fonts APIs bagus
- **Smartfren**: Wikipedia/educational domains

## 🤝 Contributing

Mau kontribusi? Awesome! 

1. Fork repository ini
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## ⚖️ Legal Disclaimer

Tool ini dibuat untuk:
- ✅ **Educational purposes** - Belajar networking dan security
- ✅ **Testing purposes** - Test network configurations
- ✅ **Research purposes** - Research network protocols

**TIDAK untuk**:
- ❌ Melanggar Terms of Service provider
- ❌ Aktivitas ilegal atau merugikan
- ❌ Commercial use tanpa izin

**Gunakan dengan bijak dan bertanggung jawab!**

## 🙏 Credits

- **FastAPI** - Modern web framework
- **BeautifulSoup** - Web scraping
- **Stunnel** - SSL tunnel
- **OpenSSH** - SSH client
- **Termux** - Android terminal emulator

## 📜 License

MIT License - Lihat file [LICENSE](LICENSE) untuk detail.

---

<div align="center">

**🔥 Made with ❤️ for Indonesian Android users**

**⭐ Star repo ini jika bermanfaat!**

</div>
