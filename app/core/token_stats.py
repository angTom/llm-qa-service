"""
Token用量统计
"""

from datetime import date, timezone

# 内存全局字典，存放每日统计数据
# key: 日期字符串 "2026-10-04"
# value: 当日统计对象 {call_count, prompt_tokens, completion_tokens, total_tokens}
token_stat: dict[str, dict] = {}

def init_day_status(day: str):
    """
    如果当天记录不存在,初始化一条新记录
    : param day: 日期字符串 "2026-10-04"
    """
    if day not in token_stat:
        token_stat[day] = {
            "call_count": 0,   # 当天调用次数
            "prompt_tokens": 0,  # 当天输入tokens总数
            "completion_tokens": 0, # 当天输出tokens总数
            "total_tokens": 0  # 当天总tokens数
        }

def add_token_stat(prompt_tokens: int, completion_tokens: int):
    """
    增加当天的token统计数据
    : param prompt_tokens: 本次调用的输入tokens数
    : param completion_tokens: 本次调用的输出tokens数
    """
    # 获取当天日期字符串
    today = date.today(timezone.utc).isoformat()
    # 判断当天记录是否存在,不存在则初始化
    init_day_status(today)
    token_stat[today]["call_count"] += 1
    token_stat[today]["prompt_tokens"] += prompt_tokens
    token_stat[today]["completion_tokens"] += completion_tokens
    token_stat[today]["total_tokens"] += (prompt_tokens + completion_tokens)

def get_token_stat() -> dict:
    """
    获取指定日期的token统计数据
    : param day: 日期字符串 "2026-10-04"
    : return: 当天统计对象 {call_count, prompt_tokens, completion_tokens, total_tokens}
    """
    today = date.today(timezone.utc).isoformat()
    init_day_status(today)
    return token_stat[today]
