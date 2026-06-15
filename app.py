from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# [수정 완료] 스크린샷(37)에서 확인한 진짜 유저님의 구글 제미나이 API 키
GEMINI_API_KEY = "AQ.Ab8RN6LIotkvtab9DVZdWlkndNmKZ2QpnuwBF-D-eVHgxQg4fA"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

@app.route('/api/calorie', methods=['POST'])
def get_calorie():
    try:
        # 1. 카카오톡이 보내준 데이터 수집
        req = request.get_json()
        
        # 2. 카카오톡 파라미터에서 유저가 입력한 음식 이름(food) 추출
        food = req.get('action', {}).get('params', {}).get('food', '')
        
        if not food:
            return jsonify({
                "version": "2.0",
                "template": {
                    "outputs": [{"simpleText": {"text": "음식 이름을 정확히 인식하지 못했어요. 다시 시도해주세요."}}]
                }
            })

        # 3. 구글 제미나이 AI에게 보낼 질문(프롬프트) 작성
        prompt_text = (
            f"너는 전문 영양사야. 카카오톡 유저가 입력한 음식인 '{food}'에 대한 칼로리 정보를 친절하게 분석해줘.\n"
            f"답변은 카카오톡 창에서 읽기 편하게 반드시 아래 양식을 지켜서 딱 3줄 요약 코멘트로 보내줘.\n\n"
            f"[🤖 생성형 AI 실시간 분석]\n"
            f"• 음식명: {food}\n"
            f"• 예상 칼로리: [정확한 kcall 정보 기재]\n"
            f"• 영양사 한줄평: [이 음식을 먹을 때 건강을 위한 조언이나 팁 1문장]"
        )

        # 4. 제미나이 AI API 호출 양식 설정
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }

        # 5. 구글 서버로 전송 및 답변 받기
        response = requests.post(GEMINI_URL, headers=headers, json=payload)
        res_json = response.json()

        # 6. 제미na이 답변에서 텍스트만 쏙 빼내기
        ai_response = res_json['candidates'][0]['content']['parts'][0]['text']

    except Exception as e:
        # 에러 발생 시 카톡방에 띄워줄 에러 메시지
        ai_response = f"죄송합니다. 영양사 AI 서버 연동 중 오류가 발생했습니다.\n(사유: {str(e)})"

    # 7. 카카오톡 오픈빌더가 원하는 최종 규격(JSON)으로 응답 반환
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": ai_response
                    }
                }
            ]
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
