# 🤖 AI Auto Tunneler - Enhanced

**Advanced Termux Free Internet with AI Auto Detection**

*Developed by: Mulky Malikul Dhaher*

---

## 🌟 **Overview**

AI Auto Tunneler Enhanced adalah sistem tunneling otomatis yang menggunakan kecerdasan buatan untuk mendeteksi dan mengkonfigurasi koneksi internet gratis melalui SNI (Server Name Indication) dan SSH tunneling. Sistem ini dirancang khusus untuk pengguna Android Termux dengan antarmuka web yang komprehensif.

## ✨ **Key Features**

### 🤖 **Auto Configuration**
- **Intelligent Environment Detection** - Deteksi otomatis platform dan kemampuan sistem
- **Network Analysis** - Analisis kecepatan dan kualitas koneksi
- **Operator Detection** - Deteksi otomatis operator Indonesia (Telkomsel, Indosat, XL, Smartfren, Tri)
- **Optimal Settings Generation** - Konfigurasi optimal berdasarkan device dan network

### 🌐 **Web Interface**
- **Modern Dashboard** - Antarmuka web responsif dengan 6 tab utama
- **Real-time Monitoring** - Charts dan metrics live performance
- **Tunnel Management** - Kontrol penuh terhadap koneksi tunnel
- **Advanced Scanner** - Scanning SNI domains dan SSH servers
- **Settings Panel** - Konfigurasi performance dan notifikasi

### 🔍 **Smart Scanning**
- **Multi-source SNI Discovery** - Facebook, WhatsApp, Google, CloudFlare CDNs
- **SSH Server Detection** - FastSSH, SSH Ocean, TCP VPN, SSH Kit
- **Bypass Testing** - Testing otomatis kombinasi SNI+SSH
- **Success Rate Tracking** - Monitoring tingkat keberhasilan

### ⚡ **Performance**
- **Fast Scanning** - 3 domains dalam 6 detik
- **Concurrent Processing** - Multi-threading untuk scanning
- **Memory Optimization** - Resource management yang efisien
- **Background Tasks** - Async processing untuk responsivitas

## 🚀 **Quick Start**

### **Option 1: Automatic Installation**
```bash
curl -fsSL https://raw.githubusercontent.com/dhackerxyz/Tunnel_Free_Internet_Termux/main/setup.sh | bash
```

### **Option 2: Manual Installation**
```bash
# Clone repository
git clone https://github.com/dhackerxyz/Tunnel_Free_Internet_Termux.git
cd Tunnel_Free_Internet_Termux

# Install dependencies
pip install -r requirements.txt

# Run application
python3 main.py
```

### **Option 3: Docker Deployment**
```bash
cd docker
docker-compose up -d
```

## 📱 **Access Points**

- **Main UI**: http://localhost:8080
- **Enhanced Dashboard**: http://localhost:8080/dashboard
- **API Documentation**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## 🔧 **Usage Guide**

### **1. Auto Configuration**
1. Buka dashboard di http://localhost:8080/dashboard
2. Klik tombol "🤖 Auto Config" di top bar
3. Tunggu proses 7-step configuration selesai
4. Sistem akan mengoptimalkan settings secara otomatis

### **2. Manual Scanning**
1. Pilih tab "Scanner" di dashboard
2. Pilih scan type: SNI, SSH, atau Bypass
3. Set limit dan target operator
4. Klik "Start Scan" dan monitor progress
5. Review hasil di tab "Results"

### **3. Tunnel Management**
1. Pilih tab "Tunnels" di dashboard
2. Pilih SNI domain dan SSH server dari dropdown
3. Masukkan credentials SSH
4. Klik "Start Tunnel" untuk koneksi
5. Monitor status di tab "Monitor"

### **4. Quick Actions**
- **Quick SNI Scan** - Scan cepat 5 SNI domains
- **Quick SSH Scan** - Scan cepat 5 SSH servers  
- **Use Best Config** - Gunakan konfigurasi terbaik otomatis
- **Emergency Stop** - Stop semua tunnel sekaligus

## 📊 **System Requirements**

### **Minimum Requirements**
- **OS**: Android 7+ (Termux) atau Linux
- **RAM**: 512MB
- **Storage**: 100MB free space
- **Network**: Internet connection

### **Recommended Requirements**
- **OS**: Android 9+ (Termux) atau Ubuntu/Debian
- **RAM**: 1GB+
- **CPU**: 2+ cores
- **Storage**: 500MB free space
- **Network**: Stable internet connection

### **Dependencies**
```bash
# Python packages
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
beautifulsoup4==4.12.2
tinydb==4.8.0
requests==2.31.0

# System packages (Termux)
pkg install python openssh stunnel curl wget nmap

# System packages (Linux)
apt install python3-pip openssh-client stunnel4 curl wget nmap
```

## 🛠️ **API Documentation**

### **Core Endpoints**
- `GET /` - Main web interface
- `GET /dashboard` - Enhanced dashboard
- `GET /health` - System health check
- `GET /api/status` - Tunnel status
- `GET /api/results` - Scan results with statistics

### **Configuration**
- `POST /api/auto-config` - Run auto-configuration
- `GET /api/info` - Detailed system information

### **Scanning**
- `POST /api/scan` - Start scanning (SNI/SSH/Bypass)
- `GET /api/results` - Get scan results with filtering

### **Tunnel Management**
- `POST /api/tunnel/start` - Start tunnel connection
- `POST /api/tunnel/stop` - Stop tunnel connection
- `GET /api/tunnel/test` - Test tunnel connection

