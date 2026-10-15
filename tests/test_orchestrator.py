import json
from pathlib import Path

import pytest

from agentic_sdlc.config import ConfigError, HarnessConfig
from agentic_sdlc.gates import FileGate
from agentic_sdlc.orchestrator import Orchestrator
from agentic_sdlc.sessions import FakeBackend
from agentic_sdlc.standards import MarkdownStandardsStore
from conftest import verdict

REQ = "REQ-FLISR-001 The plan shall refuse when tie capacity is unknown.\nREQ-FLISR-002 Tie switches shall be considered."


def make(tmp_path, cfg_dict, harness_root, script, standards_dir=None):
    cfg = HarnessConfig.from_dict(cfg_dict)
    return Orchestrator(cfg=cfg, run_dir=tmp_path / "run", backend=FakeBackend(script),
                        standards=MarkdownStandardsStore(standards_dir or harness_root / "standards"),
                        skills_dir=harness_root / "plugin/skills", gate_factory=lambda g, d, name: FileGate(d))


def decide(run_dir, gate, decision="approved", actor="alice"):
    (Path(run_dir) / "gates" / f"{gate}.decision.json").write_text(json.dumps(
        {"decision": decision, "actor": actor, "reviewers": 2, "comment": "looks right"}))


def test_config_rejects_same_model_for_coding_and_qa(cfg_dict):
    cfg_dict["models"]["qa"] = "normal"
    with pytest.raises(ConfigError):
        HarnessConfig.from_dict(cfg_dict)


def test_evaluate_boundary_cannot_be_overridden(cfg_dict):
    cfg_dict["boundaries"]["evaluate"] = {"allowed": ["**"], "codebase_access": True}
    cfg = HarnessConfig.from_dict(cfg_dict)
    assert cfg.boundary("evaluate").codebase_access is False
    assert cfg.reviewers_required(["backend/app/flisr.py"]) == 2


def test_feature_run_with_blocked_question_gates_and_qa_loop(tmp_path, cfg_dict, harness_root):
    spec = "REQ-FLISR-001 ...\nREQ-FLISR-002 ..."
    script = {
        "specify": [verdict("BLOCKED", "gap", questions=[{"id": "Q-SPEC-1", "question": "tie capacity source?",
                                                           "blocking_units": ["U1"]}]),
                    verdict("PASS", "spec", artifacts={"specification": spec})],
        "decompose": [verdict("PASS", artifacts={"units": [
            {"id": "U1", "title": "guard", "depends_on": [], "files": ["backend/app/flisr.py", "backend/tests/**"]}]})],
        "design": [verdict("PASS", artifacts={"design": "d1"}, trace=[
            {"requirement_id": "REQ-FLISR-001", "kind": "design", "ref": "D1"},
            {"requirement_id": "REQ-FLISR-002", "kind": "design", "ref": "D2"}]),
                   verdict("PASS", artifacts={"design": "d2"})],
        "architect": [verdict("VIOLATION", "STD-ARCH-1 breached", artifacts={"review": "move model"}),
                      verdict("CONFIRMED", artifacts={"review": "ok"})],
        "coding": [verdict("PASS", branch="agent/r/U1", pr_url="https://github.com/o/r/pull/1",
                           files_touched=["backend/app/flisr.py"], trace=[
                               {"requirement_id": "REQ-FLISR-001", "kind": "code", "ref": "flisr.py"},
                               {"requirement_id": "REQ-FLISR-001", "kind": "test", "ref": "t1"},
                               {"requirement_id": "REQ-FLISR-002", "kind": "code", "ref": "flisr.py"},
                               {"requirement_id": "REQ-FLISR-002", "kind": "test", "ref": "t2"}]),
                   verdict("PASS", branch="agent/r/U1", pr_url="https://github.com/o/r/pull/1")],
        "qa": [verdict("FAIL", "vector 7 off by 1", artifacts={"qa_report": "r"}), verdict("PASS")],
        "integrate": [verdict("PASS", pr_url="https://github.com/o/r/pull/1", trace=[
            {"requirement_id": "REQ-FLISR-001", "kind": "pr", "ref": "PR#1"},
            {"requirement_id": "REQ-FLISR-002", "kind": "pr", "ref": "PR#1"}])],
        "document": [verdict("PASS")],
    }
    o = make(tmp_path, cfg_dict, harness_root, script)
    o.start("feature", REQ, "REQ.md", run_id="r")
    st = o.resume()
    assert st["paused_on"]["reason"] == "questions-open"
    o.answer("Q-SPEC-1", "from the planning model", actor="alice")
    st = o.resume()
    assert st["paused_on"]["reason"] == "gate-waiting" and "after-specify" in st["gates"]
    decide(o.run_dir, "after-specify")
    st = o.resume()
    assert st["paused_on"]["gate"] == "after-architect"
    decide(o.run_dir, "after-architect")
    st = o.resume()
    assert st["paused_on"]["gate"] == "before-merge"
    decide(o.run_dir, "before-merge")
    st = o.resume()
    assert st["status"] == "ready-to-merge"
    # QA briefs ran on a different mode than coding
    modes = {(r.title.split("] ")[1].split()[0], r.devin_mode) for r in o.backend.requests}
    assert ("coding", "normal") in modes and ("qa", "ultra") in modes
    kpis = json.loads((o.run_dir / "kpis.json").read_text())
    assert kpis["loop_iterations"] == {"design-architect": 2, "coding-qa": 2}
    assert kpis["loop_resolution_rate"] == 1.0 and kpis["requirement_test_coverage"] == 1.0
    assert kpis["first_pass_approval"]["specify"] is False and kpis["first_pass_approval"]["coding"] is True
    assert o.log.verify_chain()[0]
    assert {g["actor"] for g in kpis["gates"]} == {"alice"}


