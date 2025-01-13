import json
import traceback

#Jeff3_Lin_RAG_HW1_20250108 +++
import re
#Jeff3_Lin_RAG_HW1_20250108 ---

#Jeff3_Lin_RAG_HW2_20250108 +++
import requests
#Jeff3_Lin_RAG_HW2_20250108 ---
#Jeff3_Lin_RAG_HW4_20250113 +++
import base64
from mimetypes import guess_type
#Jeff3_Lin_RAG_HW4_20250113 ---

from model_configurations import get_model_configuration

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

#Jeff3_Lin_RAG_HW3_20250109 +++
from langchain_core import memory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.base import RunnableMap
#Jeff3_Lin_RAG_HW3_20250109 ---

gpt_chat_version = 'gpt-4o'
gpt_config = get_model_configuration(gpt_chat_version)

#Jeff3_Lin_RAG_HW2_20250108 +++
# Calendarific API Key
API_KEY = "IAVnfFX0uGN2O7TZ1wl10IsGKDFNvElU"
API_URL = "https://calendarific.com/api/v2/holidays"
#Jeff3_Lin_RAG_HW2_20250108 ---

def generate_hw01(question):
    #Jeff3_Lin_RAG_HW1_20250107 +++
    # 建立回應問題的格式
    print(f"Question: {question}")
    # 呼叫 demo 函式獲取回應
    
    #Jeff3_Lin_RAG_HW3_20250109 +++
    #response = demo(question)
    response = demo(question, use_memory=False)
    #Jeff3_Lin_RAG_HW3_20250109 ---

    response_content = response.content
    
    # 將 response.content 使用 JSON 格式呈現
    formatted_question = (
    f"請將以下內容重新整理，並依照以下格式輸出為 JSON：\n"
    f"格式：\n"
    f'{{\n'
    f'    "Result": {{\n'
    f'        "date": "YYYY-MM-DD",\n'
    f'        "name": "事件名稱"\n'
    f'    }}\n'
    f'}}\n'
    f"輸出內容：{response_content}"
)
    ans = demo(formatted_question)
    
    #print(f"Formatted Response Content: {ans.content}")
    #Jeff3_Lin_RAG_HW1_20250107 ---
    #Jeff3_Lin_RAG_HW1_20250108 +++
    
    # 移除多餘格式
    clean_result = clean_json(ans.content)
    print(f"Cleaned JSON Content: {clean_result}")
    
    json_object = json.loads(clean_result)
    #if isinstance(json_object["Result"], list):
    #    json_object["Result"] = json_object["Result"][:1]
    #json_output = json.dumps(json_object, ensure_ascii=False)
    print(f"Debug: Final JSON Output: {json_object}")
    return json.dumps(json_object, ensure_ascii=False)
    
    # 回傳清理後的 JSON
    #return clean_result
           
    #Jeff3_Lin_RAG_HW1_20250108 ---
    
def generate_hw02(question):
    #Jeff3_Lin_RAG_HW2_20250108 +++
    print(f"Question: {question}")
    llm_parse_prompt = (
        f"請從以下問題中提取年份與月份，並生成適當的 API 調用參數格式：\n"
        f"問題：{question}\n"
        f"回應格式：\n"
        f'{{\n'
        f'    "year": "YYYY",\n'
        f'    "month": "MM"\n'
        f'}}'
    )
    #Jeff3_Lin_RAG_HW3_20250109 +++
    #parsed_response = demo(llm_parse_prompt)
    formatted_response = demo(llm_parse_prompt, use_memory=False)
    #Jeff3_Lin_RAG_HW3_20250109 ---
    
    # 打印 `parsed_response` 內容，檢查 LLM 回應
    print(f"Debug: LLM Parsed Response: {formatted_response.content}")
    clean_content = clean_json(formatted_response.content)
    
    parse_result = json.loads(clean_content)
    year = parse_result.get("year")
    month = parse_result.get("month")
    print(f"Parsed Year: {year}, Month: {month}")
    
    api_response = fetch_holidays_from_api(year, month)
    
    llm_format_prompt = (
        f"以下是 API 回應的原始資料，請將其整理為適當的 JSON 格式：\n"
        f"{json.dumps(api_response, ensure_ascii=False)}\n"
        f"回應格式：\n"
        f'{{\n'
        f'    "Result": [\n'
        f'        {{\n'
        f'            "date": "YYYY-MM-DD",\n'
        f'            "name": "事件名稱"\n'
        f'        }}\n'
        f'    ]\n'
        f'}}'
    )
    formatted_response = demo(llm_format_prompt)
    #print(f"Formatted Response Content: {formatted_response.content}")

    final_result = clean_json(formatted_response.content)
    print(f"Final Result (Cleaned): {final_result}")
    return json.dumps(json.loads(final_result), ensure_ascii=False)
    #Jeff3_Lin_RAG_HW2_20250108 ---

def generate_hw03(question2, question3):
   
    # 初始化記憶體
    memory = RunnableWithMessageHistory(RunnableMap({"llm": AzureChatOpenAI(**gpt_config)}))
    
    # 問題 2 的處理
    response_q2 = demo(question2, use_memory=True, memory=memory)
    print(f"Response to Question 2: {response_q2.content}")

    # 問題 3 的處理，使用相同的記憶體對象
    response_q3 = demo(question3, use_memory=True, memory=memory)
    print(f"Response to Question 3: {response_q3.content}")

    # 返回兩個問題的結果
    return {
        "question2_result": response_q2.content,
        "question3_result": response_q3.content
    }

