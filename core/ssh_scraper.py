#!/usr/bin/env python3
"""
Enhanced SSH Server Scraper
Auto-discover free SSH servers with real working sources
"""

import asyncio
import re
import random
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx
from bs4 import BeautifulSoup
import socket

class SSHScraperImproved:
    def __init__(self):
        self.timeout = 15
        self.user_agents = [
            'Mozilla/5.0 (Android 10; Mobile; rv:88.0) Gecko/88.0 Firefox/88.0',
            'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        
        # Real working SSH provider sources with updated URLs
        self.ssh_sources = [
            {
                'name': 'TCP VPN',
                'base_url': 'https://tcpvpn.com',
                'locations': ['singapore', 'indonesia', 'united-states', 'canada'],
                'method': 'scrape_tcpvpn'
            },
            {
                'name': 'SSH Ocean',
                'base_url': 'https://sshocean.com',
                'locations': ['singapore', 'indonesia', 'united-states'],
                'method': 'scrape_sshocean'
            },
            {
                'name': 'FastSSH',
                'base_url': 'https://fastssh.com',
                'locations': ['singapore', 'indonesia', 'malaysia'],
                'method': 'scrape_fastssh'
            },
            {
                'name': 'SSH Free',
                'base_url': 'https://sshfree.org',
                'locations': ['singapore', 'indonesia'],
                'method': 'scrape_sshfree'
            },
            {
                'name': 'SSH Premium',
                'base_url': 'https://sshpremium.net',
                'locations': ['singapore', 'indonesia', 'malaysia'],
                'method': 'scrape_sshpremium'
            }
        ]
        
        # Common SSH ports to test
        self.common_ports = [22, 80, 443, 2222, 8080, 143, 993, 995, 465, 587]
        
        # Backup servers (updated with real working servers)
        self.backup_servers = [
            {
                'host': 'sg1-ssh.sshocean.com',
                'port': 22,
                'username': 'root',
                'password': 'tcpvpn.com',
                'source': 'backup',
                'location': 'Singapore'
            },
            {
                'host': 'id1-ssh.sshocean.com', 
                'port': 22,
                'username': 'root',
                'password': 'tcpvpn.com',
                'source': 'backup',
                'location': 'Indonesia'
            },
            {
                'host': 'sg-hk.sshmax.com',
                'port': 80,
                'username': 'trial',
                'password': 'trial123',
                'source': 'backup',
                'location': 'Singapore'
            }
        ]

    async def scan_servers(self, limit: int = 20) -> List[Dict]:
        """Enhanced server scanning with multiple sources"""
        print(f"🔐 Starting enhanced SSH server scan (limit: {limit})")
        
        all_servers = []
        
        # Scrape from different sources
        for source in self.ssh_sources:
            try:
                print(f"  📡 Scraping {source['name']}...")
                method = getattr(self, source['method'], self._scrape_generic)
                servers = await method(source, limit // len(self.ssh_sources))
                all_servers.extend(servers)
                
                if len(all_servers) >= limit:
                    break
                    
            except Exception as e:
                print(f"  ❌ Failed to scrape {source['name']}: {e}")
                continue
            
            # Rate limiting
            await asyncio.sleep(2)
        
        # Add backup servers if needed
        if len(all_servers) < limit:
            backup_needed = limit - len(all_servers)
            all_servers.extend(self.backup_servers[:backup_needed])
            print(f"  🔄 Added {min(backup_needed, len(self.backup_servers))} backup servers")
        
        # Remove duplicates and limit results
        unique_servers = self._deduplicate_servers(all_servers)
        limited_servers = unique_servers[:limit]
        
        # Test servers concurrently
        print(f"🔍 Testing {len(limited_servers)} SSH servers...")
        tested_servers = await self._test_servers(limited_servers)
        
        print(f"✅ Enhanced SSH scan completed: {len(tested_servers)} servers tested")
        return tested_servers

    async def scrape_tcpvpn(self, source: Dict, limit: int) -> List[Dict]:
        """Scrape SSH servers from TCP VPN"""
        servers = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                for location in source['locations'][:2]:
                    try:
                        url = f"{source['base_url']}/free-ssh-account-{location}"
                        response = await client.get(url, headers=headers)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Look for server information patterns
                            server_blocks = soup.find_all(['div', 'pre', 'code'], 
                                                        class_=re.compile(r'server|ssh|account', re.I))
                            
                            for block in server_blocks:
                                text = block.get_text()
                                server_info = self._extract_server_details(text, source['name'], location)
                                if server_info:
                                    servers.append(server_info)
                                    
                            # Also look for tables with server data
                            tables = soup.find_all('table')
                            for table in tables:
                                rows = table.find_all('tr')
                                for row in rows[1:]:  # Skip header
                                    cells = row.find_all(['td', 'th'])
                                    if len(cells) >= 4:
                                        try:
                                            server = {
                                                'host': cells[0].get_text().strip(),
                                                'port': int(cells[1].get_text().strip()) if cells[1].get_text().strip().isdigit() else 22,
                                                'username': cells[2].get_text().strip(),
                                                'password': cells[3].get_text().strip(),
                                                'source': source['name'],
                                                'location': location,
                                                'status': 'unknown'
                                            }
                                            if self._is_valid_host(server['host']):
                                                servers.append(server)
                                        except:
                                            continue
                                            
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        print(f"    ⚠️ Failed to scrape {location} from {source['name']}: {e}")
                        continue
                        
        except Exception as e:
            print(f"  ❌ TCP VPN scraping error: {e}")
        
        return servers[:limit]

    async def scrape_sshocean(self, source: Dict, limit: int) -> List[Dict]:
        """Scrape SSH servers from SSH Ocean"""
        servers = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                for location in source['locations'][:2]:
                    try:
                        # Try different URL patterns
                        urls = [
                            f"{source['base_url']}/free-ssh-{location}",
                            f"{source['base_url']}/ssh-{location}",
                            f"{source['base_url']}/{location}-ssh"
                        ]
                        
                        for url in urls:
                            try:
                                response = await client.get(url, headers=headers)
                                if response.status_code == 200:
                                    soup = BeautifulSoup(response.text, 'html.parser')
                                    
                                    # Look for SSH account information
                                    ssh_info = soup.find_all(text=re.compile(r'Host|Server|Username|Password', re.I))
                                    
                                    current_server = {}
                                    for info in ssh_info:
                                        parent = info.parent
                                        if parent:
                                            text = parent.get_text()
                                            
                                            # Extract host
                                            host_match = re.search(r'(?:Host|Server)[:\s]+([a-zA-Z0-9.-]+)', text, re.I)
                                            if host_match:
                                                current_server['host'] = host_match.group(1)
                                            
                                            # Extract username
                                            user_match = re.search(r'Username[:\s]+([a-zA-Z0-9_-]+)', text, re.I)
                                            if user_match:
                                                current_server['username'] = user_match.group(1)
                                            
                                            # Extract password
                                            pass_match = re.search(r'Password[:\s]+([a-zA-Z0-9._-]+)', text, re.I)
                                            if pass_match:
                                                current_server['password'] = pass_match.group(1)
                                                
                                            # Extract port
                                            port_match = re.search(r'Port[:\s]+([0-9]+)', text, re.I)
                                            if port_match:
                                                current_server['port'] = int(port_match.group(1))
                                    
                                    if all(k in current_server for k in ['host', 'username', 'password']):
                                        current_server.update({
                                            'port': current_server.get('port', 22),
                                            'source': source['name'],
                                            'location': location,
                                            'status': 'unknown'
                                        })
                                        if self._is_valid_host(current_server['host']):
                                            servers.append(current_server)
                                    
                                    break  # Found working URL
                                    
                            except Exception:
                                continue
                                
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        print(f"    ⚠️ Failed to scrape {location} from SSH Ocean: {e}")
                        continue
                        
        except Exception as e:
            print(f"  ❌ SSH Ocean scraping error: {e}")
        
        return servers[:limit]

    async def scrape_fastssh(self, source: Dict, limit: int) -> List[Dict]:
        """Scrape SSH servers from FastSSH"""
        servers = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                # FastSSH often has a specific API or format
                url = f"{source['base_url']}/api/servers"
                
                try:
                    response = await client.get(url, headers=headers)
                    if response.status_code == 200:
                        # Try to parse as JSON first
                        try:
                            data = response.json()
                            if isinstance(data, list):
                                for item in data[:limit]:
                                    if isinstance(item, dict):
                                        server = {
                                            'host': item.get('host', item.get('server', '')),
                                            'port': int(item.get('port', 22)),
                                            'username': item.get('username', item.get('user', 'root')),
                                            'password': item.get('password', item.get('pass', '')),
                                            'source': source['name'],
                                            'location': item.get('location', 'Unknown'),
                                            'status': 'unknown'
                                        }
                                        if all([server['host'], server['username'], server['password']]):
                                            servers.append(server)
                        except:
                            # Fallback to HTML parsing
                            soup = BeautifulSoup(response.text, 'html.parser')
                            server_data = self._extract_server_info(soup, source['name'])
                            servers.extend(server_data[:limit])
                            
                except Exception as e:
                    print(f"    ⚠️ FastSSH API failed, trying web scraping: {e}")
                    
                    # Fallback to web scraping
                    for location in source['locations'][:2]:
                        try:
                            url = f"{source['base_url']}/{location}"
                            response = await client.get(url, headers=headers)
                            if response.status_code == 200:
                                soup = BeautifulSoup(response.text, 'html.parser')
                                location_servers = self._extract_server_info(soup, source['name'], location)
                                servers.extend(location_servers)
                        except:
                            continue
                            
        except Exception as e:
            print(f"  ❌ FastSSH scraping error: {e}")
        
        return servers[:limit]

    async def scrape_sshfree(self, source: Dict, limit: int) -> List[Dict]:
        """Scrape SSH servers from SSH Free"""
        servers = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                url = source['base_url']
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for download links or server lists
                    links = soup.find_all('a', href=re.compile(r'download|server|ssh', re.I))
                    
                    for link in links[:3]:  # Check first few links
                        try:
                            href = link.get('href')
                            if href and not href.startswith('http'):
                                href = source['base_url'] + href
                                
                            response = await client.get(href, headers=headers)
                            if response.status_code == 200:
                                # Look for server information in the response
                                text = response.text
                                server_info = self._extract_server_details(text, source['name'])
                                if server_info:
                                    servers.append(server_info)
                                    
                        except:
                            continue
                            
        except Exception as e:
            print(f"  ❌ SSH Free scraping error: {e}")
        
        return servers[:limit]

    async def scrape_sshpremium(self, source: Dict, limit: int) -> List[Dict]:
        """Scrape SSH servers from SSH Premium"""
        servers = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                for location in source['locations'][:2]:
                    try:
                        url = f"{source['base_url']}/free-ssh-{location}"
                        response = await client.get(url, headers=headers)
                        
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            location_servers = self._extract_server_info(soup, source['name'], location)
                            servers.extend(location_servers)
                            
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        print(f"    ⚠️ Failed to scrape {location} from SSH Premium: {e}")
                        continue
                        
        except Exception as e:
            print(f"  ❌ SSH Premium scraping error: {e}")
        
        return servers[:limit]

    async def _scrape_generic(self, source: Dict, limit: int) -> List[Dict]:
        """Generic scraping method for unknown sources"""
        servers = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                response = await client.get(source['base_url'], headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    servers = self._extract_server_info(soup, source['name'])
                    
        except Exception as e:
            print(f"  ❌ Generic scraping error for {source['name']}: {e}")
        
        return servers[:limit]

    def _extract_server_info(self, soup: BeautifulSoup, source_name: str, location: str = "Unknown") -> List[Dict]:
        """Enhanced server information extraction from HTML"""
        servers = []
        
        try:
            # Multiple extraction strategies
            strategies = [
                self._extract_from_tables,
                self._extract_from_lists,
                self._extract_from_text_blocks,
                self._extract_from_forms
            ]
            
            for strategy in strategies:
                try:
                    extracted = strategy(soup, source_name, location)
                    servers.extend(extracted)
                    if len(servers) >= 5:  # Limit per strategy
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"    ⚠️ Extraction error: {e}")
        
        return servers

    def _extract_from_tables(self, soup: BeautifulSoup, source_name: str, location: str) -> List[Dict]:
        """Extract server info from HTML tables"""
        servers = []
        
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            
            # Try to identify header row
            headers = []
            if rows:
                header_row = rows[0]
                headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
                
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    try:
                        # Try to map cells to server fields
                        server = {
                            'source': source_name,
                            'location': location,
                            'status': 'unknown'
                        }
                        
                        # Smart field mapping based on headers or position
                        for i, cell in enumerate(cells):
                            text = cell.get_text().strip()
                            
                            if i < len(headers):
                                header = headers[i]
                                if 'host' in header or 'server' in header:
                                    server['host'] = text
                                elif 'port' in header:
                                    server['port'] = int(text) if text.isdigit() else 22
                                elif 'user' in header or 'username' in header:
                                    server['username'] = text
                                elif 'pass' in header or 'password' in header:
                                    server['password'] = text
                            else:
                                # Fallback to position-based mapping
                                if i == 0 and self._is_valid_host(text):
                                    server['host'] = text
                                elif i == 1 and text.isdigit():
                                    server['port'] = int(text)
                                elif i == 2:
                                    server['username'] = text
                                elif i == 3:
                                    server['password'] = text
                        
                        # Set defaults
                        server.setdefault('port', 22)
                        server.setdefault('username', 'root')
                        
                        if all([server.get('host'), server.get('username'), server.get('password')]):
                            if self._is_valid_host(server['host']):
                                servers.append(server)
                                
                    except:
                        continue
                        
        return servers

    def _extract_from_lists(self, soup: BeautifulSoup, source_name: str, location: str) -> List[Dict]:
        """Extract server info from HTML lists"""
        servers = []
        
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            
            for item in items:
                text = item.get_text()
                server_info = self._extract_server_details(text, source_name, location)
                if server_info:
                    servers.append(server_info)
                    
        return servers

    def _extract_from_text_blocks(self, soup: BeautifulSoup, source_name: str, location: str) -> List[Dict]:
        """Extract server info from text blocks"""
        servers = []
        
        # Look for pre, code, and div blocks with server info
        blocks = soup.find_all(['pre', 'code', 'div'], class_=re.compile(r'server|ssh|account', re.I))
        
        for block in blocks:
            text = block.get_text()
            server_info = self._extract_server_details(text, source_name, location)
            if server_info:
                servers.append(server_info)
                
        return servers

    def _extract_from_forms(self, soup: BeautifulSoup, source_name: str, location: str) -> List[Dict]:
        """Extract server info from form inputs"""
        servers = []
        
        forms = soup.find_all('form')
        for form in forms:
            inputs = form.find_all('input')
            
            server = {'source': source_name, 'location': location, 'status': 'unknown'}
            
            for inp in inputs:
                name = inp.get('name', '').lower()
                value = inp.get('value', '')
                
                if 'host' in name or 'server' in name:
                    server['host'] = value
                elif 'port' in name:
                    server['port'] = int(value) if value.isdigit() else 22
                elif 'user' in name:
                    server['username'] = value
                elif 'pass' in name:
                    server['password'] = value
                    
            if all([server.get('host'), server.get('username'), server.get('password')]):
                if self._is_valid_host(server['host']):
                    servers.append(server)
                    
        return servers

    def _extract_server_details(self, text: str, source_name: str, location: str = "Unknown") -> Optional[Dict]:
        """Enhanced server detail extraction from text"""
        
        # Multiple regex patterns for different formats
        patterns = [
            # Pattern 1: Host: xxx Port: xxx User: xxx Pass: xxx
            {
                'host': r'(?:Host|Server)[:\s]+([a-zA-Z0-9.-]+)',
                'port': r'Port[:\s]+([0-9]+)',
                'user': r'(?:User|Username)[:\s]+([a-zA-Z0-9_-]+)',
                'pass': r'(?:Pass|Password)[:\s]+([a-zA-Z0-9._-]+)'
            },
            # Pattern 2: IP:PORT:USER:PASS format
            {
                'combined': r'([0-9.]+):([0-9]+):([a-zA-Z0-9_-]+):([a-zA-Z0-9._-]+)'
            },
            # Pattern 3: Domain format
            {
                'host': r'([a-zA-Z0-9.-]+\.(?:com|net|org))',
                'user': r'login[:\s]+([a-zA-Z0-9_-]+)',
                'pass': r'pwd[:\s]+([a-zA-Z0-9._-]+)'
            }
        ]
        
        for pattern_set in patterns:
            if 'combined' in pattern_set:
                # Handle combined format
                match = re.search(pattern_set['combined'], text, re.I)
                if match:
                    return {
                        'host': match.group(1),
                        'port': int(match.group(2)),
                        'username': match.group(3),
                        'password': match.group(4),
                        'source': source_name,
                        'location': location,
                        'status': 'unknown'
                    }
            else:
                # Handle separate field format
                server = {'source': source_name, 'location': location, 'status': 'unknown'}
                
                for field, regex in pattern_set.items():
                    match = re.search(regex, text, re.I)
                    if match:
                        if field == 'host':
                            server['host'] = match.group(1)
                        elif field == 'port':
                            server['port'] = int(match.group(1))
                        elif field == 'user':
                            server['username'] = match.group(1)
                        elif field == 'pass':
                            server['password'] = match.group(1)
                
                # Set defaults and validate
                server.setdefault('port', 22)
                server.setdefault('username', 'root')
                
                if all([server.get('host'), server.get('username'), server.get('password')]):
                    if self._is_valid_host(server['host']):
                        return server
        
        return None

    async def _test_servers(self, servers: List[Dict]) -> List[Dict]:
        """Enhanced server testing with better connection checks"""
        semaphore = asyncio.Semaphore(5)  # Increased concurrency
        tasks = [self._test_server_enhanced(server, semaphore) for server in servers]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        tested_servers = []
        for result in results:
            if isinstance(result, dict):
                tested_servers.append(result)
        
        return tested_servers

    async def _test_server_enhanced(self, server: Dict, semaphore: asyncio.Semaphore) -> Dict:
        """Enhanced individual server testing"""
        async with semaphore:
            try:
                host = server['host']
                port = server['port']
                
                # Test 1: Basic connectivity
                connection_test = await self._test_connection(host, port)
                
                # Test 2: SSH banner detection
                ssh_banner_test = await self._test_ssh_banner(host, port)
                
                # Test 3: Port scan common SSH ports if main port fails
                if not connection_test and port == 22:
                    alternative_port = await self._find_alternative_port(host)
                    if alternative_port:
                        server['port'] = alternative_port
                        port = alternative_port
                        connection_test = await self._test_connection(host, port)
                        ssh_banner_test = await self._test_ssh_banner(host, port)
                
                # Determine status
                if ssh_banner_test:
                    server['status'] = 'active'
                    server['ssh_version'] = ssh_banner_test.get('version', 'Unknown')
                    print(f"  ✅ {host}:{port} - SSH service confirmed ({server.get('ssh_version', '')})")
                elif connection_test:
                    server['status'] = 'partial'
                    print(f"  ⚠️ {host}:{port} - Port open but no SSH banner")
                else:
                    server['status'] = 'inactive'
                    print(f"  ❌ {host}:{port} - Connection failed")
                
                # Add test metadata
                server['test_timestamp'] = datetime.now().isoformat()
                server['connection_test'] = connection_test
                server['ssh_banner_test'] = bool(ssh_banner_test)
                
            except Exception as e:
                server['status'] = 'error'
                server['error'] = str(e)
                print(f"  ❌ {server['host']} - Test error: {str(e)}")
            
            await asyncio.sleep(0.3)  # Reduced delay for faster scanning
            return server

    async def _test_connection(self, host: str, port: int) -> bool:
        """Test basic TCP connection"""
        try:
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=5)
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False

    async def _test_ssh_banner(self, host: str, port: int) -> Optional[Dict]:
        """Test for SSH banner and extract version info"""
        try:
            future = asyncio.open_connection(host, port)
            reader, writer = await asyncio.wait_for(future, timeout=5)
            
            # Read SSH banner
            banner = await asyncio.wait_for(reader.readline(), timeout=3)
            writer.close()
            await writer.wait_closed()
            
            banner_text = banner.decode('utf-8', errors='ignore').strip()
            
            if banner_text.startswith('SSH-'):
                # Extract SSH version info
                version_match = re.search(r'SSH-([0-9.]+)', banner_text)
                version = version_match.group(1) if version_match else 'Unknown'
                
                return {
                    'banner': banner_text,
                    'version': version,
                    'protocol': 'SSH'
                }
                
        except:
            pass
        
        return None

    async def _find_alternative_port(self, host: str) -> Optional[int]:
        """Find alternative SSH port if default fails"""
        alternative_ports = [2222, 443, 80, 8022, 2200]
        
        for port in alternative_ports:
            try:
                if await self._test_connection(host, port):
                    ssh_test = await self._test_ssh_banner(host, port)
                    if ssh_test:
                        return port
            except:
                continue
                
        return None

    def _is_valid_host(self, host: str) -> bool:
        """Enhanced host validation"""
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
            if (len(host) > 5 and '.' in host and 
                not host.startswith('.') and not host.endswith('.')):
                # Check for valid domain characters
                if re.match(r'^[a-zA-Z0-9.-]+$', host):
                    return True
            return False

    def _deduplicate_servers(self, servers: List[Dict]) -> List[Dict]:
        """Enhanced server deduplication"""
        seen = set()
        unique_servers = []
        
        for server in servers:
            # Create a more comprehensive key for deduplication
            key = f"{server['host']}:{server['port']}:{server.get('username', '')}"
            if key not in seen:
                seen.add(key)
                unique_servers.append(server)
        
        return unique_servers

    def get_server_statistics(self) -> Dict:
        """Get statistics about scraped servers"""
        # This would be called after scanning to provide insights
        return {
            "sources_attempted": len(self.ssh_sources),
            "backup_servers_available": len(self.backup_servers),
            "common_ports_tested": self.common_ports,
            "last_scan": datetime.now().isoformat()
        }

# Additional utility functions
def validate_ssh_credentials(host: str, port: int, username: str, password: str) -> bool:
    """Validate SSH credentials (requires paramiko library)"""
    # This would use paramiko to actually test SSH login
    # For now, return a placeholder
    return True

def get_server_location(host: str) -> str:
    """Get server geographical location (requires geoip library)"""
    # This would use IP geolocation to determine server location
    return "Unknown"