def test_missing_standard_blocks(tmp_path, cfg_dict, harness_root):
    cfg_dict["standards"]["required"] = ["STD-DOES-NOT-EXIST"]
    o = make(tmp_path, cfg_dict, harness_root, {"specify": [verdict("PASS")]})
    o.start("feature", REQ, "REQ.md", run_id="r")
    st = o.resume()
    assert st["paused_on"]["reason"] == "standard-missing"
    assert [r["verdict"] for r in o.log if r["event"] == "stage.completed"] == ["BLOCKED"]


def test_rca_retraction_after_two_refutations(tmp_path, cfg_dict, harness_root):
    script = {"explore": [verdict("PASS", artifacts={"hypothesis": "h1", "evidence_package": "e1"}),
                          verdict("PASS", artifacts={"hypothesis": "h2", "evidence_package": "e2"})],
              "evaluate": [verdict("REFUTED", "no mechanism"), verdict("REFUTED", "still symptom only")]}
    o = make(tmp_path, cfg_dict, harness_root, script)
    o.start("rca", "Defect: back-feed", "DEFECT.md", run_id="r")
    st = o.resume()
    assert st["status"] == "retracted"
    evaluate_reqs = [r for r in o.backend.requests if "evaluate" in r.title]
    assert all(r.repos == [] for r in evaluate_reqs) and "no codebase access" in evaluate_reqs[0].prompt
    assert "constraint" in o.backend.requests[2].prompt  # second explore carries objections


def test_bot_gate_decision_is_ignored(tmp_path, cfg_dict, harness_root):
    o = make(tmp_path, cfg_dict, harness_root, {"specify": [verdict("PASS", artifacts={"specification": "REQ-FLISR-001 x"})]})
    o.start("feature", REQ, "REQ.md", run_id="r")
    o.resume()
    (o.run_dir / "gates" / "after-specify.decision.json").write_text(json.dumps(
        {"decision": "approved", "actor": "devin[bot]", "actor_type": "Bot"}))
    st = o.resume()
    assert st["paused_on"]["reason"] == "gate-waiting"
