import json

from agentic_sdlc.runlog import RunLog, replay
from agentic_sdlc.trace import TraceMatrix


def test_runlog_is_append_only_and_tamper_evident(tmp_path):
    log = RunLog(tmp_path / "runlog.jsonl")
    log.append("run.created", run_id="r1", workflow="feature")
    log.append("gate.decided", gate="after-specify", decision="approved", actor="alice", actor_type="User")
    assert log.verify_chain() == (True, "chain intact")
    lines = (tmp_path / "runlog.jsonl").read_text().splitlines()
    rec = json.loads(lines[1]); rec["actor"] = "devin-bot"
    lines[1] = json.dumps(rec, sort_keys=True)
    (tmp_path / "runlog.jsonl").write_text("\n".join(lines) + "\n")
    ok, msg = RunLog(tmp_path / "runlog.jsonl").verify_chain()
    assert not ok and "hash mismatch" in msg


def test_replay_rebuilds_state(tmp_path):
    log = RunLog(tmp_path / "runlog.jsonl")
    log.append("run.created", run_id="r1", workflow="rca", target_repo="o/r")
    log.append("stage.started", stage="explore", unit="-", attempt=1, model="normal")
    log.append("stage.completed", stage="explore", unit="-", attempt=1, verdict="PASS", summary="s",
               session_url="https://x/s/1", questions=[{"id": "Q-EXP-1", "question": "?"}])
    log.append("question.answered", question_id="Q-EXP-1", answer="yes", actor="alice")
    log.append("gate.opened", gate="after-review", ref="issue/1")
    log.append("gate.decided", gate="after-review", decision="approved", actor="alice", actor_type="User")
    st = replay(log)
    assert st["stages"][0]["verdict"] == "PASS" and st["sessions"] == ["https://x/s/1"]
    assert st["open_questions"][0]["status"] == "answered"
    assert st["gates"][0]["status"] == "approved" and st["humans"] == ["alice"]


def test_trace_incremental_and_coverage(tmp_path):
    t = TraceMatrix(tmp_path / "trace.json", r"REQ-[A-Z]+-\d{3}")
    assert t.register_requirements("REQ-FLISR-001 shall x\nREQ-FLISR-002 shall y") == ["REQ-FLISR-001", "REQ-FLISR-002"]
    t.append("design", [{"requirement_id": "REQ-FLISR-001", "kind": "design", "ref": "D1"}])
    t.append("coding", [{"requirement_id": "REQ-FLISR-001", "kind": "code", "ref": "flisr.py"},
                        {"requirement_id": "REQ-FLISR-001", "kind": "test", "ref": "test_flisr.py::t1"}])
    cov = TraceMatrix(tmp_path / "trace.json", r"REQ-[A-Z]+-\d{3}").coverage()
    assert cov["test_coverage"] == 0.5 and cov["orphans"] == ["REQ-FLISR-002"]
    assert "REQ-FLISR-002" in t.to_markdown()
