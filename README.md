# -2DGP_poppy

<날 잡아먹지 말아줘 포피!>의 개발 과정을 담은 저장소입니다.

## 실행 방법

Python 환경을 준비한 다음 저장소 루트에서 의존성을 설치하고 게임을 실행합니다.

```powershell
python -m pip install -r requirements.txt
python main.py
```

`poppy.png`는 Poppy 스프라이트 시트입니다. 게임 창에서 방향키 또는 WASD로 이동하면 스프라이트 시트의 두 번째 줄 걷기 애니메이션이 재생되고, 멈추면 첫 프레임으로 돌아옵니다. 포피는 마우스 포인터를 향해 회전하며, `Esc` 키로 종료할 수 있습니다.

게임 실행은 `main.py`, Pico2D 창과 프레임 루프는 `gameframework.py`, 게임 객체의 수명 주기는 `gameworld.py`에서 담당합니다.
