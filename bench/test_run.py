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


def test_conflict_tasks_have_the_right_answers_and_unique_ids(tmp_path):
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
    assert all(t["conditions"] == ["ctx"] and t["gating"] is False for t in T)
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
