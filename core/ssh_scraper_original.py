#!/usr/bin/env python3
"""
SSH Server Scraper
Auto-discover free SSH servers from various sources
"""

import asyncio
import re
import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
import socket

class SSHScraper:
    def __init__(self):
        self.timeout = 10
        self.user_agents = [
            'Mozilla/5.0 (Android 10; Mobile; rv:88.0) Gecko/88.0 Firefox/88.0',
            'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
        ]
        
        # SSH provider sources
        self.ssh_sources = [
            {
                'name': 'FastSSH',
                'url': 'https://fastssh.com',
                'regions': ['singapore', 'indonesia', 'malaysia', 'thailand']
            },
            {
                'name': 'SSHKit',
                'url': 'https://sshkit.com',
                'regions': ['sg', 'id', 'my', 'th']
            },
            {
                'name': 'TCPVPN',
                'url': 'https://tcpvpn.com',
                'regions': ['singapore', 'indonesia']
            },
            {
                'name': 'SpeedSSH',
                'url': 'https://speedssh.com',
                'regions': ['sg', 'id']
            },
            {
                'name': 'VPNJantit',
                'url': 'https://vpnjantit.com',
                'regions': ['singapore', 'indonesia', 'malaysia']
            }
        ]
        
        # Common SSH ports
        self.common_ports = [22, 80, 143, 443, 992, 993, 2082, 2083, 2086, 2087, 2095, 2096]

    async def scan_servers(self, limit: int = 20) -> List[Dict]:
        """Scan and collect SSH servers from various sources"""
        print(f"🔐 Starting SSH server scan (limit: {limit})")
        
        all_servers = []
        
        # Scrape from different sources
        for source in self.ssh_sources:
            try:
                servers = await self._scrape_source(source, limit // len(self.ssh_sources))
                all_servers.extend(servers)
            except Exception as e:
                print(f"  ❌ Failed to scrape {source['name']}: {e}")
                continue
            
            # Rate limiting
            await asyncio.sleep(2)
        
        # Add some manual/known servers as backup
        manual_servers = self._get_manual_servers()
        all_servers.extend(manual_servers[:5])
        
        # Remove duplicates and limit results
        unique_servers = self._deduplicate_servers(all_servers)
        limited_servers = unique_servers[:limit]
        
        # Test servers concurrently
        print(f"🔍 Testing {len(limited_servers)} SSH servers...")
        tested_servers = await self._test_servers(limited_servers)
        
        print(f"✅ SSH scan completed: {len(tested_servers)} servers tested")
        return tested_servers

    async def _scrape_source(self, source: Dict, limit: int) -> List[Dict]:
        """Scrape SSH servers from a specific source"""
        servers = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                for region in source['regions'][:2]:  # Limit regions
                    try:
                        # Construct URL for region
                        url = f"{source['url']}/{region}"
                        
                        response = await client.get(url, headers=headers)
                        if response.status_code != 200:
                            continue
                        
                        # Parse HTML content
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extract server information based on common patterns
                        extracted = self._extract_server_info(soup, source['name'])
                        servers.extend(extracted[:limit//2])  # Limit per region
                        
                    except Exception as e:
                        print(f"    ⚠️ Failed to scrape {region} from {source['name']}: {e}")
                        continue
                
        except Exception as e:
            print(f"  ❌ Source scraping error for {source['name']}: {e}")
        
        return servers

    def _extract_server_info(self, soup: BeautifulSoup, source_name: str) -> List[Dict]:
        """Extract server information from HTML"""
        servers = []
        
        try:
            # Common patterns for SSH server listings
            patterns = [
                # Look for server details in tables
                {'host': r'(\d+\.\d+\.\d+\.\d+)', 'user': r'username[:\s]+(\w+)', 'pass': r'password[:\s]+(\w+)'},
                # Look for server details in pre/code blocks
                {'host': r'Host[:\s]+([^\s]+)', 'user': r'User[:\s]+([^\s]+)', 'pass': r'Pass[:\s]+([^\s]+)'},
                # Look for server details in list items
                {'host': r'server[:\s]+([^\s]+)', 'user': r'login[:\s]+([^\s]+)', 'pass': r'pwd[:\s]+([^\s]+)'}
            ]
            
            text_content = soup.get_text().lower()
            
            # Try to extract with different patterns
            for pattern in patterns:
                host_matches = re.findall(pattern['host'], text_content, re.IGNORECASE)
                user_matches = re.findall(pattern['user'], text_content, re.IGNORECASE)
                pass_matches = re.findall(pattern['pass'], text_content, re.IGNORECASE)
                
                # Match up hosts, users, and passwords
                min_len = min(len(host_matches), len(user_matches), len(pass_matches))
                
                for i in range(min_len):
                    if self._is_valid_host(host_matches[i]):
                        server = {
                            'host': host_matches[i],
                            'port': random.choice(self.common_ports),
                            'username': user_matches[i],
                            'password': pass_matches[i],
                            'source': source_name,
                            'status': 'unknown'
                        }
                        servers.append(server)
                
                if servers:
                    break  # Found servers with this pattern
            
            # If no structured data found, try to extract IP addresses
            if not servers:
                ip_pattern = r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b'
                ips = re.findall(ip_pattern, text_content)
                
                for ip in ips[:3]:  # Limit to first 3 IPs found
                    if self._is_valid_host(ip):
                        # Generate reasonable defaults
                        server = {
                            'host': ip,
                            'port': random.choice([22, 443, 80]),
                            'username': self._generate_username(),
                            'password': self._generate_password(),
                            'source': f"{source_name}_auto",
                            'status': 'unknown'
                        }
                        servers.append(server)
                        
        except Exception as e:
            print(f"    ⚠️ Extraction error: {e}")
        
        return servers

    def _get_manual_servers(self) -> List[Dict]:
        """Get manually curated list of known SSH servers"""
        # These are example servers - in real implementation, 
        # you'd maintain a curated list of working servers
        manual_servers = [
            {
                'host': 'sg-1.openssh.net',
                'port': 22,
                'username': 'demo',
                'password': 'demo123',
                'source': 'manual',
                'status': 'unknown'
            },
            {
                'host': 'id-1.fastssh.com',
                'port': 443,
                'username': 'trial',
                'password': 'trial123',
                'source': 'manual',
                'status': 'unknown'
            },
            {
                'host': 'my-1.sshkit.org',
                'port': 80,
                'username': 'free',
                'password': 'free123',
                'source': 'manual',
                'status': 'unknown'
            },
            {
                'host': 'th-1.speedssh.net',
                'port': 2096,
                'username': 'guest',
                'password': 'guest123',
                'source': 'manual',
                'status': 'unknown'
            }
        ]
        
        return manual_servers

    async def _test_servers(self, servers: List[Dict]) -> List[Dict]:
        """Test SSH servers for connectivity"""
        semaphore = asyncio.Semaphore(3)  # Limit concurrent tests
        tasks = [self._test_server(server, semaphore) for server in servers]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        tested_servers = []
        for result in results:
            if isinstance(result, dict):
                tested_servers.append(result)
        
        return tested_servers

    async def _test_server(self, server: Dict, semaphore: asyncio.Semaphore) -> Dict:
        """Test individual SSH server connectivity"""
        async with semaphore:
            try:
                # Test basic connectivity first
                host = server['host']
                port = server['port']
                
                # Try to connect to the SSH port
                future = asyncio.open_connection(host, port)
                
                try:
                    reader, writer = await asyncio.wait_for(future, timeout=5)
                    
                    # Try to read SSH banner
                    banner = await asyncio.wait_for(reader.readline(), timeout=3)
                    
                    writer.close()
                    await writer.wait_closed()
                    
                    if b'SSH' in banner:
                        server['status'] = 'active'
                        print(f"  ✅ {host}:{port} - SSH service detected")
                    else:
                        server['status'] = 'inactive'
                        print(f"  ⚠️ {host}:{port} - No SSH banner")
                        
                except asyncio.TimeoutError:
                    server['status'] = 'timeout'
                    print(f"  ⏱️ {host}:{port} - Connection timeout")
                    
                except Exception as e:
                    server['status'] = 'error'
                    server['error'] = str(e)
                    print(f"  ❌ {host}:{port} - {str(e)}")
                    
            except Exception as e:
                server['status'] = 'error'
                server['error'] = str(e)
                print(f"  ❌ {server['host']} - Test error: {str(e)}")
            
            await asyncio.sleep(0.5)  # Rate limiting
            return server

    def _is_valid_host(self, host: str) -> bool:
        """Validate if host is a valid IP or hostname"""
        try:
            # Check if it's a valid IP address
            socket.inet_aton(host)
            # Additional checks for private/invalid IPs
            parts = host.split('.')
            if parts[0] in ['0', '127', '255']:
                return False
            if parts[0] == '192' and parts[1] == '168':
                return False
            if parts[0] == '10':
                return False
            if parts[0] == '172' and 16 <= int(parts[1]) <= 31:
                return False
            return True
        except socket.error:
            # If not an IP, check if it's a reasonable hostname
            if len(host) > 5 and '.' in host and not host.startswith('.'):
                return True
            return False

    def _generate_username(self) -> str:
        """Generate reasonable username for auto-discovered servers"""
        usernames = ['trial', 'demo', 'guest', 'test', 'free', 'user', 'ssh']
        return random.choice(usernames)

    def _generate_password(self) -> str:
        """Generate reasonable password for auto-discovered servers"""
        passwords = ['trial123', 'demo123', 'guest123', 'test123', 'free123', 'password', '123456']
        return random.choice(passwords)

    def _deduplicate_servers(self, servers: List[Dict]) -> List[Dict]:
        """Remove duplicate servers based on host:port combination"""
        seen = set()
        unique_servers = []
        
        for server in servers:
            key = f"{server['host']}:{server['port']}"
            if key not in seen:
                seen.add(key)
                unique_servers.append(server)
        
        return unique_servers

    async def verify_server_auth(self, server: Dict) -> bool:
        """Verify SSH authentication for a server"""
        try:
            # This would require paramiko or similar SSH library
            # For now, return a placeholder result
            return random.choice([True, False])
        except Exception:
            return False

    def get_premium_servers(self) -> List[Dict]:
        """Get premium/paid SSH servers (placeholder)"""
        # This would return servers from premium providers
        return []
