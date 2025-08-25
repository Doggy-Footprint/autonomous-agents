# llm_integration.py
# Google Gemini API와의 통신을 담당합니다.
# 필요한 라이브러리 설치: pip install google-generativeai

import google.generativeai as genai
from config import GEMINI_API_KEY

# API 키 설정
genai.configure(api_key=GEMINI_API_KEY)

# 사용할 모델 설정
# text-only 입력을 위해 gemini-pro를 사용합니다.
model = genai.GenerativeModel('gemini-pro')

def get_llm_response(prompt):
    """주어진 프롬프트를 Gemini 모델에 보내고 응답 텍스트를 반환합니다."""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        print("오류: Gemini API 키가 설정되지 않았습니다. config.py 파일을 확인하세요.")
        # API 키가 없을 경우, 테스트를 위해 미리 정의된 응답을 반환합니다.
        return "휴게실로 이동하여 커피를 마신다."

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"LLM API 호출 중 오류 발생: {e}")
        return "오류로 인해 행동을 결정할 수 없습니다. 잠시 후 다시 시도합니다."

def generate_action_prompt(agent, recent_memories):
    """에이전트의 다음 행동을 결정하기 위한 프롬프트를 생성합니다."""
    
    # 프롬프트 엔지니어링: LLM이 역할에 몰입하고 원하는 형식으로 답변하게 유도
    prompt = f"""
당신은 '{agent.name}'이며, '{agent.description}' 역할을 수행하는 자율 에이전트입니다.
당신의 현재 위치는 '{agent.location}' 입니다.

---
다음은 당신의 최근 기억 일부입니다:
{recent_memories}
---

위 상황과 기억을 바탕으로, 지금 당장 수행할 가장 적절한 행동 하나를 서술형으로 간결하게 생성해주세요.
행동의 예시:
- "개발팀 자리에서 코딩을 계속한다."
- "휴게실로 이동하여 동료와 대화한다."
- "회의실로 가서 오늘 회의를 준비한다."

당신의 다음 행동은 무엇입니까?
"""
    return prompt

if __name__ == '__main__':
    # 모듈 테스트
    class MockAgent:
        def __init__(self):
            self.name = "TestAgent"
            self.description = "테스트용 에이전트"
            self.location = "가상 공간"
            
    agent = MockAgent()
    memories = "- [2025-08-25 21:12:00] '개발팀 자리'에는 John이(가) 있습니다."
    
    test_prompt = generate_action_prompt(agent, memories)
    print("--- 생성된 프롬프트 ---")
    print(test_prompt)
    
    print("\n--- LLM 응답 (테스트) ---")
    response = get_llm_response(test_prompt)
    print(response)

