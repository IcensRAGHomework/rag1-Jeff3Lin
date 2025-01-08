import json
import traceback

#Jeff3_Lin_RAG_HW1_20250108 +++
import re
#Jeff3_Lin_RAG_HW1_20250108 ---

#Jeff3_Lin_RAG_HW2_20250108 +++
import requests
#Jeff3_Lin_RAG_HW2_20250108 ---

from model_configurations import get_model_configuration

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

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
    response = demo(question)
    #print(f"Raw Response from Demo: {response.content}")
    #print(f"response.content: {response.content}")
    response_content = response.content
    #print(f"Original Response Content: {response_content}")
    #print(f"response_content: {response_content}")
    
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
    #print(f"Cleaned JSON Content: {clean_result}")
    
    json_object = json.loads(clean_result)
    if isinstance(json_object["Result"], list):
        json_object["Result"] = json_object["Result"][:1]
    #json_output = json.dumps(json_object, ensure_ascii=False)
    #print(f"Debug: Final JSON Output: {json_output}")
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
    parsed_response = demo(llm_parse_prompt)
    # 打印 `parsed_response` 內容，檢查 LLM 回應
    #print(f"Debug: LLM Parsed Response: {parsed_response.content}")
    clean_content = clean_json(parsed_response.content)
    
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
    pass
    
def generate_hw04(question):
    pass
    
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

#Jeff3_Lin_RAG_HW1_20250107 +++
#generate_hw01('2024年台灣10月紀念日有哪些?')
#Jeff3_Lin_RAG_HW1_20250107 ---

#Jeff3_Lin_RAG_HW2_20250108 +++
generate_hw02("2024年台灣10月紀念日有哪些?")
#Jeff3_Lin_RAG_HW2_20250108 ---