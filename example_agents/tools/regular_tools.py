import json
import subprocess
# 工具的真正实现（实际项目中这里会调用天气 API）
def get_weather(city):
    weather_data = {
        "北京": {"temperature": 8, "condition": "多云"},
        "上海": {"temperature": 15, "condition": "晴"},
        "广州": {"temperature": 22, "condition": "阵雨"},
    }
    data = weather_data.get(city, {"temperature": "未知", "condition": "未知"})
    # json.dumps 把字典转成 JSON 字符串，ensure_ascii=False 让中文正常显示
    return json.dumps(data, ensure_ascii=False)


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"错误：文件 {path} 不存在"

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已写入 {path}"

def run_command(command):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, errors="replace", timeout=10
        )
        output = result.stdout
        # shell 惯例：返回码 0 表示成功，非 0 表示出错
        if result.returncode != 0:
            output += f"\n[错误] {result.stderr}"
        return output or "(无输出)"
    except subprocess.TimeoutExpired:
        return "[错误] 命令执行超时（10秒）"