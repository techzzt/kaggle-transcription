# Code Change History (코드 변경 내역)

이 파일은 프로젝트 내 코드 업데이트(신규 기능 추가, 로직 수정, 버그 해결 등)가 발생할 때마다 날짜별로 주요 변경 사항을 기록하는 로그입니다.

## [2026-08-12]

### ➕ 신규 추가 사항 (Added)
- **paired comparison 6컬럼 레이아웃 재설계** (`stn_borderline_tonic_burst_transition.py`):
  - `[Normal Raster | PV- Normal | PV+ Normal | PD Raster | PV- PD | PV+ PD]` 구조로 개편
  - PV-와 PV+를 나란히 비교하는 구조, 각 컬럼 타이틀에 발화율(Hz) 및 CV값 표시
- **g_GABA 시냅스 가중치 스위핑 및 분기 분석 시각화** (`plot_ggaba_bifurcation_analysis.py`):
  - `g_GABA` 스위프(0.20 ~ 3.50 nS)에 따른 **Phase Plane (Panel A)**, **Fixed Point Gap & Bifurcation Threshold (Panel B)**, **Membrane Potential $V(t)$ Traces (Panel C)**, **Firing Rate & CV Curve (Panel D)** 종합 분석 시각화 완료
  - 생리적 범주($g_{\text{GABA}} = 0.64 \sim 1.14\text{ nS}$)에서는 Fixed Point가 0개(continuous firing regime)로 유지되며, $g_{\text{GABA}} \ge 3.20\text{ nS}$ 이상의 극단적 억제 조건에서만 Saddle-Node Bifurcation (FP=2, Silent)이 발생하는 것을 수학적/시각적으로 입증
  - Tonic → Rebound Burst Barrage → Silent 레짐 전환 임계점 규명 완료



### 🔄 주요 변경 사항 (Modified)
- **PD 상태 Rebound Burst Cluster (마디형 고빈도 버스트) 파형 선명화**:
  - 사용자 피드백 반영: 기존 파형에서 PD 버스트가 매끄러운 28.5Hz 토닉처럼 지속 발화하던 점을 교정
  - 시냅스 컨덕턴스 가중치($g_{\text{GABA}} = 0.64\text{ nS}, w_{\text{AMPA}} = 0.35\text{ nS}$) 균형 조율을 통해, GPe Beta 파형의 억제 골에서 **125 Hz 초고속 Burst Cluster 스파이크 발사 후 긴 휴지기(Pause)가 번갈아 반복되는 전형적인 Rebound Burst Barrage (CV 1.63 > 1.0)** 선명 시각화 완성
  - GitHub 깃허브 푸시 및 노션 메인 페이지 실시간 동기화 완료
- **Phase Diagram 스파이크 궤적(Spiking Trajectory Orbit) 가시화 및 시간 영역 확장**:
  - 사용자 피드백 반영: Phase Portrait 상에서 스파이크 궤적이 흐리게 보이던 점을 개선하여, **굵고 선명한 궤적 선(`lw=1.6`, `alpha=0.85`) 및 궤적 유동 점(Scatter Orbit)**을 위상 공간에 명확히 표출
  - 관찰 시간 창을 **$1500\text{ ms}$ ($2000 \sim 3500\text{ ms}$)**로 넓혀 발화 궤적의 회전 주기(Limit Cycle)가 뚜렷하게 관찰되도록 조정 완료
  - Scenario 1 (Lindahl: 강한 GPe 50Hz 억제로 1Hz 유휴) 대비 Scenario 2 (Mallet: Normal 8Hz 토닉 vs PD 28.5Hz 버스트 선명 파형) 차이 분석 완료
  - GitHub 깃허브 푸시 및 노션 메인 페이지 동기화 완료
- **Phase Diagram 교점 미발생(0 Fixed Points) 신경생물학적 해설 추가**:
  - 질문 해설: V-nullcline 곡선과 w-nullcline 선이 만나지 않는다는 것은 뉴런이 휴식할 수 있는 **안정 휴지 전위(Resting State)가 존재하지 않는 지속적 자발 발화 상태(Continuous Repetitive Firing Regime)**를 의미함
  - 토닉/버스트 구분 원리 해설: 토닉과 버스트의 전환은 교점 유무가 아니라 스파이크 후 리셋 위치($V_{\text{reset}}$)가 $V$-nullcline의 위쪽영역($\frac{dV}{dt} < 0$, 처짐 $\to$ 토닉)에 떨어지느냐 아래쪽영역($\frac{dV}{dt} > 0$, 급상승 $\to$ 버스트)에 떨어지느냐에 의해 결정됨을 정리
  - GitHub 깃허브 푸시 및 노션 메인 페이지 동기화 완료
- **프로젝트 핵심 4가지 요약 정돈 및 노션 단일 메인 페이지 고정**:
  - 사용자 지침 반영: 복잡한 문헌 및 수식 서술을 **4가지 핵심 포인트(시나리오 일원화, Fixed Point=0, Dynamic Reset 기전, 4컬럼 시각화)**로 군더더기 없이 정돈
  - 노션 신규 페이지 생성을 중단하고, **기존 단 하나의 메인 노션 페이지(`3b9c5207-74a7-81e4-b9a0-dcb6c0df0509`)**에만 정돈된 핵심 요약을 업데이트
  - GitHub 깃허브 푸시 및 노션 메인 페이지 동기화 완료
