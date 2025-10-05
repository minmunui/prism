# 프로젝트 명세서: PRISM

## 1. 프로젝트 개요

* **프로젝트명**: PRISM 
* **목표**: 에코 챔버 및 필터 버블 현상을 완화하여 사회적 소통을 증진하는 웹 플랫폼 구축
* **핵심 문제**: 정보 편향, 의견 양극화
* **솔루션**:
    1.  **객관적 뉴스 제공**: 동일 사건에 대한 여러 기사를 자동 그룹화 및 요약하고, 다양한 여론을 함께 제시.
    2.  **AI 댓글 중재**: 공격적이거나 조롱하는 댓글을 AI가 건설적인 형태로 자동 정제.

---

## 2. 기술 스택 (Tech Stack)

* **Repository**: **모노레포 (Monorepo)**, 단일 GitHub Repository
* **프론트엔드**: **Next.js**
* **백엔드**: **FastAPI** (Python)
* **데이터베이스**: **PostgreSQL**
* **AI 모델 (댓글 중재)**: **Gemma3 27B** (Ollama를 통해 로컬 환경에서 구동)
* **개발/배포 환경**: **Docker**, **GitHub Actions (CI/CD)**

---

## 3. 프로젝트 구조 (Directory Structure)

```
/balanced-perspective/      # 📂 루트 레포지토리
├── .github/                # GitHub Actions 워크플로우 (CI/CD)
│   └── workflows/
│       └── deploy.yml
├── backend/                # 🐍 FastAPI 백엔드 애플리케이션
│   ├── app/
│   │   ├── api/              # API 엔드포인트
│   │   ├── core/             # 설정
│   │   ├── db/               # 데이터베이스 모델 및 세션
│   │   ├── schemas/          # 데이터 유효성 검사 (Pydantic)
│   │   ├── services/         # 비즈니스 로직 (기사 클러스터링, AI 중재 등)
│   │   └── main.py
│   ├── alembic/              # DB 마이그레이션
│   └── tests/
├── frontend/               # ⚛️ Next.js 프론트엔드 애플리케이션
│   ├── app/                  # 페이지 라우팅
│   ├── components/           # 재사용 UI 컴포넌트
│   ├── lib/                  # API 클라이언트, 커스텀 훅
│   └── store/                # 전역 상태 관리
├── docker-compose.yml      # 🐳 로컬 개발 환경 실행 파일
└── README.md
```

---

## 4. 데이터베이스 스키마 (Database Schema)

* **`users`**: 사용자 정보 (id, email, hashed_password)
* **`article_groups`**: 동일 사건으로 묶인 기사 그룹 (id, representative_title, summary)
* **`articles`**: 개별 원본 기사 (id, group_id, original_url, title, publisher)
* **`comments`**: 사용자 댓글 (id, group_id, user_id, content, moderated_content)

---

## 5. API 명세서 (API Specification)

| 기능 | Method | Endpoint |
| :--- | :--- | :--- |
| 사용자 가입 | `POST` | `/api/v1/auth/signup` |
| 로그인 | `POST` | `/api/v1/auth/token` |
| 기사 그룹 목록 | `GET` | `/api/v1/articles` |
| 기사 그룹 상세 | `GET` | `/api/v1/articles/{group_id}` |
| 댓글 목록 | `GET` | `/api/v1/articles/{group_id}/comments` |
| 댓글 작성 | `POST` | `/api/v1/articles/{group_id}/comments` |
| AI 댓글 중재 | `POST` | `/api/v1/moderate/comment` |

---

## 6. 핵심 기능 구현 전략

### 6.1. 기사 클러스터링 (Article Clustering)

**목표**: 여러 언론사의 기사를 '동일 사건' 기준으로 자동 그룹화.
**방법**: 다단계 파이프라인(Multi-stage Pipeline) 접근.

1.  **의미 분석**: `ko-sbert` 같은 모델을 사용하여 각 기사의 의미를 벡터(숫자 좌표)로 변환.
2.  **사실 확인**: 기사 간의 핵심 **개체명(인물, 장소)** 중복도와 **발행 시간** 근접성을 교차 검증.
3.  **그룹화**: `DBSCAN` 알고리즘을 사용하여 의미와 사실이 모두 유사한 기사들을 최종적으로 하나의 '사건'으로 묶음.

### 6.2. AI 댓글 중재 (AI Comment Moderation)

**목표**: 사용자의 공격적인 댓글을 핵심 의도는 유지한 채 건설적인 표현으로 순화.
**방법**: `Gemma3 27B` 모델과 프롬프트 엔지니어링 활용.

* **프롬프트 핵심**:
    * **역할 부여**: '건설적인 소통 조절자' 페르소나 지정.
    * **명확한 지침**: 핵심 주장 유지, 욕설/조롱 제거, 감정적 단어 중립화.
    * **예시 제공 (Few-shot)**: '원문 -> 수정문' 예시를 여러 개 제공하여 AI의 이해도 향상.

---

## 7. 프로젝트 로드맵 (Project Roadmap)

**Phase 0: 기획 및 설계**
* [ ] 요구사항 및 아키텍처 확정
* [ ] Git Repository 및 개발 환경 설정

**Phase 1: 핵심 기능 개발**
* [ ] 백엔드: DB 스키마, 사용자 인증, 기본 CRUD API 구현
* [ ] 프론트엔드: UI 레이아웃, 페이지, API 연동 구현

**Phase 2: 데이터 및 AI 파이프라인 구축**
* [ ] 기사 크롤링 및 클러스터링 파이프라인 구현
* [ ] AI 댓글 중재 API 및 기능 연동
* [ ] 파이프라인 자동화

**Phase 3: 통합, 테스트 및 배포**
* [ ] 전체 기능 통합 및 E2E(End-to-End) 테스트
* [ ] CI/CD 파이프라인 구축 및 최종 배포
* [ ] 서비스 모니터링 및 로깅 설정