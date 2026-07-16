import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from tools.base import BaseTool
from tools.address_tool import AddressTool

load_dotenv()

class WeatherTool(BaseTool):
    name = "weather_tool"
    description = "查询指定日期和城市的天气"
    parameters = {
        "location": "string, optional, 城市名称，不提供则查询当前位置天气",
        "date": "string, optional, YYYY-MM-DD格式，默认为今天",
    }
    
    def __init__(self, weather_api: str = None):
        self.api_key = weather_api or os.getenv("OPENWEATHER_API_KEY")
        self.address_tool = AddressTool()
        # 需要配合 AddressTool 获取坐标
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.weather_url = "https://archive-api.open-meteo.com/v1/archive"  # 历史数据
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"        # 预报数据
    
    def run(self, location: str = None, 
            date: str = None,
            ) -> str:
        # 1. 解析地址（如果没有提供location，会自动获取当前位置）
        address_result = self.address_tool.run(location)
        
        # 2. 从结果中提取城市名
        city = self._extract_city(address_result)
        
        if not city:
            return f"无法确定城市: {address_result}"
        
        # 3. 查询天气
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        weather_data = self._search_weather(target_date, city)
        
        # 4. 组合返回
        return f"{address_result}\n\n{weather_data}"
    
    def _extract_city(self, result: str) -> str:
        """从AddressTool结果中提取城市名"""
        import re
        # 匹配 "城市: xxx" 或 "当前位置: xxx"
        match = re.search(r'(?:城市|当前位置):\s*([^\n]+)', result)
        if match:
            city = match.group(1).strip()
            # 移除可能的后缀（如 ", 区域"）
            city = city.split(',')[0].strip()
            return city
        return None
    
    def _search_weather(self, target_date: str, city: str) -> str:
        coordinates = self._get_coordinates(city=city)

        lat = coordinates[0]
        lon = coordinates[-1]
        
        return self._get_weather(lat=lat, lon=lon, date=target_date)

        
    def _get_coordinates(self, city: str) -> tuple:
        """获取城市经纬度"""
        try:
            response = requests.get(
                self.geocoding_url,
                params={"name": city, "count": 1, "language": "zh"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                result = data["results"][0]
                return result["latitude"], result["longitude"]
            else: 
                response = requests.get(
                    self.geocoding_url,
                    params={"name": city, "count": 1, "language": "en"},
                    timeout=10
                    )
                response.raise_for_status()
                data = response.json()
                if data.get("results"):
                    result = data["results"][0]
                    return result["latitude"], result["longitude"]
            
            return None, None
            
        except Exception as e:
            print(f"地理编码失败: {e}")
            return None, None
    
    def _get_weather(self, lat: float, lon: float, date: str) -> str:
        """获取天气数据"""
        target_dt = datetime.strptime(date, "%Y-%m-%d")
        today = datetime.now().date()
        days_diff = (target_dt.date() - today).days
        
        # 选择API
        if days_diff >= 0:
            # 未来或今天 → 使用预报API
            url = self.forecast_url
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                "timezone": "auto",
                "forecast_days": days_diff + 1 if days_diff <= 16 else 16
            }
        else:
            # 过去 → 使用历史API
            url = self.weather_url
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                "timezone": "auto",
                "start_date": date,
                "end_date": date
            }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._format_weather_data(data, date)
            
        except Exception as e:
            return f"天气查询失败: {e}"
    
    def _format_weather_data(self, data: dict, date: str) -> str:
        """格式化天气数据"""
        daily = data.get("daily", {})
        if not daily:
            return f"未找到 {date} 的天气数据"
        
        # 提取目标日期的数据
        dates = daily.get("time", [])
        if date not in dates:
            return f"未找到 {date} 的天气数据"
        
        idx = dates.index(date)
        temp_max = daily["temperature_2m_max"][idx]
        temp_min = daily["temperature_2m_min"][idx]
        weather_code = daily["weathercode"][idx]
        
        # 天气代码转文字
        weather_desc = self._code_to_description(weather_code)
        
        return (
            f"{date} 天气\n"
            f"最高温度: {temp_max}°C\n"
            f"最低温度: {temp_min}°C\n"
            f"天气状况: {weather_desc}"
        )
    
    def _code_to_description(self, code: int) -> str:
        """将WMO天气代码转为中文描述"""
        weather_codes = {
            0: "晴天",
            1: "主要晴天",
            2: "部分多云",
            3: "多云",
            45: "雾",
            48: "沉积雾",
            51: "小毛毛雨",
            53: "中毛毛雨",
            55: "大毛毛雨",
            61: "小雨",
            63: "中雨",
            65: "大雨",
            71: "小雪",
            73: "中雪",
            75: "大雪",
            80: "阵雨",
            81: "中阵雨",
            82: "大阵雨",
            95: "雷暴",
            96: "雷暴伴小冰雹",
            99: "雷暴伴大冰雹"
        }
        return weather_codes.get(code, f"未知天气代码({code})")

if __name__ == "__main__":
    tool = WeatherTool()
    weather = tool.run(location='Beijing', date='2026-07-10')
    print(f"weather\n{weather}")
