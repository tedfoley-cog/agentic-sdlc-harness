# DEF-FLISR-7 — restoration back-fed a de-energised section

During drill 14 the restoration plan closed a tie switch that re-energised the faulted section.
Expected: the faulted section stays isolated. Observed: `build_plan (via POST /flisr/plan)` returned a close action
on the tie adjacent to the faulted section. The drill-14 savecase was not retained; reproduce on the shipped FDR-1201 model (fault on SEC-1201-04, lockout CB-1201, tie TIE-1201-1405), which stands in for drill 14.
