#!/usr/bin/env python3
"""
Connection Checker
Test and validate tunnel connections
"""

import asyncio
import time
import socket
from typing import Dict, Optional, Tuple
import httpx
import subprocess
import json

class ConnectionChecker:
    def __init__(self):
        self.timeout = 10
        self.test_urls = [
            'https://httpbin.org/ip',
            'https://ipinfo.io/ip',
            'https://api.ipify.org',
            'https://icanhazip.com',
            'https://checkip.amazonaws.com'
        ]

    async def test_socks_connection(self, socks_port: int) -> Dict:
        """Test SOCKS proxy connection"""
        print(f"🔗 Testing SOCKS proxy on port {socks_port}")
        
        result = {
            'status': 'error',
            'socks_port': socks_port,
            'connection_successful': False,
            'external_ip': None,
            'response_time': None,
            'speed_rating': 'Unknown',
            'tests_passed': 0,
            'tests_total': 0,
            'error': None
        }
        
        try:
            # First, check if the SOCKS port is listening
            if not self._is_port_listening(socks_port):
                result['error'] = f"SOCKS port {socks_port} is not listening"
                return result
            
            # Test connection through SOCKS proxy
            start_time = time.time()
            connection_results = await self._test_through_socks(socks_port)
            total_time = time.time() - start_time
            
            result.update({
                'tests_total': len(self.test_urls),
                'tests_passed': connection_results['successful_tests'],
                'response_time': round(total_time * 1000, 2),
                'external_ip': connection_results.get('external_ip'),
                'connection_successful': connection_results['successful_tests'] > 0
            })
            
            # Determine speed rating
            if result['response_time']:
                if result['response_time'] < 1000:
                    result['speed_rating'] = 'Excellent'
                elif result['response_time'] < 3000:
                    result['speed_rating'] = 'Good'
                elif result['response_time'] < 5000:
                    result['speed_rating'] = 'Average'
                else:
                    result['speed_rating'] = 'Slow'
            
            if result['connection_successful']:
                result['status'] = 'success'
            else:
                result['status'] = 'failed'
                result['error'] = 'No successful connections through proxy'
            
        except Exception as e:
            result['error'] = str(e)
            result['status'] = 'error'
        
        return result

    def _is_port_listening(self, port: int) -> bool:
        """Check if a port is listening locally"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except Exception:
            return False

    async def _test_through_socks(self, socks_port: int) -> Dict:
        """Test internet connectivity through SOCKS proxy"""
        results = {
            'successful_tests': 0,
            'failed_tests': 0,
            'external_ip': None,
            'response_times': [],
            'errors': []
        }
        
        proxies = {
            'http://': f'socks5://127.0.0.1:{socks_port}',
            'https://': f'socks5://127.0.0.1:{socks_port}'
        }
        
        async with httpx.AsyncClient(
            proxies=proxies,
            timeout=self.timeout,
            verify=False
        ) as client:
            
            for url in self.test_urls:
                try:
                    start_time = time.time()
                    response = await client.get(url)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        results['successful_tests'] += 1
                        results['response_times'].append(response_time)
                        
                        # Try to extract IP from response
                        if not results['external_ip']:
                            try:
                                response_text = response.text.strip()
                                if self._is_valid_ip(response_text):
                                    results['external_ip'] = response_text
                                elif 'ip' in response_text.lower():
                                    # Try to parse JSON response
                                    try:
                                        json_data = json.loads(response_text)
                                        if 'origin' in json_data:
                                            results['external_ip'] = json_data['origin']
                                        elif 'ip' in json_data:
                                            results['external_ip'] = json_data['ip']
                                    except:
                                        pass
                            except:
                                pass
                    else:
                        results['failed_tests'] += 1
                        results['errors'].append(f"{url}: HTTP {response.status_code}")
                        
                except Exception as e:
                    results['failed_tests'] += 1
                    results['errors'].append(f"{url}: {str(e)}")
                
                # Small delay between requests
                await asyncio.sleep(0.5)
        
        return results

    def _is_valid_ip(self, text: str) -> bool:
        """Validate if text is a valid IP address"""
        import re
        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        return bool(re.match(ip_pattern, text.strip()))

    async def check_tunnel_health(self, socks_port: int) -> Dict:
        """Comprehensive tunnel health check"""
        print(f"🏥 Running tunnel health check on port {socks_port}")
        
        health_result = {
            'overall_status': 'unknown',
            'socks_proxy': {'status': 'unknown'},
            'internet_connectivity': {'status': 'unknown'},
            'dns_resolution': {'status': 'unknown'},
            'speed_test': {'status': 'unknown'},
            'recommendations': []
        }
        
        try:
            # 1. Check SOCKS proxy
            socks_test = await self.test_socks_connection(socks_port)
            health_result['socks_proxy'] = {
                'status': 'healthy' if socks_test['connection_successful'] else 'unhealthy',
                'details': socks_test
            }
            
            # 2. Check internet connectivity
            if socks_test['connection_successful']:
                health_result['internet_connectivity'] = {
                    'status': 'healthy',
                    'external_ip': socks_test.get('external_ip'),
                    'response_time': socks_test.get('response_time')
                }
            else:
                health_result['internet_connectivity'] = {
                    'status': 'unhealthy',
                    'error': 'No internet connectivity through proxy'
                }
            
            # 3. DNS resolution test
            dns_result = await self._test_dns_resolution(socks_port)
            health_result['dns_resolution'] = dns_result
            
            # 4. Speed test
            if socks_test['connection_successful']:
                speed_result = await self._basic_speed_test(socks_port)
                health_result['speed_test'] = speed_result
            
            # 5. Generate recommendations
            health_result['recommendations'] = self._generate_recommendations(health_result)
            
            # 6. Overall status
            if (health_result['socks_proxy']['status'] == 'healthy' and 
                health_result['internet_connectivity']['status'] == 'healthy'):
                health_result['overall_status'] = 'healthy'
            else:
                health_result['overall_status'] = 'unhealthy'
                
        except Exception as e:
            health_result['overall_status'] = 'error'
            health_result['error'] = str(e)
        
        return health_result

    async def _test_dns_resolution(self, socks_port: int) -> Dict:
        """Test DNS resolution through proxy"""
        try:
            # Test resolving a few common domains
            test_domains = ['google.com', 'facebook.com', 'github.com']
            
            proxies = {
                'http://': f'socks5://127.0.0.1:{socks_port}',
                'https://': f'socks5://127.0.0.1:{socks_port}'
            }
            
            successful_resolutions = 0
            
            async with httpx.AsyncClient(proxies=proxies, timeout=5) as client:
                for domain in test_domains:
                    try:
                        response = await client.head(f'https://{domain}')
                        if response.status_code < 500:
                            successful_resolutions += 1
                    except:
                        continue
            
            if successful_resolutions > 0:
                return {
                    'status': 'healthy',
                    'resolved_domains': successful_resolutions,
                    'total_tested': len(test_domains)
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': 'DNS resolution failed for all test domains'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def _basic_speed_test(self, socks_port: int) -> Dict:
        """Basic speed test through proxy"""
        try:
            # Download a small file to test speed
            test_url = 'https://httpbin.org/bytes/1024'  # 1KB test
            
            proxies = {
                'http://': f'socks5://127.0.0.1:{socks_port}',
                'https://': f'socks5://127.0.0.1:{socks_port}'
            }
            
            start_time = time.time()
            
            async with httpx.AsyncClient(proxies=proxies, timeout=30) as client:
                response = await client.get(test_url)
                
            if response.status_code == 200:
                duration = time.time() - start_time
                data_size = len(response.content)
                speed_kbps = (data_size / 1024) / duration if duration > 0 else 0
                
                return {
                    'status': 'healthy',
                    'duration_seconds': round(duration, 2),
                    'speed_kbps': round(speed_kbps, 2),
                    'data_transferred': data_size
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f'Speed test failed with HTTP {response.status_code}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _generate_recommendations(self, health_result: Dict) -> list:
        """Generate recommendations based on health check results"""
        recommendations = []
        
        if health_result['socks_proxy']['status'] == 'unhealthy':
            recommendations.append("SOCKS proxy is not working. Check if tunnel processes are running.")
        
        if health_result['internet_connectivity']['status'] == 'unhealthy':
            recommendations.append("No internet connectivity. Try a different SNI domain or SSH server.")
        
        if health_result['dns_resolution']['status'] == 'unhealthy':
            recommendations.append("DNS resolution issues detected. Consider using a different DNS server.")
        
        speed_status = health_result.get('speed_test', {}).get('status')
        if speed_status == 'unhealthy':
            recommendations.append("Connection speed is poor. Try a different server or check network conditions.")
        
        if not recommendations:
            recommendations.append("All systems are functioning normally!")
        
        return recommendations

    def get_process_info(self) -> Dict:
        """Get information about running tunnel processes"""
        info = {
            'stunnel_processes': [],
            'ssh_processes': [],
            'listening_ports': []
        }
        
        try:
            # Get stunnel processes
            result = subprocess.run(['pgrep', '-f', 'stunnel'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                stunnel_pids = result.stdout.strip().split('\n')
                info['stunnel_processes'] = [pid for pid in stunnel_pids if pid]
            
            # Get SSH processes
            result = subprocess.run(['pgrep', '-f', 'ssh.*-D'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                ssh_pids = result.stdout.strip().split('\n')
                info['ssh_processes'] = [pid for pid in ssh_pids if pid]
            
            # Get listening ports
            result = subprocess.run(['netstat', '-tlnp'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if '127.0.0.1:' in line and 'LISTEN' in line:
                        parts = line.split()
                        if len(parts) > 3:
                            address = parts[3]
                            if ':' in address:
                                port = address.split(':')[-1]
                                info['listening_ports'].append(int(port))
                                
        except Exception as e:
            info['error'] = str(e)
        
        return info

    async def monitor_connection(self, socks_port: int, duration_minutes: int = 5) -> Dict:
        """Monitor connection stability over time"""
        print(f"📊 Monitoring connection on port {socks_port} for {duration_minutes} minutes")
        
        monitor_result = {
            'duration_minutes': duration_minutes,
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'average_response_time': 0,
            'min_response_time': float('inf'),
            'max_response_time': 0,
            'connection_drops': 0,
            'stability_score': 0
        }
        
        test_interval = 30  # Test every 30 seconds
        total_tests = (duration_minutes * 60) // test_interval
        response_times = []
        
        for i in range(total_tests):
            try:
                test_result = await self.test_socks_connection(socks_port)
                monitor_result['total_tests'] += 1
                
                if test_result['connection_successful']:
                    monitor_result['successful_tests'] += 1
                    if test_result['response_time']:
                        response_times.append(test_result['response_time'])
                        monitor_result['min_response_time'] = min(
                            monitor_result['min_response_time'], 
                            test_result['response_time']
                        )
                        monitor_result['max_response_time'] = max(
                            monitor_result['max_response_time'], 
                            test_result['response_time']
                        )
                else:
                    monitor_result['failed_tests'] += 1
                    monitor_result['connection_drops'] += 1
                
                print(f"  Test {i+1}/{total_tests}: {'✅' if test_result['connection_successful'] else '❌'}")
                
            except Exception as e:
                monitor_result['failed_tests'] += 1
                print(f"  Test {i+1}/{total_tests}: ❌ Error - {e}")
            
            # Wait for next test
            if i < total_tests - 1:
                await asyncio.sleep(test_interval)
        
        # Calculate final statistics
        if response_times:
            monitor_result['average_response_time'] = sum(response_times) / len(response_times)
        
        if monitor_result['min_response_time'] == float('inf'):
            monitor_result['min_response_time'] = 0
        
        # Calculate stability score (0-100)
        if monitor_result['total_tests'] > 0:
            success_rate = (monitor_result['successful_tests'] / monitor_result['total_tests']) * 100
            monitor_result['stability_score'] = success_rate
        
        print(f"📊 Monitoring completed: {monitor_result['stability_score']:.1f}% stability")
        return monitor_result