### **System**
- `GET /api/logs` - Get system logs
- `GET /docs` - Interactive API documentation

## 📈 **Performance Metrics**

### **Scanning Performance**
- **SNI Scan Speed**: 3 domains in 6 seconds
- **SSH Scan Speed**: 3 servers in 9 seconds
- **Success Rate**: 70-90% depending on network
- **Response Time**: <100ms for API calls

### **Resource Usage**
- **Memory**: ~50-100MB typical usage
- **CPU**: <20% on modern devices
- **Network**: ~1-5MB for scanning operations
- **Storage**: ~50MB for application + logs

## 🔒 **Security Features**

### **Privacy Protection**
- **No Data Collection** - Tidak ada pengumpulan data pribadi
- **Local Processing** - Semua processing dilakukan lokal
- **Secure Connections** - HTTPS/SSL untuk web interface
- **No External Dependencies** - Tidak ada koneksi ke server pihak ketiga

### **Connection Security**
- **Certificate Validation** - SSL certificate checking
- **Host Key Verification** - SSH host key validation
- **Timeout Protection** - Connection timeout untuk mencegah hanging
- **Error Handling** - Comprehensive error handling dan logging

## 🌍 **Operator Support**

### **Indonesian Mobile Operators**
- ✅ **Telkomsel** - Optimized SNI domains dan ports
- ✅ **Indosat Ooredoo** - Operator-specific configuration
- ✅ **XL Axiata** - Enhanced bypass techniques
- ✅ **Smartfren** - Specialized settings
- ✅ **3 Indonesia (Tri)** - Custom optimization
- ✅ **Other Operators** - Generic configuration fallback

### **International Support**
- 🌐 **Global** - Basic SNI dan SSH support
- 🌐 **Fallback Mode** - Generic configuration untuk operator lain

## 🐛 **Troubleshooting**

### **Common Issues**

**1. Application won't start**
```bash
# Check Python version
python3 --version

# Install missing dependencies
pip install -r requirements.txt

# Check port availability
netstat -an | grep 8080
```

**2. Scanning fails**
```bash
# Check internet connection
ping 8.8.8.8

# Check DNS resolution
nslookup google.com

# Check firewall settings
iptables -L
```

**3. Tunnel connection fails**
```bash
# Check SSH connectivity
ssh -o ConnectTimeout=5 user@server

# Check stunnel configuration
stunnel -version

# Check SOCKS proxy
curl --socks5 127.0.0.1:9092 https://httpbin.org/ip
```

### **Debug Mode**
```bash
# Enable debug logging
export DEBUG=1
python3 main.py

# View detailed logs
tail -f tunnel.log

# Check system status
curl http://localhost:8080/health
```

## 📁 **Project Structure**

```
AI Auto Tunneler/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── setup.sh               # Automatic installation script
├── autorun.sh             # Quick start script
├── CHANGELOG.md           # Version history
├── README.md              # This file
├── core/                  # Core modules
│   ├── auto_config.py     # Auto-configuration system
│   ├── sni_scraper.py     # SNI domain discovery
│   ├── ssh_scraper.py     # SSH server detection
│   ├── test_bypass.py     # Bypass testing
│   ├── checker.py         # Connection testing
│   └── inject_engine.sh   # Tunnel injection script
├── assets/                # Web interface files
│   ├── index.html         # Main web interface
│   ├── dashboard.html     # Enhanced dashboard
│   ├── style.css          # Main styling
│   ├── dashboard.css      # Dashboard styling
│   ├── script.js          # Main JavaScript
│   └── dashboard.js       # Dashboard JavaScript
└── docker/                # Docker deployment
    ├── Dockerfile         # Container configuration
    ├── docker-compose.yml # Multi-service setup
    └── prometheus.yml     # Monitoring configuration
```

## 🤝 **Contributing**

Kontribusi sangat diterima! Silakan:

1. **Fork** repository ini
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### **Development Guidelines**
- Follow PEP 8 untuk Python code style
- Gunakan type hints untuk semua functions
- Tambahkan docstrings untuk modules dan functions
- Test semua changes sebelum commit
- Update documentation sesuai perubahan

## 📄 **License**

Proyek ini dilisensikan di bawah **MIT License** - lihat file [LICENSE](LICENSE) untuk detail.

## 🙏 **Credits & Acknowledgments**

### **Developed by**
**Mulky Malikul Dhaher**

### **Core Technologies**
- **FastAPI** - Modern web framework untuk Python
- **BeautifulSoup** - Web scraping capabilities
- **Stunnel** - SSL tunneling solution
- **OpenSSH** - SSH client functionality
- **Chart.js** - Interactive charts dan visualizations

### **Special Thanks**
- **Termux Community** - Android terminal environment
- **Indonesian Android Community** - Testing dan feedback
- **Open Source Contributors** - Libraries dan tools yang digunakan

## 📞 **Support & Contact**

### **GitHub Repository**
https://github.com/dhackerxyz/Tunnel_Free_Internet_Termux

### **Issues & Bug Reports**
https://github.com/dhackerxyz/Tunnel_Free_Internet_Termux/issues

### **Documentation**
- **API Docs**: http://localhost:8080/docs
- **User Guide**: Lihat bagian Usage Guide di atas
- **Developer Guide**: Lihat bagian Contributing

---

**Made with ❤️ for the Indonesian Android Community**

*AI Auto Tunneler Enhanced v1.2.0*
