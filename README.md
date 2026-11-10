# 대한민국 하천 범람 위험도 지도 (초기 프로토타입)

## 이 프로젝트가 하는 일
- 하천명으로 주변 지명을 검색합니다.
- 선택한 위치의 현재 강수량과 오늘 예상 강수량을 Open-Meteo에서 조회합니다.
- 지도에 선택 위치를 표시하고 시간별 강수 예보를 시각화합니다.
- 강수량 구간을 0~100의 **예비 위험지수**로 표시합니다.

## 중요한 한계
이 점수는 실제 범람 확률(%)이 아닙니다. 공식 홍수 예측 또는 대피 판단에 사용하면 안 됩니다.
하상계수는 전국 모든 하천에 대해 검증된 단일 공개 자동조회 자료가 연결되어 있지 않으므로, 확인되지 않은 값을 자동으로 만들어내지 않습니다.
실제 범람 위험 모델을 만들려면 수위·유량·하천 단면·제방고·상류 강수량·과거 홍수 자료를 확보하고 과거 사례로 검증해야 합니다.

## GitHub에 올릴 파일
- `app.py`
- `requirements.txt`
- `README.md`

## GitHub에 업로드한 뒤 웹사이트 배포하기
GitHub 저장소에 위 파일을 올린 다음:
1. https://share.streamlit.io/ 에 접속합니다.
2. GitHub 계정으로 로그인합니다.
3. `Create app`을 누릅니다.
4. 저장소, 브랜치(`main`), 메인 파일(`app.py`)을 선택합니다.
5. `Deploy`를 누릅니다.

배포 안내: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 데이터 출처
- Open-Meteo Geocoding: https://geocoding-api.open-meteo.com/
- Open-Meteo Forecast: https://open-meteo.com/en/docs
- 기상청 단기예보 API: https://www.data.go.kr/data/15084084/openapi.do

## 다음 개발 단계
1. WAMIS/홍수통제소 수위 관측소와 하천 구간 연결
2. 기상청 공식 관측·예보 API 연결
3. 출처가 검증된 하상계수 데이터베이스 구축
4. 과거 홍수 사례로 위험 모델 보정 및 검증
5. 하천 중심선과 위험 구간을 지도에 표시
