# Dash DMC 프로젝트 자동 생성 스크립트 사용법

이 가이드는 `create_dash_dmc_project.sh` 스크립트를 이용해 Dash Mantine Components(DMC) 기반 프로젝트의 폴더 구조를 자동으로 생성하는 방법을 초보 개발자도 쉽게 따라할 수 있도록 설명합니다.

---

## 1. 스크립트 준비 및 실행 위치

### 1-1. 일반적인 개발 워크플로우 예시
1. **원하는 작업 폴더로 이동**
    ```bash
    cd ~/workspace
    ```
2. **깃 저장소를 클론**
    ```bash
    git clone https://github.com/your/repo-name
    cd repo-name
    ```
3. **`create_dash_dmc_project.sh` 파일을 복사(또는 다운로드)하여 현재 디렉토리에 둡니다.**

### 1-2. 실행 권한 부여
터미널에서 아래 명령어로 실행 권한을 부여하세요.
```bash
chmod +x create_dash_dmc_project.sh
```

---

## 2. 스크립트 실행 방법

1. **현재 디렉토리(예: repo-name)에서 아래 명령어로 실행하세요.**
    ```bash
    ./create_dash_dmc_project.sh
    ```

- **중요:** 스크립트를 실행한 "현재 디렉토리" 하위에 `backend`, `frontend`, `tests` 등 모든 폴더 구조가 생성됩니다.
- 별도의 프로젝트 이름 지정이나 변수 설정이 필요 없습니다.

---

## 3. 실행 결과
- 현재 디렉토리(예: repo-name) 하위에 Dash DMC 프로젝트에 최적화된 폴더 구조와 예시 파일들이 자동으로 만들어집니다.
- 예시:
    ```
    repo-name/
    ├── backend/
    ├── frontend/
    │   ├── components/
    │   │   ├── theming/
    │   │   │   ├── mantine-provider/
    │   │   │   └── ...
    │   │   ├── layout/
    │   │   │   ├── app-shell/
    │   │   │   └── ...
    │   │   └── ...
    │   ├── app.py
    │   └── ...
    └── tests/
    ```

---

## 4. 자주 묻는 질문(FAQ)

### Q1. **어디서 스크립트를 실행해야 하나요?**
- 반드시 **폴더 구조를 만들고 싶은 디렉토리(예: repo-name)에서 실행**하세요.
- 실행한 위치(현재 디렉토리)에 바로 backend, frontend, tests 등이 생성됩니다.

### Q2. **프로젝트 이름을 따로 지정할 수 있나요?**
- 아니요. 이제 별도의 변수나 이름 지정이 필요 없습니다.
- 프로젝트 이름을 바꾸고 싶다면, git clone 시 폴더명을 지정하거나, 디렉토리명을 직접 변경하세요.

### Q3. **이미 같은 이름의 폴더가 있으면 어떻게 되나요?**
- 기존 폴더가 있으면 그 안에 파일이 추가될 수 있으니, **중복되지 않는 이름**을 사용하거나 기존 폴더를 미리 삭제하세요.

### Q4. **생성된 프로젝트를 바로 실행할 수 있나요?**
- 네! `frontend/app.py`를 실행하면 Dash DMC 기본 화면이 나옵니다.
    ```bash
    cd frontend
    python app.py
    ```

---

## 5. 요약
- 원하는 위치(예: repo-name)에서 스크립트를 실행하면, 폴더 구조와 예시 코드가 한 번에 준비되어 바로 Dash DMC 개발을 시작할 수 있습니다.
- 별도의 변수 설정이나 프로젝트 이름 지정이 필요 없습니다.

---

궁금한 점이 있으면 언제든 README나 이 가이드에 추가해 주세요! 