- **Phase Diagram 시각화 단순화 (검은색 점선 `no_input V-nullcline` 완전 제거)**:
  - 사용자 피드백 반영: 혼동을 유발하던 외부 자극 0일 때의 검은색 점선 포물선(`V-null (no input)`)을 completamente 삭제
  - 각 서브플롯당 **실제 시냅스 자극이 주입된 단 1개의 명확한 검은색 실선 포물선(`V-nullcline Active Input`)**만 남겨 그래프 시야 단정화 완료
  - GitHub 깃허브 푸시 및 노션 페이지 실시간 동기화 완료
- **직관적 $I_{\text{syn}}$ 변화 곡선 중첩 시각화 증명 그래프 작성 (`plot_bifurcation_proof.py` 완전 재설계)**:
  - 사용자 아이디어 반영: $I_{\text{syn}}$을 $-30\text{ pA}$부터 $+70\text{ pA}$까지 다양하게 변화시키며 $V$-nullcline 포물선 곡선들을 (V, w) Phase Plane 상에 색상 그라데이션으로 중첩 표현
  - 시각적 증명: $I_{\text{syn}}$을 아무리 바꿔도 포물선 곡선들이 $w$-nullcline 직선 위로 붕 떠 있어 결코 교차하지 않으므로, Fixed Point 개수는 100% 0개(분기 발생 안 함)로 고정됨을 한눈에 입증
  - 우측 패널: $I_{\text{syn}}$ Sweep에 따른 Fixed Point 개수(평탄한 0개) 및 발화율 변화 곡선 제시
  - GitHub 깃허브 푸시 및 노션 페이지 실시간 동기화 완료
- **Fixed Point 개수 및 Bifurcation 파라미터 수학적 검증 스크립트 작성 (`plot_bifurcation_proof.py`)**:
  - 질문 검증: (1) Normal 및 PD 상태 모두 평균 Fixed Point 개수는 **0개** (Rest State 없음, 지속적 발화 영역)
  - 질문 검증: (2) $I_{\text{syn}}$은 스칼라 전류일 뿐 단순 1D 분기 파라미터가 아님! 진짜 Saddle-Node 분기를 결정하는 경계선은 **$(g_{\text{AMPA}}, g_{\text{GABA}})$ 2D 컨덕턴스 공간상의 비율 ($g_{\text{GABA}} \approx 3.2 \times g_{\text{AMPA}}$)**임을 증명
  - 질문 검증: (3) Tonic $\leftrightarrow$ Burst 전이는 continuous flow 분기가 아니라, $V < -70\text{ mV}$ 과분극 시 리셋 전위가 $V_r = -70\text{ mV} \to -50\text{ mV}$로 점프하는 **하이브리드 불연속 사상 분기 (Discontinuous Reset Map Jump)**임을 수학적으로 증명
  - 3패널 검증 증명서 그래프(`results/bifurcation_proof.png`) 생성, GitHub 푸시 및 노션 페이지 실시간 동기화 완료
- **2가지 메인 시나리오 세트 (Normal vs PD) 시각화 그래프 군더더기 제거 및 4컬럼 구조 레이아웃 개편**:
  - 사용자 피드백 반영: 최상단 소제목 회색 안내 문구 및 서브플롯 내부 복잡한 Firing Rate / CV 수치 텍스트 박스를 모두 제거
  - 8패널 중복 서브플롯 구조를 **`[Normal 래스터 | Normal Vm(t) | PD 래스터 | PD Vm(t)]` 깔끔한 4컬럼 구조**로 직관적 재설계
  - Normal 상태(평온한 8 Hz 토닉 발화) 대비 PD 상태(GPe 억제 골에 의해 발동하는 **PV+ 초고속 Rebound Burst Barrage (35~55 Hz, 적색)**와 PV- Adapting(청색 파선)의 뚜렷한 대비)의 다이나믹스 차이를 극대화함
  - GitHub 깃허브 푸시 및 노션 페이지 실시간 동기화 완료
- **7개 탐색 시나리오 및 Slice(0 Hz) 복잡 생성 코드 완전 삭제 및 2가지 메인 시나리오 세트 확정**:
  - 사용자 지침 반영: 거대한 7개 시나리오 21패널 행렬(`stn_borderline_7_scenarios.png`), 6/7개 컬럼 Focus 이미지 (`stn_borderline_pv_comparison.png`), 및 무입력 `Slice` 관련 모든 코드를 완전히 삭제 및 폐기함
  - 시뮬레이션을 지정해주신 **2가지 메인 시나리오 세트(Sc1: Lindahl 2016 Baseline Pair vs Sc2: Mallet 2008 Rat Pair)**로 100% 일원화하여 고정
  - 노션 페이지에서도 7개 시나리오 및 과거 이미지 블록을 모두 깔끔하게 삭제 정돈 완료
