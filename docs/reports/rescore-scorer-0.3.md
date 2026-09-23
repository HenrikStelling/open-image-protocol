# Rescore with scorer 0.3 (2026-09-23 19:18; applied)

Rows rescored: 67976; rows whose score dict changed: 385 (any key, including value/abs_error; correctness changes and abstention-flag changes are listed below). Previous scores are kept per row as `score_prev`.

## Correctness changes per dataset, model, condition, task type

| dataset | model | condition | task | direction | rows |
|---|---|---|---|---|---|
| bonescan-40 | glm-5.3-flash:cloud | ctx | counts_semantics | wrong→correct | 1 |
| bonescan-40 | glm-5.3-flash:cloud | ctx | flip_check_nm | correct→wrong | 10 |
| bonescan-40 | glm-5.3-flash:cloud | ctx | flip_check_nm | wrong→correct | 7 |
| bonescan-40 | glm-5.3-flash:cloud | ctx | left_edge_nm | wrong→correct | 2 |
| bonescan-40 | glm-5.3-flash:cloud | ctx_l1 | counts_semantics | wrong→correct | 1 |
| bonescan-40 | glm-5.3-flash:cloud | ctx_l1 | flip_check_nm | correct→wrong | 8 |
| bonescan-40 | glm-5.3-flash:cloud | ctx_l1 | flip_check_nm | wrong→correct | 10 |
| bonescan-40 | glm-5.3-flash:cloud | ctx_l1 | hot_side | wrong→correct | 1 |
| bonescan-40 | glm-5.3-flash:cloud | raw | counts_semantics | wrong→correct | 1 |
| bonescan-40 | glm-5.3-flash:cloud | raw | left_edge_nm | wrong→correct | 3 |
| bonescan-40 | glm-5.3-flash:cloud | raw | scale_available_nm | wrong→correct | 4 |
| bonescan-40 | medgemma1.5:4b | ctx | counts_semantics | wrong→correct | 1 |
| bonescan-40 | medgemma1.5:4b | ctx | scale_available_nm | wrong→correct | 1 |
| bonescan-40 | medgemma1.5:4b | ctx_l1 | counts_semantics | wrong→correct | 1 |
| bonescan-40 | minimax-m3:cloud | ctx | flip_check_nm | correct→wrong | 2 |
| bonescan-40 | minimax-m3:cloud | ctx | flip_check_nm | wrong→correct | 3 |
| bonescan-40 | minimax-m3:cloud | ctx_l1 | flip_check_nm | correct→wrong | 4 |
| bonescan-40 | minimax-m3:cloud | ctx_l1 | flip_check_nm | wrong→correct | 3 |
| paper-nih-50 | glm-5.3-flash:cloud | annot | left_edge | wrong→correct | 2 |
| paper-nih-50 | glm-5.3-flash:cloud | annot | mark_heart | wrong→correct | 1 |
| paper-nih-50 | glm-5.3-flash:cloud | annot | mark_side | wrong→correct | 4 |
| paper-nih-50 | glm-5.3-flash:cloud | annot | view | wrong→correct | 9 |
| paper-nih-50 | glm-5.3-flash:cloud | ctx | flip_check | correct→wrong | 4 |
| paper-nih-50 | glm-5.3-flash:cloud | ctx | flip_check | wrong→correct | 8 |
| paper-nih-50 | glm-5.3-flash:cloud | ctx | left_edge | wrong→correct | 8 |
| paper-nih-50 | glm-5.3-flash:cloud | ctx | view | wrong→correct | 1 |
| paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | flip_check | correct→wrong | 2 |
| paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | flip_check | wrong→correct | 8 |
| paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | heart_mm | wrong→correct | 1 |
| paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | left_edge | wrong→correct | 9 |
| paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | view | wrong→correct | 4 |
| paper-nih-50 | glm-5.3-flash:cloud | raw | left_edge | wrong→correct | 6 |
| paper-nih-50 | glm-5.3-flash:cloud | raw | view | wrong→correct | 1 |
| paper-nih-50 | kimi-k3:cloud | ctx | flip_check | correct→wrong | 1 |
| paper-nih-50 | medgemma1.5:4b | raw | heart_mm | wrong→correct | 1 |
| paper-nih-50 | minimax-m3:cloud | ctx | flip_check | correct→wrong | 1 |
| paper-nih-50 | minimax-m3:cloud | ctx_l1 | flip_check | correct→wrong | 2 |
| paper-vindr-100 | glm-5.3-flash:cloud | annot | mark_side | wrong→correct | 21 |
| paper-vindr-100 | glm-5.3-flash:cloud | annot | view | wrong→correct | 17 |
| paper-vindr-100 | glm-5.3-flash:cloud | ctx | flip_check | correct→wrong | 5 |
| paper-vindr-100 | glm-5.3-flash:cloud | ctx | flip_check | wrong→correct | 16 |
| paper-vindr-100 | glm-5.3-flash:cloud | ctx | left_edge | wrong→correct | 5 |
| paper-vindr-100 | glm-5.3-flash:cloud | ctx | view | wrong→correct | 8 |
| paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | flip_check | correct→wrong | 6 |
| paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | flip_check | wrong→correct | 8 |
| paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | heart_mm | wrong→correct | 6 |
| paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | left_edge | wrong→correct | 3 |
| paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | view | wrong→correct | 2 |
| paper-vindr-100 | glm-5.3-flash:cloud | raw | left_edge | wrong→correct | 6 |
| paper-vindr-100 | glm-5.3-flash:cloud | raw | scale_available | correct→wrong | 3 |
| paper-vindr-100 | minimax-m3:cloud | ctx | flip_check | correct→wrong | 2 |
| paper-vindr-100 | minimax-m3:cloud | ctx | flip_check | wrong→correct | 1 |
| pilot-vindr-20 | glm-5.3-flash:cloud | annot | view | wrong→correct | 1 |
| pilot-vindr-20 | glm-5.3-flash:cloud | ctx | left_edge | wrong→correct | 2 |
| pilot-vindr-20 | glm-5.3-flash:cloud | ctx | view | wrong→correct | 2 |
| pilot-vindr-20 | glm-5.3-flash:cloud | raw | left_edge | wrong→correct | 2 |

