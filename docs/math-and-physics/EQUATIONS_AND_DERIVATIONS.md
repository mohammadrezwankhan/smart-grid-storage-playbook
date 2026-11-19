# Equations and derivations

[Handbook](../INDEX.md) · [Parameters](PARAMETERS_AND_SYMBOLS.md) · [Assumptions and limits](ASSUMPTIONS_AND_LIMITS.md) · [Existing detailed model guide](../../models/README.md)

This chapter describes source `8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e`. Native equations are implemented constraints and accounting rules. Algebra marked **derivation** explains those rules; it does not fit equipment data or establish grid-code compliance.

## 1. Native conventions and composition

Use AC active power $P$ in MW: positive is discharge/injection, negative is charging. Reactive $Q$ is MVAr: positive injection, negative absorption. Apparent capability is MVA. Stored energy is MWh and SOC is a fraction. Profiles hold each input constant over its interval; durations in minutes convert to hours for energy and to seconds for filtering/ramping. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L103-L149) [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L221-L272)

The composed path is measurement/filter → frequency adjustment → nameplate P bound → ramp → temperature → energy → P–Q allocation → delivered-energy recomputation. Voltage independently supplies the Q request. Later constraints can override an earlier ramp target; the model is not a simultaneous optimization or dynamic network solution. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L191-L320)

## 2. P-Q capability

For a circular bound $S>0$, a request is feasible when $\sqrt{P_r^2+Q_r^2}\le S$. Otherwise:

- **Active priority:** $P=\operatorname{clip}(P_r,-S,S)$ and $Q=\operatorname{clip}(Q_r,-\sqrt{S^2-P^2},\sqrt{S^2-P^2})$.
- **Reactive priority:** apply the same construction with P and Q exchanged.
- **Proportional:** $(P,Q)=S(P_r,Q_r)/\sqrt{P_r^2+Q_r^2}$.

The implementation protects square-root arguments with a zero floor. Circular utilization is $\sqrt{P^2+Q^2}/S$; curtailments are signed requested-minus-delivered differences. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L278-L365)

For a symmetric sampled boundary $q_{\max}(p)$, points use nonnegative magnitudes, start/end on the axes, increase strictly in P, decrease strictly in Q and form a concave piecewise-linear graph. Between points,

$$
q_{\max}(p)=q_i+\frac{p-p_i}{p_{i+1}-p_i}(q_{i+1}-q_i).
$$