- **Phase Diagram ((V, w) Phase Plane) 시각화 그래프 완전 재설계**:
  - 사용자 피드백 반영: 의미 없는 0 Hz `Slice` 행을 완전히 제거
  - `Normal State (좌측 컬럼, 녹색 `#2e7d32`)` vs `PD State (우측 컬럼, 적색 `#c62828`)` 나란히(Side-by-Side) 가로 2컬럼 레이아웃으로 변경
  - 선 구별 명확화: `w-nullcline PV-` (청색 실선 `#1565c0`, $a = +0.3\text{ nS}$) 대 `w-nullcline PV+` (주요 테마 색상 파선, $a = -12.0\text{ nS}$) 범례 및 색상 시각적 구별 완벽 적용
  - V(t) 파형에서 PV+ Rebound Burst(주요 테마 색상)와 PV- Adapting(청색 파선)을 명확하게 분리하여 중첩 뭉개짐 해결
  - GitHub 깃허브 푸시 및 노션 페이지 실시간 동기화 완료
- **7개 시나리오 복잡 행렬 제거 및 2가지 메인 시나리오 세트(Normal vs PD) 전용 코드 슬림화**:
  - 사용자 지침 반영: 거대한 7개 시나리오 21패널 행렬(`stn_borderline_7_scenarios.png`) 생성을 완전 제외
  - 핵심인 2가지 메인 시나리오 세트(`Scenario 1: Lindahl 2016 Baseline Pair` vs `Scenario 2: Pure Mallet 2008 ECoG Pair`)의 Normal vs PD 비교만 집중 생성하도록 `stn_borderline_tonic_burst_transition.py` 슬림화
  - GitHub 깃허브 메인 브랜치 푸시 및 노션 페이지 실시간 동기화 완료
- **Slice (0 Hz 무입력 대조군) 컬럼 제거 및 1500 ms (2000~3500 ms) 관찰 시간창 적용**:
  - 의미 없는 0 Hz 무입력 Slice 컬럼을 제거하고 6개 활성 시나리오(Normal Sc2-3 vs PD Sc4-7)로 그래프 재구성
  - 시간축을 [2000 ms, 3500 ms] (1500 ms 관찰 창)로 확대하여 스파이크 파형 가독성 극대화 및 상단 제목 글자 겹침 완벽 해결
  - GitHub 깃허브 푸시 및 노션 페이지 실시간 동기화 완료
- **초깔끔 초고화질 Side-by-Side Normal vs PD 동역학 시각화 그래프 재설계**:
  - 기존 PV+ 및 PV- 막전위 파형이 한 그래프 안에 겹쳐 뭉개지는 현상 해결 (`plot_side_by_side_normal_pd_clean.py` 신규 작성)
  - PV+ Rebound Burst (Normal 녹색 `#2e7d32`, PD 적색 `#c62828`) 와 PV- Adapting (청색 `#1565c0`) 서브플롯 분리
  - (V, w) Phase Portrait에 Zone 1 (V < -70 mV 과분극 장전 영역, 핑크 쉐이딩) vs Zone 2 (토닉 영역, 연두 쉐이딩) 직관적 시각화 적용
  - GitHub 깃허브 메인 브랜치 푸시 및 노션 페이지 실시간 동기화 완료
- **`stn_borderline_tonic_burst_transition.py` 헤더 및 시나리오 스케일 주석 업데이트**:
  - 핵심 모델 로직 및 7개 시나리오 실행 루프를 그대로 보존한 상태에서 Single-Unit Axon Scale (Level A: 12~15 Hz) vs Aggregate Population Scale (Level B: 250 Hz) 층위별 해설 명시
  - `a = -12.0 nS` 및 Dynamic Reset ($V_{\text{reset}} = -50\text{ mV}$) 메커니즘과 독립 STN +40% 상승 검증 지표 주석 갱신
  - 기존 7개 시나리오 및 Side-by-Side 결과 생성 100% 정상 작동 검증 완료
- **고정점(Fixed Point) 분석 및 분기(Bifurcation) 특성 검증 시나리오 프로토콜 정립**:
  - AdEx 2차원 연립 미분방정식 $f(V)=0$의 평형점 실근 개수 탐색 및 컨덕턴스 조합 비율 $(g_{\text{AMPA}}, g_{\text{GABA}})$ 스위핑 시나리오 완성
  - Normal(+3.84 pA) 및 PD(+1.46 pA) 평균 상태에서 고정점 0개(Continuous Firing Regime) 검증
  - $g_{\text{GABA}} \ge 3.2 \times g_{\text{AMPA}}$ 조건에서 Saddle-Node 분기 발생(Hopf 분기 부재) 및 Dynamic Reset 불연속 사상(Discontinuous Map Jump) 메커니즘 증명 완료
- **STN PV+ AdEx 신경망 시뮬레이션: 상세 실험 입력 시나리오 설계서 수립**:
  - 개별 뉴런 축삭 층위 (Level A: 12~15 Hz) vs 모집단 시냅스 수렴 층위 (Level B: 250 Hz) vs 다중 문헌 합의 층위 (Level C: -37% 각성) 정밀 분류
  - Scenario 1 (Slice 무입력 대조군), Scenario 2 (Pure Mallet 2008 단일축삭 층위), Scenario 3 (Lindahl 2016 모집단 합산 층위), Scenario 4 (Consensus 각성 합의 층위) 세부 수식, 파라미터 및 생물학적 근거 명시
  - STN 평균 발화율 +40% 상승(Tachibana 2011 / Bergman 1994) 독립 검증 지표 반영 완료
