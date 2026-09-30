# H1 pre-registration (written before any dial fit was run)

Date: 30 Sept 2026. Dataset: DECREASE validation set (Ianevski et al. 2019, Nat Mach Intell), 210 drug-combination blocks, 8x8 dose matrices, 36 unique drug pairs, 13 cell lines, from github.com/IanevskiAleksandr/DECREASE. Reason: NCI-ALMANAC and DrugComb are unreachable from this environment; this is the largest public set of full dose-response matrices reachable.

## Hypothesis H1 (capstone section 4.5)
The dial position alpha of Theorem 8 measures the mechanistic overlap of two agents: alpha near 0 for independent mechanisms (Bliss), alpha near 1 for a shared target (Loewe additivity at Hill slope 1). Prediction: median alpha increases with overlap level. Loss condition: Spearman correlation between overlap level and per-pair median alpha is <= 0, or its permutation p-value is >= 0.05 with all 36 pairs used.

## Effect definition
192-combination file: Response is % viability. e = clip(1 - Response/100, 0, 1).
18-combination file: Response is % inhibition (0 at zero dose). e = clip(Response/100, 0, 1).

## Single agents
Fit a Hill curve e(d) = Emax d^n / (EC50^n + d^n), Emax in [0,1], n in [0.1,10], to the 7 non-zero doses of each drug in each block. Use fitted e_A(d_i), e_B(d_j) in the dial. Sensitivity analysis: raw single-agent wells instead.

## Dial fit
For each block, minimise sum over the 49 interior wells of (e_obs - D_alpha(e_A,e_B))^2, where D_alpha(a,b) = (a + b - (1+alpha) a b) / (1 - alpha a b), alpha in [-5, 1]. Also record RMSE at fixed alpha=0 (Bliss) and alpha=1 (odds-additive Loewe) and the single-agent Hill slopes.

## Aggregation and test
Per drug pair: median alpha across its cell lines. Primary test: Spearman rho between overlap level (0/1/2) and per-pair median alpha across 36 pairs, permutation p (10,000 permutations). Secondary: per-block Spearman; medians per level with bootstrap CIs; sensitivity analysis restricted to blocks with both Hill slopes in [0.5, 2].

## Mechanistic overlap annotation (from published primary targets; fixed before fitting)
Rules. 2 = shared molecular target. 1 = same signalling axis, different node (RAF/MEK/ERK; PI3K/AKT/mTOR; a receptor or upstream kinase inhibitor whose primary targets feed the partner's pathway). 0 = distinct mechanisms, including parallel pathways (MEK vs PI3K/mTOR) and chaperone or DNA-damage agents.

| Pair | Targets | Level |
|---|---|---|
| ABT-199 / Trametinib | BCL-2 / MEK | 0 |
| AVN944 / Dactolisib | IMPDH / PI3K-mTOR | 0 |
| BGB324 / Everolimus | AXL RTK / mTORC1 | 1 |
| BIIB021 / Dactolisib | HSP90 / PI3K-mTOR | 0 (flag: HSP90 clients include AKT) |
| BMS-754807 / LY3009120 | IGF-1R / pan-RAF | 1 |
| BMS-754807 / Trametinib | IGF-1R / MEK | 1 |
| Cisplatin / Everolimus | DNA crosslink / mTORC1 | 0 |
| Cisplatin / Ipatasertib | DNA crosslink / AKT | 0 |
| Danusertib / Dactolisib | Aurora / PI3K-mTOR | 0 |
| Dasatinib / Dactolisib | SRC-ABL / PI3K-mTOR | 1 |
| Dinaciclib / Dactolisib | CDK / PI3K-mTOR | 0 |
| Entinostat / Trametinib | HDAC / MEK | 0 |
| Everolimus / Dactolisib | mTORC1 / PI3K-mTOR | 2 |
| Everolimus / Trametinib | mTORC1 / MEK | 0 |
| Floxuridine / Dactolisib | antimetabolite / PI3K-mTOR | 0 |
| GDC-0068 / Dactolisib | AKT / PI3K-mTOR | 1 |
| GDC-0068 / Trametinib | AKT / MEK | 0 |
| GSK269962 / Trametinib | ROCK / MEK | 0 |
| Indibulin / Dactolisib | tubulin / PI3K-mTOR | 0 |
| Iniparib / Trametinib | non-specific (not PARP) / MEK | 0 |
| KX2-391 / Trametinib | SRC (and tubulin) / MEK | 1 (flag: tubulin activity) |
| Linsitinib / Trametinib | IGF-1R / MEK | 1 |
| NVP-LCL161 / Trametinib | IAP / MEK | 0 |
| Navitoclax / Dactolisib | BCL-2 family / PI3K-mTOR | 0 |
| Navitoclax / Trametinib | BCL-2 family / MEK | 0 |
| Nintedanib / Trametinib | VEGFR-FGFR-PDGFR / MEK | 1 |
| Olaparib / Trametinib | PARP / MEK | 0 |
| Pictilisib / Trametinib | PI3K / MEK | 0 |
| Ponatinib / Trametinib | ABL-FGFR-VEGFR-SRC / MEK | 1 |
| Refametinib / Dactolisib | MEK / PI3K-mTOR | 0 |
| SCH772984 / Trametinib | ERK / MEK | 1 |
| SNS-032 / Dactolisib | CDK / PI3K-mTOR | 0 |
| TAK-901 / Dactolisib | Aurora B / PI3K-mTOR | 0 |
| Teniposide / Dactolisib | topoisomerase II / PI3K-mTOR | 0 |
| Tosedostat / Trametinib | aminopeptidase / MEK | 0 |
| Trametinib / Dactolisib | MEK / PI3K-mTOR | 0 |

Counts: level 2, 1 pair (10 blocks); level 1, 10 pairs; level 0, 25 pairs. Weakness acknowledged in advance: only one shared-target pair, so the primary test is mainly level 1 versus level 0, and the level-2 prediction (alpha near 1 for Everolimus/Dactolisib) is checked block by block.

## Known caveats stated in advance
1. This set was chosen by its authors as novel anticancer combinations, so it is enriched for synergy; absolute alpha will skew negative. H1 concerns ordering, not level.
2. Loewe additivity sits on the dial only at Hill slope 1 (capstone 4.3). Slopes are recorded and a restricted analysis is reported.
3. Single replicate per well; noise is substantial.
