# 모아공간 예약 관리 시스템

원하는 날짜와 시간에 이용할 수 있는 회의실·연습실을 찾아 예약하는 로컬 시연용 Streamlit 앱입니다. 이용자는 예약 ID와 예약자명으로 자신의 예약을 조회하거나 취소할 수 있고, 운영 직원은 날짜와 공간별로 예약 현황을 확인할 수 있습니다. 공간 정보와 예약 내역은 CSV 파일에 저장합니다.

## 주요 기능

| 기능 | 사용 방법 |
| --- | --- |
| F-01 공간 조회 | 이용일, 시간대, 인원, 공간 유형을 입력해 예약 가능한 공간을 찾습니다. |
| F-02 예약 신청 | 조회 결과에서 공간을 선택하고 예약을 확정하면 조회·취소에 사용할 예약 ID를 받습니다. |
| F-03 예약 취소 | 예약 ID와 예약자명으로 예약을 확인한 뒤 이용 시작 전까지 취소할 수 있습니다. |
| F-04 예약 조회 | 이용자는 본인 예약의 상세 정보와 취소 가능 여부를 확인합니다. 운영 직원은 선택한 날짜와 공간의 확정·취소 내역을 조회합니다. |
| F-05 AI 챗봇 | 예약 ID와 예약자명으로 조회한 예약 한 건에 대해 질문하면 Ollama 챗봇이 해당 예약 정보를 바탕으로 답합니다. |

## 빠른 실행

Python이 설치된 Windows 환경에서 저장소를 내려받습니다. `MoaSpace_Reservation` 폴더가 보이는 위치에서 PowerShell을 열고 아래 명령을 실행합니다.

```powershell
Set-Location .\MoaSpace_Reservation
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

브라우저에서 터미널에 표시된 주소(기본 `http://localhost:8501`)를 엽니다. **공간 조회 및 예약** 메뉴에서 이용 조건을 입력하고 공간을 선택한 뒤 예약을 확정합니다. 발급된 **예약 ID**는 이후 조회와 취소에 사용하므로 보관해 주세요.

공간 조회·예약·취소와 직원 현황 조회는 Ollama 서버 없이 사용할 수 있습니다. AI 챗봇을 사용하려면 아래의 **Ollama 챗봇 설정**을 참고하세요.

## 코드와 상세 안내

- [앱 소스 코드와 CSV 데이터](MoaSpace_Reservation/)
- [기능별 사용 순서](MoaSpace_Reservation/README.md#기능별-사용-순서)
- [Ollama 챗봇 설정](MoaSpace_Reservation/README.md#ollama-챗봇-설정)
- [예약 핵심 테스트 실행 방법](MoaSpace_Reservation/README.md#4-예약-핵심-테스트-실행)