The inverse graph supplies the active limit for reactive priority. Proportional allocation intersects the requested ray with a segment; utilization is the output magnitude divided by the boundary magnitude on that ray. It is not a nominal circular utilization. A directional envelope selects one of four curves from the request signs and enforces shared-axis consistency. [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L45-L260) [models/pq_capability.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/pq_capability.py#L368-L449)

These are static envelopes. A sampled curve is not inferred from topology, voltage, temperature, SOC or manufacturer performance.

## 3. Volt-VAR and frequency-watt requests

Let $v_1<v_2\le1\le v_3<v_4$ and normalized maximum reactive request $q_m>0$. The Volt-VAR request is

$$
q(v)=
\begin{cases}
q_m,&v\le v_1,\\
q_m(v_2-v)/(v_2-v_1),&v_1<v<v_2,\\
0,&v_2\le v\le v_3,\\
-q_m(v-v_3)/(v_4-v_3),&v_3<v<v_4,\\
-q_m,&v\ge v_4.
\end{cases}
$$

The MVAr request is $Q_r=q(v)Q_{\mathrm{base}}$. Standalone Volt-VAR defaults the base to the circular MVA limit. Grid-support sequences instead derive the applicable injection/absorption axis from the selected boundary unless an explicit base is supplied. No voltage feedback from delivered Q is solved. [models/volt_var.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/volt_var.py#L18-L114) [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L221-L227)

For frequency-watt, $\delta=f_0-f_c$, deadband $d\ge0$, and full response deviation $D>d$:

$$
\alpha=
\begin{cases}
0,&|\delta|\le d,\\
\min(1,(|\delta|-d)/(D-d)),&|\delta|>d.
\end{cases}
$$

The adjustment is $\alpha P_{\max,\mathrm{dis}}$ below nominal and $-\alpha P_{\max,\mathrm{ch}}$ above nominal. Add baseline $P_b$, then clamp to $[-P_{\max,\mathrm{ch}},P_{\max,\mathrm{dis}}]$. The default 50 Hz/deadband/response values are illustrative configuration, not an applicable grid-code rule. [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L85-L136) [models/frequency_watt.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/frequency_watt.py#L220-L231)

## 4. Measurement filter, signed ramp and temperature

For a held input $u$, prior filtered output $y_0$, positive interval $\Delta t$ and time constant $\tau$ in seconds,

$$
y_1=y_0+(u-y_0)(1-e^{-\Delta t/\tau}).
$$

**Derivation:** this is the exact held-input solution of $\tau\,dy/dt=u-y$ from initial value $y_0$. The code uses `-expm1(-Δt/τ)` to preserve the small response fraction. It does not simulate sensor jitter/bias or a higher-order controller. [models/measurement_filter.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/measurement_filter.py#L35-L71)

For positive signed ramp rates $r_\uparrow,r_\downarrow$ in MW/min and available seconds $\Delta t_s$,

$$
P_{\mathrm{ramp}}=\operatorname{clip}\!\left(
P_r,\ P_0-r_\downarrow\Delta t_s/60,\ P_0+r_\uparrow\Delta t_s/60
\right).
$$

Crossing zero remains one signed trajectory. The frequency-watt API distinguishes ramp seconds from energy-response minutes; the sequence uses each interval duration for both after conversion. [models/ramp_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/ramp_limits.py#L46-L95) [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L228-L244)

Temperature limits interpolate independent charge/discharge limits linearly between supplied temperature samples. Outside the sample range they clamp to the nearest endpoint; `endpoint_clamped` distinguishes an out-of-range input from an exact endpoint. Effective directional limits are the smaller of nameplate and sampled values. Temperature is an external input, not a predicted thermal state. [models/temperature_derating.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/temperature_derating.py#L49-L182)

## 5. Exact interval energy and standing losses

Let capacity be $C$ MWh, initial energy $E_0=s_0C$, limits $E_{\min}=s_{\min}C$, $E_{\max}=s_{\max}C$, and interval $h=\Delta t_{\min}/60$ hours. Stored dispatch power is

$$
c(P)=
\begin{cases}
-P/\eta_d,&P>0,\\
-P\eta_c,&P\le0.
\end{cases}
$$

With constant stored-side auxiliary demand $A\ge0$ MW and continuous self-discharge coefficient $\lambda\ge0$ per hour, the assumed equation is

$$
\frac{dE}{dt}=c(P)-A-\lambda E.
$$

**Derivation:** integrating the constant-coefficient equation gives

$$
R=e^{-\lambda h},\qquad
H=
\begin{cases}
h,&\lambda=0,\\
(1-e^{-\lambda h})/\lambda,&\lambda>0,
\end{cases}
\qquad
E_1=E_0R+(c(P)-A)H.
$$

$H$ has units of hours. The code evaluates its nonzero branch with `-expm1(-λh)/λ`. Define $E_L=E_0R-AH$. Discharge headroom is $\eta_d(E_L-E_{\min})/H$ and charging magnitude headroom is $(E_{\max}-E_L)/(\eta_c H)$, subject to zero floors and validation. The requested signed power is reduced to the applicable endpoint. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L76-L149)

Losses that would cross the minimum SOC without sufficient charging are rejected rather than silently erased. Numerical tolerances and final bound clamping are implementation guards, not physical uncertainty bounds. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L115-L193)

The reports separate

$$
\Delta E_{\mathrm{dispatch}}=c(P)h,\quad
E_{\mathrm{aux}}=Ah,\quad
E_{\mathrm{self}}=\Delta E_{\mathrm{dispatch}}-E_{\mathrm{aux}}-(E_1-E_0).
$$

Consequently $\Delta E=\Delta E_{\mathrm{dispatch}}-E_{\mathrm{aux}}-E_{\mathrm{self}}$. The auxiliary load is supplied from stored energy in this model; a separate feeder belongs in a separate account. [models/energy_limits.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_limits.py#L144-L214) [models/README.md](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/README.md#L392-L457)

## 6. Sequence accounting and throughput

The energy sequence carries each ending SOC into the next interval. Signed net AC energy is $\sum_i P_i h_i$; curtailment energy is $\sum_i |P_{r,i}-P_i|h_i$. Charge and discharge throughput counters are positive magnitudes. [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L50-L114)

Let $E_{sd},E_{sc}$ be positive stored discharge/charge totals and $E_{ad},E_{ac}$ positive AC discharge/charge totals. Then

$$
E_{\mathrm{conversion}}=E_{sd}-E_{ad}+E_{ac}-E_{sc},\qquad
N_{\mathrm{EFC}}=(E_{sd}+E_{sc})/(2C).
$$

The conversion-balance residual is signed AC delivery plus dispatch stored change plus conversion loss. The SOC residual compares final SOC with initial SOC plus total stored change divided by capacity. EFC is a throughput ratio, not rainflow counting, capacity fade or a warranty assessment. [models/energy_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/energy_sequence.py#L115-L183)

## 7. Reserve headroom and audit semantics

For a sustainable baseline $B$ and response duration, find feasible sustained upper/lower replacement setpoints $P_u,P_d$ after preserving the Q obligation and applying energy limits:

$$
R_\uparrow=\max(0,P_u-B),\qquad
R_\downarrow=\max(0,B-P_d).
$$

The baseline itself must satisfy nameplate, selected P–Q and response-duration energy checks. If standing losses require continued charging, the highest sustainable replacement can be **negative**; upward reserve can mean reducing charge while still covering losses. [models/reserve_headroom.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_headroom.py#L87-L214)

The sequence audit evaluates this headroom at each interval's starting SOC, then advances the baseline over that schedule interval. The response duration and schedule duration are distinct. Minimum margins and interval indices describe those sampled starts; no actual activation, recovery policy or continuous-in-interval minimum is calculated. [models/reserve_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/reserve_sequence.py#L123-L220)

## 8. Composed grid-service totals

The grid-support sequence carries delivered post-capability SOC/P and filtered frequency. Requested active energy uses unconstrained frequency-plus-baseline requests, delivered active energy uses final P, and active shortfall sums absolute differences. Reactive service is $\sum |Q_i|h_i$ in MVArh, so injection and absorption do not cancel in that service total. Individual intervals retain Q sign. [models/grid_support_sequence.py](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/models/grid_support_sequence.py#L265-L335)

These totals expose a chosen control composition; they do not model network-frequency evolution, voltage response, electromagnetic transients, dispatch economics or controller stability.

## 9. Selected browser grid screen

For model time $t$ in hours, demand baseline $D$, solar peak $S_p$, fixed battery contribution $P_b$ (all kW), and carbon factor $g$ g/kWh:

$$
P_s=S_p\max(0,\sin(\pi(t-6)/12)),
$$

$$
P_d=D\left(0.8+0.18\cos(2\pi(t-19)/24)+0.12e^{-((t-19)/3)^2}\right),
$$

$$
P_g=\max(P_d-P_s-P_b,0),\qquad
\mathrm{solarShare}=100\min(1,P_s/P_d),\qquad
\mathrm{emissions}=P_g g/1000.
$$

Emissions are kg/h. The share metric includes solar, not an assumed renewable battery contribution. Exports are uncredited, carbon intensity is fixed and storage energy/charging are omitted. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L199-L204) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L284-L288)

The four configured lessons check at 19 h with absolute tolerance 0.02 in the metric's units:

| Module | D / solar / battery (kW), carbon (g/kWh) | Declared expectations |
|---|---|---|
| 1 | 500 / 600 / 0, 400 | Import 550 kW; solar 0 kW |
| 2 | 500 / 600 / 100, 400 | Import 450 kW; emissions 180 kg/h |
| 3 | 800 / 300 / 200, 400 | Import 680 kW; emissions 272 kg/h |
| 4 | 500 / 600 / 300, 200 | Import 250 kW; emissions 50 kg/h |

[docs/lesson-config.json](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/lesson-config.json#L138-L305)

These are closed-form evaluations with input/time clamping, not an ODE integration or feasibility-constrained dispatch. Finite parameters clamp to declared ranges; nonnumeric/nonfinite inputs use engine defaults, without slider-step snapping. Strict inequalities ignore checkpoint tolerance; inclusive/equality comparisons use it. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L249-L264) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L338-L353)

## 10. Other shared browser branches

Nine other branches are explicitly present in the exported engine. They are generic synthetic demonstrations, not hidden native storage features. Their local symbols and units remain distinct. The following formulas describe those implemented branches without claiming field calibration.

### Battery discharge

For capacity $Q$ in Ah, requested current $I$ in A, elapsed $t$ in hours, resistance $R$ in ohms, ambient $T_a$, and initial percentage $S_0$:

$$
S=\operatorname{clamp}(S_0-100It/Q,0,100),\quad
I_e=\begin{cases}I&S>0\\0&S=0,\end{cases}
$$

$$
V=320+0.8S-I_eR,\quad P=VI_e/1000.
$$

Depletion time is $t_e=QS_0/(100I)$ for $I>0$ and infinity for $I=0$. With $t_h=\min(t,t_e)$ and $t_c=\max(0,t-t_e)$,

$$
T=T_a+\frac{I^2R}{8}(1-e^{-t_h/0.8})e^{-t_c/0.8}.
$$

The numerical coefficients and 0.8-hour relaxation are illustrative implementation constants. The voltage law is linear in SOC; current becomes zero at depletion. No calibration, BMS, pack topology, aging, or protection behavior is represented. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L178-L184) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L266-L274)

### Single thermal mass

Let heat input be $q$ W, conductance $h$ W/K, heat capacity $C_T$ J/K, and displayed time $t$ minutes:

$$
\Delta T=(q/h)(1-e^{-h(60t)/C_T}),\quad T=T_a+\Delta T,
$$

$$
q_\mathrm{removed}=h\Delta T,\quad E=C_T\Delta T/1000,\quad
q_\mathrm{net}=q-h\Delta T.
$$

**Derivation:** this is the closed-form solution of $C_T\,d\Delta T/d\tau=q-h\Delta T$ with $\Delta T(0)=0$ and $\tau=60t$ seconds. The one-node model omits spatial gradients and phase change. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L185-L191) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L275-L278)

### Cycle aging proxy

For coefficient $f$ labeled percent/1000 cycles, constant temperature $T$, C-rate $r$, initial capacity $Q_0$, and continuous cycle coordinate $t$:

$$
k=(f/100000)e^{(T-25)/20}\sqrt r,\quad x=e^{-kt},
$$

$$
\mathrm{retention}=100x,\quad Q=Q_0x,\quad
\mathrm{resistanceGrowth}=200(1-x),
$$

$$
E_\mathrm{throughput}=\frac{3.7Q_0}{1000}\frac{1-e^{-kt}}{k}.
$$

The final expression is the integral of the declining capacity proxy times an illustrative 3.7 V. The code uses `-Math.expm1(-k*t)` for its numerator. These coefficients are not fitted battery-life parameters; calendar aging is omitted. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L192-L198) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L279-L283)