## Abstention-flag changes

| dataset | model | condition | task | change | rows |
|---|---|---|---|---|---|
| paper-vindr-100 | glm-5.3-flash:cloud | raw | scale_available | flag removed | 63 |
| paper-vindr-100 | kimi-k3:cloud | raw | scale_available | flag removed | 8 |

## Examples of changed replies (first 140 characters)

- bonescan-40 | glm-5.3-flash:cloud | ctx | counts_semantics: `The question: Can brightness of a region in this image be compared directly with brightness of same region in a scan of another patient to s`
- bonescan-40 | glm-5.3-flash:cloud | ctx | flip_check_nm: `The question asks: compare the image with the stated orientation (patient's right at LEFT edge for anterior view). Does the image agree or i`
- bonescan-40 | glm-5.3-flash:cloud | ctx | flip_check_nm: `The question asks whether the image agrees with the stated orientation (patient's right at image LEFT edge) or is mirrored.  The image is a `
- bonescan-40 | glm-5.3-flash:cloud | ctx | left_edge_nm: `The reference file says: Orientation [inferred]: image LEFT edge = L, and "assumed conventional posterior display (mirrored: patient's left `
- bonescan-40 | glm-5.3-flash:cloud | ctx | left_edge_nm: `The reference says: posterior view, mirrored: patient's left on image left. So image LEFT edge = L = patient left. Wait, posterior view mean`
- bonescan-40 | glm-5.3-flash:cloud | ctx_l1 | counts_semantics: `The question: Can brightness of a region in this image be compared directly with brightness of the same region in a scan of another patient `
- bonescan-40 | glm-5.3-flash:cloud | ctx_l1 | flip_check_nm: `The question asks: compare the image with the stated orientation (patient's R on image left). Does the image agree or is it mirrored?  I nee`
- bonescan-40 | glm-5.3-flash:cloud | ctx_l1 | flip_check_nm: `The question asks whether the image agrees with the stated orientation (patient's right at image left edge) or is mirrored.  I need to look `
- bonescan-40 | glm-5.3-flash:cloud | ctx_l1 | hot_side: `The image is a whole-body bone scintigraphy, anterior view. Image left edge = patient's right, image right edge = patient's left.  Looking a`
- bonescan-40 | glm-5.3-flash:cloud | raw | counts_semantics: `The question is about nuclear medicine imaging (looks like a bone scan or PET whole-body scan). The question: Can brightness of a region in `
- bonescan-40 | glm-5.3-flash:cloud | raw | left_edge_nm: `The image is a posterior whole-body view (bone scan). In posterior views, the patient's right side appears on the left edge of the image... `
- bonescan-40 | glm-5.3-flash:cloud | raw | left_edge_nm: `The question is about a posterior whole-body view (like a bone scan). In posterior views, the image is viewed from behind the patient, so th`
- bonescan-40 | glm-5.3-flash:cloud | raw | scale_available_nm: `The user is asking whether distances in this image can be stated in millimeters with known calibration. This is a whole-body nuclear medicin`
- bonescan-40 | glm-5.3-flash:cloud | raw | scale_available_nm: `The question asks whether distances in this image can be stated in millimeters with a known calibration. This appears to be a nuclear medici`
- bonescan-40 | medgemma1.5:4b | ctx | counts_semantics: `The brightness of a region in this image cannot be directly compared with the brightness of the same region in a scan of another patient to `
- bonescan-40 | medgemma1.5:4b | ctx | scale_available_nm: `The image is a bone scintigraphy, not a standard medical image like an X-ray or MRI. It displays counts of gamma photons, not anatomical str`
- bonescan-40 | medgemma1.5:4b | ctx_l1 | counts_semantics: `The brightness of a region in this image cannot be directly compared with the brightness of the same region in a scan of another patient to `
- bonescan-40 | minimax-m3:cloud | ctx | flip_check_nm: `Looking at the image, I need to determine if the patient's left side is on the image's left edge (as stated) or if it's mirrored.  In a post`
- bonescan-40 | minimax-m3:cloud | ctx | flip_check_nm: `Looking at this posterior view scintigraphy image, I need to identify the patient's left vs right side.  In a posterior view (looking at the`
- bonescan-40 | minimax-m3:cloud | ctx_l1 | flip_check_nm: `Looking at the image, I need to identify anatomical landmarks to determine orientation.  In this posterior whole-body bone scintigraphy: - T`
- bonescan-40 | minimax-m3:cloud | ctx_l1 | flip_check_nm: `Looking at the image to verify orientation: - The stated orientation is posterior view with image LEFT = patient's Left (L), image RIGHT = p`
- paper-nih-50 | glm-5.3-flash:cloud | annot | left_edge: `The reference says image LEFT edge = R, and there's also an "L" marker visible on the image right side (in the image itself, "L DG" marker a`
- paper-nih-50 | glm-5.3-flash:cloud | annot | left_edge: `The reference says image LEFT edge = R, which is patient right. The question asks: "Which side of the patient is at the LEFT edge of the ima`
- paper-nih-50 | glm-5.3-flash:cloud | annot | mark_heart: `The reference file lists marks: mark 1 = clavicle, mark 2 = clavicle, mark 3 = left lung, mark 4 = right lung, mark 5 = heart, mark 6 = aort`
- paper-nih-50 | glm-5.3-flash:cloud | annot | mark_side: `The reference says: mark 1 = clavicle, labeled clavicle_left region... wait, region clavicle_left = clavicle (mark 1). In conventional displ`
- paper-nih-50 | glm-5.3-flash:cloud | annot | mark_side: `Mark 1 is clavicle_left, which appears on the right side of the image (the arrow/checkmark near top right). Image left edge = R (patient rig`
- paper-nih-50 | glm-5.3-flash:cloud | annot | view: `The question asks frontal or lateral. The metadata says PA view, frontal. Answer: frontal.</think>Frontal`
- paper-nih-50 | glm-5.3-flash:cloud | annot | view: `The question asks whether this is a frontal or lateral projection. The metadata says AP (anteroposterior), which is frontal. Both lungs seen`
- paper-nih-50 | glm-5.3-flash:cloud | ctx | flip_check: `The question asks whether the image agrees with the stated orientation (patient's right on image left, per PA convention) or is mirrored.  K`
- paper-nih-50 | glm-5.3-flash:cloud | ctx | flip_check: `The image shows a chest X-ray with an "L" marker in the upper left corner of the image. The L marker indicates the patient's left side is on`
- paper-nih-50 | glm-5.3-flash:cloud | ctx | left_edge: `The image shows an "L" marker on the right side of the image, which typically indicates patient's left is on the image right. Wait, the L ma`
- paper-nih-50 | glm-5.3-flash:cloud | ctx | left_edge: `The reference says image LEFT edge = R, i.e., patient right. The image also shows an "L" marker on the right side of the image, confirming p`
- paper-nih-50 | glm-5.3-flash:cloud | ctx | view: `The question asks whether this is a frontal or lateral projection. The reference says view is frontal, PA. The image shows symmetric chest w`
- paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | flip_check: `The image shows a chest PA radiograph. There's an "L" marker in the upper left corner of the image. The stated orientation says image LEFT e`
- paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | flip_check: `The question asks whether the image agrees with the stated orientation (patient's right at image left) or is mirrored.  Looking at the image`
- paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | heart_mm: `The question asks for the transverse cardiac diameter in millimeters.  From the image, I need to estimate the width of the heart (widest hor`
- paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | heart_mm: `I need to estimate the transverse cardiac diameter (the widest horizontal extent of the heart silhouette) in millimetres from this chest X-r`
- paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | left_edge: `The question asks which side of the patient is at the left edge of the image. The reference says image LEFT edge = R (patient's right), conv`
- paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | left_edge: `The image shows a chest PA radiograph. There's an "L" marker visible in the upper right of the image (which is the patient's left side in co`
- paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | view: `The question asks frontal or lateral. The metadata says AP (anteroposterior), which is frontal. The image also shows "AP" label. Answer: fro`
- paper-nih-50 | glm-5.3-flash:cloud | ctx_l1 | view: `The question is simple: frontal or lateral. The image shows a PA chest X-ray, frontal view. Answer 'frontal'.</think>frontal`
- paper-nih-50 | glm-5.3-flash:cloud | raw | heart_mm: `The user wants an estimate of the transverse cardiac diameter (the widest horizontal diameter of the cardiac silhouette) in millimeters on t`
- paper-nih-50 | glm-5.3-flash:cloud | raw | left_edge: `The image shows a chest X-ray. There's an "L" marker visible in the upper right corner of the image (image right side). The L marker indicat`
- paper-nih-50 | glm-5.3-flash:cloud | raw | left_edge: `This is a chest X-ray marked "AP" (anteroposterior) with an "L" marker on the right side of the image (from viewer's perspective). In AP vie`
- paper-nih-50 | glm-5.3-flash:cloud | raw | view: `The image shows a chest X-ray labeled "AP" which is an anteroposterior projection - this is a frontal projection (as opposed to lateral).</t`
- paper-nih-50 | kimi-k3:cloud | ctx | flip_check: `The stated orientation says the patient's right side is on the image's left edge (L=R). This is confirmed by the visible "R" marker (which a`
- paper-nih-50 | medgemma1.5:4b | ctx_l1 | heart_mm: `<unused94>thought The user wants me to estimate the transverse cardiac diameter in millimeters based on the provided chest X-ray image.  1. `
- paper-nih-50 | medgemma1.5:4b | ctx_l1 | heart_mm: `<unused94>thought The user wants me to estimate the transverse cardiac diameter from the provided chest X-ray image. 1.  **Identify the rele`
- paper-nih-50 | medgemma1.5:4b | raw | heart_mm: `9.5 cm `
- paper-nih-50 | medgemma1.5:4b | raw | heart_mm: `11.5 cm`
- paper-nih-50 | minimax-m3:cloud | ctx | flip_check: `Looking at the chest radiograph, I need to verify the stated orientation: image LEFT edge = patient's RIGHT side.  Key observations: - The c`
- paper-nih-50 | minimax-m3:cloud | ctx_l1 | flip_check: `Looking at the image, I need to identify which side shows the cardiac silhouette (heart) and the gastric bubble.  Key observations: - The **`
- paper-nih-50 | minimax-m3:cloud | ctx_l1 | flip_check: `Looking at this radiograph, I need to determine if the cardiac silhouette and gastric bubble are on the correct sides for an AP chest X-ray.`
- paper-vindr-100 | glm-5.3-flash:cloud | annot | mark_side: `Mark 1 is clavicle. Looking at the annotated image, mark 1 is labeled near the top, at around x=750, y=330. The image left edge is R (patien`
- paper-vindr-100 | glm-5.3-flash:cloud | annot | mark_side: `Mark 1 is clavicle, located on the image's right side of the chest... wait, in the annotated image, mark 1 box is at upper area spanning... `
- paper-vindr-100 | glm-5.3-flash:cloud | annot | view: `The question asks whether this is a frontal or lateral projection. The reference file states view: frontal, PA. The image shows symmetric ri`
- paper-vindr-100 | glm-5.3-flash:cloud | annot | view: `The question asks whether this is a frontal or lateral projection. The metadata says view: frontal, posteroanterior (PA). The image shows a `
- paper-vindr-100 | glm-5.3-flash:cloud | ctx | flip_check: `The image is a chest PA radiograph. The stated orientation: image LEFT edge = R (patient's right side).  Looking at the image: there's an "R`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx | flip_check: `The question asks whether the image agrees with the stated orientation (patient's right side at LEFT edge) or is mirrored.  In a PA chest ra`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx | left_edge: `The image shows an "L" marker on the right side of the image, which conventionally indicates patient left. The reference file says image LEF`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx | left_edge: `The image shows an "L" marker on the right side of the image, indicating patient left is on the image right. Standard PA chest X-ray convent`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx | view: `The question asks whether this is a frontal or lateral projection. The metadata says PA (posteroanterior), which is frontal. The image shows`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx | view: `The question asks whether this is a frontal or lateral projection. The metadata says view: frontal, posteroanterior (PA). The image shows a `
- paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | flip_check: `The question asks whether the image agrees with the stated orientation: image LEFT edge = R (patient's right side).  Looking at the image: T`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | flip_check: `The image shows a chest X-ray with an "L" marker on the right side of the image (viewer's right), which is the patient's left side. The stat`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | heart_mm: `The user wants an estimate of the transverse cardiac diameter in mm from the chest PA radiograph.  Image is 3072 × 2540 px, pixel spacing 0.`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | heart_mm: `The user wants an estimate of the transverse cardiac diameter in millimeters from a chest PA radiograph.  The image is 2836 rows × 2336 colu`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | left_edge: `The reference says image LEFT edge = R (patient right) for PA view. The image shows an "L" marker on the right side of the image, confirming`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | left_edge: `The image shows an "L" marker on the right side of the image, which means patient left is on the image's right edge. Therefore the left edge`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | view: `The question is simple: frontal or lateral? The reference says PA frontal. The image shows a PA chest X-ray with symmetric lungs, spine, L m`
- paper-vindr-100 | glm-5.3-flash:cloud | ctx_l1 | view: `The question asks whether this is frontal or lateral. The metadata says PA (frontal). The image shows symmetric chest with both lungs, spine`
- paper-vindr-100 | glm-5.3-flash:cloud | raw | heart_mm: `The user wants an estimate of the transverse cardiac diameter on this chest X-ray in millimetres.  Looking at the chest X-ray, the heart app`
- paper-vindr-100 | glm-5.3-flash:cloud | raw | heart_mm: `The user wants an estimate of the transverse cardiac diameter (cardiac width) on a frontal chest X-ray in millimeters.  Looking at the chest`
- paper-vindr-100 | glm-5.3-flash:cloud | raw | left_edge: `The image shows a chest X-ray with an "L" marker on the left side of the image (viewer's right side... wait, let me look). The "L" marker ap`
- paper-vindr-100 | glm-5.3-flash:cloud | raw | left_edge: `This is a chest X-ray. Standard convention for frontal chest radiographs (PA or AP) is that the patient's right side is on the left edge of `
- paper-vindr-100 | glm-5.3-flash:cloud | raw | scale_available: `The question asks whether distances in this image can be stated in millimetres with a known calibration. This is a chest X-ray. X-rays are p`
- paper-vindr-100 | glm-5.3-flash:cloud | raw | scale_available: `The question asks whether distances in this image can be stated in millimetres with a known calibration. This is a chest X-ray (plain radiog`
- paper-vindr-100 | kimi-k3:cloud | ctx_l1 | heart_mm: `The user is asking to estimate the transverse cardiac diameter in millimetres from the chest X-ray.  The image is 2952 rows × 2620 columns, `
- paper-vindr-100 | kimi-k3:cloud | ctx_l1 | heart_mm: `The user is asking me to estimate the transverse cardiac diameter in millimetres from a PA chest radiograph. I need to use the scale informa`
- paper-vindr-100 | kimi-k3:cloud | raw | scale_available: `No. Distances in this chest X-ray image cannot be accurately stated in millimetres with the provided information alone. While the image incl`
- paper-vindr-100 | kimi-k3:cloud | raw | scale_available: `No. No calibration marker is visible, so distances in millimetres cannot be stated accurately.`
- paper-vindr-100 | medgemma1.5:4b | ctx_l1 | heart_mm: `<unused94>thought The user wants me to estimate the transverse cardiac diameter from the provided chest X-ray image.  1.  **Identify the rel`
- paper-vindr-100 | medgemma1.5:4b | ctx_l1 | heart_mm: `**1.6 cm**`
- paper-vindr-100 | medgemma1.5:4b | raw | heart_mm: `7.3 cm `
- paper-vindr-100 | medgemma1.5:4b | raw | heart_mm: `7.5 cm `
- paper-vindr-100 | minimax-m3:cloud | ctx | flip_check: `Looking at this chest X-ray, I need to determine if the patient's left side is on the image's right (standard PA orientation) or if it's fli`
- paper-vindr-100 | minimax-m3:cloud | ctx | flip_check: `Looking at the image, the cardiac silhouette (heart) appears on the image's LEFT side. In a normal PA chest radiograph, the heart shadow is `
- pilot-vindr-20 | glm-5.3-flash:cloud | annot | view: `The question asks whether this is a frontal or lateral projection. The metadata says PA view, which is frontal. The image shows both lungs s`
- pilot-vindr-20 | glm-5.3-flash:cloud | ctx | left_edge: `The image shows a chest X-ray with a "P" marker on the left side of the image. The reference file says image LEFT edge = R (patient right). `
- pilot-vindr-20 | glm-5.3-flash:cloud | ctx | left_edge: `The question asks which side of the patient is at the left edge of the image. According to the reference, image LEFT edge = R (patient right`
- pilot-vindr-20 | glm-5.3-flash:cloud | ctx | view: `The question asks whether this is a frontal or lateral projection. The metadata says PA view, and the image shows both lungs symmetrically, `
- pilot-vindr-20 | glm-5.3-flash:cloud | ctx | view: `The question asks whether this is a frontal or lateral projection. The metadata says PA view, and the image shows both lungs, symmetric ribc`
- pilot-vindr-20 | glm-5.3-flash:cloud | raw | heart_mm: `The user wants an estimate of the transverse cardiac diameter on this chest X-ray in millimetres.  Looking at the image, the heart appears n`
- pilot-vindr-20 | glm-5.3-flash:cloud | raw | heart_mm: `The user wants an estimate of the transverse cardiac diameter in mm from this chest X-ray.  Let me estimate. The image appears to be about 1`
- pilot-vindr-20 | glm-5.3-flash:cloud | raw | left_edge: `Chest X-ray, PA view. Convention: patient's right side is on the left edge of the image. The image shows the heart apex toward the right sid`
- pilot-vindr-20 | glm-5.3-flash:cloud | raw | left_edge: `The image is a PA chest X-ray with an "R" marker... wait, the marker says "P" on the left side of the image. Let me look. There's a "P" mark`
- pilot-vindr-20 | medgemma1.5:4b | ctx_l1 | heart_mm: `<unused94>thought The user wants me to estimate the transverse cardiac diameter in millimeters based on the provided chest X-ray image.  1. `
- pilot-vindr-20 | medgemma1.5:4b | ctx_l1 | heart_mm: `The image shows a transverse view of the heart. Based on the provided image and typical chest X-ray measurements, the transverse cardiac dia`
- pilot-vindr-20 | medgemma1.5:4b | raw | heart_mm: `4.1 cm `
- pilot-vindr-20 | medgemma1.5:4b | raw | heart_mm: `6.5 cm `

