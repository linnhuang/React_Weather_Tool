import requests
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from tools.base import BaseTool

load_dotenv()

class AddressTool(BaseTool):
    name = "address_tool"
    description = (
        "将地名解析为结构化的地址信息，提取城市、行政区等。"
        "如果不提供地点，会自动获取当前位置。"
    )
    parameters = {
        "location": "string, optional, 例如 '北京市海淀区' 或 'Shanghai'。不提供则获取当前位置"
    }

    def __init__(self, api_key = None):
        # 获取目标地址
        # self.geolocator = Nominatim(
        #     user_agent="ReAct_weather_agent/v1.0(contact: huanglinn@u.nus.edu)"
        # )
        self.geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        # IP定位服务（免费）
        self.ip_api_url = "http://ip-api.com/json/"
        # 备用方案：使用 ipinfo.io（需要token，但更准确）
        self.ipinfo_url = "https://ipinfo.io/json"
    
    def run(self, location: str = None) -> str:
        """解析地址，如果没有输入则获取当前位置"""
        
        # 1. 如果用户提供了地点，尝试解析
        if location and location.strip():
            result = self._geocode_location(location)
            if result and "解析成功" in result:  # 解析成功
                return result
            # 解析失败，记录日志，继续尝试获取当前位置
            print(f"地址 '{location}' 解析失败，回退到当前位置")
        
        # 2. 没有地点或解析失败 → 获取当前位置
        return self._get_current_location()

    def get_location_info(self, location: str = None):
        params = {
            "q": location,
            "limit": 1,
            "appid": self.api_key
        }
        
        try:
            response = requests.get(self.geocode_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return f"错误：OpenWeatherMap无法解析地址 '{location}'。"

            result = data[0]
            city = result.get('name')
            state = result.get('state')
            country = result.get('country')
            lat, lon = result.get('lat'), result.get('lon')
            
        except Exception as e:
            return f"地址解析请求失败: {e}"

    def _geocode_location(self, location: str) -> str:
        # """使用 Nominatim 解析地址"""
        """使用 OpenWeatherMap Geocoding API 解析地址"""
        params = {
            "q": location,
            "limit": 1,
            "appid": self.api_key
        }
        
        try:
            response = requests.get(self.geocode_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return f"错误：OpenWeatherMap无法解析地址 '{location}'。"

            result = data[0]
            city = result.get('name')
            state = result.get('state')
            country = result.get('country')
            lat, lon = result.get('lat'), result.get('lon')
            
            return (f"解析成功\n"
                    f"城市: {city}\n"
                    f"州/省: {state}\n"
                    f"国家: {country}\n"
                    f"坐标: ({lat:.4f}, {lon:.4f})")
        except Exception as e:
            return f"地址解析请求失败: {e}"

    
    def _get_current_location(self) -> str:
        """通过 IP 获取当前位置"""
        try:
            # 方案A: 使用 ip-api.com (免费，无需密钥)
            response = requests.get(self.ip_api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                city = data.get('city')
                region = data.get('regionName')
                country = data.get('country')
                lat = data.get('lat')
                lon = data.get('lon')
                timezone = data.get('timezone')
                
                return (
                    f"当前位置（通过IP定位）\n"
                    f"城市: {city}\n"
                    f"区域: {region}\n"
                    f"国家: {country}\n"
                    f"坐标: ({lat:.4f}, {lon:.4f})\n"
                    f"时区: {timezone}\n"
                    f"提示: 如需精确位置，请直接输入地名"
                )
            else:
                return "无法获取当前位置，请手动输入城市名称"
                
        except Exception as e:
            # 如果主方案失败，尝试备用方案
            return self._get_current_location_backup()
    
    def _get_current_location_backup(self, ipinfo_token=None) -> str:
        """备用方案：使用 ipinfo.io（需要免费token）"""
        try:
            token = ipinfo_token or os.getenv("IPINFO_TOKEN")
            if not token:
                return "无法获取当前位置（备用定位未配置），请手动输入城市名称"
            
            response = requests.get(
                f"https://ipinfo.io/json?token={token}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            city = data.get('city')
            region = data.get('region')
            country = data.get('country')
            loc = data.get('loc', '').split(',')
            lat, lon = loc[0] if len(loc) > 0 else None, loc[1] if len(loc) > 1 else None
            
            return (
                f"当前位置（通过IP定位）\n"
                f"城市: {city}\n"
                f"区域: {region}\n"
                f"国家: {country}\n"
                f"坐标: ({lat}, {lon})\n"
                f"提示: 如需精确位置，请直接输入地名(ipinfo)"
            )
            
        except Exception as e:
            return f"位置获取失败: {e}，请手动输入城市名称"

if __name__ == "__main__":
    tool = AddressTool()
    here = tool.run()
    shanghai = tool.run(location='shanghai, China')
    print(f"here\n{here}")
    print(f"shanghai\n{shanghai}")
    print(shanghai.lat, shanghai.lon)