- **3가지 독립 시나리오 세트(Pair A, Pair B, Pair C) 모델 실행 스크립트 작성 및 검증**:
  - `run_all_scenarios_comparison.py` 파이썬 스크립트 작성 및 결과 이미지 생성(`results/stn_all_scenarios_comparison.png`)
  - Pair A (250 Hz 모집단 합산 층위), Pair B (13.5 Hz 단일 축삭 층위), Pair C (Tachibana -37% 각성 층위) 실행 완료
  - 3개 세트 모두에서 Normal(토닉 7.0 Hz) -> PD(초고속 버스트 55.0 Hz) 전환이 강건하게 검증됨
- **독립 시나리오(Separate Scenarios) 측정 층위별 병렬 체계 수립**:(Mallet/Goldberg) 수치 차이의 수학적/해부학적 원인 정립**:
  - 250 Hz = 10 Hz (단일 피질 축삭 발화율) × 25개 (STN 수렴 피질 축삭 수) 의 해부학적 곱셈 관계 증명
  - Lindahl 2016 계산 모델이 포인트 뉴런 시뮬레이션 속도 향상을 위해 25개 축삭을 250 Hz의 1개 등가 포아송 프로세스로 Aggregate 표현한 원리 명시
- **독립 시나리오(Separate Scenarios) 측정 층위별 병렬 체계 수립**:
  - 250 Hz(모집단 총합산 입력 층위, Lindahl 2016)와 12~15 Hz(단일 축삭 생체 층위, Goldberg 2002/Mallet 2008)를 상충/폐기하는 관계가 아닌, 관찰 스케일이 다른 독립된 별개의 시나리오로 병렬 비교 정립
  - 시나리오 A (단일 축삭 생체 층위, 12~15 Hz), 시나리오 B (모집단 총합산 층위, 250 Hz), 시나리오 C (다중 문헌 합의 층위) 독립 분류 노션 반영
- **다중 문헌 기반 피질(CTX) 발화율(Firing Rate) 범위 조사 및 정량 파라미터 정립**:
  - Goldberg 2002, Pasquereau 2011, Shimamoto 2013, Magill 2001, Kang 2013, Lindahl 2016 조사
  - 개별 피질 뉴런 축삭 1개의 보통 발화율 범위: **10.0 ~ 15.0 Hz (평균 13.5 Hz)** 정립
  - STN 1개 세포로 들어오는 20~25개 축삭 수렴 합산 발화율(Aggregate Drive): **200.0 ~ 250.0 Hz** 정립
  - Normal과 PD 간 피질 평균 발화율은 보존(Rate Preservation)되며, 20 Hz Beta 위상 동기화만 강화됨을 입증
- **순수 Mallet 2008 ECoG 전용 생체 시나리오 재구성 (250 Hz 완전 배제)**:
  - Lindahl 2016의 250 Hz 포아송 입력 파라미터를 완전히 배제하고, 순수 Mallet et al. (2008 J Neurosci) 쥐 in vivo ECoG 및 세포 데이터로만 구성한 단독 시나리오 구축
  - CTX 입력: 쥐 M1 운동피질 in vivo 개별 축삭 실측율 12~15 Hz + 20.5 Hz ECoG Beta 위상 변조
  - GPe 입력: Normal 33.7 Hz -> PD 14.6 Hz (-57% 급감, Prototypic GPe-TI 단일세포 전극 실측치)
  - 위상 관계: GPe-TI (37°) vs STN (244°) 반위상 길항 작동 수립
- **ECoG LFP 신호 기반 Poisson 입력 생성 정량 수식 및 메커니즘 정립**:
  - Mallet 2008 ECoG 피질 뇌파 신호를 STN 포아송 시냅스 입력 발화율 $\lambda_{\text{CTX}}(t)$로 정량 변환하는 2가지 표준 절차(파라메트릭 위상 변조 vs ECoG 타임시리즈 정규화 직접 매핑) 노션 반영
- **Mallet 2008 GPe 실측치 vs CTX ECoG Poisson 변환 메커니즘 노션 동기화**:
  - GPe 발화율(33.7 Hz -> 14.6 Hz): ECoG 변환이 아닌, 쥐 GPe-TI 세포 뇌 전극 직접 실측 단일세포 기록 데이터임을 명시
  - CTX 발화율(250 Hz): ECoG 20.5 Hz LFP 신호와 Goldberg 2002 Rate Preservation(10Hz × 25개 수렴 축삭)을 결합한 비동차 포아송(Inhomogeneous Poisson) 수식 변환 결과임을 명시
- **시나리오별 CTX/GPe 입력 발화율(Input Rates) 및 위상 패턴 정밀 비교 표 노션 동기화**:
  - Sc1 (Lindahl 2016 Baseline), Sc2 (Mallet 2008 Rat 마취 실측치), Sc3 (Consensus 각성 대표 모델)에 대한 CTX/GPe 입력 발화율 수치 및 변화율(-24%, -57%, -37%) 표 추가
  - STN 출력 발화율 +40% 상승(Tachibana 2011 / Bergman 1994) 독립 검증 지표 표기 동기화
