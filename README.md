# -2DGP_poppy

<날 잡아먹지 말아줘 포피!>의 개발 과정을 담은 저장소입니다.

## 실행 방법

Python 환경을 준비한 다음 저장소 루트에서 의존성을 설치하고 게임을 실행합니다.

```powershell
python -m pip install -r requirements.txt
python main.py
```

`player.png`와 `poppy.png`는 각각 플레이어와 포피의 스프라이트 시트입니다. WASD로 플레이어를 움직이고, 움직이는 동안 플레이어는 마우스 포인터 방향을 향합니다. 3초 동안 움직이지 않으면 플레이어와 포피의 idle 애니메이션이 재생됩니다. 마우스 좌클릭으로 포피에게 이동 위치를 명령할 수 있습니다. 아이템 획득용 `get` 상태는 아직 동작이 구현되지 않은 상태로 남겨 두었습니다. `Esc` 키로 종료할 수 있습니다.

게임 실행은 `main.py`, Pico2D 창과 프레임 루프는 `gameframework.py`, 게임 객체의 수명 주기는 `gameworld.py`에서 담당합니다.
