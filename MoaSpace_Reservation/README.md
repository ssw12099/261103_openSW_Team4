# 모아공간 예약 관리 시스템

회의실과 연습실을 조회하고 예약하는 로컬 시연용 Streamlit 앱입니다. 공간 정보와 예약 내역은 CSV로 관리합니다. 예약 ID와 예약자명으로 본인 예약을 조회하거나 취소할 수 있으며, 운영 직원 화면에서는 날짜별로 확정·취소 내역을 확인할 수 있습니다. 직원 화면은 로그인 없이 이용할 수 있고 CSV 저장은 한 사람이 순차적으로 사용하는 환경을 전제로 합니다.

| 기능 | 실제 동작 |
| --- | --- |
| F-01 공간 조회 | 이용일, 시간, 인원, 공간 유형에 맞는 공간을 조회합니다. |
| F-02 예약 신청 | 조회된 공간을 선택하고 예약을 확정하면 예약 ID를 발급합니다. |
| F-03 예약 취소 | 예약 ID와 예약자명이 일치하고 취소 조건을 충족하면 상태를 취소로 기록합니다. |
| F-04 예약 조회 | 본인 예약 상세 정보와 운영 직원의 날짜·공간별 예약 현황을 제공합니다. |
| F-05 AI 챗봇 | 본인 확인을 마친 예약 한 건에 관한 질문에 Ollama로 답합니다. |

## Windows PowerShell에서 설치 및 실행

저장소 최상위에서 앱 폴더로 이동합니다. 이후 PowerShell 명령은 별도 표시가 없으면 이 폴더에서 실행합니다.

```powershell
Set-Location .\MoaSpace_Reservation
```

### 1. 가상환경 생성

Python이 설치되어 있고 `python` 명령을 사용할 수 있어야 합니다.

```powershell
python --version
python -m venv .venv
```

### 2. 의존성 설치

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Streamlit 앱 실행

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

브라우저에서 터미널에 표시된 로컬 주소(기본 `http://localhost:8501`)를 엽니다. 설치한 Python 패키지는 앱을 실행할 때 필요합니다. 공간 조회·예약·본인 예약 조회·취소·직원 현황은 Ollama 서버 없이 사용할 수 있습니다. AI 답변을 받으려면 아래 Ollama 설정을 완료하세요.

### 4. 예약 핵심 테스트 실행

같은 폴더의 별도 PowerShell에서 실행합니다. 이 테스트는 임시 CSV로 신규 예약, 겹치는 시간의 중복 예약 방지, 본인 확인, 취소 후 같은 시간대 재예약 가능 여부를 검사합니다.

```powershell
.\.venv\Scripts\python.exe smoke_test.py
```

## Ollama 챗봇 설정

