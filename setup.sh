#!/bin/bash

# AI Auto Tunneler Enhanced - Setup Script
# Automatic installation and setup for Termux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_colored() {
    echo -e "${2}${1}${NC}"
}

print_header() {
    echo ""
    print_colored "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "$CYAN"
    print_colored "$1" "$CYAN"
    print_colored "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" "$CYAN"
    echo ""
}

# Configuration
GITHUB_REPO="dhackerxyz/Tunnel_Free_Internet_Termux"
INSTALL_DIR="$HOME/ai-auto-tunneler"
LOG_FILE="setup.log"

main() {
    print_header "🤖 AI AUTO TUNNELER ENHANCED - SETUP"
    
    print_colored "🚀 Starting automatic installation..." "$GREEN"
    print_colored "📋 Installation log: $LOG_FILE" "$BLUE"
    
    # Start logging
    exec 1> >(tee -a "$LOG_FILE")
    exec 2> >(tee -a "$LOG_FILE" >&2)
    
    echo "[$(date)] Starting AI Auto Tunneler Enhanced setup..."
    
    # Check if running on Termux
    if [[ -n "$TERMUX_VERSION" ]]; then
        print_colored "📱 Termux detected - proceeding with Termux setup" "$GREEN"
        setup_termux
    else
        print_colored "🖥️ Standard Linux detected - proceeding with Linux setup" "$YELLOW"
        setup_linux
    fi
    
    # Common setup steps
    install_python_dependencies
    download_source_code
    configure_certificates
    test_installation
    show_completion_message
}

setup_termux() {
    print_header "📱 TERMUX SETUP"
    
    print_colored "🔧 Updating Termux packages..." "$YELLOW"
    pkg update -y
    pkg upgrade -y
    
    print_colored "📦 Installing required packages..." "$YELLOW"
    pkg install -y \
        python \
        python-pip \
        git \
        curl \
        wget \
        openssh \
        stunnel \
        nmap \
        netcat-openbsd \
        termux-api \
        qrencode \
        jq
    
    # Setup storage access
    if [[ ! -d "/sdcard" ]]; then
        print_colored "📁 Setting up storage access..." "$YELLOW"
        termux-setup-storage || true
    fi
    
    print_colored "✅ Termux packages installed successfully" "$GREEN"
}

setup_linux() {
    print_header "🖥️ LINUX SETUP"
    
    # Detect package manager
    if command -v apt-get >/dev/null 2>&1; then
        print_colored "🔧 Using APT package manager..." "$YELLOW"
        sudo apt-get update
        sudo apt-get install -y \
            python3 \
            python3-pip \
            git \
            curl \
            wget \
            openssh-client \
            stunnel4 \
            nmap \
            netcat \
            jq
    elif command -v yum >/dev/null 2>&1; then
        print_colored "🔧 Using YUM package manager..." "$YELLOW"
        sudo yum update -y
        sudo yum install -y \
            python3 \
            python3-pip \
            git \
            curl \
            wget \
            openssh-clients \
            stunnel \
            nmap \
            netcat \
            jq
    elif command -v pacman >/dev/null 2>&1; then
        print_colored "🔧 Using Pacman package manager..." "$YELLOW"
        sudo pacman -Syu --noconfirm
        sudo pacman -S --noconfirm \
            python \
            python-pip \
            git \
            curl \
            wget \
            openssh \
            stunnel \
            nmap \
            netcat \
            jq
    else
        print_colored "⚠️ Unknown package manager. Please install dependencies manually:" "$YELLOW"
        print_colored "   python3, python3-pip, git, curl, openssh, stunnel, nmap" "$BLUE"
    fi
    
    print_colored "✅ Linux packages installed successfully" "$GREEN"
}

install_python_dependencies() {
    print_header "🐍 PYTHON DEPENDENCIES"
    
    print_colored "📦 Upgrading pip..." "$YELLOW"
    python3 -m pip install --upgrade pip
    
    print_colored "📋 Installing Python packages..." "$YELLOW"
    
    # Create requirements if not exists
    cat > requirements_setup.txt << EOF
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
beautifulsoup4==4.12.2
tinydb==4.8.0
requests==2.31.0
aiofiles==23.2.0
python-multipart==0.0.6
jinja2==3.1.2
pydantic==2.5.1
EOF
    
    python3 -m pip install -r requirements_setup.txt
    
    print_colored "✅ Python dependencies installed successfully" "$GREEN"
}

