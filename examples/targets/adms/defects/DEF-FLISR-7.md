# DEF-FLISR-7 — restoration back-fed a de-energised section

During drill 14 the restoration plan closed a tie switch that re-energised the faulted section.
Expected: the faulted section stays isolated. Observed: `plan_restoration` returned a close action
on the tie adjacent to the faulted section. Reproduce with the drill-14 savecase in `backend/tests/data`.
