# BackDown agent rules

**Status:** active from 2026-11-14
**Repo:** `https://github.com/KA-1205/BackDown.git` (branch `main`)
**Scope:** every agent session that works in this repository.

This file governs **process**. `KARTIK.md`, `docs/SPEC.md`, and `docs/CONTRACT.md` govern **research substance**. If they conflict, the research docs win on what to build; this file wins on how agents work, sync, and hand off.

Change this file only with human approval, and commit that change like any other task.

---

## 1. Roles

| Role | Who / what | Owns | Must not do |
|---|---|---|---|
| **Orchestrator** | **BigPickle** — OpenCode model `opencode/big-pickle` (the "move" agent) | Session movement, task breakdown and handoff, skill selection, token budget, git pull/push, verification gate, escalation | Write code, analysis, figures, or report prose. Edit repo content. Resolve conflicts silently. |
| **Worker** | **GPT-6 Astra, medium** — `openai/gpt-6-astra#medium` (OpenCode alias: `opencode/gpt-6-astra#medium`) | All substantive work: planning, code, analysis, figures, docs, and report drafts | Run git write operations (no commit/push). Act as a model under test. |
| **Humans** | Harshil, Daksh, Kartik | Approve contract changes, fill human labels, review results, submit the report | — |

**Model bindings are fixed for the sprint.** BigPickle orchestrates; GPT-6 Astra (medium variant) does the work. Do not silently substitute another model or variant. If a binding must change, record the reason in the task brief and the commit body.

**Rule 1.1 — Git has one writer.** Only the orchestrator runs `git commit` and `git push`. Astra may run read-only git (`status`, `diff`, `log`, `show`). This prevents two agents racing on the index or on `main`.

**Rule 1.2 — One task, one session.** Each task runs in a fresh session. The orchestrator hands over a task brief and pointers, never a full transcript. This is the token-control mechanism.

---

## 2. Non-negotiable research rules

1. **Agents are tooling, never subjects.** No agent, including GPT-6 Astra, is a model under test or a grader. Subjects are the four models in `config/models.json`; graders are Claude Haiku, GLM 5.3 Flash, and GPT-5.6 Terra.
2. **No fabricated results or citations.** Every number must trace to a file in `results/`. Every citation must be a source a human opened.
3. **Never hand-edit `results/raw/` or `results/graded/`.** Regenerate them with `backdown/run.py` and `backdown/grade.py`. Hand edits break the data contract.
4. **Human labels are human-only.** Agents may generate blind sheets and blank CSVs; agents must never fill `results/human/labels_*.csv` scores. Blindness is part of the method.
5. **Missing is missing, not zero.** A record without a grader has no score from that grader. Do not impute, average around it, or treat it as 0.
6. **`docs/CONTRACT.md` needs approval.** Do not change any shared format without Harshil and Daksh agreeing. Record the approval in the commit body.
7. **Owners control their data.** Type A items/templates/results belong to Harshil. Type B items/templates/results belong to Daksh. Do not edit another owner's data; if it is missing, mark the task **blocked**.
8. **No invented type-B data.** If `data/items/B_fact.jsonl` or type-B raw results do not exist, the task is blocked. Do not synthesize them as if real.
9. **Keep the reference copy read-only.** `/home/kartik/hackathons/BackDown-from-zip/` is a snapshot. Do not edit it. The live repo is `/home/kartik/hackathons/BackDown/`.
10. **Secrets never enter git.** `.env` is ignored. Never print, commit, or paste API keys.

---

## 3. Git workflow (mandatory)

### 3.1 Before every task

The orchestrator runs, in order:

```bash
git -C /home/kartik/hackathons/BackDown pull --rebase
git -C /home/kartik/hackathons/BackDown status --short
```

- The tree must be clean before a task starts. If it is dirty, stop and report the stray files; do not stash, reset, or discard them.
- No task starts on a stale tree. Pull first, always.

### 3.2 After every task

1. Verify against the task's acceptance command (see §5).
2. Review the diff yourself: only files in the task's touch set may change.
3. Stage explicit paths — never a blind `git add -A`:

   ```bash
   git add <task files>
   git commit -m "Area: imperative summary"
   git push origin main
   ```

4. No task ends unpushed. If the push is rejected, run `git pull --rebase`, re-run the acceptance check, then push again.
5. If the rebase conflicts, **stop**. Do not resolve it blindly. Report the conflicted files and wait for a human.

### 3.3 Commit format

Match the existing repo style (imperative, short subject):

```
Analyze: add median-grader metrics and bootstrap CIs

Why: <one line>
What: <2-4 bullets>
Verified: <the acceptance command and its result>
```

One task = one commit. Do not bundle unrelated changes.

### 3.4 Forbidden git operations

- `git push --force` / `--force-with-lease`
- Rewriting published history (`reset --hard` on shared commits, history rewrites)
- `git commit --amend` on a commit that was already pushed
- Committing `.env`, `data/raw/`, `tests/fixtures/`, `dist/`, or `results/graded/_cache/` (they are gitignored for a reason)
- Discarding another person's uncommitted work

### 3.5 Git identity

Commits need a real identity, set **repo-locally** in `/home/kartik/hackathons/BackDown`:

```bash
git config user.name  "Kartik"
git config user.email "kartikarora.125@outlook.com"
```

The GitHub account owning `origin` is `KA-1205`; commits are authored under the email above. If the human supplies a different name, email, or GitHub ID, update both values before the next commit. Never commit under another teammate's identity (the existing history is authored by Harshil; new commits must be yours). Never invent an email.

### 3.6 Authentication

`gh` must be installed and authenticated before the orchestrator can push. There is no SSH key or credential helper, so HTTPS pushes need a credential. Accept one of:

- `gh auth login` after installing `gh` (preferred), or
- a fine-grained/classic PAT with `repo` scope supplied via the human's chosen method (never commit or echo it), or
- an SSH key registered with GitHub, with `origin` switched to the SSH URL.

The orchestrator may set up the remote and the identity, but must not push until authentication succeeds.

---

## 4. Task protocol (orchestrator ↔ Astra)

### 4.1 Task brief template

The orchestrator gives Astra only this:

```text
Task ID: <YYYY-MM-DD-NN>
Goal: <one sentence>
Touch set: <exact files/dirs Astra may create or edit>
Acceptance: <one command or checklist that proves it works>
Constraints: <research rules that apply, dependencies, budgets>
Out of scope: <what not to touch>
```

### 4.2 Flow

1. **Orchestrator:** pull, check clean tree, load only the skill(s) the task needs, write the task brief.
2. **Astra:** plan briefly, then implement and self-check against the acceptance command.
3. **Orchestrator:** review the diff against the touch set, run the acceptance command independently, then commit and push.
4. **On failure:** return to Astra with the exact error. Maximum **two** fix loops, then escalate to a human.
5. **On completion:** write a five-line handoff summary (what changed, what was verified, what is next, blockers, files touched) and close the session.

### 4.3 Stop and escalate immediately if

- a pull/rebase conflict appears;
- a task needs to change `docs/CONTRACT.md`, another owner's data, or `config/models.json`;
- the acceptance command fails twice;
- a change would touch more than ~10 files (split it instead);
- a secret or personal data appears in a diff;
- the remote or git identity is wrong;
- required data is missing (for example type B).

---

## 5. Verification gate

A task is done only when all of these hold:

- [ ] The acceptance command passes and its output is quoted in the commit body.
- [ ] The diff contains only files in the touch set.
- [ ] No hand-edits to `results/raw/` or `results/graded/`.
- [ ] No secrets, scratch files, or generated caches staged.
- [ ] Numbers in docs/report trace to a `results/` file and a reproducible command.
- [ ] Commit is pushed to `origin/main`.

Default checks for this repo:

```bash
python scripts/status.py                         # collection/grading progress
python -m backdown.analyze --in results/graded --out figures/   # once it exists
```

---

## 6. Token and skill discipline

1. **Load a skill only when its trigger matches the current task.** Never preload the whole skill library.
2. **One skill at a time** unless the task genuinely spans two domains; note why in the task brief.
3. **Read narrowly.** Use `grep` and offset reads; do not re-read files already summarized in the handoff.
4. **Keep the touch set small.** If a task needs more than ~10 files, split it.
5. **Fresh session per task.** Carry a five-line handoff, not history.
6. **Checkpoint at commit boundaries.** A pushed commit is the recovery point if a session runs long.
7. **Scratch goes in `/tmp/opencode/`.** Never commit scratch or fixtures.
8. **Prefer one strong pass over many rewrites.** Run the acceptance check before asking for review.

---

## 7. File boundaries

| Path | Owner | Agent access |
|---|---|---|
| `backdown/analyze.py`, `figures/` | Kartik (Astra implements) | Create/edit |
| `scripts/make_fake_graded.py`, `tests/fixtures/` | Kartik (Astra implements) | Create/edit (fixtures gitignored) |
| `docs/chat_app_study.md`, `results/chat_app/` | Kartik (Astra drafts) | Create/edit |
| `report/` | Kartik (Astra drafts) | Create/edit; humans review and submit |
| `results/human/labels_*.csv` | Humans | **Read only**; never fill scores |
| `results/human/sheets/`, `sample_*.csv` | Generated by `pick_label_sample.py` | Do not hand-edit |
| `data/items/A_evidence.jsonl`, `templates/A_evidence.json`, type-A results | Harshil | Do not edit |
| `data/items/B_fact.jsonl`, `templates/B_fact.json`, type-B results | Daksh | Do not edit; blocked until delivered |
| `docs/CONTRACT.md` | All three | Change only with approval |
| `config/models.json` | Harshil | Change only with approval |
| `backdown/run.py`, `backdown/grade.py`, `backdown/clients.py`, `backdown/config.py`, `backdown/io.py` | Shared harness | Edit only for a task that explicitly says so |
| `results/raw/`, `results/graded/` | Generated | **Never hand-edit** |
| `/home/kartik/hackathons/BackDown-from-zip/` | Reference snapshot | Read only |
| `rules.md` | Team | Change only with human approval |

---

## 8. Current priority queue

Ordered by `KARTIK.md`. The orchestrator works top-down unless a human reorders.

| Priority | Task | Status |
|---|---|---|
| P0 | `backdown/analyze.py` on the real 640 type-A records: median grader, metrics, bootstrap CIs, Krippendorff's alpha, figures/tables | Ready |
| P1 | Human-vs-grader comparison in `analyze.py` | Blocked on human labels |
| P1 | Fill Kartik's 36 blind labels (12 conversations) | Human-only |
| P2 | `docs/chat_app_study.md` protocol + `results/chat_app/` collation | Ready |
| P3 | Report drafts (Intro, Related Work, Methodology, Limitations appendix; Results/Discussion later) | Partly ready |
| — | Type B pipeline and results | Blocked on Daksh |

---

## 9. Definition of done for the sprint

- `python -m backdown.analyze --in results/graded --out figures/` runs clean on real data and reproduces every number in the report.
- `figures/headline.png`, `metrics_table.csv`, `metrics_table.md`, `grader_agreement.md` exist and are committed.
- Human labels are filled by humans and compared in `analyze.py`.
- The report is ≤8 pages on the official template, has a 150–250 word abstract, includes the required Limitations and Dual-Use appendix, and every citation/number is verified.
- The final PDF is in `report/`, and Harshil submits through the sprint form.