#Jeff3_Lin_RAG_HW4_20250113 +++
def generate_hw04(question):
    image_path = 'baseball.png'
    data_url = local_image_to_data_url(image_path)
    api_url = f"{gpt_config['api_base']}openai/deployments/{gpt_config['deployment_name']}/chat/completions?api-version={gpt_config['api_version']}"
    api_key = gpt_config['api_key']
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "請問中華台北的積分是多少"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100,
        "stream": False
    }
    # 發送 POST 請求
    response = requests.post(api_url, headers=headers, data=json.dumps(payload))
    # 打印 response 物件
    #print("Response object:", response)
    
    # 解析回應
    response_json = response.json()
    # 打印 response_json 內容
    #print("Response JSON:", json.dumps(response_json, ensure_ascii=False, indent=2))
    
    answer = response_json['choices'][0]['message']['content']
    # 打印 answer 內容
    match = re.search(r'\d+', answer)
    score = int(match.group(0))
    result = {"Result": {"score": score}}
    
    # 打印結果
    #print(json.dumps(result, ensure_ascii=False))
    #print(json.dumps(result, ensure_ascii=False, indent=4))
    return json.dumps({"Result": {"score": score}}, ensure_ascii=False)
#Jeff3_Lin_RAG_HW4_20250113 +++
    
#Jeff3_Lin_RAG_HW3_20250109 +++
"""
def demo(question):
    llm = AzureChatOpenAI(
            model=gpt_config['model_name'],
            deployment_name=gpt_config['deployment_name'],
            openai_api_key=gpt_config['api_key'],
            openai_api_version=gpt_config['api_version'],
            azure_endpoint=gpt_config['api_base'],
            temperature=gpt_config['temperature']
    )
    message = HumanMessage(
            content=[
                {"type": "text", "text": question},
            ]
    )
    response = llm.invoke([message])
    
    return response
"""

def demo(question, use_memory=False, memory=None):
    """
    通用的 LLM 呼叫函式，支援動態決定是否啟用記憶功能。
    :param question: 問題文本
    :param use_memory: 是否啟用記憶功能
    :param memory: 傳入的記憶體物件（若 use_memory=True 時需要）
    :return: LLM 回應
    """
   
    # 初始化 LLM
    llm = AzureChatOpenAI(
        model=gpt_config['model_name'],
        deployment_name=gpt_config['deployment_name'],
        openai_api_key=gpt_config['api_key'],
        openai_api_version=gpt_config['api_version'],
        azure_endpoint=gpt_config['api_base'],
        temperature=gpt_config['temperature']
    )

    if use_memory:
        if not memory:
            raise ValueError("使用記憶功能時必須提供記憶體物件。")
        # 將 LLM 包裝到記憶模組
        llm_with_memory = RunnableWithMessageHistory(llm, memory=memory)
        response = llm_with_memory.invoke(question)
    else:
        # 單次呼叫 LLM
        message = HumanMessage(content=[{"type": "text", "text": question}])
        response = llm.invoke([message])

    return response
#Jeff3_Lin_RAG_HW3_20250109 ---

#Jeff3_Lin_RAG_HW1_20250108 +++
def clean_json(json_string):
    """移除多餘的格式，僅保留純 JSON"""
    match = re.search(r'```json\s*(\{.*\})\s*```', json_string, re.S)
    if match:
        return match.group(1).strip()  # 僅提取 JSON 內容部分
    return json_string
#Jeff3_Lin_RAG_HW1_20250108 ---

#Jeff3_Lin_RAG_HW2_20250108 +++
def fetch_holidays_from_api(year, month):
    """
    調用 Calendarific API 獲取假日資料。
    """

    params = {
        "api_key": API_KEY,
        "country": "TW",
        "year": year,
        #"type": "national"
    }
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # 過濾指定月份的假日資料
    holidays = data.get("response", {}).get("holidays", [])
    filtered_holidays = [
        {
            "date": holiday["date"]["iso"],
            "name": holiday["name"]
        }
        for holiday in holidays if holiday["date"]["datetime"]["month"] == int(month)
    ]
    return {"Result": filtered_holidays}
#Jeff3_Lin_RAG_HW2_20250108 ---

#Jeff3_Lin_RAG_HW4_20250113 +++
# Function to encode a local image into data URL
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream' # Default MIME type if none is found
    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')
    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"
#Jeff3_Lin_RAG_HW4_20250113 ---

#Jeff3_Lin_RAG_HW1_20250107 +++
generate_hw01('2024年台灣10月紀念日有哪些?')
#Jeff3_Lin_RAG_HW1_20250107 ---

#Jeff3_Lin_RAG_HW2_20250108 +++
generate_hw02("2024年台灣10月紀念日有哪些?")
#Jeff3_Lin_RAG_HW2_20250108 ---

#Jeff3_Lin_RAG_HW4_20250113 +++
# 執行 generate_hw04 函數
#question = "請問中華台北的積分是多少"
generate_hw04('請問中華台北的積分是多少')
#Jeff3_Lin_RAG_HW4_20250113 ---