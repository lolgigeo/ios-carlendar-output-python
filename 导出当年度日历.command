#!/bin/bash

# 一键导出当年度macOS日历日程到CSV文件

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到脚本所在目录
cd "$DIR"

# 显示提示信息
echo "欢迎使用macOS日历一键导出工具！"
echo "=================================="

# 获取当前年份并设置日期范围
current_year=$(date +%Y)
start_date="${current_year}-01-01"
end_date="${current_year}-12-31"

# 显示导出信息
echo "本工具将导出${current_year}年度（${start_date} 至 ${end_date}）的所有日历日程。"
echo ""

# 询问是否要指定特定日历
echo "是否要指定特定日历进行导出？"
echo "1) 导出所有日历"
echo "2) 导出指定日历"
echo ""
read -p "请选择 (1-2): " calendar_choice

# 初始化变量
calendar_name=""

# 根据选择设置日历参数
case $calendar_choice in
    1)
        echo "您选择了导出所有日历"
        ;;
    2)
        read -p "请输入日历名称: " calendar_name
        ;;
    *)
        echo "将默认导出所有日历"
        ;;
esac

# 获取输出文件名
echo ""
read -p "请输入输出文件名 (默认为: ${current_year}年日历.csv): " output_file

# 如果没有指定输出文件名，则使用默认名称
if [ -z "$output_file" ]; then
    output_file="${current_year}年日历.csv"
fi

# 构建Python命令参数
python_cmd="python3 calendar_export.py --start $start_date --end $end_date --output $output_file"
if [ -n "$calendar_name" ]; then
    python_cmd+=" --calendar $calendar_name"
fi

# 执行导出命令
echo ""
echo "开始导出${current_year}年度日历日程，请稍候..."
echo "执行命令: $python_cmd"
echo ""

# 运行Python脚本
$python_cmd

# 导出完成后的提示
echo ""
echo "=================================="
echo "${current_year}年度日历导出操作已完成！"
echo "导出的CSV文件保存在当前目录下：$output_file"
echo "您可以按回车键关闭此窗口。"
read -p "" dummy
