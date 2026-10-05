"""Runner conditions for the verification ablation (OEP-003/004): the ablation conditions follow their base condition for task
applicability, the *_instr conditions carry the verify sentence in the system prompt, and the prompts differ only where intended.
Run: ~/oip-venv/bin/python -m pytest bench/test_run.py -q"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "bench")); sys.path.insert(0, str(ROOT / "src"))
import run  # noqa: E402

PKG = ROOT / "spec/examples/synthetic-dx-chest.oip"
FLIP = {"type": "flip_check", "question": "q", "answer": "agree", "flipped": False, "conditions": ["ctx_l1", "ctx"], "gating": True, "pkg": str(PKG), "id": "x:flip_check"}
EDGE = {"type": "left_edge", "question": "q", "answer": "patient right", "gating": True, "pkg": str(PKG), "id": "x:left_edge"}
MISLED = {"type": "findings_misled", "question": "q", "answer": ["No finding"], "misleading_label": "Nodule/Mass", "gating": False, "pkg": str(PKG), "id": "x:findings_misled"}


def test_ablation_conditions_follow_ctx_for_applicability():
    for c in ("ctx", "ctx_ctl", "ctx_cue", "ctx_instr", "ctx_cue_instr"):
        assert run.applies(FLIP, c), c
        assert run.applies(EDGE, c), c
        assert not run.applies(MISLED, c), c
    assert not run.applies(FLIP, "raw") and not run.applies(FLIP, "annot")


def test_system_prompt_gets_the_verify_sentence_only_for_instr_conditions():
    assert run.system_for("ctx") == run.SYSTEM
    assert run.system_for("ctx_cue") == run.SYSTEM
    assert run.system_for("ctx_instr") == run.SYSTEM + run.VERIFY_INSTR
    assert run.system_for("ctx_cue_instr") == run.SYSTEM + run.VERIFY_INSTR
    assert "[inferred]" in run.VERIFY_INSTR


def test_prompts_differ_only_where_intended():
    ctx, _ = run.build_prompt(EDGE, "ctx"); ctl, _ = run.build_prompt(EDGE, "ctx_ctl"); instr, _ = run.build_prompt(EDGE, "ctx_instr")
    cue, _ = run.build_prompt(EDGE, "ctx_cue"); both, _ = run.build_prompt(EDGE, "ctx_cue_instr")
    assert ctx == ctl == instr                      # the control and the instruction arm send the shipped file unchanged
    assert cue == both and cue != ctx               # the cue arms send the 0.3-draft file
    assert "cardiac apex" in cue and "cardiac apex" not in ctx
    assert ctx.endswith("\n\nQuestion: q") and cue.endswith("\n\nQuestion: q")


def test_every_condition_is_documented():
    for c in ("ctx_ctl", "ctx_cue", "ctx_instr", "ctx_cue_instr"):
        assert c in run.CONDITIONS and c in run.BASE_CONDITION


# round 3: orientation conflict trials (text correct/wrong x image normal/mirrored)
def test_text_flipped_swaps_the_edge_labels_in_the_file_only():
    t = dict(EDGE, text_flipped=True)
    normal, _ = run.build_prompt(EDGE, "ctx"); swapped, _ = run.build_prompt(t, "ctx")
    assert "image LEFT edge = R, RIGHT edge = L" in normal
    assert "image LEFT edge = L, RIGHT edge = R" in swapped
    assert "left edge? → L" in swapped and "left edge? → R" in normal      # the self-check follows the swapped labels
    assert normal.replace("LEFT edge = R, RIGHT edge = L", "").count("Question:") == 1


def test_conflict_tasks_have_the_right_answers_and_unique_ids(tmp_path, monkeypatch):
    import json, shutil
    import numpy as np
    from PIL import Image
    import tasks
    src = ROOT / "spec/examples/synthetic-dx-chest.oip"; pkg = tmp_path / "abcdef012345.oip"; shutil.copytree(src, pkg)
    m = json.loads((pkg / "oip.json").read_text()); rows, cols = m["geometry"]["rows"], m["geometry"]["columns"]
    (pkg / "derived/masks").mkdir(parents=True, exist_ok=True)
    heart = np.zeros((rows, cols), bool); heart[rows // 2: rows // 2 + rows // 5, int(cols * 0.52): int(cols * 0.72)] = True
    Image.fromarray((heart * 255).astype(np.uint8)).save(pkg / "derived/masks/heart.png")
    T = [t for t in tasks.tasks_for_package(pkg) if t["type"] == "orient_conflict"]
    assert len(T) == 4 and len({t["id"] for t in T}) == 4
    cells = {t["cell"]: t["answer"] for t in T}
    assert cells == {"TN": "agree", "TM": "mirrored", "WN": "mirrored", "WM": "agree"}
    assert all(t["conditions"] == ["ctx", "ctx3", "ctx3_mask"] and t["gating"] is False for t in T)
    monkeypatch.setattr(tasks, "_marker_excluded", lambda: {pkg.name})          # a package with a residual marker keeps the legacy condition only
    assert all(t["conditions"] == ["ctx"] for t in tasks.tasks_for_package(pkg) if t["type"] == "orient_conflict")
    # a text-only policy ("agree" always) and a pixel-only policy (judge the image alone) each score 2 of 4
    from score import score
    assert sum(score(t, "agree")["correct"] for t in T) == 2
    assert sum(score(t, "mirrored" if t["flipped"] else "agree")["correct"] for t in T) == 2
    assert sum(score(t, t["answer"])["correct"] for t in T) == 4


def test_no_conflict_tasks_without_a_clear_cue(tmp_path):
    import shutil, tasks
    src = ROOT / "spec/examples/synthetic-dx-chest.oip"; pkg = tmp_path / "0123456789ab.oip"; shutil.copytree(src, pkg)
    assert not [t for t in tasks.tasks_for_package(pkg) if t["type"] == "orient_conflict"]   # no heart mask -> no cue -> no trial


def test_separately_returned_thinking_is_stored_in_front_of_the_answer_and_not_scored():
    # think=true: the daemon returns reasoning in message.thinking; the row keeps it as <think>…</think> + answer (the form
    # glm emits itself with think=false), so score._tail() scores the answer alone.
    from score import score
    reply, thinking = run._compose_reply("**0.41**", "CTR = 350/850 = 0.41")
    assert reply == "<think>CTR = 350/850 = 0.41</think>**0.41**" and thinking == "CTR = 350/850 = 0.41"
    assert run._compose_reply("**0.41**", "") == ("**0.41**", "")
    task = {"type": "ctr", "answer": 0.55, "tolerance": 0.05}
    assert score(task, run._compose_reply("**0.55**", "first 350/850 = 0.41, no, 0.55")[0])["value"] == 0.55


# ---------------------------------------------------------------- round 3 (2026-09-30)
def _r3_pkg(tmp_path, monkeypatch):
    """Synthetic example package with two lung regions added (image-left lung = patient right) and the render cache redirected."""
    import json, shutil
    src = ROOT / "spec/examples/synthetic-dx-chest.oip"; pkg = tmp_path / "abcdef012345.oip"; shutil.copytree(src, pkg)
    m = json.loads((pkg / "oip.json").read_text())
    base = m["derived"]["regions"][0]   # copy an existing region so every field the template reads is present
    m["derived"]["regions"] += [dict(base, id="lung_right", label="right lung", assertion_level="inferred", mark="3", bbox_px=[300, 150, 1400, 700]),
                                dict(base, id="lung_left", label="left lung", assertion_level="inferred", mark="4", bbox_px=[300, 800, 1400, 1350])]
    (pkg / "oip.json").write_text(json.dumps(m))
    monkeypatch.setattr(run, "RENDER_CACHE", tmp_path / "cache")
    return pkg, m


def test_marker_mask_keeps_the_size_and_blanks_everything_outside_the_box(tmp_path, monkeypatch):
    import io
    import numpy as np
    from PIL import Image
    pkg, m = _r3_pkg(tmp_path, monkeypatch)
    box = run.mask_box(m)
    assert box == [300 + int(0.15 * 1100), 150 - 30, 1400 + 54, 1350 + 30]          # top moved down 15 % of the lung height
    canon = np.asarray(Image.open(pkg / "renders/canonical.png").convert("L"))
    a = np.asarray(Image.open(io.BytesIO(run._masked(pkg, False)))); b = np.asarray(Image.open(io.BytesIO(run._masked(pkg, True))))
    assert a.shape == canon.shape and (b == a[:, ::-1]).all()
    fy, fx = canon.shape[0] / 1800, canon.shape[1] / 1500
    r0, c0, r1, c1 = int(box[0] * fy), int(box[1] * fx), int(box[2] * fy), int(box[3] * fx)
    assert (a[r0:r1, c0:c1] == canon[r0:r1, c0:c1]).all()
    outside = a.copy(); outside[r0:r1, c0:c1] = 0
    assert outside.max() == 0
    m["derived"]["regions"] = [r for r in m["derived"]["regions"] if not r["id"].startswith("lung")]
    assert run.mask_box(m) is None                                                   # no lungs, no mask


def test_badge_read_truth_is_balanced_and_follows_the_printed_labels(tmp_path, monkeypatch):
    import tasks
    from score import score
    pkg, _ = _r3_pkg(tmp_path, monkeypatch)
    T = [t for t in tasks.tasks_for_package(pkg) if t["type"] == "badge_read"]
    assert [t["answer"] for t in T] == ["patient right", "patient left"] and [t["label_swap"] for t in T] == [False, True]
    assert len({t["id"] for t in T}) == 2 and all(t["gating"] is False and t["conditions"] == ["labels3"] for t in T)
    (txt0, img0), (txt1, img1) = (run.build_prompt(t, "labels3") for t in T)
    assert txt0 == txt1 and "Reference file" not in txt0 and img0[0][1] != img1[0][1]   # same question, no file, different printed labels
    assert sum(score(t, "patient right")["correct"] for t in T) == 1                    # a convention prior scores 50 %
    assert run.applies(T[0], "labels3") and not run.applies(T[0], "ctx") and not run.applies(T[0], "annot")


def test_mark_side_runs_with_and_without_the_region_list(tmp_path, monkeypatch):
    import tasks
    pkg, _ = _r3_pkg(tmp_path, monkeypatch)
    t = next(t for t in tasks.tasks_for_package(pkg) if t["type"] == "mark_side")
    assert run.applies(t, "annot") and run.applies(t, "annot3") and run.applies(t, "annot3_l1") and not run.applies(t, "ctx3")
    full, _ = run.build_prompt(t, "annot3"); l1, _ = run.build_prompt(t, "annot3_l1")
    assert "lung_left" in full and "lung_left" not in l1 and "lung_right" not in l1    # the leak is in the region list only
    assert "Estimating from the image" in full                                          # round 3 renders the shipped template (0.2.1)
    ctx, _ = run.build_prompt(t, "annot")
    assert "Estimating from the image" not in ctx                                       # legacy condition keeps the 0.2 wording


def test_prompt_hash_identifies_what_was_sent():
    a = run.prompt_sha256("s", "t", [("image/png", b"x")])
    assert a == run.prompt_sha256("s", "t", [("image/png", b"x")]) and len(a) == 64
    assert len({a, run.prompt_sha256("s", "t", [("image/png", b"y")]), run.prompt_sha256("s", "u", [("image/png", b"x")]), run.prompt_sha256("z", "t", [("image/png", b"x")])}) == 4


def test_think_policy_and_output_caps(monkeypatch):
    monkeypatch.setattr(run, "OLLAMA_THINK_MODE", "auto"); monkeypatch.setattr(run, "_NO_THINK", {})
    # auto: nobody thinks (the paper's setting); models that reason inside content get the larger output cap
    assert not run._think_for("glm-5.3-flash:cloud") and not run._think_for("kimi-k3:cloud")
    assert run._num_predict("glm-5.3-flash:cloud", False) == 8000 and run._num_predict("kimi-k3:cloud", False) == 800
    monkeypatch.setattr(run, "OLLAMA_THINK_MODE", "on")
    assert run._think_for("kimi-k3:cloud") and run._num_predict("kimi-k3:cloud", True) == 4000
    monkeypatch.setattr(run, "_NO_THINK", {"kimi-k3:cloud": True})
    assert not run._think_for("kimi-k3:cloud") and run._num_predict("kimi-k3:cloud", False) == 800
    monkeypatch.setattr(run, "OLLAMA_THINK_MODE", "off")
    assert not run._think_for("glm-5.3-flash:cloud") and run._num_predict("glm-5.3-flash:cloud", False) == 800   # paper runs


def test_misleading_label_is_stable_across_processes(tmp_path, monkeypatch):
    import subprocess, tasks
    pkg, _ = _r3_pkg(tmp_path, monkeypatch)
    here = next(t for t in tasks.tasks_for_package(pkg, labels=[]) if t["type"] == "findings_misled")["misleading_label"]
    code = f"import sys; sys.path.insert(0, {str(ROOT / 'bench')!r}); import tasks, pathlib; print(next(t for t in tasks.tasks_for_package(pathlib.Path({str(pkg)!r}), labels=[]) if t['type'] == 'findings_misled')['misleading_label'])"
    other = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env={"PYTHONHASHSEED": "12345", "PATH": ""}).stdout.strip()
    assert other == here


def test_a_reply_cut_off_inside_its_reasoning_carries_no_answer():
    task = {"type": "flip_check", "answer": "mirrored"}
    cut = "the apex points right so the image is mirrored, but the label says"           # fragment, no closing tag
    assert run.score_row(task, cut, {"done_reason": "length"}) == {"correct": False, "truncated": True}
    assert run.score_row(task, cut, {"done_reason": "stop"})["correct"] is True              # complete reply: scored as before
    assert run.score_row(task, "<think>long</think>mirrored", {"done_reason": "length"})["correct"] is True   # answer after the tag survives
