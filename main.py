#!/usr/bin/env python3
"""
AI Auto Tunneler - Enhanced Main FastAPI Backend
Termux Tunnel Free Internet with AI Auto Detection
Enhanced version with improved features and API documentation
"""

import json
import asyncio
import subprocess
import os
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query as QueryParam
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query

# Import core modules
from core.sni_scraper import SNIScraper
from core.ssh_scraper import SSHScraperImproved as SSHScraper
from core.test_bypass import BypassTester
from core.checker import ConnectionChecker

# Global variables
current_tunnel_process = None
tunnel_status = {"active": False, "socks_port": None, "config": None}
app_start_time = time.time()
total_scans_performed = 0

# Database setup
db = TinyDB('db.json')
config_db = TinyDB('config.json')

class TunnelConfig(BaseModel):
    sni_domain: str = Field(..., description="SNI domain for SSL bypass", example="free.facebook.com")
    ssh_host: str = Field(..., description="SSH server hostname or IP", example="sg-1.openssh.net")
    ssh_port: int = Field(22, description="SSH server port", example=22)
    ssh_user: str = Field(..., description="SSH username", example="demo")
    ssh_pass: str = Field(..., description="SSH password", example="demo123")
    local_port: int = Field(9092, description="Local SOCKS proxy port", example=9092)

class ScanRequest(BaseModel):
    scan_type: str = Field(..., description="Type of scan to perform", pattern="^(sni|ssh|bypass)$")
    limit: int = Field(10, description="Maximum number of targets to scan", ge=1, le=50)

