# T20 pre-registration: does dark energy sit at the observer's horizon ceiling?

Frozen 12 Oct 2026, before any model was fitted to these data. Only the file structures (column names, redshift list and quantity labels) were inspected.

## The prediction (Doc 20, from the forcing chain)

1. **Ceiling.** Composition across a boundary is area-law (Doc 19). No region can hold more than its own horizon allows. So the vacuum energy within the observer's horizon of size $L$ obeys $\rho_{\rm de}\le 3/(8\pi G L^2)$ (Cohen–Kaplan–Nelson form).
2. **Horizon.** The observer's horizon in UHL's sense is the boundary of everything finite composition can ever reach, i.e. the **future event horizon** $L=a\int_t^\infty dt'/a$.
3. **Saturation** [H]. Equilibrium is forgetting's fixed point, and it saturates the ceiling. So $\rho_{\rm de}=3c^2/(8\pi G L^2)$ with **$c=1$ exactly**.

This is Li's holographic dark energy with $c$ fixed to 1:

- $d\Omega_{\rm de}/d\ln a=\Omega_{\rm de}(1-\Omega_{\rm de})(1+2\sqrt{\Omega_{\rm de}})$;
- $E^2(a)=\Omega_{m0}a^{-3}/(1-\Omega_{\rm de}(a))$;
- $w=-\tfrac13-\tfrac23\sqrt{\Omega_{\rm de}}$;
- flat, with matter plus dark energy and radiation neglected. Radiation is neglected identically for $\Lambda$CDM.

## Data

- **DESI DR2 BAO:** files `desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_{mean,cov}.txt` from github.com/CobayaSampler/bao_data, commit `bb0c1c90`, SHA-256 prefixes `9ac154ab583ce759` (mean) and `252a143274c8a07c` (cov). There are 13 measurements: $D_V/r_d$, $D_M/r_d$ and $D_H/r_d$ for $0.295\le z\le2.33$.
- **Pantheon+:** `Pantheon+SH0ES.dat` and `Pantheon+SH0ES_STAT+SYS.cov` from github.com/PantheonPlusSH0ES/DataRelease (main). Use `m_b_corr` at `zHD`, with the redshift cut zHD > 0.01. The absolute magnitude is marginalised analytically (uncalibrated; no SH0ES).

## Models compared (the same number of free parameters)

| Model | Free parameters |
|---|---|
| $\Lambda$CDM (flat) | $\Omega_m$, $H_0r_d$ (BAO), SN offset (analytic) |
| UHL horizon-saturated dark energy ($c=1$) | $\Omega_{m0}$, $H_0r_d$, SN offset |

## Decision rule (primary: BAO + SNe)

$\Delta\chi^2=\chi^2_{\min}(c{=}1)-\chi^2_{\min}(\Lambda\text{CDM})$.

- **FAVOURED** if $\Delta\chi^2\le-4$.
- **DISFAVOURED** if $\Delta\chi^2\ge+4$.
- **NEUTRAL** otherwise: as good as $\Lambda$CDM, but not preferred.

BAO alone is reported as a secondary result, with the same thresholds.

## Exploratory (not decisive)

- the best fit $c$ when $c$ is free;
- the implied $w_0$ and $w_a$;
- how close $\Lambda$CDM's own vacuum energy sits to the event-horizon ceiling.

## Not in the decisive test

CMB is excluded, because it needs early-universe physics (radiation, the sound horizon) outside this derivation. The published result, that holographic dark energy is disfavoured once CMB is added (arXiv:2411.08639), is reported alongside and not hidden.

## Validation before the run

The pipeline is run on synthetic data, with the real covariances, generated from $\Lambda$CDM and from the $c=1$ model. It must recover which model generated each dataset. The code is frozen and hashed after validation, then run once on the real data.

## Freeze record (appended before the decisive run)

- Frozen code: `run_t20.py`, SHA-256 prefix `9af25be0c46bc792`.
- Validation on synthetic data (`t20_validation.txt`): with BAO + SNe, data generated from ΛCDM give Δχ² = +10.10 (DISFAVOURED), and data generated from the c=1 model give Δχ² = −7.13 (FAVOURED). So the combined test separates the two models. BAO alone separates them more weakly (+2.42 and −3.73), which is why it is secondary.

*Transparency note (added after the run):* the freeze record was appended at 17:30:29 by a shell command that expanded the `$...$` maths markers as shell variables, garbling this one paragraph. Its numbers and the hash were written correctly. The paragraph above restores the intended text, word for word, without the maths markers. Nothing else in this file was changed.
