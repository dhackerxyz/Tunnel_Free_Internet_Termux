#!/usr/bin/env python3
"""
AI Auto Tunneler - Main FastAPI Backend
Termux Tunnel Free Internet with AI Auto Detection
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

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from tinydb import TinyDB, Query

# Import core modules
from core.sni_scraper import SNIScraper
from core.ssh_scraper import SSHScraper
from core.test_bypass import BypassTester
from core.checker import ConnectionChecker

app = FastAPI(title="AI Auto Tunneler", description="Termux Tunnel Free Internet with AI")

# Database setup
db = TinyDB('db.json')
config_db = TinyDB('config.json')

# Global variables
current_tunnel_process = None
tunnel_status = {"active": False, "socks_port": None, "config": None}

class TunnelConfig(BaseModel):
    sni_domain: str
    ssh_host: str
    ssh_port: int
    ssh_user: str
    ssh_pass: str
    local_port: int = 9092

class ScanRequest(BaseModel):
    scan_type: str  # 'sni' or 'ssh' or 'bypass'
    limit: int = 10

# Serve static files
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/")
async def root():
    """Serve main Web UI"""
    return FileResponse('assets/index.html')

@app.get("/api/status")
async def get_status():
    """Get current tunnel status"""
    return {
        "tunnel_active": tunnel_status["active"],
        "socks_port": tunnel_status.get("socks_port"),
        "config": tunnel_status.get("config"),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/scan")
async def scan_targets(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start scanning for SNI domains or SSH servers"""
    
    if request.scan_type == "sni":
        background_tasks.add_task(scan_sni_domains, request.limit)
        return {"status": "started", "message": f"Scanning SNI domains (limit: {request.limit})"}
    
    elif request.scan_type == "ssh":
        background_tasks.add_task(scan_ssh_servers, request.limit)
        return {"status": "started", "message": f"Scanning SSH servers (limit: {request.limit})"}
    
    elif request.scan_type == "bypass":
        background_tasks.add_task(test_bypass_combinations)
        return {"status": "started", "message": "Testing bypass combinations"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid scan type")

@app.get("/api/results")
async def get_results():
    """Get scan results"""
    try:
        # Get latest SNI results
        sni_results = db.search(Query().type == 'sni')[-10:] if db.search(Query().type == 'sni') else []
        
        # Get latest SSH results  
        ssh_results = db.search(Query().type == 'ssh')[-10:] if db.search(Query().type == 'ssh') else []
        
        # Get working combinations
        working_combos = config_db.all()[-5:] if config_db.all() else []
        
        return {
            "sni_domains": sni_results,
            "ssh_servers": ssh_results,
            "working_combinations": working_combos
        }
    except Exception as e:
        return {"error": str(e), "sni_domains": [], "ssh_servers": [], "working_combinations": []}

@app.post("/api/tunnel/start")
async def start_tunnel(config: TunnelConfig):
    """Start tunnel with given configuration"""
    global current_tunnel_process, tunnel_status
    
    try:
        # Stop existing tunnel if running
        if current_tunnel_process:
            await stop_tunnel()
        
        # Create stunnel config
        stunnel_config = create_stunnel_config(config)
        
        # Start tunnel process
        current_tunnel_process = await start_tunnel_process(config, stunnel_config)
        
        # Update status
        tunnel_status = {
            "active": True,
            "socks_port": config.local_port,
            "config": config.dict(),
            "started_at": datetime.now().isoformat()
        }
        
        return {"status": "success", "message": "Tunnel started successfully", "socks_port": config.local_port}
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to start tunnel: {str(e)}"}

@app.post("/api/tunnel/stop")
async def stop_tunnel():
    """Stop current tunnel"""
    global current_tunnel_process, tunnel_status
    
    try:
        if current_tunnel_process:
            current_tunnel_process.terminate()
            try:
                await asyncio.wait_for(current_tunnel_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                current_tunnel_process.kill()
                await current_tunnel_process.wait()
            
            current_tunnel_process = None
        
        # Kill any remaining stunnel/ssh processes
        try:
            subprocess.run(['pkill', '-f', 'stunnel'], check=False)
            subprocess.run(['pkill', '-f', 'ssh.*-D'], check=False)
        except:
            pass
        
        tunnel_status = {"active": False, "socks_port": None, "config": None}
        
        return {"status": "success", "message": "Tunnel stopped"}
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to stop tunnel: {str(e)}"}

@app.get("/api/tunnel/test")
async def test_connection():
    """Test current tunnel connection"""
    if not tunnel_status["active"]:
        return {"status": "error", "message": "No active tunnel"}
    
    try:
        checker = ConnectionChecker()
        result = await checker.test_socks_connection(tunnel_status["socks_port"])
        return result
    except Exception as e:
        return {"status": "error", "message": f"Connection test failed: {str(e)}"}

@app.get("/api/logs")
async def get_logs():
    """Get recent logs"""
    try:
        log_file = Path("tunnel.log")
        if log_file.exists():
            with open(log_file, "r") as f:
                lines = f.readlines()[-50:]  # Last 50 lines
                return {"logs": lines}
        return {"logs": []}
    except Exception as e:
        return {"logs": [f"Error reading logs: {str(e)}"]}

# Background tasks
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
                            "speed": result.get('speed'),
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
cert = /data/data/com.termux/files/usr/etc/stunnel/cert.pem
key = /data/data/com.termux/files/usr/etc/stunnel/key.pem
client = yes
debug = 4

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

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    log_message("AI Auto Tunneler started")
    
    # Create directories if not exist
    os.makedirs("assets", exist_ok=True)
    os.makedirs("core", exist_ok=True)
    
    print("🚀 AI Auto Tunneler is running!")
    print("📱 Access Web UI at: http://localhost:8080")
    print("🔧 SOCKS proxy will run on port 9092 when active")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await stop_tunnel()
    log_message("AI Auto Tunneler stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
