# llm_client.py
# Google Gemini API와의 통신을 담당하는 클라이언트입니다.
# 필요한 라이브러리 설치: pip install google-generativeai

import google.generativeai as genai
from config import GEMINI_API_KEY

class GeminiClient:
    """Google Gemini 모델을 사용하기 위한 클라이언트 클래스."""
    def __init__(self, api_key):
        if not api_key or api_key == "YOUR_GEMINI_API_KEY":
            raise ValueError("Gemini API 키가 config.py에 설정되지 않았습니다.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        print("Gemini 클라이언트가 성공적으로 초기화되었습니다.")

    def generate_response(self, prompt):
        """주어진 프롬프트에 대한 모델의 응답을 생성합니다."""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API 호출 중 오류 발생: {e}")
            # 오류 발생 시, 에이전트가 멈추지 않도록 기본 행동을 반환합니다.
            return "DO: 잠시 생각에 잠긴다."

if __name__ == '__main__':
    # 이 파일이 직접 실행될 때 간단한 테스트를 수행합니다.
    try:
        client = GeminiClient(api_key=GEMINI_API_KEY)
        prompt = "하늘이 파란 이유를 간단히 설명해줘."
        response = client.generate_response(prompt)
        print(f"테스트 프롬프트: {prompt}")
        print(f"Gemini 응답: {response}")
    except ValueError as e:
        print(e)

