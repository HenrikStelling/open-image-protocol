# Sources

## MCP
- https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro
- https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture
- https://modelcontextprotocol.io/docs/2026-07-28/learn/server-concepts
- https://www.anthropic.com/news/model-context-protocol
- https://modelcontextprotocol.io/community/sep-guidelines
- https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1400 (SEP-1400 semver)
- https://github.com/modelcontextprotocol/modelcontextprotocol/issues/932 (SEP-001 governance)
- https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
- https://blog.modelcontextprotocol.io/posts/mcp-roadmap/
- https://arxiv.org/pdf/2605.22333 (auth security study; version history)

## LSP
- https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/
- https://opencode.ai/docs/lsp/
- Video: https://youtu.be/lffYEu5MhSQ (LSP in Claude Code; Serena MCP) — analysed with ai-vision-mcp

## Model Hardware Standard
- https://www.anthropic.com/news/model-hardware-standard-research-preview
- https://modelhardwarestandard.com
- Video: https://youtu.be/P1zBiAQU1IA — analysed with ai-vision-mcp
- https://www.heise.de/en/news/Anthropic-introduces-communication-standard-for-hardware-11435794.html
- https://truescho.com/en/blog/anthropic-model-hardware-standard-2026
- https://thenextweb.com/news/anthropic-model-hardware-standard-mhs-eu-machinery-regulation-2027

## DICOM and imaging standards
- DICOM JSON model: https://dicom.nema.org/medical/dicom/current/output/chtml/part18/chapter_f.html
- NM Image IOD: https://dicom.innolitics.com/ciods/nuclear-medicine-image ; https://dicom.nema.org/dicom/2013/output/chtml/part03/sect_A.5.html
- DX Image module: https://dicom.innolitics.com/ciods/digital-x-ray-image/dx-image
- Pixel spacing calibration macro: https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_10.7.html ; CP-586 https://dicom.nema.org/dicom/CP/CPack-34_PDF/cp586_lb.pdf
- TID 1500 / highdicom: https://highdicom.readthedocs.io/en/latest/tid1500.html ; https://link.springer.com/article/10.1007/s10278-022-00683-y
- Sup 219 JSON SR: https://www.dicomstandard.org/news/supplements/view/json-representation-of-dicom-structured-reports
- IHE AI Results: https://connectathon.ihe-europe.net/highlighted-ihe-profiles
- FHIR ImagingStudy: https://hl7.org/fhir/imagingstudy.html
- RSNA RadElement CDEs: https://www.rsna.org/practice-tools/data-tools-and-standards/radelement-common-data-elements ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12572421/
- OME-NGFF: https://ngff.openmicroscopy.org/latest/ ; RFC-4 orientation https://ngff.openmicroscopy.org/rfc/4/index.html ; nifti-zarr https://github.com/neuroscales/nifti-zarr
- dicom-mcp: https://www.christianhinge.com/projects/dicom-mcp/
- llms.txt: https://limy.ai/blog/llms-txt-in-2026-the-full-guide ; https://evilmartians.com/chronicles/how-to-make-your-website-visible-to-llms

## VLMs and medical imaging
- WindowNet: https://pmc.ncbi.nlm.nih.gov/articles/PMC10743662/
- CXR-LLaVA: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12166004/
- LLaVA-Rad / CheXprompt: https://www.nature.com/articles/s41467-025-58344-x
- MAIRA-2: https://arxiv.org/abs/2406.04449 ; https://huggingface.co/microsoft/maira-2
- GPT-4o on X-rays: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12113413/
- MC-CXR (context disruption): https://arxiv.org/html/2608.24118v1
- MedVision (quantitative benchmark): https://arxiv.org/html/2511.18676
- "Your other Left!" (MIRP): https://arxiv.org/pdf/2508.00549
- Point, Detect, Count: https://arxiv.org/html/2505.16647v1
- Set-of-Mark prompting: https://arxiv.org/pdf/2310.11441
- Grid overlays / coordinates (GPT-5.x): https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/gpt-capability-in-understanding-coordinates-how-gpt-5-4-transforms-spatial-preci/4506726
- RadAgents: https://arxiv.org/html/2509.20490
- ReXrank + metrics: https://arxiv.org/pdf/2411.15122 ; RaTEScore https://arxiv.org/pdf/2406.16845 ; RadEval https://arxiv.org/pdf/2509.18030

## Measurement and segmentation
- DL CTR clinical evaluation (ICC 0.959): https://ncbi.nlm.nih.gov/pmc/articles/PMC8925133
- CTR DL performance: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10525628/ ; https://pmc.ncbi.nlm.nih.gov/articles/PMC10585545/
- CheXmask: https://physionet.org/content/chexmask-cxr-segmentation-data/1.0.0/ ; https://arxiv.org/html/2307.03293v3
- CXAS: https://github.com/ConstantinSeibold/ChestXRayAnatomySegmentation
- MedSAM for CXR: https://arxiv.org/pdf/2512.23089
- DAT SPECT quantification: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8113194/ ; https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7648825/
- Quantitative bone SPECT/CT: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6933900/

## Datasets
- VinDr-CXR: https://arxiv.org/pdf/2012.15029 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC9300612/
- RSNA Pneumonia: https://www.kaggle.com/competitions/rsna-pneumonia-detection-challenge
- CheXpert Plus: https://arxiv.org/pdf/2405.19538
- MIMIC-CXR: https://www.nature.com/articles/s41597-019-0322-0
- COVID dataset pitfalls: https://arxiv.org/pdf/2111.05679
- BS-80K: https://pubmed.ncbi.nlm.nih.gov/36334360/
- Paraguay bone scans: https://zenodo.org/records/13900966 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC11699483/
- Thyroid scintigraphy multicentre: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10453808/ ; https://arxiv.org/abs/2503.00366
- kagglehub: https://github.com/Kaggle/kagglehub
