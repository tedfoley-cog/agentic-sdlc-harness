from agentic_sdlc import checks

DIFF_ZERO = """diff --git a/backend/app/flisr.py b/backend/app/flisr.py
--- a/backend/app/flisr.py
+++ b/backend/app/flisr.py
@@ -10,4 +10,6 @@ def plan(feeder):
-    if load is None:
-        raise FlisrError("load unknown")
+    load = telemetry.get("load_kw", 0)
+    margin = capacity or 0
     return load
"""

DIFF_MODEL = """diff --git a/backend/app/models.py b/backend/app/models.py
--- a/backend/app/models.py
+++ b/backend/app/models.py
@@ -1,3 +1,8 @@
 @dataclass
 class Switch:
     mrid: str
+    def can_close(self):
+        if self.locked:
+            return False
+        return True
diff --git a/backend/app/flisr.py b/backend/app/flisr.py
--- a/backend/app/flisr.py
+++ b/backend/app/flisr.py
@@ -1,2 +1,5 @@
+@dataclass
+class TieCapacity:
+    kw: float
 def x():
     pass
"""


def test_missing_input_as_zero_and_removed_guard_fail():
    res = {r.name: r for r in checks.run_all(DIFF_ZERO, brief_files=["backend/app/flisr.py"])}
    assert res["missing_input_as_zero"].verdict == "FAIL"
    assert {f["text"] for f in res["missing_input_as_zero"].findings} == {
        'load = telemetry.get("load_kw", 0)', "margin = capacity or 0"}
    assert res["removed_error_handling"].verdict == "FAIL"
    assert res["scope"].verdict == "PASS"
    assert checks.overall(list(res.values())) == "FAIL"


def test_model_logic_separation_both_directions():
    res = {r.name: r for r in checks.run_all(DIFF_MODEL, model_globs=["**/models.py"])}
    rules = {f["rule"] for f in res["model_logic_separation"].findings}
    assert "logic-in-model-file" in rules and "behaviour-method-in-model" in rules
    assert "model-in-logic-file" in rules


def test_zero_ok_allowlist_and_clean_diff_pass():
    clean = DIFF_ZERO.replace('telemetry.get("load_kw", 0)', 'telemetry.get("load_kw", 0)  # harness: zero-ok STD-X-1') \
        .replace("+    margin = capacity or 0\n", "+    if capacity is None:\n+        raise FlisrError('capacity unknown')\n")
    res = {r.name: r for r in checks.run_all(clean)}
    assert res["missing_input_as_zero"].verdict == "PASS"
    assert res["removed_error_handling"].verdict == "PASS"


def test_governance_check():
    gov = {"trailer": "AI-Governance", "draft_only": True, "pr_label": "ai-generated", "branch_prefix": "agent/"}
    res = checks.run_all("", commit_messages=["fix: x\n\nAI-Governance: run=r1 stage=coding agent=devin model=normal"],
                         pr={"draft": False, "labels": [], "head": "feature/x", "merged": True}, governance=gov)
    gov_res = [r for r in res if r.name == "governance"][0]
    assert {f["rule"] for f in gov_res.findings} == {"pr-not-draft", "missing-ai-generated-label", "branch-prefix",
                                                     "merged-by-agent"}
    res2 = checks.run_all("", commit_messages=["no trailer"], pr={"draft": True, "labels": ["ai-generated"],
                                                                  "head": "agent/r1/U1"}, governance=gov)
    assert [f["rule"] for f in res2[-1].findings] == ["missing-governance-trailer"]


def test_zero_pattern_in_docstring_or_comment_is_not_a_finding():
    prose = DIFF_ZERO.replace('+    load = telemetry.get("load_kw", 0)\n+    margin = capacity or 0\n',
                              '+    """Inspection: no `or 0` left in flisr.py."""\n+    load = telemetry.get("load_kw")  # was `or 0`\n')
    assert prose != DIFF_ZERO
    res = {r.name: r for r in checks.run_all(prose)}
    assert res["missing_input_as_zero"].verdict == "PASS", res["missing_input_as_zero"].findings


def test_waived_id_leaves_test_coverage_but_stays_in_matrix(tmp_path):
    from agentic_sdlc.trace import TraceMatrix
    tm = TraceMatrix(tmp_path / "trace.json", r"REQ-X-\d+|DEF-Y-\d+")
    tm.register_requirements("REQ-X-1 shall ...\nDEF-Y-7 is out of scope ...")
    tm.append("coding", [{"requirement_id": "REQ-X-1", "kind": "test", "ref": "tests/test_x.py"}])
    assert tm.coverage()["with_test"] == 1 and tm.coverage()["requirements"] == 2
    tm.waive("DEF-Y-7", actor="ops-lead", reason="scope exclusion picked up by the id scanner")
    cov = TraceMatrix(tmp_path / "trace.json", r"REQ-X-\d+|DEF-Y-\d+").coverage()
    assert cov["requirements"] == 1 and cov["test_coverage"] == 1.0 and cov["waived"] == ["DEF-Y-7"]


def test_replayed_loop_rounds_count_once(tmp_path):
    from agentic_sdlc import kpis
    from agentic_sdlc.runlog import RunLog
    log = RunLog(tmp_path / "runlog.jsonl")
    log.append("run.started", run_id="r", workflow="feature", target="x", requirement="y")
    for it, resolved in ((1, False), (1, False), (2, True)):  # round 1 replayed once after a pause
        log.append("loop.iteration", loop="design-architect", iteration=it, verdict="X", resolved=resolved)
    assert kpis.compute(tmp_path)["loop_iterations"]["design-architect"] == 2