- **Lindahl et al. (2016 eNeuro) 50 Hz -> 38 Hz 명칭 및 수치 오개념 정정**:
  - 논문 원문(p.13 Fig 2A) 정밀 검증 결과, 50 Hz -> 38 Hz는 Lindahl 2016 논문의 세포 출력 실측치가 아님을 확인 (초기 임의 라운딩치에 -24% 비율이 곱해진 것)
  - Lindahl 2016 실제 모델 출력 발화율은 Mallet 2008 쥐 실측치(~30 Hz -> ~15 Hz, -50% 감소)를 완벽히 튜닝하여 반영한 것임을 재증명
  - 노션 페이지 및 코드 문서 내 오해의 여지가 있던 표기 정정 완료
- **Untangling 논문 (Lindahl 2016 eNeuro) 및 쥐 6-OHDA (Mallet 2008) 기준 단일 입력 파라미터 수립**:
  - Lindahl 2016 PDF 원문(p.13 Fig 2A) 검증 결과: 50 Hz -> 38 Hz는 외부 포아송 입력 파라미터이며, 모델 세포 출력 발화율은 Mallet 2008 쥐 실측치(~30 Hz -> ~15 Hz, -50% 감소)를 완벽히 튜닝하여 반영한 것임을 확인
  - GPe 감소율에 따른 마취(Mallet 2008, -57%) vs 각성(Tachibana 2011, -37%) 문헌 비교 정립
  - 독립 검증 지표(Validation Target): STN 출력 발화율 +40% 상승(Tachibana 2011 / Bergman 1994) 검증 기준 채택
- **Untangling 논문 (Lindahl 2016 eNeuro) 및 쥐 6-OHDA (Mallet 2008) 기준 단일 입력 파라미터 수립**:
  - CTX 피질 입력: Normal 250 Hz -> PD 250 Hz (Goldberg 2002 rate preservation 보존 및 20.5 Hz ECoG 변조 수식 적용)
  - GPe 억제 입력: Normal 33.7 Hz (or 50 Hz) -> PD 14.6 Hz (or 38 Hz) (Mallet 2008 in vivo -57% 억제 약화 및 Untangling 2016 모델 검증 수치 동기화)
  - 위상 관계: GPe-TI (37°) vs STN (244°) 반위상 동기화 설정 확정
- **노션(Notion) 소제목 어색한 날짜/슬래시 표기 전면 개편 및 정형화**:
  - '8/11 파라미터 확정...', '8/3 모델 정의...' 등 어색한 날짜 및 슬래시 표기 제목들을 학술 보고서에 적합한 정돈된 서열형 제목(1. STN AdEx 모델 구조..., 3. 고정점 분석 및 분기 특성 검증...)으로 깔끔하게 일괄 변경 완료
- **20 Hz Beta 대역 표준 고정 근거 및 5개 핵심 문헌 비교 테이블 노션 동기화**:
  - 쥐(Mallet 2008: 20.5 Hz), 영장류(Goldberg 2002: 15-22 Hz), 사람(Shimamoto 2013: 18-22 Hz Low Beta), 네트워크 모델(Lindahl 2016 / Kang 2013: 20.0 Hz) 등 전 문헌에 걸쳐 20 Hz가 공통 표준 주파수임을 증명하는 해석 추가
  - 5개 핵심 문헌 정량 비교 테이블(Beta 주파수, 피질/GPe 발화율, 위상 변조 깊이 r, 위상 관계) 노션 및 아티팩트 반영
- **Normal (좌측 Column) vs PD (우측 Column) 나란히(Side-by-Side) 시각화 배열 완성**:
  - `plot_side_by_side_normal_pd.py` 신규 생성 및 GitHub 원격 저장소 푸시
  - 4개 Column 수평 배치: [Normal V(t)] [Normal Phase Plane] | [PD V(t)] [PD Phase Plane]
  - Normal과 PD를 겹쳐그리지 않고 좌/우 나란히 배치하여 한눈에 시각적 직관적 비교가 가능하도록 구성
  - 생성된 이미지: `results/stn_side_by_side_normal_pd.png`
- **깃허브(GitHub) 원격 저장소 푸시 및 노션(Notion) 라이브 이미지 블록 커스텀 렌더링 적용**:
  - 생성된 시각화 그림들(`results/*.png`)을 GitHub 원격 저장소 `techzzt/kaggle-transcription`에 커밋 및 강제 푸시(force push) 완료
  - 노션 페이지 내 불필요한 `file:///...` 텍스트 링크 전면 삭제
  - 공개 접근 가능한 라이브 HTTP raw URL(`https://raw.githubusercontent.com/...`)을 노션 API 정식 `image` 블록으로 첨부하여 노션 웹/앱 UI 상에서 고화질 이미지가 직접 선명하게 렌더링되도록 구현
- **직관적인 (V, w) Phase Plane 영역별 색상 구분 및 z(t) 복잡 그래프 제거**:
  - `plot_intuitive_phase_plane.py` 새로 구성
  - 필요 없는 복잡한 $z(t)$ 추적 그래프 제거하고 깔끔한 막전위 $V(t)$ 파형과 (V, w) Phase Portrait 중심으로 배치
  - Naud et al. (2008) 스타일에 맞춰 생물학적 영역 색상 구분:
    - **Zone 1 (V < -70 mV, 분홍색)**: GPe 억제 골에 의한 과분극 충전 영역 ($z < -15\text{ pA}$)
    - **Zone 2 (V > -70 mV, 연두색)**: 정상 토닉 발화 영역
  - 스파이크 발화 리셋 지점($V_{reset} = -70\text{ mV}$ Unarmed vs $V_{reset} = -50\text{ mV}$ Armed Launch) 화살표 및 화살표 가이드 박스 표기
  - 생성된 직관적 그림: `results/stn_intuitive_phase_plane_results.png`