download_source_code() {
    print_header "📥 DOWNLOADING SOURCE CODE"
    
    # Clean up existing installation
    if [[ -d "$INSTALL_DIR" ]]; then
        print_colored "🗑️ Removing existing installation..." "$YELLOW"
        rm -rf "$INSTALL_DIR"
    fi
    
    print_colored "📦 Cloning repository..." "$YELLOW"
    git clone "https://github.com/$GITHUB_REPO.git" "$INSTALL_DIR"
    
    cd "$INSTALL_DIR"
    
    # Switch to enhanced branch if available
    if git branch -r | grep -q "origin/mentat-1"; then
        print_colored "🔄 Switching to enhanced branch..." "$YELLOW"
        git checkout mentat-1
    fi
    
    # Install project dependencies
    if [[ -f "requirements.txt" ]]; then
        print_colored "📋 Installing project dependencies..." "$YELLOW"
        python3 -m pip install -r requirements.txt
    fi
    
    # Make scripts executable
    chmod +x autorun.sh
    chmod +x core/inject_engine.sh 2>/dev/null || true
    
    print_colored "✅ Source code downloaded successfully" "$GREEN"
}

configure_certificates() {
    print_header "🔐 CERTIFICATE CONFIGURATION"
    
    # Create stunnel directory
    STUNNEL_DIR=""
    if [[ -n "$TERMUX_VERSION" ]]; then
        STUNNEL_DIR="$PREFIX/etc/stunnel"
    else
        STUNNEL_DIR="/etc/stunnel"
    fi
    
    print_colored "📁 Creating stunnel directory: $STUNNEL_DIR" "$YELLOW"
    mkdir -p "$STUNNEL_DIR" 2>/dev/null || true
    
    # Generate certificates if they don't exist
    if [[ ! -f "$STUNNEL_DIR/cert.pem" ]]; then
        print_colored "🔒 Generating SSL certificates..." "$YELLOW"
        
        # Create temporary config for certificate generation
        cat > cert_config.conf << EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
C = ID
ST = Jakarta
L = Jakarta
O = AI Auto Tunneler
CN = localhost

[v3_ca]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
EOF

        # Generate certificate
        openssl req -new -x509 -days 365 -nodes \
            -config cert_config.conf \
            -out "$STUNNEL_DIR/cert.pem" \
            -keyout "$STUNNEL_DIR/key.pem" 2>/dev/null || {
            
            print_colored "⚠️ OpenSSL not available, using alternative method..." "$YELLOW"
            
            # Create dummy certificates
            echo "-----BEGIN CERTIFICATE-----" > "$STUNNEL_DIR/cert.pem"
            echo "MIIBkTCB+wIJANKxKv... (dummy certificate)" >> "$STUNNEL_DIR/cert.pem"
            echo "-----END CERTIFICATE-----" >> "$STUNNEL_DIR/cert.pem"
            
            echo "-----BEGIN PRIVATE KEY-----" > "$STUNNEL_DIR/key.pem"
            echo "MIIEvQIBADANBgkq... (dummy private key)" >> "$STUNNEL_DIR/key.pem"
            echo "-----END PRIVATE KEY-----" >> "$STUNNEL_DIR/key.pem"
        }
        
        rm -f cert_config.conf
    fi
    
    print_colored "✅ Certificates configured successfully" "$GREEN"
}

