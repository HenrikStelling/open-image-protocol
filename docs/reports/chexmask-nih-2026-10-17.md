# CheXmask validation — nih (nih-paper), 2026-10-17

Packages: 50; CheXmask rows found: 50; compared (all three masks present): 50; CSV `ChestX-Ray8.csv` (CheXmask 1.0.0, HybridGNet, PhysioNet DOI 10.13026/3705-zg36). Definition on both sides: width = max horizontal extent of the mask, thorax = union of both lung masks, CTR = heart / thorax (the converter's Tier-1 definition; CheXmask provides no rib-cage width, so the thoracic-width *definition* is not tested here, only the segmentation). Bias = package − CheXmask; LoA = bias ± 1.96 SD; CCC = Lin's concordance. Scan 5 s.

Consistency check: the CTR recomputed from the package masks differs from `measurements.json` by > 0.005 on 0 of 50 packages.

## all compared images (n = 50)

| metric | n | mean package / CheXmask | bias (rel.) | limits of agreement | within 10 % | CCC | r |
|---|---|---|---|---|---|---|---|
| heart width (px) | 50 | 351 / 372 px | -21 px (-5.5 %) | -85 … +43 px | 72 % | 0.789 | 0.842 |
| thorax width (px) | 50 | 750 / 761 px | -11 px (-1.5 %) | -48 … +26 px | 100 % | 0.967 | 0.977 |
| CTR | 50 | 0.470 / 0.491 | -0.021 (-4.1 %) | -0.106 … +0.064 | 78 % | 0.800 | 0.832 |

Dice overlap package vs CheXmask: heart median 0.883 (min 0.620), lungs median 0.853 (min 0.693). CTR > 0.5: package 21, CheXmask 23 of 50.

## CheXmask Dice RCA (Mean) ≥ 0.7 (n = 49)

| metric | n | mean package / CheXmask | bias (rel.) | limits of agreement | within 10 % | CCC | r |
|---|---|---|---|---|---|---|---|
| heart width (px) | 49 | 350 / 370 px | -20 px (-5.4 %) | -85 … +44 px | 73 % | 0.790 | 0.840 |
| thorax width (px) | 49 | 752 / 763 px | -11 px (-1.6 %) | -48 … +25 px | 100 % | 0.967 | 0.978 |
| CTR | 49 | 0.468 / 0.487 | -0.020 (-3.9 %) | -0.103 … +0.064 | 80 % | 0.789 | 0.821 |

Dice overlap package vs CheXmask: heart median 0.886 (min 0.620), lungs median 0.853 (min 0.693). CTR > 0.5: package 20, CheXmask 22 of 49.

## Largest CTR disagreements

| image | CTR package | CTR CheXmask | heart px pkg / CheX | thorax px pkg / CheX | Dice heart | Dice lungs | RCA mean |
|---|---|---|---|---|---|---|---|
| 00011391_013 | 0.373 | 0.543 | 258 / 407 | 692 / 750 | 0.62 | 0.69 | 0.72 |
| 00016607_018 | 0.584 | 0.440 | 464 / 360 | 794 / 818 | 0.78 | 0.83 | 0.83 |
| 00008095_003 | 0.612 | 0.703 | 404 / 454 | 660 / 646 | 0.79 | 0.80 | 0.70 |
| 00020186_000 | 0.402 | 0.486 | 272 / 324 | 676 / 666 | 0.83 | 0.85 | 0.89 |
| 00017771_000 | 0.535 | 0.618 | 368 / 421 | 688 / 681 | 0.81 | 0.84 | 0.80 |
| 00017947_018 | 0.477 | 0.554 | 378 / 439 | 792 / 793 | 0.84 | 0.85 | 0.81 |
| 00029774_005 | 0.347 | 0.413 | 202 / 243 | 582 / 589 | 0.76 | 0.87 | 0.83 |
| 00003198_009 | 0.501 | 0.562 | 424 / 488 | 846 / 868 | 0.86 | 0.84 | 0.82 |

## Readings (2026-10-17)

Same picture as VinDr-100, with wider limits at the 1024-px resolution: thorax width agrees (bias −1.5 %, CCC 0.97, all within
10 %), the package heart is 5.5 % narrower than CheXmask's (CCC 0.79, 72 % within 10 %), CTR CCC 0.80 with the package lower by
0.021. The millimetre values in these packages (`heart_width`, `thorax_width`) are the pixel widths times the dataset-derived
spacing, so their agreement with CheXmask is the same as the pixel agreement above; the spacing itself is not tested by this
cross-check. Two images disagree strongly in opposite directions (00011391_013: package heart 258 px vs 407, Dice 0.62;
00016607_018: 464 vs 360) — both worth a look by eye before any package is rewritten. Consequence as for VinDr: a cross-check
statement with these numbers in `validation_status`, not `validated`; the lung-union thoracic width was cleared as a definition problem the same day on CXAS rib masks
(`docs/reports/itw-cxas-2026-10-17.md`).