class HealthStatus(BaseModel):
    status: str
    uptime: float
    version: str
    active_tunnels: int
    total_scans: int
    database_entries: int

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    log_message("AI Auto Tunneler Enhanced started")
    
    # Create directories if not exist
    os.makedirs("assets", exist_ok=True)
    os.makedirs("core", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("🚀 AI Auto Tunneler Enhanced is running!")
    print("📱 Access Web UI at: http://localhost:8080")
    print("📚 API Documentation: http://localhost:8080/docs")
    print("🔧 SOCKS proxy will run on port 9092 when active")
    
    yield
    
    # Shutdown
    await stop_tunnel()
    log_message("AI Auto Tunneler Enhanced stopped")

app = FastAPI(
    title="🤖 AI Auto Tunneler Enhanced",
    description="""
    Advanced Termux Free Internet with AI Detection
    
    This system automatically discovers SNI domains and SSH servers to create bypass tunnels.
    
    ## Features
    - 🔍 Auto SNI domain discovery
    - 🔐 SSH server scanning from multiple sources
    - 🧪 Intelligent bypass testing
    - 📊 Real-time monitoring and statistics
    - 🌐 Web-based user interface
    - 🔧 SOCKS proxy automation
    """,
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "AI Auto Tunneler",
        "url": "https://github.com/dhackerxyz/Tunnel_Free_Internet_Termux",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/", tags=["Web UI"], summary="Main Web Interface")
async def root():
    """Serve the main Web UI interface"""
    return FileResponse('assets/index.html')

@app.get("/health", response_model=HealthStatus, tags=["System"], summary="System Health Check")
async def health_check():
    """
    Comprehensive system health check endpoint
    
    Returns system status, uptime, and basic statistics
    """
    uptime = time.time() - app_start_time
    
    # Count database entries
    total_db_entries = len(db.all()) + len(config_db.all())
    
    return HealthStatus(
        status="healthy" if uptime > 0 else "starting",
        uptime=round(uptime, 2),
        version="1.1.0",
        active_tunnels=1 if tunnel_status["active"] else 0,
        total_scans=total_scans_performed,
        database_entries=total_db_entries
    )

@app.get("/api/info", tags=["System"], summary="Detailed System Information")
async def get_system_info():
    """
    Get comprehensive system information including:
    - System stats and uptime
    - Database statistics  
    - Process information
    - Current tunnel status
    """
    try:
        # Get process information
        checker = ConnectionChecker()
        process_info = checker.get_process_info()
        
        # Get database stats
        db_stats = {
            "total_entries": len(db.all()),
            "sni_domains": len(db.search(Query().type == 'sni')),
            "ssh_servers": len(db.search(Query().type == 'ssh')),
            "working_combinations": len(config_db.all()),
            "database_size_bytes": Path("db.json").stat().st_size if Path("db.json").exists() else 0
        }
        
        return {
            "system": {
                "uptime": round(time.time() - app_start_time, 2),
                "version": "1.1.0",
                "python_version": subprocess.getoutput("python3 --version"),
                "os_info": subprocess.getoutput("uname -a"),
                "memory_usage": subprocess.getoutput("free -h | head -2") if os.path.exists("/usr/bin/free") else "N/A"
            },
            "tunnel_status": tunnel_status,
            "database_stats": db_stats,
            "process_info": process_info,
            "performance": {
                "total_scans": total_scans_performed,
                "avg_scan_time": "2-5 seconds",
                "success_rate": "Variable based on network conditions"
            }
        }
    except Exception as e:
        return {"error": str(e), "message": "Failed to get system information"}

@app.get("/api/status", tags=["Tunnel"], summary="Current Tunnel Status")
async def get_status():
    """
    Get current tunnel status with enhanced connection quality information
    
    Returns tunnel state, configuration, and connection quality metrics
    """
    status_response = {
        "tunnel_active": tunnel_status["active"],
        "socks_port": tunnel_status.get("socks_port"),
        "config": tunnel_status.get("config"),
        "timestamp": datetime.now().isoformat(),
        "uptime": round(time.time() - app_start_time, 2)
    }
    
    # Add connection quality if tunnel is active
    if tunnel_status["active"] and tunnel_status.get("socks_port"):
        try:
            checker = ConnectionChecker()
            connection_test = await checker.test_socks_connection(tunnel_status["socks_port"])
            status_response["connection_quality"] = {
                "status": "good" if connection_test["connection_successful"] else "poor",
                "response_time": connection_test.get("response_time"),
                "external_ip": connection_test.get("external_ip"),
                "speed_rating": connection_test.get("speed_rating", "Unknown")
            }
        except Exception as e:
            status_response["connection_quality"] = {"status": "unknown", "error": str(e)}
    
    return status_response

@app.post("/api/scan", tags=["Scanning"], summary="Start Scanning Operation")
async def scan_targets(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Start scanning for SNI domains, SSH servers, or testing bypass combinations
    
    - **sni**: Scan for working SNI domains from various CDN sources
    - **ssh**: Scan for free SSH servers from multiple providers  
    - **bypass**: Test combinations of SNI domains and SSH servers
    """
    global total_scans_performed
    
    if request.scan_type == "sni":
        background_tasks.add_task(scan_sni_domains, request.limit)
        total_scans_performed += 1
        return {
            "status": "started", 
            "message": f"Scanning SNI domains (limit: {request.limit})",
            "scan_id": f"sni_{int(time.time())}",
            "estimated_duration": f"{request.limit * 2} seconds",
            "targets": "Facebook, WhatsApp, Google, CloudFlare CDNs"
        }
    
    elif request.scan_type == "ssh":
        background_tasks.add_task(scan_ssh_servers, request.limit)
        total_scans_performed += 1
        return {
            "status": "started", 
            "message": f"Scanning SSH servers (limit: {request.limit})",
            "scan_id": f"ssh_{int(time.time())}",
            "estimated_duration": f"{request.limit * 3} seconds",
            "sources": "FastSSH, SSHKit, TCPVPN, SpeedSSH, VPNJantit"
        }
    
    elif request.scan_type == "bypass":
        background_tasks.add_task(test_bypass_combinations)
        return {
            "status": "started", 
            "message": "Testing bypass combinations",
            "scan_id": f"bypass_{int(time.time())}",
            "estimated_duration": "30-60 seconds",
            "process": "Testing SNI+SSH combinations for bypass capability"
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid scan type. Use: sni, ssh, or bypass")

@app.get("/api/results", tags=["Scanning"], summary="Get Scan Results")
async def get_results(
    limit: int = QueryParam(20, description="Maximum results to return", ge=1, le=100),
    status_filter: Optional[str] = QueryParam(None, description="Filter by status (active/inactive)")
):
    """
    Get scan results with enhanced filtering and statistics
    
    Returns latest scan results for SNI domains, SSH servers, and working combinations
    with comprehensive statistics and filtering options
    """
    try:
        # Get SNI results with filtering
        all_sni = db.search(Query().type == 'sni')
        if status_filter:
            all_sni = [s for s in all_sni if s.get('status') == status_filter]
        sni_results = sorted(all_sni, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        
        # Get SSH results with filtering  
        all_ssh = db.search(Query().type == 'ssh')
        if status_filter:
            all_ssh = [s for s in all_ssh if s.get('status') == status_filter]
        ssh_results = sorted(all_ssh, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        
        # Get working combinations
        working_combos = config_db.all()
        working_combos_sorted = sorted(working_combos, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        
        # Calculate comprehensive statistics
        sni_active = [s for s in all_sni if s.get('status') == 'active']
        ssh_active = [s for s in all_ssh if s.get('status') == 'active']
        
        stats = {
            "sni_total": len(all_sni),
            "sni_active": len(sni_active),
            "sni_success_rate": round((len(sni_active) / len(all_sni) * 100) if all_sni else 0, 1),
            "ssh_total": len(all_ssh),
            "ssh_active": len(ssh_active),
            "ssh_success_rate": round((len(ssh_active) / len(all_ssh) * 100) if all_ssh else 0, 1),
            "working_combinations": len(working_combos),
            "last_scan": max([s.get('timestamp', '') for s in all_sni + all_ssh] + ['']) if (all_sni or all_ssh) else None,
            "best_sni_domains": [s['domain'] for s in sni_active[:5]],
            "best_ssh_servers": [f"{s['host']}:{s['port']}" for s in ssh_active[:5]]
        }
        
        return {
            "sni_domains": sni_results,
            "ssh_servers": ssh_results,
            "working_combinations": working_combos_sorted,
            "statistics": stats,
            "pagination": {
                "limit": limit,
                "total_available": len(all_sni) + len(all_ssh),
                "filter_applied": status_filter
            }
        }
    except Exception as e:
        return {
            "error": str(e), 
            "sni_domains": [], 
            "ssh_servers": [], 
            "working_combinations": [],
            "statistics": {}
        }

@app.post("/api/tunnel/start", tags=["Tunnel"], summary="Start Tunnel Connection")
async def start_tunnel(config: TunnelConfig):
    """
    Start tunnel with given configuration and enhanced monitoring
    
    Creates a stunnel + SSH tunnel combination and tests the connection
    """
    global current_tunnel_process, tunnel_status
    
    try:
        # Validate configuration
        if not all([config.sni_domain, config.ssh_host, config.ssh_user, config.ssh_pass]):
            raise HTTPException(status_code=400, detail="Missing required configuration fields")
        
        # Stop existing tunnel if running
        if current_tunnel_process:
            await stop_tunnel()
        
        log_message(f"Starting tunnel: {config.sni_domain} -> {config.ssh_host}:{config.ssh_port}")
        
        # Create stunnel config
        stunnel_config = create_stunnel_config(config)
        
        # Start tunnel process
        current_tunnel_process = await start_tunnel_process(config, stunnel_config)
        
        # Update status with enhanced information
        tunnel_status = {
            "active": True,
            "socks_port": config.local_port,
            "config": config.dict(),
            "started_at": datetime.now().isoformat(),
            "tunnel_type": "stunnel+ssh",
            "connection_attempts": 1
        }
        
        # Test connection after a delay
        await asyncio.sleep(3)
        try:
            checker = ConnectionChecker()
            test_result = await checker.test_socks_connection(config.local_port)
            tunnel_status["initial_test"] = {
                "success": test_result["connection_successful"],
                "response_time": test_result.get("response_time"),
                "external_ip": test_result.get("external_ip"),
                "speed_rating": test_result.get("speed_rating")
            }
        except Exception as e:
            tunnel_status["initial_test"] = {"success": False, "error": str(e)}
        
        return {
            "status": "success", 
            "message": "Tunnel started successfully", 
            "socks_port": config.local_port,
            "config_used": {
                "sni_domain": config.sni_domain,
                "ssh_host": config.ssh_host,
                "ssh_port": config.ssh_port
            },
            "initial_test": tunnel_status.get("initial_test", {}),
            "instructions": [
                f"Configure your browser to use SOCKS5 proxy: 127.0.0.1:{config.local_port}",
                f"Test with: curl --socks5 127.0.0.1:{config.local_port} https://ipinfo.io/ip",
                "Use /api/tunnel/test to monitor connection quality"
            ]
        }
        
    except Exception as e:
        log_message(f"Tunnel start error: {str(e)}")
        return {"status": "error", "message": f"Failed to start tunnel: {str(e)}"}

@app.post("/api/tunnel/stop", tags=["Tunnel"], summary="Stop Tunnel Connection")
async def stop_tunnel():
    """
    Stop current tunnel with comprehensive cleanup
    
    Terminates all tunnel processes and cleans up temporary files
    """
    global current_tunnel_process, tunnel_status
    
    try:
        was_active = tunnel_status.get("active", False)
        old_config = tunnel_status.get("config", {})
        
        if current_tunnel_process:
            log_message("Stopping tunnel process...")
            current_tunnel_process.terminate()
            try:
                await asyncio.wait_for(current_tunnel_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                log_message("Force killing tunnel process...")
                current_tunnel_process.kill()
                await current_tunnel_process.wait()
            
            current_tunnel_process = None
        
        # Kill any remaining processes
        cleanup_commands = [
            ['pkill', '-f', 'stunnel'],
            ['pkill', '-f', 'ssh.*-D'],
            ['pkill', '-f', 'sshpass']
        ]
        
        for cmd in cleanup_commands:
            try:
                subprocess.run(cmd, check=False, capture_output=True)
            except:
                pass
        
        # Clean up temporary files
        try:
            import glob
            for temp_file in glob.glob('/tmp/stunnel_*.conf') + glob.glob('/tmp/ai_tunneler_*'):
                os.remove(temp_file)
        except:
            pass
        
        tunnel_status = {
            "active": False, 
            "socks_port": None, 
            "config": None, 
            "stopped_at": datetime.now().isoformat()
        }
        
        if was_active:
            log_message("Tunnel stopped successfully")
        
        return {
            "status": "success", 
            "message": "Tunnel stopped successfully" if was_active else "No active tunnel to stop",
            "was_active": was_active,
            "previous_config": old_config if was_active else None,
            "cleanup_performed": True
        }
        
    except Exception as e:
        log_message(f"Tunnel stop error: {str(e)}")
        return {"status": "error", "message": f"Failed to stop tunnel: {str(e)}"}

@app.get("/api/tunnel/test", tags=["Tunnel"], summary="Test Tunnel Connection")
async def test_connection():
    """
    Test current tunnel connection with comprehensive diagnostics
    
    Performs connection tests and returns detailed quality metrics
    """
    if not tunnel_status["active"]:
        return {
            "status": "error", 
            "message": "No active tunnel",
            "suggestion": "Start a tunnel first using /api/tunnel/start"
        }
    
    try:
        checker = ConnectionChecker()
        
        # Run comprehensive test
        socks_port = tunnel_status["socks_port"]
        result = await checker.test_socks_connection(socks_port)
        
        # Add extra diagnostics
        result["tunnel_config"] = tunnel_status.get("config", {})
        result["tunnel_uptime"] = (
            (datetime.now() - datetime.fromisoformat(tunnel_status["started_at"])).total_seconds()
            if tunnel_status.get("started_at") else 0
        )
        
        # Update tunnel status with test results
        tunnel_status["last_test"] = {
            "timestamp": datetime.now().isoformat(),
            "success": result.get("connection_successful", False),
            "response_time": result.get("response_time"),
            "external_ip": result.get("external_ip")
        }
        
        return result
        
    except Exception as e:
        log_message(f"Connection test error: {str(e)}")
        return {
            "status": "error", 
            "message": f"Connection test failed: {str(e)}",
            "troubleshooting": [
                "Check if tunnel processes are running",
                "Verify SOCKS port is not blocked", 
                "Try restarting the tunnel",
                "Check network connectivity"
            ]
        }

@app.get("/api/logs", tags=["System"], summary="Get System Logs")
async def get_logs(lines: int = QueryParam(50, description="Number of log lines to return", ge=1, le=1000)):
    """
    Get recent system logs with filtering options
    
    Returns application logs with metadata and filtering capabilities
    """
    try:
        log_file = Path("tunnel.log")
        if log_file.exists():
            with open(log_file, "r") as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if lines > 0 else all_lines
                
                return {
                    "logs": [line.strip() for line in recent_lines],
                    "metadata": {
                        "total_lines": len(all_lines),
                        "showing_lines": len(recent_lines),
                        "log_file_size": log_file.stat().st_size,
                        "last_modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                    }
                }
        return {
            "logs": ["No log file found"],
            "metadata": {
                "total_lines": 0,
                "showing_lines": 0,
                "log_file_size": 0,
                "last_modified": None
            }
        }
    except Exception as e:
        return {
            "logs": [f"Error reading logs: {str(e)}"],
            "error": str(e)
        }

# Background task functions
async def scan_sni_domains(limit: int):
    """Background task to scan SNI domains"""
    try:
        scraper = SNIScraper()
        domains = await scraper.scan_domains(limit)
        
        # Save results to database
        for domain in domains:
            db.insert({
                "type": "sni",
                "domain": domain["domain"],
                "status": domain["status"],
                "response_time": domain.get("response_time"),
                "ssl_valid": domain.get("ssl_valid", False),
                "redirect_detected": domain.get("redirect_detected", False),
                "timestamp": datetime.now().isoformat()
            })
            
        log_message(f"SNI scan completed: {len(domains)} domains found")
        
    except Exception as e:
        log_message(f"SNI scan error: {str(e)}")

async def scan_ssh_servers(limit: int):
    """Background task to scan SSH servers"""
    try:
        scraper = SSHScraper()
        servers = await scraper.scan_servers(limit)
        
        # Save results to database
        for server in servers:
            db.insert({
                "type": "ssh",
                "host": server["host"],
                "port": server["port"],
                "username": server["username"],
                "password": server["password"],
                "status": server["status"],
                "source": server.get("source", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
            
        log_message(f"SSH scan completed: {len(servers)} servers found")
        
    except Exception as e:
        log_message(f"SSH scan error: {str(e)}")

async def test_bypass_combinations():
    """Background task to test bypass combinations"""
    try:
        # Get recent SNI and SSH results
        sni_domains = [item for item in db.search(Query().type == 'sni') if item.get('status') == 'active'][-5:]
        ssh_servers = [item for item in db.search(Query().type == 'ssh') if item.get('status') == 'active'][-5:]
        
        if not sni_domains or not ssh_servers:
            log_message("Insufficient data for bypass testing. Run SNI and SSH scans first.")
            return
        
        tester = BypassTester()
        
        for sni in sni_domains:
            for ssh in ssh_servers:
                try:
                    config = TunnelConfig(
                        sni_domain=sni['domain'],
                        ssh_host=ssh['host'],
                        ssh_port=ssh['port'],
                        ssh_user=ssh['username'],
                        ssh_pass=ssh['password']
                    )
                    
                    result = await tester.test_combination(config)
                    
                    if result['success']:
                        # Save working combination
                        config_db.insert({
                            "sni_domain": config.sni_domain,
                            "ssh_host": config.ssh_host,
                            "ssh_port": config.ssh_port,
                            "ssh_user": config.ssh_user,
                            "ssh_pass": config.ssh_pass,
                            "success": True,
                            "speed_score": result.get('speed_score', 0),
                            "connection_time": result.get('connection_time', 0),
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        log_message(f"Working combination found: {config.sni_domain} + {config.ssh_host}")
                    
                except Exception as e:
                    log_message(f"Test error: {str(e)}")
                    continue
                    
                # Small delay between tests
                await asyncio.sleep(2)
        
        log_message("Bypass testing completed")
        
    except Exception as e:
        log_message(f"Bypass test error: {str(e)}")

def create_stunnel_config(config: TunnelConfig) -> str:
    """Create stunnel configuration"""
    stunnel_conf = f"""
# AI Auto Tunneler Enhanced - Stunnel Configuration
cert = /data/data/com.termux/files/usr/etc/stunnel/cert.pem
key = /data/data/com.termux/files/usr/etc/stunnel/key.pem
client = yes
debug = 4
output = tunnel_stunnel.log

[tunnel]
accept = 127.0.0.1:{config.local_port + 1000}
connect = {config.sni_domain}:443
verifyChain = no
sni = {config.sni_domain}
"""
    
    # Write config file
    with open("stunnel.conf", "w") as f:
        f.write(stunnel_conf)
    
    return stunnel_conf

async def start_tunnel_process(config: TunnelConfig, stunnel_config: str):
    """Start the actual tunnel process"""
    
    # Start stunnel
    stunnel_process = await asyncio.create_subprocess_exec(
        "stunnel", "stunnel.conf",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait a bit for stunnel to start
    await asyncio.sleep(2)
    
    # Start SSH tunnel
    ssh_cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=10",
        "-D", f"127.0.0.1:{config.local_port}",
        "-p", str(config.ssh_port),
        f"{config.ssh_user}@{config.ssh_host}",
        "-N"
    ]
    
    # Use sshpass if available for password auth
    try:
        ssh_process = await asyncio.create_subprocess_exec(
            "sshpass", "-p", config.ssh_pass, *ssh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    except FileNotFoundError:
        # Fallback without sshpass
        ssh_process = await asyncio.create_subprocess_exec(
            *ssh_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    
    return ssh_process

def log_message(message: str):
    """Log message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Write to log file
    with open("tunnel.log", "a") as f:
        f.write(log_entry)
    
    print(log_entry.strip())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