### Compute cooling proxy

For server count $N$, nominal utilization $U_0$ percent, COP $\eta$, ambient $T_a$, and minutes $t$:

$$
u=\operatorname{clamp}(U_0+8\sin(t/8)+3\cos(t/3),0,100),
$$

$$
P_\mathrm{IT}=N(0.12+0.38u/100),\quad
P_c=\frac{P_\mathrm{IT}}{\eta}(1+0.025\max(T_a-20,0)),\quad
\mathrm{PUE}=1+P_c/P_\mathrm{IT},
$$

$$
T_\mathrm{in}=22+(T_a-22)e^{-t/15}
+\frac{4P_\mathrm{IT}}{N\eta}(1-e^{-t/15}).
$$

Powers are kW. The inlet expression is a heuristic evaluated using the instantaneous synthetic IT load; it is not a solved coupled airflow/thermal state equation. Coefficients have implicit units in the formula and are not sourced equipment characteristics. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L206-L212) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L290-L296)

### Agent coordination queue

For arrival rate $\lambda$, agent count $n$, per-agent rate $\mu$, and overhead $o$ percent:

$$
c=n\mu\left(1-\frac{o}{100}\frac{n-1}{n}\right),\quad
B=\max(0,\lambda-c)t,\quad R=\min(\lambda,c),
$$

