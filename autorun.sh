#!/bin/bash

# AI Auto Tunneler - Auto Run Script
# Automatically start the AI tunneler system

set -e

echo "🤖 AI Auto Tunneler - Auto Run Script"
echo "====================================="

# Configuration
HOST="0.0.0.0"
PORT="8080"
AUTO_SCAN=${AUTO_SCAN:-false}
LOG_FILE="autorun.log"

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

# Function to check if a command exists
check_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        print_colored "❌ Error: $1 is not installed" "$RED"
        return 1
    fi
    return 0
}

# Function to check if a Python package is installed
check_python_package() {
    if ! python3 -c "import $1" >/dev/null 2>&1; then
        print_colored "❌ Error: Python package '$1' is not installed" "$RED"
        return 1
    fi
    return 0
}

# Function to install Python dependencies
install_dependencies() {
    print_header "📦 INSTALLING DEPENDENCIES"
    
    print_colored "🔍 Checking Python..." "$YELLOW"
    if ! check_command python3; then
        print_colored "💡 Install Python with: pkg install python" "$BLUE"
        exit 1
    fi
    
    print_colored "🔍 Checking pip..." "$YELLOW"
    if ! check_command pip; then
        print_colored "💡 Install pip with: pkg install python-pip" "$BLUE"
        exit 1
    fi
    
    print_colored "📋 Installing Python packages..." "$YELLOW"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_colored "✅ Python dependencies installed" "$GREEN"
    else
        print_colored "❌ requirements.txt not found" "$RED"
        exit 1
    fi
}

# Function to check system requirements
check_requirements() {
    print_header "🔍 CHECKING SYSTEM REQUIREMENTS"
    
    local missing_tools=()
    
    # Essential tools
    essential_tools=("python3" "curl" "stunnel" "ssh")
    
    for tool in "${essential_tools[@]}"; do
        if check_command "$tool"; then
            print_colored "✅ $tool is installed" "$GREEN"
        else
            print_colored "❌ $tool is missing" "$RED"
            missing_tools+=("$tool")
        fi
    done
    
    # Optional but recommended tools
    optional_tools=("sshpass" "nmap" "netstat")
    
    print_colored "🔍 Checking optional tools..." "$YELLOW"
    for tool in "${optional_tools[@]}"; do
        if check_command "$tool"; then
            print_colored "✅ $tool is available" "$GREEN"
        else
            print_colored "⚠️ $tool is recommended but not required" "$YELLOW"
        fi
    done
    
    # Check if any essential tools are missing
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_colored "❌ Missing essential tools: ${missing_tools[*]}" "$RED"
        print_colored "💡 Install missing tools with:" "$BLUE"
        print_colored "   pkg install ${missing_tools[*]}" "$CYAN"
        exit 1
    fi
    
    print_colored "✅ All essential requirements met!" "$GREEN"
}

# Function to setup directories and files
setup_environment() {
    print_header "🛠️ SETTING UP ENVIRONMENT"
    
    # Create directories
    mkdir -p assets core logs
    
    # Create log file
    touch "$LOG_FILE"
    
    # Create stunnel certificate if it doesn't exist
    if [ ! -f "/data/data/com.termux/files/usr/etc/stunnel/cert.pem" ]; then
        print_colored "🔐 Creating stunnel certificates..." "$YELLOW"
        mkdir -p /data/data/com.termux/files/usr/etc/stunnel
        
        # Generate self-signed certificate
        openssl req -new -x509 -days 365 -nodes \
            -config <(echo '[req]
                       distinguished_name=req
                       [v3_ca]
                       basicConstraints=CA:FALSE
                       keyUsage=digitalSignature,keyEncipherment
                       subjectAltName=@alt_names
                       [alt_names]
                       DNS.1=localhost
                       IP.1=127.0.0.1') \
            -out /data/data/com.termux/files/usr/etc/stunnel/cert.pem \
            -keyout /data/data/com.termux/files/usr/etc/stunnel/key.pem \
            -subj "/C=ID/ST=Jakarta/L=Jakarta/O=AI-Tunneler/CN=localhost" 2>/dev/null || {
            
            # Fallback: copy system certs if available
            if [ -f "/data/data/com.termux/files/usr/etc/tls/cert.pem" ]; then
                cp /data/data/com.termux/files/usr/etc/tls/cert.pem /data/data/com.termux/files/usr/etc/stunnel/
                cp /data/data/com.termux/files/usr/etc/tls/key.pem /data/data/com.termux/files/usr/etc/stunnel/ 2>/dev/null || true
            fi
        }
        print_colored "✅ Stunnel certificates ready" "$GREEN"
    fi
    
    print_colored "✅ Environment setup completed" "$GREEN"
}

# Function to show network information
show_network_info() {
    print_header "🌐 NETWORK INFORMATION"
    
    # Get IP addresses
    print_colored "📍 Local IP addresses:" "$YELLOW"
    ip addr show | grep -E 'inet [0-9]' | grep -v '127.0.0.1' | awk '{print "   " $2}' || true
    
    # Show current network interface
    print_colored "📡 Active network interface:" "$YELLOW"
    ip route get 8.8.8.8 2>/dev/null | head -1 | awk '{print "   " $5}' || echo "   Unknown"
    
    # Test internet connectivity
    print_colored "🔍 Testing internet connectivity..." "$YELLOW"
    if curl -s --connect-timeout 5 https://google.com >/dev/null 2>&1; then
        print_colored "✅ Internet connection: OK" "$GREEN"
    else
        print_colored "❌ Internet connection: Failed" "$RED"
        print_colored "⚠️ Check your internet connection before starting tunnels" "$YELLOW"
    fi
}

