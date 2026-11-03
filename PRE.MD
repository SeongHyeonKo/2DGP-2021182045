# Boy 상태 머신 구현 정리

## 목표

`transitions` 라이브러리로 Boy 캐릭터의 IDLE, RUN, SLEEP, AUTO_RUN 상태를 관리한다. 상태별 동작은 `Labs/LEC12_CharacterController/boy.py`와 `auto_run.py`에 구현한다.

## 상태와 전이

| 현재 상태 | 입력 또는 조건 | 다음 상태 | 동작 |
|---|---|---|---|
| IDLE | 왼쪽/오른쪽 방향키 누름 | RUN | 누른 방향으로 이동 |
| IDLE | 5초 경과 | SLEEP | 제자리에서 잠듦 |
| IDLE | `a` 키 누름 | AUTO_RUN | 자동 무적 런 시작 |
| RUN | 방향키를 모두 뗌 | IDLE | 이동을 멈추고 IDLE 타이머 재시작 |
| SLEEP | SPACE 누름 | IDLE | 깨어나고 IDLE 타이머 재시작 |
| SLEEP | 방향키 누름 | RUN | 누른 방향으로 깨어나 달림 |
| AUTO_RUN | 5초 경과 | IDLE | 자동 런 종료, IDLE 타이머 재시작 |
| AUTO_RUN | 방향키 누름 | RUN | 자동 런을 취소하고 누른 방향으로 이동 |

왼쪽과 오른쪽은 별도 상태가 아니다. 하나의 RUN 상태에서 방향 값으로 이동 방향과 스프라이트를 정한다. 두 방향키를 함께 누르면 마지막으로 누른 방향을 우선하며, 그 키를 떼면 아직 눌려 있는 반대 방향으로 이동한다.

## AutoRun 동작

`auto_run.py`의 `AutoRun` 클래스가 AUTO_RUN 상태의 동작을 담당한다.

- Boy가 IDLE일 때 `a` 키를 누르면 AUTO_RUN으로 진입한다.
- 보통 RUN보다 빠르게 이동하고 스프라이트를 1.6배 확대한다.
- 화면 가장자리에서 방향을 자동으로 반전한다. 확대된 캐릭터 전체가 화면 안에 남도록 이동 범위를 제한한다.
- AUTO_RUN 동안 `Boy.is_invincible`이 참이다. 현재 예제에는 적/피해 판정이 없으므로 이 플래그는 이후 충돌 또는 피해 처리에서 사용할 수 있다.
- AUTO_RUN에서 방향키를 누르면 상태를 취소하고 입력 방향으로 RUN한다.
- 진입 후 5초가 지나면 IDLE로 돌아간다.

## 애니메이션과 이동

- IDLE과 RUN은 각 상태의 8프레임 애니메이션을 반복한다.
- SLEEP은 마지막 이동 방향의 스프라이트를 회전해 얼굴이 하늘을 향하는 자세로 표시한다.
- 일반 RUN은 화면 안쪽 `x = 50..750` 범위로 이동한다.
- AUTO_RUN은 확대 크기를 반영해 `x = 80..720` 범위에서 반사 이동한다.

## 실행 및 파일

- 실행: `Labs/LEC12_CharacterController` 폴더에서 `python main.py`
- `boy.py`: 상태 머신과 Boy 입력/애니메이션
- `auto_run.py`: 별도 AutoRun 클래스와 자동 이동, 반사, 시간 제한
- `main.py`: 키보드 이벤트 전달 및 게임 루프
- `state_diagram.svg`: 전체 상태 전이 그림
- 실행 환경에는 `pico2d`, `transitions` 패키지가 필요하다.