$$
U=100\min(1,\lambda/c),\quad W=B/c+1/\mu.
$$

Here $R$ is a completion **rate**, unlike the accumulated processed-count metric of the generic security branch. $W$ is a deterministic proxy for delay, not a stochastic queueing theorem or measured service-level guarantee. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L213-L219) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L297-L301)

### Price-spread scenario

With basis-point inputs $b$, fees $f$, slippage $s$, notional $N$ USD, and hours $t$:

$$
b_t=b+12\sin(2\pi t/12)+5\sin(2\pi t/5),\quad e=b_t-f-s,
$$

$$
\mathrm{PnL}=Ne/10000,\quad \mathrm{cost}=N(f+s)/10000.
$$

This is one hypothetical opportunity at time $t$, not an integrated return series or a trading interface. All waves and inputs are synthetic. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L220-L226) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L302-L306)

### Second-order response

The documented differential equation is

$$
y''+2\zeta\omega_n y'+\omega_n^2y=K\omega_n^2r,\qquad
y(0)=y'(0)=0.
$$

The implementation evaluates the corresponding normalized step $s(t)$ analytically, with $y=Kr\,s$ and velocity $Kr\,s'$. Let $\omega=\omega_n$.

- For $|\zeta-1|<10^{-8}$: $s=1-e^{-\omega t}(1+\omega t)$ and $s'=\omega^2t e^{-\omega t}$.
- For $\zeta<1$, let $q=\sqrt{1-\zeta^2}$: $s=1-e^{-\zeta\omega t}[\cos(\omega qt)+(\zeta/q)\sin(\omega qt)]$ and $s'=(\omega/q)e^{-\zeta\omega t}\sin(\omega qt)$.
- For $\zeta>1$, let $q=\sqrt{\zeta^2-1}$, $r_1=-\omega(\zeta-q)$, $r_2=-\omega(\zeta+q)$: $s=1+[r_2e^{r_1t}-r_1e^{r_2t}]/(r_1-r_2)$ and $s'=r_1r_2[e^{r_1t}-e^{r_2t}]/(r_1-r_2)$.

