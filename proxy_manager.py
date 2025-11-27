"""
免费代理获取和管理模块
从多个免费代理网站获取代理列表，并测试可用性
"""
import requests
import random
import time
from typing import List, Dict, Optional
import re


class ProxyManager:
    """免费代理管理器"""

    def __init__(self):
        self.proxies = []
        self.working_proxies = []

    def fetch_proxies_from_proxy_list_download(self) -> List[Dict[str, str]]:
        """从 proxy-list.download 获取代理"""
        proxies = []

        try:
            # HTTP 代理
            url = "https://www.proxy-list.download/api/v1/get?type=http"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and ':' in line:
                        proxies.append({
                            'http': f'http://{line}',
                            'https': f'http://{line}'
                        })

            print(f"  - 从 proxy-list.download 获取到 {len(proxies)} 个代理")

        except Exception as e:
            print(f"  - 从 proxy-list.download 获取代理失败: {e}")

        return proxies

    def fetch_proxies_from_free_proxy_list(self) -> List[Dict[str, str]]:
        """从 free-proxy-list.net 获取代理"""
        proxies = []

        try:
            url = "https://free-proxy-list.net/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                # 使用正则表达式提取 IP:Port
                pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d+)</td>'
                matches = re.findall(pattern, response.text)

                for ip, port in matches[:50]:  # 只取前50个
                    proxy_url = f'http://{ip}:{port}'
                    proxies.append({
                        'http': proxy_url,
                        'https': proxy_url
                    })

            print(f"  - 从 free-proxy-list.net 获取到 {len(proxies)} 个代理")

        except Exception as e:
            print(f"  - 从 free-proxy-list.net 获取代理失败: {e}")

        return proxies

    def fetch_proxies_from_geonode(self) -> List[Dict[str, str]]:
        """从 geonode.com 获取代理（备用源）"""
        proxies = []

        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=lastChecked&sort_type=desc"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for item in data.get('data', []):
                    ip = item.get('ip')
                    port = item.get('port')
                    if ip and port:
                        proxy_url = f'http://{ip}:{port}'
                        proxies.append({
                            'http': proxy_url,
                            'https': proxy_url
                        })

            print(f"  - 从 geonode.com 获取到 {len(proxies)} 个代理")

        except Exception as e:
            print(f"  - 从 geonode.com 获取代理失败: {e}")

        return proxies

    def test_proxy(self, proxy: Dict[str, str], test_url: str = "https://www.google.com", timeout: int = 5) -> bool:
        """测试代理是否可用"""
        try:
            response = requests.get(
                test_url,
                proxies=proxy,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            return response.status_code == 200
        except:
            return False

    def fetch_all_proxies(self) -> List[Dict[str, str]]:
        """从所有源获取代理"""
        print("开始获取免费代理...")

        all_proxies = []

        # 从多个源获取
        all_proxies.extend(self.fetch_proxies_from_proxy_list_download())
        all_proxies.extend(self.fetch_proxies_from_free_proxy_list())
        all_proxies.extend(self.fetch_proxies_from_geonode())

        # 去重
        unique_proxies = []
        seen = set()

        for proxy in all_proxies:
            proxy_str = proxy.get('http', '')
            if proxy_str and proxy_str not in seen:
                seen.add(proxy_str)
                unique_proxies.append(proxy)

        print(f"总共获取到 {len(unique_proxies)} 个唯一代理")

        self.proxies = unique_proxies
        return unique_proxies

    def find_working_proxies(self, max_test: int = 20, max_working: int = 5) -> List[Dict[str, str]]:
        """测试并找到可用的代理"""
        print(f"开始测试代理（最多测试 {max_test} 个，找到 {max_working} 个可用代理）...")

        if not self.proxies:
            self.fetch_all_proxies()

        # 随机打乱代理列表
        test_proxies = random.sample(self.proxies, min(max_test, len(self.proxies)))

        working = []

        for i, proxy in enumerate(test_proxies, 1):
            if len(working) >= max_working:
                break

            print(f"  - 测试代理 {i}/{len(test_proxies)}: {proxy.get('http', '')[:50]}...", end=' ')

            if self.test_proxy(proxy):
                print("✓ 可用")
                working.append(proxy)
            else:
                print("✗ 不可用")

        self.working_proxies = working
        print(f"找到 {len(working)} 个可用代理")

        return working

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """获取一个随机的可用代理"""
        if not self.working_proxies:
            self.find_working_proxies()

        if self.working_proxies:
            return random.choice(self.working_proxies)

        return None

    def get_all_working_proxies(self) -> List[Dict[str, str]]:
        """获取所有可用代理"""
        if not self.working_proxies:
            self.find_working_proxies()

        return self.working_proxies


def get_proxy_for_request() -> Optional[Dict[str, str]]:
    """
    便捷函数：获取一个可用代理
    用于在其他模块中快速获取代理
    """
    manager = ProxyManager()
    return manager.get_random_proxy()


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("免费代理管理器测试")
    print("=" * 60)

    manager = ProxyManager()

    # 获取代理
    manager.fetch_all_proxies()

    # 测试代理
    working_proxies = manager.find_working_proxies(max_test=30, max_working=5)

    if working_proxies:
        print("\n可用代理列表：")
        for i, proxy in enumerate(working_proxies, 1):
            print(f"{i}. {proxy.get('http', '')}")
    else:
        print("\n未找到可用代理")

