#!/bin/bash

# 一键导出最近一个月的macOS日历日程到CSV文件

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到脚本所在目录
cd "$DIR"

# 计算开始日期（一个月前）
start_date=$(date -v-1m +%Y-%m-%d)
# 获取当前日期作为结束日期
end_date=$(date +%Y-%m-%d)

# 生成输出文件名
timestamp=$(date +%Y%m%d_%H%M%S)
output_file="最近一个月日历_${start_date}_to_${end_date}_${timestamp}.csv"

# 显示信息
echo "欢迎使用macOS日历一键导出工具！"
echo "=================================="
echo "本工具将导出从 $start_date 到 $end_date 的所有日历日程。"
echo ""
echo "开始导出日历日程，请稍候..."

# 执行导出命令
python3 calendar_export.py --start "$start_date" --end "$end_date" --output "$output_file"

# 导出完成后的提示
echo ""
echo "=================================="
echo "日历导出操作已完成！"
echo "导出的CSV文件保存在当前目录下：$output_file"
echo "您可以按回车键关闭此窗口。"
read -p "" dummy
