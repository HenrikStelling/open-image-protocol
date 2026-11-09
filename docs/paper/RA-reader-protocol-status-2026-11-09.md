# Status for the RA session: reader protocol 1.0 (interim, 2026-11-09)

Reply to the work order `oipbench/lancet/Uebergabe_OIP_Leseprotokoll_1.0.md` (2026-11-05). Interim: the protocol is drafted and
approved by the first author pending the last author's check; nothing is frozen, tagged or registered yet. The final report
(commit, tag, OSF URL with timestamp, ethics wording, list of changes) follows after the freeze.

## 1. What exists

| item | state |
|---|---|
| `bench/reader/PROTOCOL.md` 1.0 (English) | drafted; sections 1–6 translated without change of substance; section 9 lists every change since 0.1 with date and reason; section 10 is the freeze record (placeholders) |
| `bench/reader/PROTOKOLL.md` 0.2 | kept, superseded note at the top |
| `bench/reader/leserinformation.html` / `.pdf` | one-page German information sheet for the readers; no pointer to the repository or the key file |
| `bench/reader/README.md` | points to PROTOCOL.md; wording "the assistant's visual check" replaced |
| `docs/paper/osf-form-text-reader-protocol-1.0.md` | form text for the second registration in project ntgrb (placeholders for tag, dates, committee answer) |
| workflow terms | none left in PROTOCOL.md, README.md, reader_template.html, items.json, leserinformation.html (grep for owner, session, model and tool names) |
| readings | none; `bench/reader/readings/` does not exist (to be confirmed again at the freeze) |

Commits (local until pushed): 1b1159e, 03aca29, 928525e. The first reader (a board-certified radiologist from a practice in
Potsdam, R1) has been recruited; a second reader is found; the nuclear medicine reader and the adjudicating radiologist are
still to be named. Readers' role: co-authors (decision of the authors, 2026-11-09).

## 2. Changes from 0.1 (summary; full list in PROTOCOL.md section 9)

1. 2026-11-04, section 2: blinding stated as procedural (key file and package values are public); running number instead of
   item id; reader attestation by e-mail after the reading; named in the limitations.
2. 2026-11-06, section 7: ethics route via the last author to the Ethics Committee of the OVGU Magdeburg instead of the first
   author's institution; question 3 (external co-authors and readers) included. Status 11-09: committee says no vote is
   required; a written waiver is requested and outstanding.
3. 2026-11-06: English; workflow terms removed; script work attributed to `build_set.py` and `collect.py`.
4. 2026-11-09, section 2: readers are co-authors.
5. Structure: section 8 (operating the sheet) stated as not frozen; sections 9 and 10 added.

Unchanged since 0.1: `items.json` (sha256 `2349a71e6e278e536bc293f170b7550572341cb37b1b0e1b997c0b53fb5281d2`), blocks,
measurement definitions, adjudication rule, analysis plan.

## 3. Three points for RA to confirm or correct

1. **Author roles.** PROTOCOL.md uses "the last author" for the OVGU co-author as the work order says. If the author order is
   not yet fixed, "the corresponding author" or a neutral "the co-author at the OVGU" is safer; one word to change.
2. **Reason for the ethics route.** Section 9 item 2 gives as reason only that the inquiry was routed through the last author's
   institution. If there is a substantive reason, send it; otherwise it stays as is.
3. **Earlier marker screen.** Section 1 names the earlier check of the masked renders as "the earlier model-assisted visual
   screen … recorded in `bench/marker_review.json`". This names the AI assistance without naming a tool as actor. If RA
   prefers "the earlier visual screen recorded in `bench/marker_review.json`", say so.

## 4. Ethics: an open question that affects section 7

The last author holds an earlier waiver of the FAU Erlangen-Nürnberg stating that no vote is needed for work on anonymised
public data only. Whether it covers external authors is being asked. Before section 7 can cite it, four facts are needed:
issuing body and date; whether it is project-specific or a general statement; the author's affiliation at the time versus
now; the exact scope (external co-authors, readers). Proposal: keep the OVGU inquiry running for a current, project-specific
waiver; cite the FAU document, if at all, as supporting evidence with its date and scope. Section 7 and the OSF text name the
OVGU committee as consulted; if the FAU waiver becomes the primary document, both texts change before the freeze, not after.

## 5. Planned order

kimi-k3 repeats complete (first author's decision to wait) → the last author's check of PROTOCOL.md, information sheet and
README → section 7 (date and form of the committee's answer) and section 10 filled → commit, tag `reader-protocol-1.0`, push →
OSF registration in ntgrb submitted by the first author (form text ready) → first reading. The waiver letter is added later to
section 7 and to Methods as a dated addendum; the registration is not edited.

## 6. What RA gets at the end

Commit hash and tag; OSF URL (and DOI when issued) with timestamp; ethics wording or reference number; the list of changes
(section 9); sha256 of `PROTOCOL.md` and `items.json`.
