#!/bin/bash

# AI Auto Tunneler Enhanced - Auto Run Script
# Universal startup script for all platforms
# Developed by: Mulky Malikul Dhaher

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

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

# Parse command line arguments
PORT=8080
AUTO_CONFIG=false
BACKGROUND=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --auto-config)
            AUTO_CONFIG=true
            shift
            ;;
        --background)
            BACKGROUND=true
            shift
            ;;
        --help)
            echo "AI Auto Tunneler Enhanced - Auto Run Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --port PORT        Set custom port (default: 8080)"
            echo "  --auto-config      Run auto-configuration on startup"
            echo "  --background       Run in background mode"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Start normally on port 8080"
            echo "  $0 --port 9090              # Start on custom port"
            echo "  $0 --auto-config            # Start with auto-configuration"
            echo "  $0 --background              # Start in background"
            echo "  $0 --port 9090 --background # Custom port + background"
            echo ""
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

main() {
    print_header "🤖 AI AUTO TUNNELER ENHANCED"
    print_colored "Universal startup script for Termux and Linux" "$BLUE"
    print_colored "Developed by: Mulky Malikul Dhaher" "$YELLOW"
    echo ""
    
    # Check current directory
    if [[ ! -f "main.py" ]]; then
        print_colored "❌ main.py not found in current directory" "$RED"
        print_colored "📁 Please run this script from the AI Auto Tunneler directory" "$YELLOW"
        exit 1
    fi
    
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
    
    # Check Python installation
    print_colored "🔍 Checking Python installation..." "$BLUE"
    if ! command -v python3 &> /dev/null; then
        print_colored "❌ Python3 not found" "$RED"
        print_colored "📦 Please install Python3 first:" "$YELLOW"
        case $PLATFORM in
            "termux")
                print_colored "   pkg install python" "$BLUE"
                ;;
            "linux")
                print_colored "   sudo apt install python3 python3-pip" "$BLUE"
                ;;
            "macos")
                print_colored "   brew install python3" "$BLUE"
                ;;
        esac
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version)
    print_colored "✅ $PYTHON_VERSION found" "$GREEN"
    
    # Check and install requirements
    print_colored "🔍 Checking dependencies..." "$BLUE"
    
    MISSING_DEPS=()
    REQUIRED_MODULES=("fastapi" "uvicorn" "httpx" "bs4" "tinydb" "requests")
    
    for module in "${REQUIRED_MODULES[@]}"; do
        if ! python3 -c "import $module" &> /dev/null; then
            MISSING_DEPS+=("$module")
        fi
    done
    
    if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
        print_colored "📦 Installing missing dependencies..." "$YELLOW"
        print_colored "   Missing: ${MISSING_DEPS[*]}" "$BLUE"
        
        if [[ -f "requirements.txt" ]]; then
            python3 -m pip install -r requirements.txt
        else
            # Install basic requirements if file doesn't exist
            python3 -m pip install fastapi uvicorn httpx beautifulsoup4 tinydb requests
        fi
        
        print_colored "✅ Dependencies installed" "$GREEN"
    else
        print_colored "✅ All dependencies satisfied" "$GREEN"
    fi
    
    # Check port availability
    print_colored "🔍 Checking port $PORT..." "$BLUE"
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$PORT "; then
            print_colored "⚠️ Port $PORT is already in use" "$YELLOW"
            print_colored "🔧 Trying to stop existing processes..." "$BLUE"
            
            # Try to find and kill existing processes
            if command -v lsof &> /dev/null; then
                EXISTING_PID=$(lsof -ti:$PORT 2>/dev/null || true)
                if [[ -n "$EXISTING_PID" ]]; then
                    kill $EXISTING_PID 2>/dev/null || true
                    sleep 2
                fi
            fi
            
            # Kill any Python processes running main.py
            pkill -f "python.*main.py" 2>/dev/null || true
            sleep 1
        fi
    fi
    
    # Create logs directory
    mkdir -p logs
    
    # Show startup information
    print_colored "🚀 Starting AI Auto Tunneler Enhanced..." "$GREEN"
    print_colored "📊 Configuration:" "$CYAN"
    print_colored "   • Port: $PORT" "$BLUE"
    print_colored "   • Platform: $PLATFORM" "$BLUE"
    print_colored "   • Auto-config: $([ "$AUTO_CONFIG" = true ] && echo "Enabled" || echo "Disabled")" "$BLUE"
    print_colored "   • Background: $([ "$BACKGROUND" = true ] && echo "Yes" || echo "No")" "$BLUE"
    echo ""
    
    print_colored "🌐 Access URLs (after startup):" "$CYAN"
    print_colored "   • Main UI: http://localhost:$PORT" "$BLUE"
    print_colored "   • Enhanced Dashboard: http://localhost:$PORT/dashboard" "$BLUE"
    print_colored "   • API Documentation: http://localhost:$PORT/docs" "$BLUE"
    print_colored "   • Health Check: http://localhost:$PORT/health" "$BLUE"
    echo ""
    
    # Prepare startup command
    if [[ "$PORT" != "8080" ]]; then
        # If custom port, modify main.py temporarily or use environment variable
        export TUNNELER_PORT="$PORT"
    fi
    
    # Start the application
    if [[ "$BACKGROUND" = true ]]; then
        print_colored "🔄 Starting in background mode..." "$YELLOW"
        nohup python3 main.py > logs/tunneler.log 2>&1 &
        APP_PID=$!
        echo $APP_PID > tunneler.pid
        print_colored "✅ Application started in background (PID: $APP_PID)" "$GREEN"
        print_colored "📋 Log file: logs/tunneler.log" "$BLUE"
        print_colored "🛑 To stop: kill $APP_PID" "$BLUE"
        
        # Run auto-configuration if requested
        if [[ "$AUTO_CONFIG" = true ]]; then
            print_colored "🤖 Waiting for startup, then running auto-configuration..." "$YELLOW"
            sleep 8
            
            if curl -s --max-time 10 http://localhost:$PORT/health &> /dev/null; then
                print_colored "🔧 Running auto-configuration..." "$BLUE"
                curl -s -X POST http://localhost:$PORT/api/auto-config > /dev/null || true
                print_colored "✅ Auto-configuration completed" "$GREEN"
            else
                print_colored "⚠️ Could not connect to application for auto-config" "$YELLOW"
            fi
        fi
        
        print_colored "🎉 Setup completed! Check logs/tunneler.log for details" "$GREEN"
    else
        print_colored "🔄 Starting application..." "$YELLOW"
        print_colored "🛑 Press Ctrl+C to stop" "$BLUE"
        echo ""
        
        # Handle cleanup on exit
        trap cleanup EXIT INT TERM
        
        # Start the application in foreground
        python3 main.py &
        APP_PID=$!
        
        # Wait for startup
        sleep 5
        
        # Run auto-configuration if requested
        if [[ "$AUTO_CONFIG" = true ]]; then
            print_colored "🤖 Running auto-configuration..." "$YELLOW"
            
            if curl -s --max-time 10 http://localhost:$PORT/health &> /dev/null; then
                print_colored "🔧 Auto-configuration starting..." "$BLUE"
                curl -s -X POST http://localhost:$PORT/api/auto-config > /dev/null || true
                print_colored "✅ Auto-configuration completed" "$GREEN"
            else
                print_colored "⚠️ Could not connect to application for auto-config" "$YELLOW"
            fi
        fi
        
        # Show final status
        if curl -s --max-time 5 http://localhost:$PORT/health &> /dev/null; then
            print_colored "🎉 AI Auto Tunneler Enhanced is running successfully!" "$GREEN"
            print_colored "🌐 Open: http://localhost:$PORT/dashboard" "$CYAN"
        else
            print_colored "⚠️ Application may not be fully ready yet" "$YELLOW"
        fi
        
        # Wait for the main process
        wait $APP_PID
    fi
}

cleanup() {
    print_colored "🛑 Shutting down..." "$YELLOW"
    
    # Kill any remaining processes
    pkill -f "python.*main.py" 2>/dev/null || true
    
    # Remove PID file if exists
    rm -f tunneler.pid
    
    print_colored "👋 AI Auto Tunneler stopped" "$GREEN"
}

# Error handling
trap 'print_colored "❌ Startup failed. Check the error above." "$RED"; exit 1' ERR

# Run main function
main "$@"
