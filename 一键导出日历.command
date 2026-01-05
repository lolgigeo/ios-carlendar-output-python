#!/bin/bash

# 一键导出macOS日历日程到CSV文件

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到脚本所在目录
cd "$DIR"

# 显示提示信息
echo "欢迎使用macOS日历一键导出工具！"
echo "=================================="
echo "本工具将帮助您导出macOS系统日历中的日程记录。"
echo ""
echo "请选择导出方式："
echo "1) 导出所有日历的所有日程"
echo "2) 导出指定时间范围内的日程"
echo "3) 导出指定日历的所有日程"
echo "4) 导出指定日历和时间范围内的日程"
echo "5) 导出当年度日历"
echo "6) 导出去年度日历"
echo ""

# 获取用户选择
read -p "请输入选项编号 (1-6): " choice

# 初始化变量
calendar_name=""
start_date=""
end_date=""
output_file=""

# 根据用户选择设置参数
case $choice in
    1)
        echo "您选择了导出所有日历的所有日程"
        ;;
    2)
        echo "您选择了导出指定时间范围内的日程"
        read -p "请输入开始日期 (格式: YYYY-MM-DD): " start_date
        read -p "请输入结束日期 (格式: YYYY-MM-DD): " end_date
        ;;
    3)
        echo "您选择了导出指定日历的所有日程"
        read -p "请输入日历名称: " calendar_name
        ;;
    4)
        echo "您选择了导出指定日历和时间范围内的日程"
        read -p "请输入日历名称: " calendar_name
        read -p "请输入开始日期 (格式: YYYY-MM-DD): " start_date
        read -p "请输入结束日期 (格式: YYYY-MM-DD): " end_date
        ;;
    5)
        # 导出当年度日历
        current_year=$(date +%Y)
        start_date="${current_year}-01-01"
        end_date="${current_year}-12-31"
        echo "您选择了导出${current_year}年度日历 (${start_date} 至 ${end_date})"
        ;;
    6)
        # 导出去年度日历
        last_year=$(date -v-1y +%Y)
        start_date="${last_year}-01-01"
        end_date="${last_year}-12-31"
        echo "您选择了导出${last_year}年度日历 (${start_date} 至 ${end_date})"
        ;;
    *)
        echo "无效的选项，将默认导出所有日历的所有日程"
        ;;
esac

# 获取输出文件名
echo ""
read -p "请输入输出文件名 (默认为自动生成): " output_file

# 构建Python命令参数
python_cmd="python3 calendar_export.py"
if [ -n "$calendar_name" ]; then
    python_cmd+=" --calendar $calendar_name"
fi
if [ -n "$start_date" ]; then
    python_cmd+=" --start $start_date"
fi
if [ -n "$end_date" ]; then
    python_cmd+=" --end $end_date"
fi
if [ -n "$output_file" ]; then
    python_cmd+=" --output $output_file"
fi

# 执行导出命令
echo ""
echo "开始导出日历日程，请稍候..."
echo "执行命令: $python_cmd"
echo ""

# 运行Python脚本
$python_cmd

# 导出完成后的提示
echo ""
echo "=================================="
echo "日历导出操作已完成！"
echo "导出的CSV文件保存在当前目录下。"
echo "您可以按回车键关闭此窗口。"
read -p "" dummy
