# Building TrueVector with a Coding Agent — A Primer for Nate

Welcome, Nate. You know computers well, but you haven't built software with an AI coding agent before. This guide gets you from zero to confidently steering an agent to build your thermal-analysis report system. You don't need to learn to code. You need to learn to *direct*.

Read this once start to finish (about 20 minutes), then keep it open as a reference for your first few sessions.

---

## 1. GitHub in five minutes

GitHub is two things at once: a **filing cabinet with perfect memory** for your project's files, and a **shared workspace** where you and David (and an agent) coordinate. Here are the only concepts you need at first.

A **repository** ("repo") is the project folder — everything for TrueVector lives in one. Yours has code, documentation, and a sample inspection.

A **commit** is a saved snapshot with a short note describing what changed. Think of it like hitting "save" but with a labeled history you can scroll back through forever. Nothing is ever truly lost once committed, which is why git is safe to experiment in.

**History** is the full list of commits. This matters more than it sounds: anything ever committed stays visible in history. (That's exactly why we recently had to scrub a client's address and your cert number out of this repo — deleting them in a new commit wasn't enough, because old commits still showed them. More on that in the Guardrails section.)

A **branch** is a parallel copy where you can try changes without disturbing the working version. The main branch is called `main`. Agents often work on a branch, you review, then "merge" it into `main`.

A **pull request** ("PR") is a proposal to merge a branch's changes, with a side-by-side view of exactly what's different. It's your review checkpoint — the moment you look at what the agent did before it becomes official.

An **issue** is a written note for a task, decision, or question. Your repo already has nine of them (see `docs/Issues.md`), grouped into "Phase 0" and "Phase 1" milestones with labels like `mvp`, `template`, and `question`. Issues are where the *why* of the project lives, so decisions don't get lost in chat.

**Public vs private** is about who can read it. Your code repo is public (anyone can see it). Your business documents and real client data are *not* in it — they belong in a private location and in Google Drive. Keeping that line clean is your job, and the agent's.

That's enough GitHub to start. You'll pick up the rest by doing.

---

## 2. What "vibe coding" actually is

"Vibe coding" means you describe what you want in plain English, and the agent writes the actual code. You stay in the role of the **director and the domain expert** — you know what a good roof-inspection report looks like; the agent knows Python. You meet in the middle through conversation.

What this changes for you: you don't memorize syntax, you don't fight with tools, and you can build a real, working system by describing outcomes and reviewing results. What it does *not* change: you are still responsible for what gets built. The agent is fast and capable but not infallible — it will occasionally misunderstand, over-build, or confidently do the wrong thing. Your judgment is the safety net.

A useful mental model: the agent is a talented junior developer who works incredibly fast, never gets tired, has read everything, but has no idea what your business actually needs unless you tell it — and will sometimes guess wrong rather than ask. Your value is taste, context, and review.

---

## 3. The core loop

Almost everything you do with an agent follows the same rhythm:

1. **Describe** the outcome you want, with enough context that the agent isn't guessing.
2. **Ask for a plan** before any big change — "tell me how you'd approach this before writing code." This catches misunderstandings while they're cheap.
3. **Let it build**, in the smallest useful chunk.
4. **Review** what it produced. Ask it to explain anything you don't follow.
5. **Iterate** — "good, but the findings table should come before the photos."

The single most important habit: **small steps, reviewed often.** One change, look at it, then the next. A long unattended run that touches twenty files is hard to review and easy to regret. Short loops keep you in control.

---

## 4. How to talk to an agent well

The quality of what you get out is mostly about the quality of what you put in. A few principles, with examples drawn from your project.

**Give context, not just commands.** The agent can read your repo, so point it at the truth. Weak: "make a report generator." Strong: "Read `docs/product/mvp-spec.md` and `docs/product/data-format.md`, then build the `generate-report` command described in issue #5. It should read `inspection.yaml`, validate it, and produce a `.docx` from the template."

**Be concrete about done.** Your issues already contain acceptance criteria — use them. "It's done when it loads the sample fixture, renders the template, and prints a clear error if an image is missing" beats "make it work."

**One thing at a time.** Don't ask for the schema, the renderer, and PDF export in one breath. Do the schema, review it, then the renderer. Each becomes a clean, reviewable step.

**Ask it to explain itself.** "Why did you choose that library?" or "walk me through what this does in plain English." A good agent will explain at whatever level you ask. This is how you learn the system you're building.

**Ask for verification.** "Add a test that proves a duplicate anomaly ID gets rejected." "Generate a report from the sample and show me the output." Don't take "it works" on faith — ask the agent to *show* you it works.

**When it goes sideways, shrink the step.** If the agent is thrashing or the result is wrong, don't pile on more instructions. Back up: "undo that, and let's do just the first part."

---

## 5. Guardrails that matter for *this* project

These are the few rules that protect you and your clients. Internalize them before your first real session.

**Real client data never goes in the public repo.** Names, addresses, contact info, cert numbers, and actual thermal imagery stay in Google Drive and your private documents. The repo gets only *synthetic* sample data (we replaced the real example with a fake one: `123 Example Ave`, `redacted@example.com`). If you ever find yourself pasting a real inspection into the agent while working in the public repo, stop.

**Secrets stay out of code.** Passwords, API keys, and tokens never get typed into files that get committed. If an agent suggests putting a key in the code, that's your cue to say "use an environment variable instead."

**Review before you commit and push.** The agent can change files instantly, but *you* decide what becomes part of the project. Read the diff (the PR view makes this easy). If you don't understand a change, ask before accepting it.

**Remember history is forever.** Because anything committed stays in history, a leaked secret or client record isn't fixed by deleting it later — it has to be purged from history, which is painful. The cheap fix is to never let it in. When in doubt, ask the agent: "is there anything sensitive in what we're about to commit?"

**Keep the boundary clean.** Code and automation in the public repo; business docs in private; real inspections and images in Drive. The full map is in `docs/repository-structure.md`. When you ask the agent to add something, a fair question is "which of the three places does this belong?"

---

## 6. The decisions you'll actually have to make

The agent will build whatever you decide — but *you* have to decide. These are the real choices ahead, most already captured as issues. None require coding knowledge; they require your domain judgment.

**The data format.** What fields must every inspection have, and what's optional? How strict should validation be — should a missing photo stop the report, or just warn? (Issues #4, and the rules in `mvp-spec.md`.) You're the one who knows what a report can't ship without.

**The template.** You own the report's look and content. The big technical decision baked in: the template avoids fragile features like text boxes so the agent's renderer can fill it reliably, and so you can restyle it later without touching code (issue #3). Decide what sections every report needs and in what order.

**PDF export.** The whole reason this project exists is that print-to-PDF produced broken, unsearchable reports. The decision is to use a real export path and verify the text is actually searchable (issues #1 and #6). Hold the line on this — it's the original problem.

**The certification badge.** A live decision waiting on you: was the ITC Level II cert renewed? That answer determines whether the badge stays, gets updated, or comes off (issue #2). This is a domain call only you can make.

**Big reports.** Decide whether large inspections (25+ anomalies) need section/quadrant overview pages, or whether a findings table is enough for the MVP (issue #8). You know how clients actually read these.

**Scope — now vs later.** The MVP is deliberately small: local report generation, nothing more. Things like an annotation UI, a project database, and re-scan comparison are *intentionally* later. When the agent (or your own excitement) wants to build ahead, the discipline is to ask "does the MVP need this?" Shipping the small thing first is the strategy, not a limitation.

**When to loop in David.** He's product direction and implementation coordination; you're domain expert and acceptance reviewer. Anything that changes report structure, client-facing terminology, or scope is worth a written note (an issue comment) so the decision is on record, not just in your head.

---

## 7. Your first session, step by step

Do this once and the rest stops feeling abstract. Open the repo in your coding agent and try these in order:

1. **Orient.** "Read the README and the files in `docs/`, then explain in plain English what this project does and what state it's in." This teaches you the repo and tests that the agent understands it.
2. **Look around safely.** "List the files in this repo and tell me what each top-level folder is for." Pure reading, no changes — a gentle start.
3. **Make it run.** "Using the spec in `docs/product/mvp-spec.md` and the sample in `examples/`, generate a report from the sample inspection and show me the result." If the generator doesn't exist yet, this naturally becomes: "let's build it — start with a plan."
4. **Make one small change.** Pick something tiny and visible, like changing a heading in the template, and ask the agent to do just that. Review the diff.
5. **Save it.** "Commit this with a clear message explaining what changed." Watch how a commit works.
6. **Reflect.** "Summarize what we just did and what would be a sensible next step." 

By the end you'll have read the repo, run the tool, made and saved a change, and seen the full loop. That's the whole job, scaled up from here.

---

## 8. When something goes wrong

You can't break anything permanently — that's the point of version control, so experiment freely.

If the agent's output is wrong, say so plainly and specifically: "that's not right — the area total should be the sum of the anomalies, not a fixed number." If it's thrashing, stop and shrink the task. If a change made things worse, ask "undo your last change" — and because everything is in git, you can always return to a known-good commit. If you're lost, ask the agent: "explain what state we're in and what the options are." Confusion is normal and the agent is a patient guide; there's no such thing as a dumb question to it.

---

## 9. Mini-glossary

- **Repo:** the project folder, with full history.
- **Commit:** a saved, labeled snapshot of changes.
- **Branch:** a safe parallel copy for trying things.
- **Pull request (PR):** a reviewable proposal to merge changes.
- **Merge:** accepting a branch's changes into `main`.
- **Diff:** the highlighted before/after of a change.
- **Issue:** a written task, decision, or question.
- **Milestone:** a group of issues toward a goal (e.g. "Phase 1").
- **Fixture / sample:** fake data used to test the system safely.
- **Schema / validation:** the rules that define a correct `inspection.yaml`.
- **Environment variable:** a setting kept outside the code, used for secrets.

---

## 10. A pocket set of prompts

Keep these handy until they're second nature:

- "Before you write any code, explain your plan."
- "Do just the first step, then stop so I can review."
- "Explain this change in plain English."
- "Add a test that proves this works, and show me it passing."
- "Is there anything sensitive in what we're about to commit?"
- "Which belongs where — public repo, private docs, or Drive?"
- "Undo your last change."
- "Summarize what we did and suggest the next sensible step."

You've got this. Start with section 7, take small steps, review often, and let the agent carry the typing while you carry the judgment.
