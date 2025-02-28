# CCELKit Packmol 모듈

CCELKit의 Packmol 모듈은 분자 시스템을 생성하기 위한 도구입니다. 이 모듈은 고체, 액체, 기체 상태의 분자들을 조합하여 시스템을 구성할 수 있습니다.

## 필수 조건

- PACKMOL이 설치되어 있어야 하며, 환경 변수에 등록되어 있어야 합니다.
- ASE (Atomic Simulation Environment)
- NumPy
- PyYAML

## 사용 방법

### 1. 디렉토리 초기화

bash
ccelkit make_system init_dir

다음과 같은 디렉토리 구조가 생성됩니다:

root_dir/
├── src/
│ ├── solid/
│ ├── liquid/
│ ├── gas/
│ └── cell_POSCAR

### 2. 설정 파일 초기화

bash
ccelkit make_system init_config

`config_init.yml` 파일이 생성됩니다. 이 파일에서 다음 설정들을 수정할 수 있습니다:
- 각 분자의 밀도
- tolerance: 분자 간 최소 거리
- seed: 난수 생성 시드
- population: 생성할 시스템의 수

### 3. 분자 구조 파일 준비
- `src/solid/`: 고체 상태 분자 구조 파일 (POSCAR, xyz, cif, pdb 형식)
- `src/liquid/`: 액체 상태 분자 구조 파일
- `src/gas/`: 기체 상태 분자 구조 파일
- `cell_POSCAR`: 시스템 전체 cell 정보. system lattice 만이 해당 POSCAR 에서 사용됩니다. 

### 4. 시스템 생성

bash
ccelkit make_system -c config.yml


## 주의사항

1. cell_POSCAR의 벡터는 반드시 직교해야 합니다.
2. 분자 구조 파일의 이름은 `_POSCAR` 또는 확장자를 제외한 부분이 config 파일의 키값으로 사용됩니다.
3. 생성된 시스템은 `out` 디렉토리에 저장됩니다.

## 출력 파일

- `out/system_{index:02d}_POSCAR`: 최종 생성된 시스템 구조 (index는 시스템 인덱스)
- `out/liquid_gas_packmol_{index:02d}.inp`: Packmol 입력 파일
- `out/liquid_gas_packmol_{index:02d}.xyz`: Packmol 출력 파일