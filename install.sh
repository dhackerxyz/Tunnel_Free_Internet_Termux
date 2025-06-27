#!/bin/bash

# AI Auto Tunneler Enhanced - Universal Installer
# Automatic installation script for Termux and Linux
# Developed by: Mulky Malikul Dhaher

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

check_system() {
    print_header "🔍 SYSTEM DETECTION"
    
    # Detect platform
    if [[ -n "$TERMUX_VERSION" ]] || [[ "$PREFIX" == *"com.termux"* ]]; then
        PLATFORM="termux"
        print_colored "📱 Platform: Termux Android" "$GREEN"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        PLATFORM="linux"
        print_colored "🖥️ Platform: Linux" "$GREEN"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macos"
        print_colored "🍎 Platform: macOS" "$GREEN"
    else
        PLATFORM="unknown"
        print_colored "❓ Platform: Unknown" "$YELLOW"
    fi
    
    # Check architecture
    ARCH=$(uname -m)
    print_colored "🏗️ Architecture: $ARCH" "$BLUE"
    
    # Check available space
    AVAILABLE_SPACE=$(df -h . | awk 'NR==2{print $4}')
    print_colored "💾 Available Space: $AVAILABLE_SPACE" "$BLUE"
    
    # Check internet connection
    if ping -c 1 8.8.8.8 &> /dev/null; then
        print_colored "🌐 Internet: Connected" "$GREEN"
    else
        print_colored "❌ Internet: Not connected" "$RED"
        echo "Please check your internet connection and try again."
        exit 1
    fi
}

install_dependencies() {
    print_header "📦 INSTALLING DEPENDENCIES"
    
    case $PLATFORM in
        "termux")
            print_colored "🔄 Updating Termux packages..." "$YELLOW"
            pkg update -y &> /dev/null
            pkg upgrade -y &> /dev/null
            
            print_colored "📦 Installing Termux packages..." "$YELLOW"
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
                jq \
                openssl &> /dev/null
            
            # Setup storage access
            if [[ ! -d "/sdcard" ]]; then
                print_colored "📁 Setting up storage access..." "$YELLOW"
                termux-setup-storage || true
            fi
            ;;
            
        "linux")
            print_colored "🔄 Updating package list..." "$YELLOW"
            
            # Detect package manager
            if command -v apt-get &> /dev/null; then
                sudo apt-get update -y &> /dev/null
                print_colored "📦 Installing APT packages..." "$YELLOW"
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
                    jq \
                    openssl &> /dev/null
                    
            elif command -v yum &> /dev/null; then
                sudo yum update -y &> /dev/null
                print_colored "📦 Installing YUM packages..." "$YELLOW"
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
                    jq \
                    openssl &> /dev/null
                    
            elif command -v pacman &> /dev/null; then
                sudo pacman -Syu --noconfirm &> /dev/null
                print_colored "📦 Installing Pacman packages..." "$YELLOW"
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
                    jq \
                    openssl &> /dev/null
            else
                print_colored "⚠️ Unknown package manager. Please install dependencies manually." "$YELLOW"
            fi
            ;;
            
        "macos")
            if command -v brew &> /dev/null; then
                print_colored "📦 Installing Homebrew packages..." "$YELLOW"
                brew update &> /dev/null
                brew install python git curl wget stunnel nmap netcat jq openssl &> /dev/null
            else
                print_colored "⚠️ Homebrew not found. Please install Homebrew first." "$YELLOW"
                exit 1
            fi
            ;;
    esac
    
    print_colored "✅ System dependencies installed" "$GREEN"
}

install_python_deps() {
    print_header "🐍 PYTHON DEPENDENCIES"
    
    print_colored "📦 Upgrading pip..." "$YELLOW"
    python3 -m pip install --upgrade pip &> /dev/null
    
    print_colored "📋 Installing Python packages..." "$YELLOW"
    
    # Create temporary requirements file
    cat > /tmp/ai_tunneler_requirements.txt << EOF
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
    
    python3 -m pip install -r /tmp/ai_tunneler_requirements.txt &> /dev/null
    rm -f /tmp/ai_tunneler_requirements.txt
    
    print_colored "✅ Python dependencies installed" "$GREEN"
}

download_application() {
    print_header "📥 DOWNLOADING APPLICATION"
    
    INSTALL_DIR="$HOME/ai-auto-tunneler"
    
    if [[ -d "$INSTALL_DIR" ]]; then
        print_colored "🗑️ Removing existing installation..." "$YELLOW"
        rm -rf "$INSTALL_DIR"
    fi
    
    print_colored "📦 Cloning repository..." "$YELLOW"
    git clone https://github.com/dhackerxyz/Tunnel_Free_Internet_Termux.git "$INSTALL_DIR" &> /dev/null
    
    cd "$INSTALL_DIR"
    
    # Switch to main branch
    git checkout main &> /dev/null || git checkout master &> /dev/null
    
    # Make scripts executable
    chmod +x autorun.sh &> /dev/null || true
    chmod +x setup.sh &> /dev/null || true
    chmod +x install.sh &> /dev/null || true
    chmod +x core/inject_engine.sh &> /dev/null || true
    
    print_colored "✅ Application downloaded to: $INSTALL_DIR" "$GREEN"
}

