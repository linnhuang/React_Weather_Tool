from datetime import datetime, timedelta, date
from tools.base import BaseTool
import re

class DateTool(BaseTool):
    name = "date_tool"
    description = (
        "计算日期。可以计算指定日期的前后日期，支持自然语言和标准格式。"
        "date: YYYY-MM-DD 或 自然语言（只支持：今天'今天'、'明天'、'昨天'、'一周'、'两周'、'半个月'、'一个月'、'N天后'、'N天前'、'N周后'、'N周前'、'now'、'today'、'tomorrow'、'yesterday'、'the day after tomorrow'、'the day before yesterday'、 'half a month'、'a month'、'this month'"
        "days: 距离前一个变量天数"
    )
    parameters = {
        "date": "string, 日期描述",
        "days": "integer, 要加减的天数，默认为0"
    }

    def run(self, date: str = "now", days: int = 0) -> str:
        base_date = self._parse_date(date)
        target_date = base_date + timedelta(days=int(days))
        return f"date={target_date.isoformat()}, weekday={target_date.strftime('%A')}"
    
    def _parse_date(self, date_str: str) -> date:
        """解析日期"""
        today = datetime.now().date()
        date_str = date_str.strip()
        
        # 1. 标准格式 YYYY-MM-DD
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass
        
        # 2. 关键词
        keywords = {
            "现在": 0, "now": 0,
            "今天": 0, "明天": 1, "昨天": -1,
            "today": 0, "tomorrow": 1, "yesterday": -1,
            "后天": 2, "前天": -2, 
            "the day after tomorrow":2, "the day before yesterday":-2,
            "半个月":15, "半月": 15, "一个月": 30,
            "half a month": 15, "a month":30, "this month":30,
        }
        if date_str in keywords:
            return today + timedelta(days=keywords[date_str])
        
        # 3. X天后 / X天前
        match = re.search(r"(\d+)\s*天后", date_str)
        if match:
            return today + timedelta(days=int(match.group(1)))
        
        match = re.search(r"(\d+)\s*天前", date_str)
        if match:
            return today - timedelta(days=int(match.group(1)))

        # 4. X周后 / X周前
        match = re.search(r"(\d+)\s*周后", date_str)
        if match:
            return today + timedelta(days=int(match.group(1))*7)
        
        match = re.search(r"(\d+)\s*周前", date_str)
        if match:
            return today - timedelta(days=int(match.group(1))*7)
        
        # 4. 无法解析
        raise ValueError(f"无法解析日期: '{date_str}'")

if __name__ == "__main__":
    tool = DateTool()
    now = tool.run()
    tomorrow = tool.run(date='tomorrow')
    specific = tool.run(date='2026-2-4', days=6)
    print(f"now\n{now}")
    print(f"tomorrow\n{tomorrow}")
    print(f"specific\n{specific}")

