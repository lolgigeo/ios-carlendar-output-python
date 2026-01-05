#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import csv
import datetime
import argparse
import os

"""
macOS 日历导出工具

功能：
- 导出 macOS 系统日历中的所有日程记录
- 支持按照时间范围筛选导出
- 将日程信息（名称、时间、描述等）保存为 CSV 格式

使用方法：
- 直接运行：导出所有日历的所有日程
- 指定时间范围：python3 calendar_export.py --start 2023-01-01 --end 2023-12-31
- 指定日历名称：python3 calendar_export.py --calendar "工作"
"""

def run_applescript(script):
    """执行 AppleScript 脚本并返回结果"""
    try:
        # 先尝试运行Calendar应用程序（如果未运行）
        subprocess.run(['open', '-g', '-a', 'Calendar'], check=False)
        # 给Calendar应用一些时间启动
        import time
        time.sleep(1)
        
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript 执行错误: {e}")
        print(f"错误输出: {e.stderr}")
        sys.exit(1)

def export_calendar_events(calendar_name=None, start_date=None, end_date=None):
    """
    导出指定日历和时间范围内的事件
    
    参数:
    - calendar_name: 日历名称，None 表示所有日历
    - start_date: 开始日期，格式为 YYYY-MM-DD
    - end_date: 结束日期，格式为 YYYY-MM-DD
    
    返回:
    - 事件列表
    """
    # 构建日历筛选条件
    calendar_filter = "" if calendar_name is None else f"whose name is \"{calendar_name}\""
    
    # 使用简单可靠的AppleScript，避免复杂的嵌套条件
    # 不使用自定义函数，避免语法问题
    script = f'''
    tell application "Calendar"
        set eventList to ""
        set allCals to every calendar {calendar_filter}
        
        repeat with cal in allCals
            set calName to name of cal
            set allEvents to every event of cal
            
            repeat with ev in allEvents
                try
                    -- 获取事件基本信息
                    set eventName to summary of ev
                    set eventStart to start date of ev
                    set eventEnd to end date of ev
                    
                    -- 处理可能为空的字段
                    set eventDescription to ""
                    try
                        set eventDescription to description of ev
                        if eventDescription is missing value then set eventDescription to ""
                    end try
                    
                    set eventLocation to ""
                    try
                        set eventLocation to location of ev
                        if eventLocation is missing value then set eventLocation to ""
                    end try
                    
                    -- 格式化日期时间为ISO格式字符串
                    -- 这里使用更简单的日期格式化方式，避免复杂的文本操作
                    set formattedStart to (year of eventStart as text) & "-" & ¬
                        text -2 thru -1 of ("0" & (month of eventStart as number)) & "-" & ¬
                        text -2 thru -1 of ("0" & day of eventStart) & " " & ¬
                        text -2 thru -1 of ("0" & hours of eventStart) & ":" & ¬
                        text -2 thru -1 of ("0" & minutes of eventStart)
                    
                    set formattedEnd to (year of eventEnd as text) & "-" & ¬
                        text -2 thru -1 of ("0" & (month of eventEnd as number)) & "-" & ¬
                        text -2 thru -1 of ("0" & day of eventEnd) & " " & ¬
                        text -2 thru -1 of ("0" & hours of eventEnd) & ":" & ¬
                        text -2 thru -1 of ("0" & minutes of eventEnd)
                    
                    -- 直接构建事件字符串，避免自定义函数
                    set eventText to calName & "||" & eventName & "||" & formattedStart & "||" & formattedEnd & "||" & eventDescription & "||" & eventLocation
                    
                    -- 添加到结果列表，使用换行符分隔
                    if eventList is not "" then
                        set eventList to eventList & "\n"
                    end if
                    set eventList to eventList & eventText
                end try
            end repeat
        end repeat
        
        return eventList
    end tell
    '''
    
    result = run_applescript(script)
    if not result:  # 如果没有事件
        return []
    
    # 解析结果
    events = []
    
    # 分割事件，每个事件由换行符分隔
    event_lines = result.split('\n')
    
    # 转换开始和结束日期为datetime对象，用于筛选
    start_dt = None
    end_dt = None
    if start_date:
        start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)  # 包含当天结束
    
    for line in event_lines:
        line = line.strip()
        if not line:  # 跳过空行
            continue
        
        try:
            # 使用双竖线分隔字段
            parts = line.split('||', 5)
            if len(parts) >= 5:
                # 清理字段值
                def clean_field(field):
                    if not field:
                        return ""
                    # 清理可能的空值标记
                    if field.strip() == "missing value":
                        return ""
                    return field.strip()
                
                # 提取字段
                calendar = clean_field(parts[0])
                summary = clean_field(parts[1])
                start_date_str = clean_field(parts[2])
                end_date_str = clean_field(parts[3])
                description = clean_field(parts[4] if len(parts) > 4 else '')
                location = clean_field(parts[5] if len(parts) > 5 else '')
                
                # 检查是否需要进行日期筛选
                include_event = True
                if start_dt or end_dt:
                    try:
                        # 解析事件日期
                        event_start_dt = datetime.datetime.strptime(start_date_str, '%Y-%m-%d %H:%M')
                        
                        # 应用日期筛选
                        if start_dt and event_start_dt < start_dt:
                            include_event = False
                        if end_dt and event_start_dt >= end_dt:
                            include_event = False
                    except ValueError:
                        # 如果日期解析失败，默认包含该事件
                        pass
                
                if include_event:
                    events.append({
                        'calendar': calendar,
                        'summary': summary,
                        'start_date': start_date_str,
                        'end_date': end_date_str,
                        'description': description,
                        'location': location
                    })
        except Exception as e:
            print(f"解析事件时出错: {e}, 事件行: {line}")
            continue
    
    return events