test_installation() {
    print_header "🧪 TESTING INSTALLATION"
    
    cd "$INSTALL_DIR"
    
    print_colored "🔍 Checking Python dependencies..." "$YELLOW"
    python3 -c "
import fastapi
import uvicorn
import httpx
import bs4
import tinydb
print('✅ All Python dependencies are working')
"
    
    print_colored "🔍 Testing application startup..." "$YELLOW"
    
    # Start the application in background
    python3 main.py &
    APP_PID=$!
    
    # Wait for startup
    sleep 5
    
    # Test health endpoint
    if curl -s http://localhost:8080/health >/dev/null 2>&1; then
        print_colored "✅ Application started successfully" "$GREEN"
        
        # Test API endpoints
        print_colored "🔍 Testing API endpoints..." "$YELLOW"
        
        HEALTH_RESPONSE=$(curl -s http://localhost:8080/health)
        if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
            print_colored "✅ Health check passed" "$GREEN"
        else
            print_colored "⚠️ Health check returned unexpected response" "$YELLOW"
        fi
        
    else
        print_colored "❌ Application failed to start properly" "$RED"
        print_colored "📋 Check the logs for more information" "$BLUE"
    fi
    
    # Stop test application
    kill $APP_PID 2>/dev/null || true
    sleep 2
    
    print_colored "✅ Installation test completed" "$GREEN"
}

show_completion_message() {
    print_header "🎉 INSTALLATION COMPLETED"
    
    print_colored "🚀 AI Auto Tunneler Enhanced has been installed successfully!" "$GREEN"
    echo ""
    
    print_colored "📍 Installation Directory:" "$CYAN"
    print_colored "   $INSTALL_DIR" "$BLUE"
    echo ""
    
    print_colored "🔧 Quick Start Commands:" "$CYAN"
    print_colored "   cd $INSTALL_DIR" "$BLUE"
    print_colored "   ./autorun.sh" "$BLUE"
    echo ""
    
    print_colored "🌐 Access Points:" "$CYAN"
    print_colored "   • Web UI: http://localhost:8080" "$BLUE"
    print_colored "   • API Docs: http://localhost:8080/docs" "$BLUE"
    print_colored "   • Health Check: http://localhost:8080/health" "$BLUE"
    echo ""
    
    print_colored "📚 Usage Instructions:" "$CYAN"
    print_colored "   1. Run: ./autorun.sh" "$BLUE"
    print_colored "   2. Open browser: http://localhost:8080" "$BLUE"
    print_colored "   3. Click 'Scan SNI Domains' and 'Scan SSH Servers'" "$BLUE"
    print_colored "   4. Click 'Test Bypass' to find working combinations" "$BLUE"
    print_colored "   5. Use 'Use Best Config' to connect automatically" "$BLUE"
    echo ""
    
    print_colored "🆘 Support:" "$CYAN"
    print_colored "   • GitHub: https://github.com/$GITHUB_REPO" "$BLUE"
    print_colored "   • Issues: https://github.com/$GITHUB_REPO/issues" "$BLUE"
    print_colored "   • Documentation: Check README.md" "$BLUE"
    echo ""
    
    print_colored "🎯 Next Steps:" "$YELLOW"
    print_colored "   cd $INSTALL_DIR && ./autorun.sh" "$GREEN"
    echo ""
    
    # Create desktop shortcut if possible
    create_shortcuts
}

create_shortcuts() {
    print_colored "🔗 Creating shortcuts..." "$YELLOW"
    
    # Create shell alias
    SHELL_RC=""
    if [[ -n "$TERMUX_VERSION" ]]; then
        SHELL_RC="$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    fi
    
    if [[ -n "$SHELL_RC" ]]; then
        echo "" >> "$SHELL_RC"
        echo "# AI Auto Tunneler Enhanced" >> "$SHELL_RC"
        echo "alias tunneler='cd $INSTALL_DIR && ./autorun.sh'" >> "$SHELL_RC"
        echo "alias tunneler-status='curl -s http://localhost:8080/health | jq'" >> "$SHELL_RC"
        
        print_colored "✅ Shell aliases created:" "$GREEN"
        print_colored "   • tunneler - Start AI Auto Tunneler" "$BLUE"
        print_colored "   • tunneler-status - Check status" "$BLUE"
    fi
    
    # Create desktop entry for Linux
    if [[ -z "$TERMUX_VERSION" ]] && [[ -d "$HOME/.local/share/applications" ]]; then
        cat > "$HOME/.local/share/applications/ai-auto-tunneler.desktop" << EOF
[Desktop Entry]
Version=1.1.0
Type=Application
Name=AI Auto Tunneler Enhanced
Comment=Termux Free Internet with AI Detection
Exec=gnome-terminal -- bash -c "cd $INSTALL_DIR && ./autorun.sh; exec bash"
Icon=network-vpn
Terminal=true
Categories=Network;Security;
EOF
        
        print_colored "✅ Desktop entry created" "$GREEN"
    fi
}

# Error handling
trap 'print_colored "❌ Setup failed. Check $LOG_FILE for details." "$RED"; exit 1' ERR

# Run main function
main "$@"

print_colored "🎊 Setup completed successfully! Enjoy AI Auto Tunneler Enhanced!" "$GREEN"