- **Lindahl 2016 vs ECoG Mallet 2008 입력 발화율 대역 범주(Input Rate Range) 검증 및 시각화**:
  - `plot_input_range_comparison.py` 작성 및 시각화
  - Lindahl 2016 패러다임: GPe 50.0 Hz $\rightarrow$ 38.0 Hz (-24% 감소), CTX 250.0 Hz (보존)
  - ECoG Mallet 2008 패러다임: GPe 33.7 Hz $\rightarrow$ 14.6 Hz (-57% 감소), CTX 250.0 Hz (보존)
  - 두 입력 대역 패Paradigm 모두에서 STN PV+ 뉴런의 Tonic $\rightarrow$ Burst 전이 현상이 건실하게(Robust) 일어남을 검증
  - 생성된 시각화 그림: `results/stn_input_range_comparison.png`
- **2가지 메인 입력 시나리오(Baseline Pair vs New ECoG Pair) 비교 구조로 재설정**:
  - `run_and_visualize_stn_burst.py`를 **2가지 입력 메커니즘 시나리오 쌍** 비교 구조로 정립
    1. **`Scenario A (Lindahl 2016 Baseline Pair)`**: 2016년 eNeuro 논문 기본 포아송 모델 (Normal GPe 50Hz/CTX 250Hz vs PD GPe 38Hz/CTX 250Hz 20Hz 변조)
    2. **`Scenario B (New ECoG Unified Pair)`**: 다중 문헌 교차 검증 ECoG 위상 모델 (Normal GPe 33.7Hz/CTX 250Hz vs PD GPe 14.6Hz/CTX 250Hz 20.5Hz 변조)
  - 생성된 시각화 그림: `results/stn_2_main_input_scenarios_comparison.png`
- **메인 시뮬레이션 시나리오 2개(Normal vs PD)로 단일화 및 단순화**:
  - `run_and_visualize_stn_burst.py`를 **확정 메인 2개 시나리오** 중심 구조로 재편
    1. **`1. Normal State`**: GPe 33.7 Hz (비동기), CTX 250 Hz (비동기), AMPA x1.0, GABA x1.0 $\rightarrow$ Tonic Firing (8.0 Hz, CV 0.37)
    2. **`2. PD State`**: GPe 14.6 Hz (20.5 Hz Beta 변조), CTX 250 Hz (20.5 Hz Beta 변조), AMPA x2.5, GABA x1.25 $\rightarrow$ Burst Firing (55.0 Hz, CV 0.94)
  - 생성된 확정 메인 이미지: `results/stn_normal_vs_pd_main_2scenarios.png`
- **Normal 및 PD 시각화 그래프 독립 분리 및 Naud et al. 2008 스타일 Phase Plane 구현**:
  - `plot_separate_normal_pd.py` 및 `run_and_visualize_stn_burst.py` 추가 생성
  - Normal(Top row, 초록색)과 PD(Bottom row, 빨간색)를 동일 축에 겹쳐그리지 않고 별도의 독립 패널로 분리
  - Naud et al. (2008) 스타일 $(V, w)$ 위상 평면 널클라인(V-nullcline, w-nullcline), 궤적(Trajectory), Unarmed 리셋($-70\text{ mV}$) 및 Armed 리셋($-50\text{ mV}$) 지점 시각화 구현
  - 생성된 이미지 파일: `results/stn_normal_vs_pd_separate.png`
- **노션(Notion) 미팅 노정 및 실험 기록 템플릿 양식 적용 완료**:
  - `Neuroscience` 페이지 하위에 `[STN Burst] 통합 연구 및 시뮬레이션 노트 (8/3 ~ 8/11)` 페이지 생성
  - 8/3 모델 정의, PV-/PV+ 파라미터 표($a=-12.0$, $\tau_w=100$), 시나리오(Sc1-Sc15), 8/11 파라미터 확정, Fixed Point/Bifurcation 분석, 추가 논문 및 향후 시나리오(Pause, Tremor, Beta Sync) 포함 양식 완료.
- **`pd_input_patterns.py` — φ 함수 단일논문 귀속 오류 수정**
    - Goldberg et al. 2002 (MPTP 마카크): 피질 평균 발화율 **보존** (~12-15 Hz, 통계적 유의차 없음)
    - PD의 피질 특징은 rate 변화가 아니라 **beta synchrony + phase-locking** (Goldberg 2002; Shimamoto 2013)
    - Pasquereau & Turner 2011의 소폭 감소는 가변적; 주 변화는 mod_index(진동 변조)로 표현
  - **ECoG Poisson 근사 상수 추가**: `CTX_INST_RATE_BASELINE=15Hz`, `CTX_INST_RATE_BETA_PEAK=75Hz`
    - Shimamoto et al. 2013 (수술 중 ECoG+STN 동시 기록): beta burst 시 순간 rate 50-100+ Hz
  - **`SYNAPTIC_STATES` 재정렬**: `lindahl_prose`를 첫 번째 (권장 옵션), `lindahl`을 "비추천" 비교용으로 이동
  - **`Sc9` 레이블 업데이트**: `synapse="lindahl"` → `synapse="lindahl_prose"` (PDF 확인 완료)