def save_to_csv(events, filename):
    """将事件列表保存为 CSV 文件"""
    if not events:
        print("没有找到符合条件的日历事件")
        return
    
    headers = ['日历名称', '日程名称', '开始时间', '结束时间', '日程描述', '地点']
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            # 使用csv模块的writer对象，配置QUOTE_ALL确保所有字段都被正确引用
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            
            # 写入表头
            writer.writerow(headers)
            
            # 写入事件数据
            for event in events:
                # 提取并清理每个字段
                calendar = event.get('calendar', '').strip()
                summary = event.get('summary', '').strip()
                start_date = event.get('start_date', '').strip()
                end_date = event.get('end_date', '').strip()
                description = event.get('description', '').strip()
                location = event.get('location', '').strip()
                
                # 写入一行数据
                writer.writerow([calendar, summary, start_date, end_date, description, location])
        
        print(f"成功导出 {len(events)} 个日历事件到 {filename}")
    except Exception as e:
        print(f"保存 CSV 文件时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='导出 macOS 日历事件到 CSV')
    parser.add_argument('--calendar', help='指定要导出的日历名称')
    parser.add_argument('--start', help='开始日期，格式 YYYY-MM-DD')
    parser.add_argument('--end', help='结束日期，格式 YYYY-MM-DD')
    parser.add_argument('--output', help='输出 CSV 文件名', default=None)
    args = parser.parse_args()
    
    # 验证日期格式
    if args.start:
        try:
            datetime.datetime.strptime(args.start, '%Y-%m-%d')
        except ValueError:
            print("开始日期格式错误，请使用 YYYY-MM-DD 格式")
            sys.exit(1)
    
    if args.end:
        try:
            datetime.datetime.strptime(args.end, '%Y-%m-%d')
        except ValueError:
            print("结束日期格式错误，请使用 YYYY-MM-DD 格式")
            sys.exit(1)
    
    # 生成输出文件名
    if args.output:
        output_file = args.output
    else:
        # 默认文件名包含日期范围信息
        current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        time_range = ""
        if args.start and args.end:
            time_range = f"_{args.start}_to_{args.end}"
        elif args.start:
            time_range = f"_from_{args.start}"
        elif args.end:
            time_range = f"_to_{args.end}"
        
        output_file = f"calendar_events{time_range}_{current_time}.csv"
    
    # 导出事件
    print("正在导出日历事件...")
    if args.calendar:
        print(f"日历: {args.calendar}")
    else:
        print("日历: 所有日历")
        
    if args.start:
        print(f"开始日期: {args.start}")
    if args.end:
        print(f"结束日期: {args.end}")
    
    events = export_calendar_events(args.calendar, args.start, args.end)
    save_to_csv(events, output_file)

if __name__ == '__main__':
    main()
