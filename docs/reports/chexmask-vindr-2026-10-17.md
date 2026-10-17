# CheXmask validation — vindr (vindr-paper), 2026-10-17

Packages: 100; CheXmask rows found: 100; compared (all three masks present): 100; CSV `VinDr-CXR.csv` (CheXmask 1.0.0, HybridGNet, PhysioNet DOI 10.13026/3705-zg36). Definition on both sides: width = max horizontal extent of the mask, thorax = union of both lung masks, CTR = heart / thorax (the converter's Tier-1 definition; CheXmask provides no rib-cage width, so the thoracic-width *definition* is not tested here, only the segmentation). Bias = package − CheXmask; LoA = bias ± 1.96 SD; CCC = Lin's concordance. Scan 4 s.

Consistency check: the CTR recomputed from the package masks differs from `measurements.json` by > 0.005 on 0 of 100 packages.

## all compared images (n = 100)

| metric | n | mean package / CheXmask | bias (rel.) | limits of agreement | within 10 % | CCC | r |
|---|---|---|---|---|---|---|---|
| heart width (px) | 100 | 899 / 936 px | -37 px (-4.0 %) | -143 … +68 px | 86 % | 0.903 | 0.933 |
| thorax width (px) | 100 | 1884 / 1876 px | +9 px (+0.5 %) | -44 … +62 px | 100 % | 0.993 | 0.994 |
| CTR | 100 | 0.477 / 0.500 | -0.023 (-4.5 %) | -0.080 … +0.034 | 87 % | 0.760 | 0.838 |

Dice overlap package vs CheXmask: heart median 0.927 (min 0.647), lungs median 0.846 (min 0.746). CTR > 0.5: package 33, CheXmask 46 of 100.

## CheXmask Dice RCA (Mean) ≥ 0.7 (n = 100)

| metric | n | mean package / CheXmask | bias (rel.) | limits of agreement | within 10 % | CCC | r |
|---|---|---|---|---|---|---|---|
| heart width (px) | 100 | 899 / 936 px | -37 px (-4.0 %) | -143 … +68 px | 86 % | 0.903 | 0.933 |
| thorax width (px) | 100 | 1884 / 1876 px | +9 px (+0.5 %) | -44 … +62 px | 100 % | 0.993 | 0.994 |
| CTR | 100 | 0.477 / 0.500 | -0.023 (-4.5 %) | -0.080 … +0.034 | 87 % | 0.760 | 0.838 |

Dice overlap package vs CheXmask: heart median 0.927 (min 0.647), lungs median 0.846 (min 0.746). CTR > 0.5: package 33, CheXmask 46 of 100.

## Largest CTR disagreements

| image | CTR package | CTR CheXmask | heart px pkg / CheX | thorax px pkg / CheX | Dice heart | Dice lungs | RCA mean |
|---|---|---|---|---|---|---|---|
| ae93342f946e | 0.496 | 0.643 | 834 / 1096 | 1680 / 1705 | 0.71 | 0.82 | 0.76 |
| f4785c48c9a8 | 0.439 | 0.533 | 851 / 1032 | 1938 / 1935 | 0.84 | 0.85 | 0.87 |
| 3e8719d1ba69 | 0.479 | 0.567 | 806 / 947 | 1682 / 1669 | 0.91 | 0.85 | 0.84 |
| 0f81902a673f | 0.451 | 0.538 | 784 / 937 | 1737 / 1741 | 0.80 | 0.82 | 0.79 |
| fc47195078ba | 0.443 | 0.524 | 792 / 903 | 1786 / 1723 | 0.87 | 0.84 | 0.81 |
| 2cf24e4b4380 | 0.509 | 0.582 | 996 / 1135 | 1956 / 1951 | 0.81 | 0.82 | 0.79 |
| e9af0316eb1e | 0.401 | 0.467 | 668 / 745 | 1664 / 1595 | 0.94 | 0.86 | 0.84 |
| 43d6a61fac5f | 0.535 | 0.595 | 918 / 1027 | 1716 / 1726 | 0.80 | 0.82 | 0.84 |

## Readings (2026-10-17)

1. **Thoracic width: the two segmentations agree** (bias +0.5 %, limits ±3 %, CCC 0.993, every image within 10 %). Whatever is
   wrong with the Tier-1 CTR is not the lung segmentation.
2. **Cardiac width: the package's PSPNet heart is 4 % narrower than CheXmask's HybridGNet heart** (bias −37 px, limits −143 … +68 px,
   CCC 0.90, 86 % within 10 %; Dice 0.93 median). The disagreement sits at the lateral heart borders, with CheXmask wider on
   most images; which of the two is closer to a radiologist's border cannot be decided from two automatic sources.
3. **CTR: agreement is moderate** (CCC 0.76, r 0.84; package 0.477 vs CheXmask 0.500 on average, 87 % within 10 %), with the
   package systematically lower by 0.023. The sign reverses the September concern: against CheXmask the package CTR is biased
   low, not high. CTR > 0.5 on 33 % (package) and 46 % (CheXmask) of the 100 images, both far above the expected prevalence
   (~18 %), which confirms that the shared lung-union thoracic width under-estimates the internal thoracic width — a
   definition problem that this cross-check cannot resolve, because CheXmask has no rib-cage width either.
4. **Quality filter is moot here:** all 100 CheXmask rows have Dice RCA (Mean) ≥ 0.7, so the filtered table equals the full one.
5. **Consequence for the packages:** `validation_status` should move from `unvalidated` to a cross-check statement rather than
   `validated` — e.g. `cross_checked: {source: CheXmask 1.0.0, n: 100, ccc_heart_width: 0.90, ccc_thorax_width: 0.99, ccc_ctr: 0.76,
   bias_ctr: −0.023}` — and the paper's §5.8 sentence that the measurements are "the package's own segmentation-derived values"
   gains the numbers above. Tier-2 truth for CTR still needs a rib-cage (internal thoracic) width; the CheXmask lung masks give a
   second opinion on the segmentation, not a reference for the ratio. Next: the same on NIH-50 (ChestX-Ray8.csv downloading) and
   on the 1,000-package VinDr store when the external drive is attached.