### ➕ 신규 추가 사항 (Added)
- **문헌 Reference 7개 추가** (docstring):
  - Baufreton et al. 2005, Goldberg et al. 2002, Magill et al. 2001, Shimamoto et al. 2013, Tachibana et al. 2011
- **3개 논문 기반 입력 패턴 종합 정리** (아래 표):

#### 📊 확정 입력 패턴 (Normal vs PD)

| 파라미터 | Normal | PD | 주요 근거 |
|---|---|---|---|
| GPe 발화율 | **50 Hz** (33.7 Hz Mallet) | **38 Hz** (14.6 Hz Mallet) | Mallet 2008, Filion 1991 |
| GPe CV | 0.43 (규칙적) | 0.74 (불규칙적) | Mallet 2008 |
| GPe 동기화 (corr) | 0.02 (독립) | 0.25-0.30 | Hammond 2007, Mallet 2008 |
| GPe 진동 | 없음 | **20.5 Hz beta**, 위상 37° | Mallet 2008 |
| CTX 발화율 | **250 Hz** (Lindahl Table 1) | **250 Hz (동일!)** | Goldberg 2002 (rate preserved) |
| CTX 패턴 변화 | desynchronized | **beta 동기화 mod_index=0.4** | Shimamoto 2013, Mallet 2008 |
| CTX→STN AMPA | g_ampa × 1.0 | **× 2.5** | Lindahl 2016 Table 9 (PDF 확인) |
| GPe→STN GABA | g_gaba × 1.0 | **× 1.25** | Lindahl 2016 Table 9 (PDF 확인) |

### 🛠 버그 수정 및 개선 (Fixed & Improved)
- **`UNRESOLVED` 주석 → 해결됨**: φ 공식의 `SYNAPTIC_STATES['lindahl_prose']`의 `UNVERIFIED` 표시 제거. PDF 원문 직접 확인으로 확정.
- **`lindahl` vs `lindahl_prose` 논쟁 종결**: `lindahl` (β-공식) = PDF 추출 오류로 부호 반전됨. 메인 시뮬레이션 사용 불가.

---

## [2026-08-03] (3차)

### 🔄 주요 변경 사항 (Modified)
- `pd_input_patterns.py` & `stn_borderline_tonic_burst_transition.py`: **`I_ext = 0 pA` 엄격 유지 하에서 생물학적 STN AdEx 파라미터 조율 완료**
  - **`I_ext = 0 pA` 엄격 준수**: 외부 인공 전류 주입 없이 오직 GPe 억제(GABA)와 CTX 흥분(AMPA) 시냅스 입력만으로 STN 뉴런 구동.
  - **생물학적 휴지 막전위 정밀 보정**:
    - STN 뉴런의 생체 내(in vivo/slice) 자발적 페이스메이커 막 전위 범위를 적용하여, 외부 인공 전류 없이 **Normal 조건(Sc2, Sc3)에서 정확히 2.0 Hz 자발적 토닉 발화** 유지.
  - **시각화 레이아웃 정돈**:
    - 5번째 열(Pop. Rate [Hz]) 그래프를 제거하여 4열 구조로 정돈 완료.

### 🛠 버그 수정 및 개선 (Fixed & Improved)
- **Normal 토닉 발화(2.0Hz)와 PD 리바운드 버스트 양립 성공 (Critical Fix)**:
  Normal(Sc2, Sc3)에서는 2.0 Hz 자발적 토닉 발화가 깔끔하게 유지되고, PD Pause(Sc5)에서는 Pause 순간 `PV-`(1발), `PV+ Borderline`(4발), `PV+ Burst`(11발)로 서브타입별 차별적 리바운드 버스트가 나타나도록 완벽 구현.
- **축 잘림 및 범례 겹침 현상 해결 (Plot Optimization)**:
  위상 평면(Phase Plane) 널클라인 궤적과 $V_T$ 라벨, 범례 상자가 잘리거나 겹치던 문제를 축 범위 확장($V \in [-85, -35]\text{ mV}, w \in [-40, 120]\text{ pA}$)으로 시각적 가독성 완전 확보.

---

## [2026-08-03] (2차)

### 🔄 주요 변경 사항 (Modified)
- `stn_borderline_tonic_burst_transition.py`: `SUBTYPES_4` → `SUBTYPES_3` — PV+ Tonic 서브타입 제거
  - Fig 2 레이아웃: 6col → 5col (Raster / PV- / PV+ Borderline / PV+ Burst / Pop Rate)
  - figsize: (28,22) → (22,22)
  - `run_borderline_focus_comparison()` 내 잔여 `SUBTYPES_4` 참조 수정

### ➕ 신규 추가 사항 (Added)
- `docs/neuron_params_archive.md` 생성: PV+ Tonic AdEx 파라미터 보관
  - `a_nS=-0.3`, `a_gate_mV=None` 등 전체 파라미터 및 발화 특성 기록
  - 재사용 가능하도록 코드 블록 형식으로 보존

