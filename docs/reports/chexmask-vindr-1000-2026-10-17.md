# CheXmask validation — vindr (vindr), 2026-10-17

Packages: 1000; CheXmask rows found: 1000; compared (all three masks present): 1000; CSV `VinDr-CXR.csv` (CheXmask 1.0.0, HybridGNet, PhysioNet DOI 10.13026/3705-zg36). Definition on both sides: width = max horizontal extent of the mask, thorax = union of both lung masks, CTR = heart / thorax (the converter's Tier-1 definition; CheXmask provides no rib-cage width, so the thoracic-width *definition* is not tested here, only the segmentation). Bias = package − CheXmask; LoA = bias ± 1.96 SD; CCC = Lin's concordance. Scan 21 s.

Consistency check: the CTR recomputed from the package masks differs from `measurements.json` by > 0.005 on 0 of 1000 packages.

## all compared images (n = 1000)

| metric | n | mean package / CheXmask | bias (rel.) | limits of agreement | within 10 % | CCC | r |
|---|---|---|---|---|---|---|---|
| heart width (px) | 1000 | 905 / 941 px | -36 px (-3.7 %) | -170 … +99 px | 90 % | 0.881 | 0.904 |
| thorax width (px) | 1000 | 1883 / 1877 px | +6 px (+0.3 %) | -66 … +78 px | 99 % | 0.990 | 0.990 |
| CTR | 1000 | 0.481 / 0.503 | -0.021 (-4.0 %) | -0.092 … +0.049 | 89 % | 0.745 | 0.802 |

Dice overlap package vs CheXmask: heart median 0.929 (min 0.369), lungs median 0.844 (min 0.493). CTR > 0.5: package 338, CheXmask 482 of 1000.

## CheXmask Dice RCA (Mean) ≥ 0.7 (n = 992)

| metric | n | mean package / CheXmask | bias (rel.) | limits of agreement | within 10 % | CCC | r |
|---|---|---|---|---|---|---|---|
| heart width (px) | 992 | 906 / 939 px | -33 px (-3.5 %) | -153 … +87 px | 90 % | 0.902 | 0.923 |
| thorax width (px) | 992 | 1885 / 1878 px | +6 px (+0.3 %) | -65 … +78 px | 99 % | 0.990 | 0.991 |
| CTR | 992 | 0.481 / 0.501 | -0.020 (-3.8 %) | -0.081 … +0.041 | 89 % | 0.786 | 0.839 |

Dice overlap package vs CheXmask: heart median 0.929 (min 0.369), lungs median 0.845 (min 0.493). CTR > 0.5: package 334, CheXmask 474 of 992.

## Largest CTR disagreements

| image | CTR package | CTR CheXmask | heart px pkg / CheX | thorax px pkg / CheX | Dice heart | Dice lungs | RCA mean |
|---|---|---|---|---|---|---|---|
| 277b457e1e34 | 0.468 | 0.754 | 792 / 1258 | 1692 / 1669 | 0.46 | 0.70 | 0.66 |
| 0a0ac65c40a9 | 0.377 | 0.661 | 576 / 1069 | 1529 / 1618 | 0.49 | 0.66 | 0.68 |
| 97bd85612088 | 0.554 | 0.807 | 972 / 1420 | 1756 / 1759 | 0.60 | 0.58 | 0.58 |
| 24e9b243d734 | 0.473 | 0.723 | 734 / 1255 | 1553 / 1736 | 0.62 | 0.58 | 0.68 |
| f4962890f0c6 | 0.469 | 0.701 | 730 / 1078 | 1558 / 1537 | 0.55 | 0.77 | 0.70 |
| 7d0e636b3ef2 | 0.445 | 0.662 | 639 / 910 | 1435 / 1374 | 0.63 | 0.75 | 0.70 |
| ed6f20cff422 | 0.602 | 0.802 | 913 / 1239 | 1517 / 1545 | 0.69 | 0.65 | 0.75 |
| 98ec15bd4fec | 0.506 | 0.699 | 686 / 936 | 1356 / 1339 | 0.66 | 0.77 | 0.71 |

## Readings (2026-10-17)

The 100-image paper subset was representative: on all 1,000 VinDr packages the thorax width agrees (bias +0.3 %, CCC 0.99, 99 %
within 10 %), the package heart is 3.7 % narrower than CheXmask's (CCC 0.88, 90 % within 10 %; 0.90 after the RCA ≥ 0.7 filter,
which removes 8 images), and the CTR is 0.021 lower (CCC 0.75 / 0.79 filtered, 89 % within 10 %). CTR > 0.5 on 34 % (package) and
48 % (CheXmask) of images, both far above the ~18 % population prevalence: the shared lung-union thoracic width is the open
definition problem, unchanged. Mask overlap: heart Dice median 0.93 (min 0.37), lungs 0.84 (min 0.49) — the worst cases are
single images where one of the two segmentations failed, visible in the disagreement table. Applied: `validation_status:
cross_checked` with the `cross_check` record on `ctr` in all 1,000 packages (backups in `~/oip-bench/_backup/vindr/`). The
300-package NIH store on the external drive has no anatomy masks (never segmented) and was not compared; the 50 NIH paper packages
were.
