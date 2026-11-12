# 모아공간 예약 관리 시스템

`4팀_다시책방(1).md`의 모아공간 제안서 F-01~F-05 기준으로 구성한 로컬 시연용 Streamlit 프로젝트입니다.

## 설치 및 실행

Python 3.11 이상 권장. 프로젝트 폴더에서 다음을 실행합니다.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\python -m pip install -r requirements.txt
# Windows PowerShell: .venv\Scripts\python -m streamlit run app.py
# macOS/Linux: .venv/bin/pip install -r requirements.txt
# macOS/Linux: .venv/bin/python -m streamlit run app.py
```

AI 챗봇을 사용하려면 Ollama를 별도로 설치하고 실행한 후 `.env.example`을 `.env`로 복사하고 모델명을 설정합니다.

```bash
ollama pull qwen3.5:2b-q4_K_M
```

`python smoke_test.py`로 예약 핵심 로직을 테스트할 수 있습니다. 이 테스트는 임시 CSV를 사용하며 실제 예약 파일을 수정하지 않습니다.

## 주요 파일

- `app.py`: Streamlit 화면 (공간 조회·예약, 내 예약·챗봇, 취소, 직원 현황)
- `reservation.py`: CSV 입출력, 예약 조건 검증, 중복 검사, 취소
- `chatbot.py`: Ollama 기반 예약 조회 전용 답변
- `data/spaces.csv`: 가상 공간 6개
- `data/reservations.csv`: 예약 데이터 (처음에는 빈 파일)

## 가정 및 미확정 사항

- 제안서에 운영 시간과 예약 단위의 구체적 숫자가 없어 **09:00~22:00, 30분 단위**를 시연 기본값으로 설정했습니다. 발주처 확정 후 `reservation.py` 상수를 변경하세요.
- 제안서 D-01은 취소된 시간 재예약을 허용하지만 4.5에서는 미정입니다. 현재는 D-01에 따라 허용합니다.
- 동시 접속은 지원하지 않습니다. CSV는 로컬 순차 사용을 전제로 합니다.
- 직원 화면에는 인증 기능이 없습니다(제안서의 로그인 제외 범위).
- Ollama 연결 장애가 발생해도 기본 예약 조회는 정상 동작합니다.
- Streamlit 1.67.0은 요청에 따라 명시했으며 설치 가능 여부는 별도 확인이 필요합니다.

## 외부 라이브러리

Streamlit (Apache-2.0), pandas (BSD-3-Clause), ollama Python (MIT), python-dotenv (BSD-3-Clause), httpx (BSD-3-Clause). 모델 라이선스는 선택한 Ollama 모델의 배포 조건을 확인하세요.