## Per run

| run | dataset | rows | changed |
|---|---|---|---|
| 20260908-161636-ollama_gemma4_e4b-it-qat+ollama_medgemma1.5_4b-11473 | pilot-vindr-20 | 908 | 1 |
| 20260908-163422-ollama_minimax-m3_cloud-18589 | pilot-vindr-20 | 454 | 0 |
| 20260908-163425-ollama_glm-5.3-flash_cloud-18619 | pilot-vindr-20 | 454 | 9 |
| 20260908-163428-ollama_gemma4_31b-cloud-18635 | pilot-vindr-20 | 454 | 0 |
| 20260908-165355-ollama_gemma4_e4b-it-qat+ollama_medgemma1.5_4b-24903 | pilot-vindr-20 | 40 | 0 |
| 20260908-170629-ollama_kimi-k3_cloud-28106 | pilot-vindr-20 | 454 | 0 |
| 20260908-170632-ollama_mistral-large-3_675b-cloud-28118 | pilot-vindr-20 | 699 | 0 |
| 20260908-170635-ollama_qwen3.5_cloud-28137 | pilot-vindr-20 | 454 | 0 |
| 20260909-080920-ollama_gemma4_31b-cloud+ollama_minimax-m3_cloud+ollama_glm-5-25105 | pilot-vindr-20 | 120 | 0 |
| 20260909-100702-ollama_gemma4_e4b-it-qat+ollama_medgemma1.5_4b-53789 | pilot-vindr-20 | 1184 | 3 |
| 20260909-104234-ollama_gemma4_e4b-it-qat+ollama_medgemma1.5_4b-64771 | pilot-vindr-20 | 1424 | 7 |
| 20260910-061756-ollama_gemma4_e4b-it-qat+ollama_medgemma1.5_4b-73188 | bonescan-40 | 1412 | 3 |
| 20260910-071431-ollama_gemma4_e4b-it-qat+ollama_medgemma1.5_4b-80442 | paper-vindr-100 | 7056 | 13 |
| 20260910-111549-ollama_gemma4_e4b-it-qat+ollama_medgemma1.5_4b-35490 | paper-nih-50 | 3000 | 12 |
| 20260910-145029-ollama_gemma4_31b-cloud-56234 | paper-vindr-100 | 3528 | 0 |
| 20260910-145033-ollama_minimax-m3_cloud-56242 | paper-vindr-100 | 3528 | 3 |
| 20260910-201011-ollama_gemma4_31b-cloud-18115 | paper-nih-50 | 1300 | 0 |
| 20260910-204720-ollama_gemma4_31b-cloud-25857 | bonescan-40 | 664 | 0 |
| 20260911-023758-ollama_minimax-m3_cloud-73979 | paper-nih-50 | 1300 | 3 |
| 20260911-070805-ollama_minimax-m3_cloud-37304 | bonescan-40 | 664 | 12 |
| 20260911-080632-ollama_qwen3.5_cloud-44192 | paper-vindr-100 | 3528 | 0 |
| 20260911-202044-ollama_qwen3.5_cloud-98700 | paper-nih-50 | 1300 | 0 |
| 20260912-092608-ollama_qwen3.5_cloud-87460 | bonescan-40 | 664 | 0 |
| 20260912-100228-ollama_kimi-k3_cloud-94809 | paper-vindr-100 | 3528 | 10 |
| 20260913-175422-ollama_kimi-k3_cloud-91602 | paper-nih-50 | 1300 | 1 |
| 20260914-035831-ollama_glm-5.3-flash_cloud-24674 | paper-vindr-100 | 3528 | 189 |
| 20260914-120204-ollama_mistral-large-3_675b-cloud-30100 | paper-vindr-100 | 3528 | 0 |
| 20260915-030506-ollama_glm-5.3-flash_cloud-20338 | paper-nih-50 | 1300 | 71 |
| 20260915-045336-ollama_mistral-large-3_675b-cloud-42972 | paper-nih-50 | 1300 | 0 |
| 20260915-090411-ollama_kimi-k3_cloud-72195 | bonescan-40 | 669 | 0 |
| 20260915-091907-ollama_glm-5.3-flash_cloud-75424 | bonescan-40 | 664 | 48 |
| 20260915-103529-ollama_mistral-large-3_675b-cloud-91545 | bonescan-40 | 664 | 0 |
| 20260921-163321-gemini-44812 | paper-vindr-100 | 3528 | 0 |
| 20260921-204254-gemini-98135 | paper-nih-50 | 1300 | 0 |
| 20260921-213947-gemini-10358 | bonescan-40 | 664 | 0 |
| 20260922-064539-gpt-17237 | paper-vindr-100 | 3528 | 0 |
| 20260922-104235-gpt-70905 | paper-nih-50 | 1300 | 0 |
| 20260922-114116-gpt-83217 | bonescan-40 | 664 | 0 |
| 20260922-160359-claude-37919 | paper-vindr-100 | 3528 | 0 |
| 20260922-183045-claude-69699 | paper-nih-50 | 1300 | 0 |
| 20260922-190926-claude-77924 | bonescan-40 | 664 | 0 |
| CONTAMINATED-20260908-160228-gemma4_e4b | pilot-vindr-20 | 454 | 0 |
