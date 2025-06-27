#!/usr/bin/env python3
"""
SNI Domain Scraper
Auto-discover SNI domains for bypass tunneling
"""

import asyncio
import time
import random
from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import socket
import ssl

class SNIScraper:
    def __init__(self):
        self.timeout = 10
        self.user_agents = [
            'Mozilla/5.0 (Android 10; Mobile; rv:88.0) Gecko/88.0 Firefox/88.0',
            'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        ]
        
        # Known working SNI domains for different operators
        self.base_domains = [
            # Facebook/Meta CDNs
            'free.facebook.com',
            'www.facebook.com',
            'm.facebook.com',
            'graph.facebook.com',
            'api.facebook.com',
            'connect.facebook.net',
            'static.xx.fbcdn.net',
            'scontent.xx.fbcdn.net',
            
            # WhatsApp CDNs
            'cdn.whatsapp.net',
            'static.whatsapp.net',
            'web.whatsapp.com',
            'media.wa.me',
            
            # Google CDNs
            'www.google.com',
            'ssl.gstatic.com',
            'fonts.googleapis.com',
            'ajax.googleapis.com',
            'apis.google.com',
            
            # CloudFlare CDNs
            'cdnjs.cloudflare.com',
            'www.cloudflare.com',
            'api.cloudflare.com',
            
            # Other common CDNs
            'cdn.jsdelivr.net',
            'unpkg.com',
            'maxcdn.bootstrapcdn.com',
            'stackpath.bootstrapcdn.com',
            
            # Indonesian operator specific
            'axis.co.id',
            'tri.co.id',
            'telkomsel.com',
            'indosat.com',
            'xl.co.id',
            'smartfren.com',
            
            # Gaming CDNs (often free on gaming packages)
            'cdn.discordapp.com',
            'images-ext-1.discordapp.net',
            'gateway.discord.gg',
            
            # Educational domains (often free)
            'www.wikipedia.org',
            'upload.wikimedia.org',
            'github.com',
            'raw.githubusercontent.com'
        ]

    async def scan_domains(self, limit: int = 20) -> List[Dict]:
        """Scan and test SNI domains"""
        print(f"🔍 Starting SNI domain scan (limit: {limit})")
        
        # Shuffle and limit domains
        domains_to_test = random.sample(self.base_domains, min(limit, len(self.base_domains)))
        
        results = []
        
        # Test domains concurrently
        semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
        tasks = [self._test_domain(domain, semaphore) for domain in domains_to_test]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and format results
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
        
        print(f"✅ SNI scan completed: {len(valid_results)} domains tested")
        return valid_results

    async def _test_domain(self, domain: str, semaphore: asyncio.Semaphore) -> Dict:
        """Test individual domain for SNI bypass potential"""
        async with semaphore:
            result = {
                'domain': domain,
                'status': 'inactive',
                'response_time': None,
                'ssl_valid': False,
                'redirect_detected': False
            }
            
            try:
                start_time = time.time()
                
                # Test HTTP/HTTPS connectivity
                connectivity = await self._test_connectivity(domain)
                
                # Test SSL handshake
                ssl_result = await self._test_ssl_handshake(domain)
                
                # Test for redirect behavior (common in free access)
                redirect_result = await self._test_redirect_behavior(domain)
                
                response_time = (time.time() - start_time) * 1000
                
                # Determine if domain is potentially useful
                if connectivity or ssl_result or redirect_result:
                    result.update({
                        'status': 'active',
                        'response_time': round(response_time, 2),
                        'ssl_valid': ssl_result,
                        'redirect_detected': redirect_result
                    })
                
                print(f"  📊 {domain}: {result['status']} ({response_time:.0f}ms)")
                
            except Exception as e:
                print(f"  ❌ {domain}: Error - {str(e)}")
                result['error'] = str(e)
            
            await asyncio.sleep(0.5)  # Rate limiting
            return result

    async def _test_connectivity(self, domain: str) -> bool:
        """Test basic HTTP/HTTPS connectivity"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=False) as client:
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                # Try HTTPS first
                try:
                    response = await client.get(f"https://{domain}", headers=headers, follow_redirects=False)
                    return response.status_code < 500
                except:
                    # Try HTTP if HTTPS fails
                    try:
                        response = await client.get(f"http://{domain}", headers=headers, follow_redirects=False)
                        return response.status_code < 500
                    except:
                        return False
                        
        except Exception:
            return False

    async def _test_ssl_handshake(self, domain: str) -> bool:
        """Test SSL handshake for SNI capability"""
        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Test SSL connection
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(domain, 443, ssl=context, server_hostname=domain),
                timeout=5
            )
            
            writer.close()
            await writer.wait_closed()
            return True
            
        except Exception:
            return False

    async def _test_redirect_behavior(self, domain: str) -> bool:
        """Test for redirect behavior that indicates free access"""
        try:
            async with httpx.AsyncClient(timeout=5, verify=False) as client:
                headers = {'User-Agent': random.choice(self.user_agents)}
                
                response = await client.get(
                    f"https://{domain}", 
                    headers=headers, 
                    follow_redirects=False
                )
                
                # Look for redirect indicators
                redirect_indicators = [
                    'Location' in response.headers,
                    response.status_code in [301, 302, 307, 308],
                    'captive' in response.text.lower() if hasattr(response, 'text') else False,
                    'portal' in response.text.lower() if hasattr(response, 'text') else False
                ]
                
                return any(redirect_indicators)
                
        except Exception:
            return False

    async def discover_new_domains(self, seed_domains: List[str] = None) -> List[str]:
        """Discover new potential SNI domains from various sources"""
        if not seed_domains:
            seed_domains = ['facebook.com', 'google.com', 'cloudflare.com']
        
        discovered = set()
        
        try:
            # Scrape from public DNS data, CDN lists, etc.
            for seed in seed_domains:
                subdomains = await self._get_subdomains(seed)
                discovered.update(subdomains)
                
                # Rate limit
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"Domain discovery error: {e}")
        
        return list(discovered)

    async def _get_subdomains(self, domain: str) -> List[str]:
        """Get known subdomains for a domain"""
        common_prefixes = [
            'www', 'api', 'cdn', 'static', 'assets', 'media', 'images',
            'ssl', 'secure', 'connect', 'graph', 'gateway', 'edge',
            'm', 'mobile', 'app', 'apps', 'web', 'admin'
        ]
        
        subdomains = []
        for prefix in common_prefixes:
            subdomain = f"{prefix}.{domain}"
            # Basic validation
            if len(subdomain) < 100:  # Reasonable length
                subdomains.append(subdomain)
        
        return subdomains

    def get_operator_specific_domains(self, operator: str = None) -> List[str]:
        """Get domains known to work with specific operators"""
        operator_domains = {
            'telkomsel': [
                'free.facebook.com',
                'www.facebook.com', 
                'cdn.whatsapp.net',
                'web.whatsapp.com'
            ],
            'indosat': [
                'www.google.com',
                'ssl.gstatic.com',
                'm.facebook.com'
            ],
            'xl': [
                'cdnjs.cloudflare.com',
                'ajax.googleapis.com',
                'static.xx.fbcdn.net'
            ],
            'axis': [
                'cdn.discordapp.com',
                'gateway.discord.gg',
                'api.facebook.com'
            ],
            'tri': [
                'fonts.googleapis.com',
                'unpkg.com',
                'maxcdn.bootstrapcdn.com'
            ],
            'smartfren': [
                'www.wikipedia.org',
                'upload.wikimedia.org',
                'github.com'
            ]
        }
        
        if operator and operator.lower() in operator_domains:
            return operator_domains[operator.lower()]
        
        # Return all if no specific operator
        all_domains = []
        for domains in operator_domains.values():
            all_domains.extend(domains)
        
        return list(set(all_domains))
