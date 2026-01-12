구글의 **Antigravity** 에이전트에게 이 파일을 통째로 업로드하거나 내용을 복사해 주면, 에이전트가 전체 구조를 이해하고 코딩을 시작할 수 있도록 작성된 **최종 개발 명세서(Technical Specification)**입니다.

---

# 📜 Project Specification: AI IT Newsroom

## 1. 프로젝트 개요
*   **서비스 명:** 나만의 1장 IT 뉴스룸 (My AI IT Newsroom)
*   **목표:** 지정된 IT 뉴스 RSS 피드에서 최근 3일치 데이터를 수집, Gemini API를 통해 주제별로 분석하여 신문 1면 형태의 일일 보고서를 자동 생성함.
*   **특이사항:** 별도의 DB 없이 GitHub 리포지토리의 JSON 파일을 데이터 저장소로 활용하며, Streamlit Cloud로 배포함.

## 2. 기술 스택 (Tech Stack)
*   **언어:** Python 3.10+
*   **프레임워크:** Streamlit
*   **AI 모델:** Google Gemini 1.5 Pro (또는 최신 Gemini 모델)
*   **데이터 저장:** GitHub Repository (JSON 방식)
*   **주요 라이브러리:**
    *   `feedparser`: RSS 피드 파싱
    *   `google-generativeai`: Gemini API 연동
    *   `PyGithub`: GitHub API를 통한 JSON 파일 CRUD
    *   `pandas`: 통계 데이터 처리

## 3. 데이터 아키텍처 (JSON 구조)

### 3.1 `data/feeds.json` (RSS 목록)
```json
["https://rss.url1.com", "https://rss.url2.com"]
```

### 3.2 `data/news_data.json` (분석 결과 저장)
```json
{
  "2025-11-20": {
    "briefing": "오늘의 전체 흐름 요약...",
    "topics": [
      {
        "title": "토픽 제목",
        "content": "분석된 상세 내용",
        "links": ["원문주소1", "원문주소2"]
      }
    ]
  }
}
```

### 3.3 `data/stats.json` (접속 통계)
```json
{
  "2025-11-20": 150,
  "2025-11-21": 210
}
```

## 4. 핵심 기능 요구사항

### 4.1 메인 화면 (Public View)
*   **최신 보고서 우선:** 접속 시 가장 최근 날짜의 분석 보고서를 메인에 출력.
*   **날짜 네비게이션:** 사이드바의 SelectBox를 통해 과거 날짜의 보고서로 즉시 이동 가능.
*   **보고서 레이아웃:** 
    *   헤더: 날짜와 "오늘의 IT 브리핑" 요약 정보.
    *   본문: 토픽별 카드 레이아스트(제목, 분석 내용, 관련 뉴스 링크 리스트).

### 4.2 관리자 대시보드 (Admin Dashboard)
*   **보안:** 사이드바 내 비밀번호 입력을 통해서만 메뉴 활성화.
*   **RSS 관리:** 현재 등록된 피드 리스트 확인, 새로운 피드 URL 추가 및 기존 피드 삭제 기능.
*   **수집 및 분석 실행 (Trigger):**
    1.  `feeds.json`의 모든 URL 순회.
    2.  각 피드에서 **최근 3일 이내**의 기사만 추출 (Title, Summary, Link, Date).
    3.  수집된 원문 데이터를 Gemini API에 전달.
    4.  **Gemini 프롬프트 조건:** 
        *   "IT 전문 기자처럼 분석해줘."
        *   "유사한 기사는 하나의 토픽으로 묶어줘."
        *   "결과는 반드시 지정된 JSON 포맷으로 반환해줘."
    5.  분석 결과를 `news_data.json`에 저장(GitHub Commit).
*   **접속 통계:** `stats.json`을 기반으로 일별 방문자 수를 `st.line_chart`로 시각화.

### 4.3 GitHub 저장소 연동 (Storage Logic)
*   `PyGithub` 라이브러리를 사용해 데이터 읽기/쓰기 구현.
*   파일 업데이트 시 기존 SHA 값을 확인하여 `update_file` API 호출.
*   Streamlit의 캐싱(`@st.cache_data`)을 활용해 GitHub API 호출 횟수 최적화.

## 5. 환경 변수 설정 (Secrets)
앱 실행을 위해 다음 Secrets 상수가 필요함:
*   `GITHUB_TOKEN`: GitHub Personal Access Token
*   `REPO_NAME`: "계정명/저장소명"
*   `GEMINI_API_KEY`: Google AI Studio API Key
*   `ADMIN_PASSWORD`: 대시보드 접속용 비번

## 6. 개발 단계별 가이드 (Antigravity용)

1.  **Step 1 (초기화):** 프로젝트 폴더 구조 생성 및 `requirements.txt` 작성.
2.  **Step 2 (GitHub 클래스):** JSON 파일을 읽고 쓰는 `GitHubStorage` 클래스 구현.
3.  **Step 3 (수집/분석 엔진):** `feedparser`와 `Gemini API`를 연동한 분석 함수 구현.
4.  **Step 4 (UI - 메인):** 날짜별 뉴스 보고서 렌더링 화면 구현.
5.  **Step 5 (UI - 관리자):** 피드 관리 UI 및 분석 트리거 버튼, 통계 그래프 구현.
6.  **Step 6 (최종 검토):** 전체 데이터 흐름 및 예외 처리(데이터 없을 때 등) 점검.

---

**Antigravity 에이전트에게 보내는 메시지:**
> "위 명세서를 바탕으로 Python Streamlit 코드를 작성해줘. GitHub API 연동 시 보안에 유의하고, 사용자가 쉽게 날짜를 이동하며 뉴스를 볼 수 있는 신문 형태의 UI를 완성해줘."