#!/bin/bash
"""
Inject Engine Script
Start stunnel + SSH tunnel combination
"""

# AI Auto Tunneler - Injection Engine
# Usage: ./inject_engine.sh <sni_domain> <ssh_host> <ssh_port> <ssh_user> <ssh_pass> <local_port>

set -e

# Configuration
SNI_DOMAIN="$1"
SSH_HOST="$2"
SSH_PORT="$3"
SSH_USER="$4"
SSH_PASS="$5"
LOCAL_PORT="${6:-9092}"
STUNNEL_PORT=$((LOCAL_PORT + 1000))

# Validation
if [ -z "$SNI_DOMAIN" ] || [ -z "$SSH_HOST" ] || [ -z "$SSH_PORT" ] || [ -z "$SSH_USER" ] || [ -z "$SSH_PASS" ]; then
    echo "❌ Usage: $0 <sni_domain> <ssh_host> <ssh_port> <ssh_user> <ssh_pass> [local_port]"
    echo "Example: $0 free.facebook.com sg-1.openssh.net 22 demo demo123 9092"
    exit 1
fi

echo "🚀 AI Auto Tunneler - Starting Injection"
echo "📊 Configuration:"
echo "   SNI Domain: $SNI_DOMAIN"
echo "   SSH Server: $SSH_HOST:$SSH_PORT"
echo "   SSH User: $SSH_USER"
echo "   SOCKS Port: $LOCAL_PORT"
echo "   Stunnel Port: $STUNNEL_PORT"
echo ""

# Create stunnel configuration
STUNNEL_CONF="/tmp/ai_tunneler_stunnel.conf"
cat > "$STUNNEL_CONF" << EOF
# AI Auto Tunneler - Stunnel Configuration
cert = /data/data/com.termux/files/usr/etc/stunnel/cert.pem
key = /data/data/com.termux/files/usr/etc/stunnel/key.pem
client = yes
debug = 4
output = /tmp/ai_tunneler_stunnel.log

[ai_tunnel]
accept = 127.0.0.1:$STUNNEL_PORT
connect = $SNI_DOMAIN:443
verifyChain = no
sni = $SNI_DOMAIN
EOF

echo "📝 Stunnel config created: $STUNNEL_CONF"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🧹 Cleaning up processes..."
    
    # Kill SSH tunnel
    pkill -f "ssh.*$SSH_HOST" 2>/dev/null || true
    
    # Kill stunnel
    pkill -f "stunnel.*$STUNNEL_CONF" 2>/dev/null || true
    
    # Remove config file
    rm -f "$STUNNEL_CONF"
    
    echo "✅ Cleanup completed"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Check if required tools are available
check_tool() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "❌ Error: $1 is not installed"
        echo "💡 Install with: pkg install $1"
        exit 1
    fi
}

echo "🔍 Checking required tools..."
check_tool stunnel
check_tool ssh

# Check for sshpass (optional but recommended)
if ! command -v sshpass >/dev/null 2>&1; then
    echo "⚠️ Warning: sshpass not found. Password authentication may not work."
    echo "💡 Install with: pkg install sshpass"
fi

# Start stunnel
echo "🔧 Starting stunnel..."
stunnel "$STUNNEL_CONF" &
STUNNEL_PID=$!

# Wait for stunnel to initialize
sleep 3

# Check if stunnel is running
if ! kill -0 $STUNNEL_PID 2>/dev/null; then
    echo "❌ Failed to start stunnel"
    echo "📋 Check log: /tmp/ai_tunneler_stunnel.log"
    exit 1
fi

echo "✅ Stunnel started (PID: $STUNNEL_PID)"

# Prepare SSH command
SSH_CMD=(
    "ssh"
    "-o" "StrictHostKeyChecking=no"
    "-o" "UserKnownHostsFile=/dev/null"
    "-o" "ConnectTimeout=15"
    "-o" "ServerAliveInterval=30"
    "-o" "ServerAliveCountMax=3"
    "-D" "127.0.0.1:$LOCAL_PORT"
    "-p" "$SSH_PORT"
    "$SSH_USER@$SSH_HOST"
    "-N"
)

# Start SSH tunnel
echo "🔐 Starting SSH tunnel..."

if command -v sshpass >/dev/null 2>&1; then
    # Use sshpass for password authentication
    echo "🔑 Using sshpass for authentication..."
    sshpass -p "$SSH_PASS" "${SSH_CMD[@]}" &
    SSH_PID=$!
else
    # Try without sshpass (will likely fail for password auth)
    echo "🔑 Attempting SSH without sshpass..."
    "${SSH_CMD[@]}" &
    SSH_PID=$!
fi

# Wait for SSH to establish connection
echo "⏳ Waiting for SSH connection to establish..."
sleep 5

# Check if SSH is running
if kill -0 $SSH_PID 2>/dev/null; then
    echo "✅ SSH tunnel established (PID: $SSH_PID)"
else
    echo "❌ SSH tunnel failed to start"
    exit 1
fi

# Test the SOCKS proxy
echo "🧪 Testing SOCKS proxy..."
test_proxy() {
    if command -v curl >/dev/null 2>&1; then
        # Test with curl
        RESULT=$(curl --socks5 "127.0.0.1:$LOCAL_PORT" --connect-timeout 10 --max-time 15 -s "https://httpbin.org/ip" 2>/dev/null || echo "FAILED")
        
        if [ "$RESULT" != "FAILED" ] && echo "$RESULT" | grep -q "origin"; then
            echo "✅ SOCKS proxy test successful!"
            echo "🌐 External IP: $(echo "$RESULT" | grep -o '"origin": "[^"]*"' | cut -d'"' -f4)"
            return 0
        else
            echo "❌ SOCKS proxy test failed"
            return 1
        fi
    else
        echo "⚠️ curl not available for testing"
        return 0
    fi
}

if test_proxy; then
    echo ""
    echo "🎉 AI Auto Tunneler Successfully Started!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Connection Details:"
    echo "   SOCKS Proxy: 127.0.0.1:$LOCAL_PORT"
    echo "   SNI Domain: $SNI_DOMAIN"
    echo "   SSH Server: $SSH_HOST:$SSH_PORT"
    echo ""
    echo "🔧 Usage Instructions:"
    echo "   • Configure your browser to use SOCKS5 proxy: 127.0.0.1:$LOCAL_PORT"
    echo "   • Test with: curl --socks5 127.0.0.1:$LOCAL_PORT https://ipinfo.io"
    echo "   • Press Ctrl+C to stop the tunnel"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Keep running until interrupted
    echo "⏳ Tunnel is running... Press Ctrl+C to stop"
    
    # Monitor processes and keep running
    while true; do
        # Check if stunnel is still running
        if ! kill -0 $STUNNEL_PID 2>/dev/null; then
            echo "❌ Stunnel process died, restarting..."
            stunnel "$STUNNEL_CONF" &
            STUNNEL_PID=$!
            sleep 2
        fi
        
        # Check if SSH is still running
        if ! kill -0 $SSH_PID 2>/dev/null; then
            echo "❌ SSH process died, attempting restart..."
            if command -v sshpass >/dev/null 2>&1; then
                sshpass -p "$SSH_PASS" "${SSH_CMD[@]}" &
                SSH_PID=$!
            else
                "${SSH_CMD[@]}" &
                SSH_PID=$!
            fi
            sleep 3
        fi
        
        # Show status every 30 seconds
        sleep 30
        echo "📊 Status: Tunnel active - SOCKS proxy on port $LOCAL_PORT"
    done
    
else
    echo "❌ Tunnel setup failed - SOCKS proxy not working"
    exit 1
fi
