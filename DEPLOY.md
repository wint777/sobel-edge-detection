# Render 배포 안내

이미지를 올리면 Sobel 엣지 검출 결과(PNG)를 내려받을 수 있는 Flask 웹 서비스를 [Render](https://render.com)에 배포하는 방법입니다.

## 1. 프로젝트 구성

| 파일 | 역할 |
|---|---|
| `app.py` | Flask 웹 서버 (`/` 업로드 화면, `/api/edge` 변환 API, `/healthz` 상태 확인) |
| `edge_detection.py` | Sobel 엣지 검출 (OpenCV) |
| `templates/index.html` | 업로드 화면 |
| `requirements.txt` | 설치할 패키지 목록 |
| `.python-version` | 파이썬 버전 (3.11.7) |
| `render.yaml` | Render 설정 파일 (Blueprint 배포용) |

> `requirements.txt`에는 반드시 `opencv-python-headless`가 들어가야 합니다.
> 일반 `opencv-python`을 쓰면 Render 서버에 화면 관련 라이브러리(libGL)가 없어 `ImportError: libGL.so.1`이 납니다.

## 2. 내 컴퓨터에서 먼저 실행해 보기

```bash
cd "/Users/wintyikyaw/Projects/AI 용합/edge_detection"
python3 -m venv .venv                 # 처음 한 번만
.venv/bin/pip install -r requirements.txt
PORT=8000 .venv/bin/python app.py     # http://localhost:8000 접속
```

> macOS에서는 AirPlay 수신 기능이 5000번 포트를 쓰고 있어서 기본 포트(5000)로 실행하면 `Address already in use` 오류가 납니다. 위처럼 `PORT=8000`을 붙여 실행하세요.

## 3. GitHub에 올리기

Render는 GitHub 저장소에 있는 코드를 가져가서 배포합니다.

1. GitHub에서 새 저장소를 만듭니다 (예: `sobel-edge-detection`). README 등은 추가하지 않습니다.
2. 프로젝트 폴더에서 아래 명령을 실행합니다. `<내-아이디>`는 본인 GitHub 아이디로 바꾸세요.

```bash
git init
git add .
git commit -m "Sobel edge detection web service"
git branch -M main
git remote add origin https://github.com/<내-아이디>/sobel-edge-detection.git
git push -u origin main
```

`.gitignore`에 `.venv`가 들어 있어서 가상환경 폴더는 올라가지 않습니다.

## 4. Render에 배포하기

두 가지 방법 중 하나를 고르세요.

### 방법 A: Blueprint (render.yaml 사용, 추천)

1. [dashboard.render.com](https://dashboard.render.com)에 GitHub 계정으로 로그인합니다.
2. **New +** → **Blueprint**를 누릅니다.
3. 방금 올린 저장소를 선택합니다. Render가 `render.yaml`을 읽어서 설정을 자동으로 채웁니다.
4. **Apply**를 누르면 빌드와 배포가 시작됩니다.

### 방법 B: 직접 입력

1. **New +** → **Web Service** → 저장소를 선택합니다.
2. 아래처럼 입력합니다.

| 항목 | 값 |
|---|---|
| Language | Python 3 |
| Branch | main |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60` |
| Instance Type | Free |

3. **Advanced**에서 Health Check Path를 `/healthz`로 설정합니다.
4. **Create Web Service**를 누릅니다.

## 5. 배포 확인

- 빌드 로그 마지막에 `Your service is live 🎉`가 나오면 성공입니다.
- 화면 위쪽의 `https://<서비스이름>.onrender.com` 주소로 접속해서 이미지를 올려 보세요.
- `https://<서비스이름>.onrender.com/healthz`에 접속하면 `ok`가 나와야 합니다.

## 6. 코드 수정 후 다시 배포

GitHub에 push하면 Render가 자동으로 다시 배포합니다.

```bash
git add .
git commit -m "수정 내용"
git push
```

## 7. 알아두면 좋은 점

- **무료 플랜은 잠들어요.** 15분 동안 접속이 없으면 서버가 멈추고, 다음 접속 때 깨어나는 데 30초~1분 정도 걸립니다. 수업 시연 전에 미리 한 번 접속해 두세요.
- **업로드 크기 제한은 10MB**입니다. 더 큰 사진은 413 오류가 납니다.
- 올린 이미지는 메모리에서만 처리하고 서버에 저장하지 않습니다.

## 8. 자주 나는 오류

| 증상 | 원인과 해결 |
|---|---|
| `ImportError: libGL.so.1` | `requirements.txt`에 `opencv-python`이 들어 있음 → `opencv-python-headless`로 바꾸기 |
| `ModuleNotFoundError: No module named 'app'` | `app.py`가 저장소 맨 위 폴더에 없음 → Settings에서 Root Directory 확인 |
| 배포는 됐는데 접속이 안 됨 | Start Command에 `--bind 0.0.0.0:$PORT`가 빠졌는지 확인 |
| `WORKER TIMEOUT` | 너무 큰 이미지 → 이미지 크기를 줄이거나 `--timeout` 값을 늘리기 |
| 빌드 중 numpy/opencv 설치 실패 | 파이썬 버전 확인 → `.python-version`이 `3.11.7`인지 확인 |
