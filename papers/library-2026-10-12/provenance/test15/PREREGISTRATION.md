# T15 pre-registration: logit curvature equals hidden fitness variance

Written before any curvature was computed: 12 Oct 2026. *Timestamp correction, added after the run: the file-system time of this file is 13:20:42 AEDT, and the first results file is 13:21:51. The "13:30" originally typed here was a typing error. No other content was changed.*

**Data.** Schlecht et al. 2017, *Nature Communications* 8:15586 (PPiSeq). The file is `ncomms15586-s2.csv` from github.com/sashaflevy/Fit-Seq.

- 2,500 barcoded yeast lineages: 100 genotypes (protein-pair strains), 25 independent barcodes each.
- Raw read counts at generations 0, 3, 6, 9 and 12.
- 5 conditions, each with and without methotrexate (MTX), giving 10 environments, each in 3 replicate cultures. The t = 0 sample is shared.

**Law under test (Doc 11, Thm 11.6).** For a group A of lineages and the rest of the pool R, let $L(t)=\log(\text{reads}_A/\text{reads}_R)$. If types have constant fitness, then
$$\frac{d^2L}{dt^2}=\mathrm{Var}_{A,t}(s)-\mathrm{Var}_{R,t}(s).$$
For a group made of one genotype only, its internal variance is zero. For two single genotypes compared with each other, the logit is exactly a straight line (the two-type, UHL closure).

**Procedure (out of sample).**

1. Estimate genotype fitness $\hat s_g$ from replicates $j,k$ only. Fit $\log(\text{reads}_{g,t}+0.5)=a_g+s_gt+c_t$ by count-weighted least squares, pooling each genotype's 25 barcodes.
2. In the held-out replicate $i$, use only **aggregate group reads** to compute the observed second differences $D_{\rm obs}(t)=L(t+3)-2L(t)+L(t-3)$ at $t=3,6,9$.
3. Predict $D_{\rm pred}(t)$ from $L_{\rm pred}(t)=\log\sum_{g\in A}N_g(0)e^{\hat s_gt}-\log\sum_{g\notin A}N_g(0)e^{\hat s_gt}$.
4. Rotate $i$ over all 3 replicates.
5. Groups are the 10 bait groups and 10 prey groups (each 10 genotypes and 250 lineages) in each of the 10 environments.

**Predictions.**

- **P-a (heterogeneity).** Across all group × environment × time points, the regression of $D_{\rm obs}$ on $D_{\rm pred}$ has slope within $[0.7,1.3]$ and Pearson $r\ge0.7$. The prediction beats the two-type baseline $D=0$ in RMSE.
- **P-b (two-type closure).** For single-genotype pairs (genotype $g$ against a fixed well-measured reference genotype), the curvature of the observed logit is consistent with zero: its root-mean-square is no larger than the replicate-to-replicate noise in the same quantity, and much smaller than for mixed groups in MTX.
- **P-c (environment).** Curvature is large under MTX selection, where fitness differences are large, and near zero without MTX.

**Loss conditions.**

- Slope outside $[0.7,1.3]$, or $r<0.7$, or no RMSE gain over $D=0$: the law fails as a predictive tool on this data.
- Systematic curvature in single-genotype pairs well above replicate noise: the two-type closure fails (non-constant fitness, frequency dependence or lag), and the law's premise is violated in these populations.

**Caveat declared in advance.** Given constant-fitness types, the law is mathematically Fisher's fundamental theorem. A pass therefore tests (i) that real lineages behave as fixed types over 12 generations, and (ii) the practical claim that **aggregate share data alone reveals hidden variety**. It is not an independent test of hyperbolic geometry.