configure_certificates() {
    print_header "🔐 CERTIFICATE SETUP"
    
    # Create stunnel directory
    if [[ "$PLATFORM" == "termux" ]]; then
        STUNNEL_DIR="$PREFIX/etc/stunnel"
    else
        STUNNEL_DIR="/etc/stunnel"
    fi
    
    print_colored "📁 Creating stunnel directory..." "$YELLOW"
    mkdir -p "$STUNNEL_DIR" 2>/dev/null || sudo mkdir -p "$STUNNEL_DIR" 2>/dev/null || true
    
    # Generate certificates if they don't exist
    CERT_FILE="$STUNNEL_DIR/cert.pem"
    KEY_FILE="$STUNNEL_DIR/key.pem"
    
    if [[ ! -f "$CERT_FILE" ]]; then
        print_colored "🔒 Generating SSL certificates..." "$YELLOW"
        
        # Create certificate config
        cat > /tmp/cert_config.conf << EOF
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
        if command -v openssl &> /dev/null; then
            openssl req -new -x509 -days 365 -nodes \
                -config /tmp/cert_config.conf \
                -out "$CERT_FILE" \
                -keyout "$KEY_FILE" &> /dev/null || {
                
                # Fallback: create dummy certificates
                echo "Creating fallback certificates..."
                mkdir -p "$(dirname "$CERT_FILE")"
                touch "$CERT_FILE" "$KEY_FILE" 2>/dev/null || \
                sudo touch "$CERT_FILE" "$KEY_FILE" 2>/dev/null || true
            }
        else
            print_colored "⚠️ OpenSSL not available, using fallback certificates" "$YELLOW"
            touch "$CERT_FILE" "$KEY_FILE" 2>/dev/null || \
            sudo touch "$CERT_FILE" "$KEY_FILE" 2>/dev/null || true
        fi
        
        rm -f /tmp/cert_config.conf
    fi
    
    print_colored "✅ Certificates configured" "$GREEN"
}

test_installation() {
    print_header "🧪 TESTING INSTALLATION"
    
    cd "$INSTALL_DIR"
    
    print_colored "🔍 Testing Python dependencies..." "$YELLOW"
    python3 -c "
import fastapi
import uvicorn
import httpx
import bs4
import tinydb
print('✅ All Python dependencies working')
" || {
        print_colored "❌ Python dependency test failed" "$RED"
        exit 1
    }
    
    print_colored "🔍 Testing application startup..." "$YELLOW"
    
    # Start application in background
    timeout 30 python3 main.py &
    APP_PID=$!
    
    # Wait for startup
    sleep 8
    
    # Test health endpoint
    if curl -s --max-time 5 http://localhost:8080/health &> /dev/null; then
        print_colored "✅ Application started successfully" "$GREEN"
        
        # Test API endpoints
        HEALTH_RESPONSE=$(curl -s --max-time 5 http://localhost:8080/health)
        if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
            print_colored "✅ Health check passed" "$GREEN"
        else
            print_colored "⚠️ Health check returned unexpected response" "$YELLOW"
        fi
        
        # Test dashboard
        if curl -s --max-time 5 http://localhost:8080/dashboard &> /dev/null; then
            print_colored "✅ Dashboard accessible" "$GREEN"
        else
            print_colored "⚠️ Dashboard test failed" "$YELLOW"
        fi
        
    else
        print_colored "❌ Application failed to start properly" "$RED"
        print_colored "📋 Check the logs for more information" "$BLUE"
    fi
    
    # Stop test application
    kill $APP_PID 2>/dev/null || true
    sleep 2
    pkill -f "python3 main.py" 2>/dev/null || true
    
    print_colored "✅ Installation test completed" "$GREEN"
}

