import os
from openai import OpenAI

# 在根目录下创建.env 文件写入API_KEY 和 BASE_URL
# 这样可以不用配置电脑环境变量（注意不要把.env提交到git上了）
# 这行会把 .env 文件里的内容加载到 os.environ 中
from dotenv import load_dotenv

load_dotenv() # 把 .env 文件里的内容加载到 os.environ 中

# 从环境变量读取，避免把 API Key 硬编码到代码里
API_KEY = os.environ.get("API_KEY")
BASE_URL = os.environ.get("BASE_URL")
if not API_KEY or not BASE_URL:
    raise RuntimeError("请先设置环境变量 API_KEY 和 BASE_URL")

# 本轮对话历史
message_history = ""

class UserMessage:
    def __init__(self, user_msg, thinking_mode="disabled", thinking_strength = "medium"):
        self.user_msg = user_msg
        self.thinking_mode = thinking_mode
        self.thinking_strength = thinking_strength


# 接受用户信息
def build_user_message():

    # 1. 用户的 prompt
    user_input=input("你：")
    if user_input == "q":
        return "q"

    message_history.append({"role": "user", "content": user_input})

    # 思考模式相关（是否开启思考，思考强度）
    # DS的思考模式不支持 temperature、presence_penalty、frequency_penalty 参数
    thinking_option="disabled"
    user_thinking_option = input("是否启用思考模式？(y/n): ").strip().lower()
    if user_thinking_option == "y":
        thinking_option = "enabled"

    # 2. 思考强度选择
    thinking_strength = "medium"  # 默认中等强度
    if thinking_option == "enabled":
        user_strength_option = input("选择思考强度 (low/medium/high): ").strip().lower()
        if user_strength_option in ["low", "medium", "high"]:
            thinking_strength = user_strength_option
        else:
            print("无效的强度选项，使用默认值 medium。")

    return UserMessage(user_input, thinking_option, thinking_strength)

def get_response(user_message, client):
    global message_history

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=message_history,
        reasoning_effort=user_message.thinking_strength,
        extra_body={"thinking": {"type": user_message.thinking_mode}}
    )

    reply = response.choices[0].message.content
    # reasoning_content = response.choices[0].message.reasoning_content，openai接口本身不包含这个参数，所以确保没有是是none
    reasoning_content = getattr(response.choices[0].message, "reasoning_content", None)

    # 官方文档的写法：messages.append(response.choices[0].message)
    message_history.append({"role": "assistant", "content": reply})

    print(f"AI: {reply}\n")

def get_response_stream(user_message, client):

    global message_history

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=message_history,
        reasoning_effort=user_message.thinking_strength,
        stream=True,
        extra_body={"thinking": {"type": user_message.thinking_mode}}
    )

    reply = ""
    reasoning_content = ""

    print("AI:",end="")
    for chunk in response:
        delta = chunk.choices[0].delta
        delta_reasoning = getattr(delta, "reasoning_content", None)
        if delta_reasoning:
            reasoning_content += delta_reasoning
        else:
            reply_part = delta.content
            if reply_part is not None:
                reply += reply_part
                print(f"{reply_part}", end="", flush=True)

    # 模型默认会忽略掉 reasoning_content
    message_history.append({"role": "assistant", "reasoning_content": reasoning_content, "content": reply})

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
SYSTEM_PROMPT = "You`re a funny guy who always answer in Chinese"

message_history = [{
    "role": "system",
    "content": SYSTEM_PROMPT
}]

print(f"[人设]{SYSTEM_PROMPT}")
print("输入消息开始聊天，输入 q 退出\n")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
SYSTEM_PROMPT = "You`re a funny guy who always answer in Chinese"

message_history = [{
    "role": "system",
    "content": SYSTEM_PROMPT
}]

while True:
    user_message = build_user_message()
    if user_message == "q":
        break

    is_stream = input("选择流式输出(y/n): ").strip().lower()
    if is_stream == "y":
        get_response_stream(user_message, client)
        print()
    elif is_stream == "n":
        get_response(user_message, client)
    else:
        print("输入无效，默认采用流式输出")
        get_response_stream(user_message, client)