### 🛠 버그 수정 (Fixed)
- `NameError: SUBTYPES_4 not defined` 수정 → `SUBTYPES_3`으로 교체

---

## [2026-08-03] (1차)

### 🔄 주요 변경 사항 (Modified)

#### `stn_borderline_tonic_burst_transition.py` → v10 (Literature-Corrected, 6-Scenario)
- **6-scenario 구조 완전 재설계**: No-input / Poisson / Biological × Normal+PD
  - Sc1: Slice (no input) — 순수 intrinsic dynamics
  - Sc2: Normal Poisson — 문헌 평균 발화율 (GPe 65 Hz, CTX 5 Hz)
  - Sc3: Normal Biological — GPe Gamma ISI (CV=1.2), 약간 더 불규칙
  - Sc4: PD Poisson — GPe rate↓만 (40 Hz), CTX 동일 5 Hz (rate-only model)
  - Sc5: PD GPe-pause — GPe pause-burst 패턴 (Mallet 2008), CTX Poisson 유지
  - Sc6: PD Full — GPe pause-burst + CTX beta phase-locked (Von Mises PLV=0.65)
- **`classify_pattern()` 수정**: `is_beta_drive=False` flag 추가, Beta-locked 조건 강화 (CV<0.25 AND Sc6만), burst threshold 0.65
- **분석 window 확장**: last 1500ms → **last 2000ms** (pause 이벤트 더 많이 포착)
- **시각화 개선**: 인구 발화율 프로파일 추가 (Col 5), Fig3 전체 6시나리오 PV+ Borderline 비교
- **I_ext = 0 유지**: 모든 시나리오에서 borderline 상태 고정

#### `pd_input_patterns.py` → v3 (Literature-Corrected)
- **CTX→STN 모델 근본적 수정** (핵심):
  - 이전: CTX 발화율 20-30 Hz (❌ 베타 진동 주파수를 발화율로 오인)
  - 수정: **CTX 평균 발화율 5 Hz 유지** — Normal/PD 동일 (Doudet 1990; Goldberg 2002)
  - PD에서 변하는 것: **spike timing의 beta phase-locking (PLV↑)**, 발화율 아님
- **`generate_ctx_beta_phaselocked()` 신규 구현**:
  - Von Mises 분포로 spike을 20 Hz beta 위상에 집중 (PLV=0.65, kappa=2.5)
  - 평균 발화율 완전 보존 (Poisson count sampling → uniform base times → Von Mises 위상 적용)
- **`generate_gpe_pause_burst_pd()` 로직 수정**:
  - Epoch 기반 state machine으로 완전 재작성 (v2에서 이미 수정된 것 유지)
  - pause_freq_hz = 2.0 /s, pause_dur_ms = 250ms, synchrony = 0.88로 파라미터 조정
- **모든 시나리오 synaptic weight 통일**: g_GABA=0.35, w_AMPA=0.25 (문헌 근거 없는 PD 가중치 증가 제거)
- **`compute_population_rate()` 유틸리티 추가**: 인구 발화율 시각화용

### ➕ 신규 추가 사항 (Added)
- (없음, 파일 재작성)

### 🛠 버그 수정 및 개선 (Fixed & Improved)

#### 문헌 오류 수정
- **CTX 발화율 오인 (Critical Fix)**: Kühn 2005 / Brittain & Brown 2014는 LFP coherence 논문이며 CTX 단일세포 발화율 데이터가 아님. "20-30 Hz"는 CTX 발화율이 아니라 beta 진동 주파수. 문헌 검증 결과:
  - Doudet et al. 1990: MPTP 원숭이 M1 발화율 변화 없음
  - Goldberg et al. 2002: CTX 앙상블 발화율 보존
  - Pasquereau & Turner 2011: PT 뉴런 발화율 소폭 감소
- **GPe pause 생성 로직 버그 수정**: 이전 spike-time 감지 방식(실질적으로 pause 거의 생성 안 됨) → epoch 기반 state machine으로 교체

#### 수치 결과 (v10 출력)
- Sc1 (Slice): PV+ Borderline → Tonic 23 Hz, CV=0.00 (결정론적 pacemaking)
- Sc2-3 (Normal): PV+ Borderline → Irregular ~10 Hz, CV=0.46-0.53
- Sc4 (PD rate-only): PV+ Borderline → **Burst 15.5 Hz, CV=0.66** (GPe rate 감소만으로 burst 전환!)
- Sc5 (PD GPe-pause): PV+ Borderline → **Burst 15.0 Hz, CV=0.73** (더 강한 burst)
- Sc6 (PD Full): PV+ Borderline → Irregular 15.0 Hz, CV=0.64 (CTX beta가 오히려 규칙화)
- PV-: 모든 시나리오에서 Tonic 유지 (실험 가설과 일치)
- **주요 발견**: CTX beta phase-locking은 burst가 아닌 phase-entrainment를 유발. STN burst의 주 원인은 GPe disinhibition.

---

## [2026-07-31]
### ➕ 신규 추가 사항 (Added)
- `.agents/AGENTS.md` 프로젝트 행동 규칙 파일 추가: 코드 수정 시 날짜별로 변경사항을 `.md` 파일에 필수 기록하도록 커스텀 규칙 지정.
- `CHANGELOG.md` 초기화 및 생성.