# Function to generate QR code for mobile access
generate_qr_code() {
    local url="$1"
    
    if check_command qrencode; then
        print_colored "📱 QR Code for mobile access:" "$CYAN"
        echo "$url" | qrencode -t UTF8
    else
        print_colored "📱 Mobile access URL: $url" "$CYAN"
        print_colored "💡 Install qrencode for QR code: pkg install qrencode" "$BLUE"
    fi
}

# Function to start the auto tunneler
start_tunneler() {
    print_header "🚀 STARTING AI AUTO TUNNELER"
    
    # Check if already running
    if pgrep -f "python.*main.py" >/dev/null; then
        print_colored "⚠️ AI Auto Tunneler is already running" "$YELLOW"
        print_colored "🔍 Use 'pkill -f python.*main.py' to stop it first" "$BLUE"
        exit 1
    fi
    
    # Determine access URLs
    local local_url="http://localhost:$PORT"
    local network_url=""
    
    # Try to get network IP
    local_ip=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K[0-9.]+' | head -1)
    if [ -n "$local_ip" ] && [ "$local_ip" != "127.0.0.1" ]; then
        network_url="http://$local_ip:$PORT"
    fi
    
    print_colored "🌐 Starting web server on $HOST:$PORT..." "$YELLOW"
    
    # Start the main application
    python3 main.py > "$LOG_FILE" 2>&1 &
    local main_pid=$!
    
    # Wait a moment for startup
    sleep 3
    
    # Check if it started successfully
    if kill -0 $main_pid 2>/dev/null; then
        print_colored "✅ AI Auto Tunneler started successfully!" "$GREEN"
        
        print_header "🎉 READY TO USE!"
        
        print_colored "📊 Access Information:" "$CYAN"
        print_colored "   • Local access: $local_url" "$GREEN"
        
        if [ -n "$network_url" ]; then
            print_colored "   • Network access: $network_url" "$GREEN"
            generate_qr_code "$network_url"
        fi
        
        print_colored "🔧 Usage Instructions:" "$YELLOW"
        print_colored "   1. Open the URL in your browser" "$BLUE"
        print_colored "   2. Click 'Scan SNI Domains' to find working domains" "$BLUE"
        print_colored "   3. Click 'Scan SSH Servers' to find SSH servers" "$BLUE"
        print_colored "   4. Click 'Test Bypass' to find working combinations" "$BLUE"
        print_colored "   5. Use 'Use Best Config' to connect automatically" "$BLUE"
        
        print_colored "📋 Control Commands:" "$YELLOW"
        print_colored "   • View logs: tail -f $LOG_FILE" "$BLUE"
        print_colored "   • Stop tunneler: pkill -f 'python.*main.py'" "$BLUE"
        print_colored "   • Restart: $0" "$BLUE"
        
        # Auto scan if enabled
        if [ "$AUTO_SCAN" = "true" ]; then
            print_colored "🔄 Auto-scan enabled - starting background scanning..." "$YELLOW"
            sleep 5
            curl -s -X POST "http://localhost:$PORT/api/scan" \
                -H "Content-Type: application/json" \
                -d '{"scan_type":"sni","limit":10}' >/dev/null &
            
            sleep 2
            curl -s -X POST "http://localhost:$PORT/api/scan" \
                -H "Content-Type: application/json" \
                -d '{"scan_type":"ssh","limit":10}' >/dev/null &
        fi
        
        # Keep running and show status
        print_colored "⏳ AI Auto Tunneler is running... Press Ctrl+C to stop" "$GREEN"
        
        # Monitor and show periodic status
        trap 'print_colored "🛑 Shutting down AI Auto Tunneler..." "$YELLOW"; kill $main_pid 2>/dev/null; exit 0' INT TERM
        
        while kill -0 $main_pid 2>/dev/null; do
            sleep 60
            print_colored "📊 Status: AI Auto Tunneler running (PID: $main_pid)" "$CYAN"
        done
        
        print_colored "❌ AI Auto Tunneler stopped unexpectedly" "$RED"
        exit 1
        
    else
        print_colored "❌ Failed to start AI Auto Tunneler" "$RED"
        print_colored "📋 Check logs: tail $LOG_FILE" "$BLUE"
        exit 1
    fi
}

# Main execution
main() {
    print_header "🤖 AI AUTO TUNNELER - INITIALIZATION"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --auto-scan)
                AUTO_SCAN=true
                shift
                ;;
            --port)
                PORT="$2"
                shift 2
                ;;
            --host)
                HOST="$2"
                shift 2
                ;;
            --help)
                echo "AI Auto Tunneler - Auto Run Script"
                echo ""
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --auto-scan     Start automatic scanning on startup"
                echo "  --port PORT     Set web server port (default: 8080)"
                echo "  --host HOST     Set web server host (default: 0.0.0.0)"
                echo "  --help          Show this help message"
                echo ""
                exit 0
                ;;
            *)
                print_colored "❌ Unknown option: $1" "$RED"
                print_colored "💡 Use --help for usage information" "$BLUE"
                exit 1
                ;;
        esac
    done
    
    # Run startup sequence
    check_requirements
    install_dependencies
    setup_environment
    show_network_info
    start_tunneler
}

# Run main function
main "$@"