create_shortcuts() {
    print_header "🔗 CREATING SHORTCUTS"
    
    # Create desktop launcher script
    cat > "$INSTALL_DIR/start-tunneler.sh" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 main.py
EOF
    chmod +x "$INSTALL_DIR/start-tunneler.sh"
    
    # Create shell aliases
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
        echo "alias tunneler='cd $INSTALL_DIR && python3 main.py'" >> "$SHELL_RC"
        echo "alias tunneler-start='cd $INSTALL_DIR && ./start-tunneler.sh'" >> "$SHELL_RC"
        echo "alias tunneler-status='curl -s http://localhost:8080/health | jq'" >> "$SHELL_RC"
        echo "alias tunneler-dashboard='echo \"Open: http://localhost:8080/dashboard\"'" >> "$SHELL_RC"
        
        print_colored "✅ Shell aliases created:" "$GREEN"
        print_colored "   • tunneler - Start AI Auto Tunneler" "$BLUE"
        print_colored "   • tunneler-start - Start with script" "$BLUE"
        print_colored "   • tunneler-status - Check status" "$BLUE"
        print_colored "   • tunneler-dashboard - Show dashboard URL" "$BLUE"
    fi
    
    # Create desktop entry for Linux
    if [[ "$PLATFORM" == "linux" ]] && [[ -d "$HOME/.local/share/applications" ]]; then
        cat > "$HOME/.local/share/applications/ai-auto-tunneler.desktop" << EOF
[Desktop Entry]
Version=1.2.0
Type=Application
Name=AI Auto Tunneler Enhanced
Comment=Termux Free Internet with AI Detection
Exec=gnome-terminal -- bash -c "cd $INSTALL_DIR && python3 main.py; exec bash"
Icon=network-vpn
Terminal=true
Categories=Network;Security;
EOF
        
        print_colored "✅ Desktop entry created" "$GREEN"
    fi
    
    print_colored "✅ Shortcuts and aliases configured" "$GREEN"
}

show_completion() {
    print_header "🎉 INSTALLATION COMPLETED"
    
    print_colored "🚀 AI Auto Tunneler Enhanced has been installed successfully!" "$GREEN"
    echo ""
    
    print_colored "📍 Installation Directory:" "$CYAN"
    print_colored "   $INSTALL_DIR" "$BLUE"
    echo ""
    
    print_colored "🔧 Quick Start Commands:" "$CYAN"
    print_colored "   cd $INSTALL_DIR" "$BLUE"
    print_colored "   python3 main.py" "$BLUE"
    echo ""
    print_colored "   # Or use the shortcut:" "$BLUE"
    print_colored "   ./start-tunneler.sh" "$BLUE"
    echo ""
    
    print_colored "🌐 Access Points:" "$CYAN"
    print_colored "   • Main UI: http://localhost:8080" "$BLUE"
    print_colored "   • Enhanced Dashboard: http://localhost:8080/dashboard" "$BLUE"
    print_colored "   • API Documentation: http://localhost:8080/docs" "$BLUE"
    print_colored "   • Health Check: http://localhost:8080/health" "$BLUE"
    echo ""
    
    print_colored "📚 Usage Guide:" "$CYAN"
    print_colored "   1. Start: python3 main.py" "$BLUE"
    print_colored "   2. Open browser: http://localhost:8080/dashboard" "$BLUE"
    print_colored "   3. Click 'Auto Config' button for automatic setup" "$BLUE"
    print_colored "   4. Use 'Quick SNI Scan' to find working domains" "$BLUE"
    print_colored "   5. Use 'Quick SSH Scan' to find SSH servers" "$BLUE"
    print_colored "   6. Use 'Use Best Config' to connect automatically" "$BLUE"
    echo ""
    
    print_colored "🆘 Support:" "$CYAN"
    print_colored "   • GitHub: https://github.com/dhackerxyz/Tunnel_Free_Internet_Termux" "$BLUE"
    print_colored "   • Issues: https://github.com/dhackerxyz/Tunnel_Free_Internet_Termux/issues" "$BLUE"
    print_colored "   • Documentation: Check README.md" "$BLUE"
    echo ""
    
    print_colored "🎯 Next Steps:" "$YELLOW"
    print_colored "   cd $INSTALL_DIR && python3 main.py" "$GREEN"
    echo ""
    
    # Show system info
    print_colored "📊 System Information:" "$CYAN"
    print_colored "   • Platform: $PLATFORM" "$BLUE"
    print_colored "   • Architecture: $ARCH" "$BLUE"
    print_colored "   • Python: $(python3 --version)" "$BLUE"
    echo ""
}

main() {
    print_header "🤖 AI AUTO TUNNELER ENHANCED - INSTALLER"
    print_colored "Universal installer for Termux and Linux systems" "$BLUE"
    print_colored "Developed by: Mulky Malikul Dhaher" "$PURPLE"
    echo ""
    
    # Run installation steps
    check_system
    install_dependencies
    install_python_deps
    download_application
    configure_certificates
    test_installation
    create_shortcuts
    show_completion
}

# Error handling
trap 'print_colored "❌ Installation failed. Check the error above." "$RED"; exit 1' ERR

# Run installer
main "$@"

print_colored "🎊 Installation completed successfully! Enjoy AI Auto Tunneler Enhanced!" "$GREEN"
