# CCELKIT Visual 기능 사용법

CCELKIT의 visual 기능은 원자 구조 파일을 POV-Ray를 사용하여 고품질 이미지로 렌더링하는 도구입니다.

## 필수 요구사항

- POV-Ray가 설치되어 있어야 합니다
- 환경 변수 `POVRAY`에 POV-Ray 설치 경로가 지정되어 있어야 합니다

## 사용 방법

### 1. 명령줄 인터페이스 (CLI) 사용

기본 명령어:

```bash
ccelkit visual [옵션]
```

#### 주요 옵션
- `--target`: 특정 패턴의 모든 파일을 처리 (예: "POSCAR")
- `-i, --input_filepath`: 입력 구조 파일 경로
- `-o, --output_filepath`: 출력 이미지 파일 경로
- `-r, --repeatation`: 구조 반복 횟수 [x y z] (기본값: [1,1,1])
- `-ori, --orientation`: 카메라 방향. 다음 프리셋 또는 VESTA 형식 행렬 사용 가능:
  - "top": 위에서 보기
  - "side_x": x축 방향에서 보기
  - "side_y": y축 방향에서 보기
  - "perspective": 사선 방향에서 보기 (기본값)
- `--cell_on`: 격자 표시 여부
- `-t, --transmittances`: 원자 투명도 설정 (0~1 사이 값)
- `-H, --heatmaps`: 원자 히트맵 값 (0: 파란색, 1: 빨간색)
- `-w, --canvas_width`: 이미지 너비 (픽셀, 기본값: 800)
- `-cs, --color_species`: 원자 종류별 색상 지정
- `-ci, --color_index`: 원자 인덱스별 색상 지정

#### 카메라 각도 조절 방법

![기본 vesta 이미지](./images/step_01.png)
![step02](./images/step_02.png)
![step03](./images/step_03.png)

#### 색상 지정 권장사항
원자 종류별(`color_species`) 또는 원자 인덱스별(`color_index`) 색상 지정은 명령줄 인터페이스로 하기에는 복잡하므로, 설정 파일(config.yaml)을 사용하는 것을 권장합니다.

### 2. 설정 파일(config.yaml) 사용

```bash
ccelkit visual -c config.yaml
```

#### 기본 설정 파일 생성

```bash
ccelkit visual create_config
```

#### 설정 파일 구조 (config.yaml)

```yaml
target: "POSCAR"              # 대상 파일 패턴
input_filepath: null          # 입력 파일 경로
output_filepath: null         # 출력 파일 경로
repeatation: [1, 1, 1]        # 구조 반복
orientation: "perspective"     # 카메라 방향
cell_on: true                 # 격자 표시 여부
transmittances: null          # 원자 투명도
heatmaps: null                # 원자 히트맵
canvas_width: 800             # 이미지 너비
color_species:                # 원자 종류별 색상
  # Re: [0.580, 0, 0.827]
  # H: [0.529, 0.808, 0.980]
color_index:                  # 원자 인덱스별 색상
  # 0: [0.580, 0, 0.827]
  # 1: [0.529, 0.808, 0.980]
```

## 사용 예시

### 1. 단일 파일 처리

```bash
# 기본 렌더링
ccelkit visual -i structure.vasp -o output.png

# 구조 반복 및 격자 표시
ccelkit visual -i structure.vasp -o output.png -r 2 2 1 --cell_on

# 특정 방향에서 보기
ccelkit visual -i structure.vasp -o output.png -ori "top"
```

### 2. 여러 파일 일괄 처리

```bash
# POSCAR 파일 모두 처리
ccelkit visual --target POSCAR

# 특정 설정으로 여러 파일 처리
ccelkit visual --target POSCAR -r 2 2 2 --cell_on
```

### 3. 원자 색상 및 투명도 설정

```bash
# 투명도 설정
ccelkit visual -i structure.vasp -o output.png -t 0.5 0.3 0.7

# 히트맵 설정
ccelkit visual -i structure.vasp -o output.png -H 0.2 0.5 0.8
```

## 주의사항
- `target` 옵션 사용 시 출력 파일명은 자동으로 'img_'가 접두사로 붙습니다
- `target`과 `input_filepath`/`output_filepath`는 동시에 사용할 수 없습니다
- 색상값은 RGB 형식으로 0~1 사이의 값을 사용합니다
- 투명도와 히트맵 값은 원자 수만큼 지정해야 합니다