The error metric is $r-y$, while theoretical overshoot is relative to the final $Kr$ level: $100e^{-\zeta\pi/\sqrt{1-\zeta^2}}$ for $\zeta<1$, otherwise zero. Thus nonunit gain changes steady error without changing the definition of theoretical overshoot. There is no discrete controller, saturation, sensor model, or numerical ODE solver. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L227-L233) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L307-L322)

### Charging proxy

For capacity $Q$ kWh, charger power $P_\mathrm{in}$ kW, efficiency $\eta$ percent, initial percentage $S_0<80$, and $h=t/60$ hours:

$$
P_e=P_\mathrm{in}\eta/100,\quad
h_{80}=(80-S_0)Q/(100P_e),\quad
\tau=0.2Q/P_e.
$$

Before taper, $S=S_0+100P_eh/Q$ and $P=P_e$. After taper begins,

$$
S=100-20e^{-(h-h_{80})/\tau},\quad
P=P_e e^{-(h-h_{80})/\tau}.
$$

Stored energy is $(S-S_0)Q/100$ and loss power is $P(100/\eta-1)$. SOC and charge power are continuous at 80%; the exponential approaches 100% asymptotically. The model does not implement a charger protocol, electrochemical charge limit, temperature constraint, or field-validated charging curve. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L241-L247) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L327-L334)


### Defensive review queue

For arrival rate $\lambda$, automatic-resolution fraction $a$ percent, reviewer count $n$, per-reviewer rate $\mu$, elapsed minutes $t$ and empty initial queue, let $d=\lambda(1-a/100)$ and $c=n\mu$:

$$
B=\max(0,d-c)t,\quad
C=100\min(1,(\lambda a/100+c)/\lambda),
$$
$$
R=(\lambda a/100+\min(d,c))t,\qquad U=100\min(1,d/c).
$$

$B$ and $R$ are counts, $C$ and $U$ percentages. **Derivation:** $B+R=\lambda t$ for the stated constant-rate assumptions. Correct automatic resolution is assumed; precision, recall, severity and real staffing performance are absent. This generic branch is not the selected grid lesson. [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L234-L239) [docs/index.html](https://github.com/mohammadrezwankhan/smart-grid-storage-playbook/blob/8bf7dd1d4cc1899dfc9fbb034f1fb3c35bd9763e/docs/index.html#L323-L325)

## Interpretation and numerical evidence

Native deterministic tests, browser arithmetic checkpoints and domain validation are separate evidence classes. The [ledger](../maintainer/VERIFICATION_EVIDENCE_LEDGER.md) records what ran. No equation above establishes a vendor rating, grid-code certificate, controller approval, safe energization decision or warranty result. Preserve explicit validity bounds and the [parameter provenance](PARAMETERS_AND_SYMBOLS.md).
