# Self-review register

<!-- Written by skills/self-review/scripts/self_review.py. Delete a `rejected` row to allow
     that pattern again. States: open, rejected, fixed, waiting. -->

watermark: 57ab6e0ddb74f17e55d4410056677ffcbd413ce1

| fingerprint | state | tasks | task_id | fixed_at | title | file |
|---|---|---|---|---|---|---|
| vacuous-assertion-or-noop-mutation-control | fixed | T075,T082,T083,T085,T088,T101,T105,T109 | T257 | 9f12f2510d1e963d1976fe203345981c3b1530b4 | A test assertion, guard or mutation control that cannot go RED (vacuous, no-op or decayed) ships and is only caught by a | skills/tdd/SKILL.md |
| pin-tests-collide-with-later-tasks | fixed | T064,T066,T070,T075,T082,T094,T103 | T258 | b8f8a7c5ff2532590c51354edb22c059775324e2 | Location, size or byte-identity pin tests (test_agent_guide_dedup, test_vital_slice, memory budget) break on unrelated l | templates/TASK_GUIDE_template.md |
| stale-claim-after-behaviour-change | fixed | T069,T073,T087,T095,T098,T101,T105 | T259 | bf540033abe656bb809a4ba35a72c4e46ab21312 | A change makes a pointer, comment, docstring, doc sentence or board note false, and the stale text is found only at Stag | skills/code-review/SKILL.md |