1. Windows용 Ollama를 설치하고 실행합니다. 일반 설치에서는 Ollama가 백그라운드에서 실행됩니다. 새 PowerShell에서 `ollama list`로 연결을 확인하고, 서버가 실행 중이 아니라면 별도 터미널에서 `ollama serve`를 실행합니다. [Ollama Windows 공식 가이드](https://docs.ollama.com/windows)
2. 모델을 내려받고 목록에서 설치된 이름을 확인합니다.

   ```powershell
   ollama pull qwen3.5:2b-q4_K_M
   ollama list
   ```

3. 앱 폴더에서 [환경설정 예시](.env.example)를 복사합니다. 기존 `.env`가 있으면 그대로 두고 필요한 값만 직접 수정합니다.

   ```powershell
   if (-not (Test-Path -LiteralPath .env)) {
       Copy-Item .env.example .env
   }
   ```

   | 환경변수 | 코드 기본값 | 설정 방법 |
   | --- | --- | --- |
   | `OLLAMA_MODEL` | `qwen3.5:2b-q4_K_M` | 다른 모델을 쓰려면 `ollama list`에 표시된 이름과 태그로 바꿉니다. |
   | `OLLAMA_BASE_URL` | `http://localhost:11434` | 다른 주소에서 실행하는 경우 Ollama 서버 주소로 바꿉니다. |

4. 앱 실행 중에 설정을 수정했다면 Streamlit을 다시 시작합니다. Ollama 연결이나 모델 응답에 실패해도 본인 예약 상세 정보는 조회할 수 있습니다.

## 기능별 사용 순서

### 공간 조회 및 예약

1. 사이드바에서 **공간 조회 및 예약**을 선택합니다.
2. **이용일**, **시작 시각**, **종료 시각**, **이용 인원**, **공간 유형**(전체·회의실·연습실)을 지정하고 **이용 가능 공간 조회**를 누릅니다.
3. 결과 아래 **예약할 공간**에서 공간을 고르고 **예약자명**을 1~60자로 입력합니다.
4. **예약 확정**을 누른 뒤 결과에 표시된 **예약 ID**를 보관합니다.

이용 시간은 09:00~22:00이고 시작과 종료는 30분 단위입니다. 종료 시각은 시작보다 늦어야 하며 시작은 현재보다 이후여야 합니다. 이용 인원은 1명 이상이고 공간의 수용 인원 이하여야 합니다. 같은 공간에서 시간이 겹치는 확정 예약이 있으면 해당 공간을 신청할 수 없습니다. 취소된 예약의 시간대는 다시 예약할 수 있습니다.

### 내 예약 조회 및 AI 챗봇

1. **내 예약 조회 · AI 챗봇**에서 **예약 ID**와 **예약자명**을 입력합니다.
2. **예약 조회 및 본인 확인**을 누릅니다. 두 값이 일치하면 예약 상세와 취소 가능 여부가 표시됩니다.
3. **예약에 관해 질문하세요**에 질문을 1~1000자로 입력하고 **질문 전송**을 누릅니다.

챗봇은 조회 전용입니다. 본인 확인을 마친 예약 한 건을 바탕으로 답하며 예약 생성·변경·취소를 실행하지 않습니다.

### 예약 취소

1. **예약 취소**에서 **예약 ID**와 **예약자명**을 입력하고 **예약 확인**을 누릅니다.
2. 상세 정보와 취소 가능 여부를 확인합니다. 아직 취소되지 않았고 이용 시작 시각 전이면 **취소 확정** 버튼이 표시됩니다.
3. **취소 확정**을 누르면 예약 상태가 **취소**로 기록됩니다.

### 운영 직원 예약 현황

1. **운영 직원 예약 현황**에서 **조회 날짜**와 **공간 필터**(전체 또는 개별 공간)를 선택합니다.
2. **예약 조회**를 누르면 해당 조건의 예약이 공간과 시작 시각 순으로 표시됩니다.

## 데이터와 시연

- [공간 CSV](data/spaces.csv)에는 가상 공간 6개가 있습니다.
- [예약 CSV](data/reservations.csv)에는 예시 예약 `R0001` 한 건이 들어 있습니다. 이용일은 2026-11-13이고 상태는 **취소**입니다. 예시 데이터로 조회는 시연할 수 있지만, 지난 날짜에 새 예약을 만들거나 이미 취소된 예약을 다시 취소할 수는 없습니다.
- 신규 예약과 취소를 함께 시연하려면 앱 폴더의 별도 복사본에서 앞으로의 이용일과 가상 예약자명으로 새 예약을 만듭니다. 예약과 취소는 실행한 앱 폴더의 예약 CSV에 기록됩니다.

## 오픈소스와 라이선스

| 구성 요소 | 용도 | 라이선스 | 공식 출처 |
| --- | --- | --- | --- |
| Streamlit | 브라우저 화면과 입력 폼 | Apache-2.0 | [Streamlit 1.67.0](https://pypi.org/project/streamlit/1.67.0/) |
| pandas | 공간·예약 CSV 읽기, 필터링, 저장 | BSD-3-Clause | [pandas 패키지 개요](https://pandas.pydata.org/docs/getting_started/overview.html) |
| Ollama Python | Ollama 서버에 챗봇 요청 전송 | MIT | [Ollama Python 0.6.3](https://pypi.org/project/ollama/0.6.3/) |
| python-dotenv | 앱 폴더의 `.env` 읽기 | BSD-3-Clause | [python-dotenv 1.2.1](https://pypi.org/project/python-dotenv/1.2.1/) |
| HTTPX | Ollama 연결 오류 처리 | BSD-3-Clause | [HTTPX 0.28.1](https://pypi.org/project/httpx/0.28.1/) |
| Ollama 프로그램 | 로컬 모델 실행 및 API 제공 | MIT | [Ollama 라이선스](https://github.com/ollama/ollama/blob/main/LICENSE) |
| Qwen3.5 2B Q4_K_M 모델 | 기본 챗봇 답변 생성 | Apache-2.0 | [배포 모델과 라이선스](https://ollama.com/library/qwen3.5:2b-q4_K_M) |

다른 모델을 선택하면 해당 모델의 배포 조건을 확인하세요.

## 참고 자료

- 기능과 제한 조건은 저장소의 [화면 코드](app.py), [예약 로직](reservation.py), [챗봇 로직](chatbot.py), [테스트 코드](smoke_test.py), [의존성 목록](requirements.txt), 위 CSV를 기준으로 정리했습니다.
- 문서 보완 범위는 [GitHub 이슈 #5](https://github.com/ssw12099/261103_openSW_Team4/issues/5)에서 확인했습니다. Ollama 설치 절차는 위 Windows 공식 가이드를 참고했습니다.

## AI 사용 내역

- **개발 보조** — 이슈 #5 작업에서 Codex를 사용해 앱 코드와 CSV를 대조하고, PowerShell 설치·실행 절차와 기능별 안내를 작성했습니다. 환경설정 예시와 Git 제외 규칙을 추가하고 문서 설정을 검증했습니다. 기존 로컬 Python으로 예약 핵심 테스트를 실행했습니다. 이전 개발 단계의 AI 도구, 모델, 프롬프트 및 기여 범위는 팀 기록 확인이 필요합니다.
- **앱 내 AI** — F-05에서 Ollama를 통해 본인 확인된 예약에 관한 답변을 생성합니다. 이용자 질문과 해당 예약의 조회 정보가 설정된 Ollama 서버로 전달됩니다.
