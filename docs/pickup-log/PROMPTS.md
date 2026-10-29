# Prompts for the ticket sessions

Start each as a new session on `joosphotos/Maple-Classic-Exp-Overlay`, branch `main`. Paste the prompt as is.
Where things stand: `STATUS.md`. **Wave 1 (PL-01, PL-02, PL-03) is done and merged.**
Sessions in the same wave can run at the same time. Merge a wave's pull requests before starting the next.

## Wave 1 (all at once): done

### PL-01 Cloud test bench
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"). Then do docs/pickup-log/tickets/PL-01.md exactly. No private recordings are needed. When done, fill in the ticket's Results section and open a pull request into main. Ask me only for owner decisions the ticket names.
```

### PL-02 Truth and message catalogue (Mac)
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"). Then do docs/pickup-log/tickets/PL-02.md exactly. Attach the private repo joosphotos/maple-captures with push access, clone it and set MAPLE_CAPTURES to its folder; truth files and contact sheets go there, never into the public repo. You can view images: transcribe every line yourself from the contact sheets. Before you finish, show me two contact sheets with your transcription so I can spot-check. Then fill in the ticket's Results section, push the truth to maple-captures and open a pull request into main.
```

### PL-03 Item list
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"). Then do docs/pickup-log/tickets/PL-03.md exactly. It needs meowdb.com: check its terms first, and if you can't reach it, stop and tell me rather than inventing names. No private recordings are needed. When done, fill in the ticket's Results section and open a pull request into main.
```

## Wave 2

### PL-04 Font (after PL-02 is merged)
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"). Then do docs/pickup-log/tickets/PL-04.md exactly. First check that PL-02's Results are filled in on main; if not, stop and tell me. Attach the private repo joosphotos/maple-captures (read only), clone it and set MAPLE_CAPTURES to its folder; never commit pictures or crops to the public repo. Read docs/pickup-log/CATALOGUE.md and PL-02's Results first. When done, fill in the ticket's Results section and open a pull request into main.
```

## Wave 3 (at the same time)

### PL-02b Windows truth (after your Windows recordings are in maple-captures)
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md, docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"), docs/pickup-log/RECORDING.md and docs/pickup-log/CATALOGUE.md. Then do docs/pickup-log/tickets/PL-02b.md exactly. Attach the private repo joosphotos/maple-captures with push access, clone it and set MAPLE_CAPTURES to its folder; captures/NOTES.md says what each new recording is. Use tools/pickup_label.py from PL-02. Show me two contact sheets with your transcription before you finish. Then fill in the ticket's Results section, push the truth to maple-captures and open a pull request into main.
```

### PL-05 Synthetic logs (after PL-04 is merged)
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"). Then do docs/pickup-log/tickets/PL-05.md exactly. First check that PL-04's Results are filled in on main; if not, stop and tell me. Attach the private repo joosphotos/maple-captures (read only), clone it and set MAPLE_CAPTURES to its folder, for the realism check and real scenes; tests must also run without it. Never commit pictures to the public repo. When done, fill in the ticket's Results section and open a pull request into main.
```

### PL-07 Reading a line (after PL-04 and PL-03 are merged)
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"), then docs/pickup-log/CATALOGUE.md and the Results of PL-02, PL-03 and PL-04. Then do docs/pickup-log/tickets/PL-07.md exactly. First check those three tickets' Results are filled in on main; if not, stop and tell me. Attach the private repo joosphotos/maple-captures (read only), clone it and set MAPLE_CAPTURES to its folder. Zero wrong readings is the hard rule: when in doubt, return None with the reason. When done, fill in the ticket's Results section and open a pull request into main.
```

## Wave 4 (at the same time)

### PL-06 Finding the log (after PL-04 and PL-02b are merged)
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"), then docs/pickup-log/CATALOGUE.md and the Results of PL-02, PL-02b and PL-04. Then do docs/pickup-log/tickets/PL-06.md exactly. First check those tickets' Results are filled in on main; if not, stop and tell me. Attach the private repo joosphotos/maple-captures (read only), clone it and set MAPLE_CAPTURES to its folder. A wrong anchor is worse than none. When done, fill in the ticket's Results section and open a pull request into main.
```

### PL-08 Following the stack (after PL-05 is merged)
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"), then the Results of PL-02, PL-04 and PL-05. Then do docs/pickup-log/tickets/PL-08.md exactly. First check those tickets' Results are filled in on main; if not, stop and tell me. Attach the private repo joosphotos/maple-captures (read only), clone it and set MAPLE_CAPTURES to its folder. This is the hardest ticket: never report a confident wrong count; when it can't be told, report a gap. Take the time to get every synthetic suite to 100% before finishing. When done, fill in the ticket's Results section and open a pull request into main.
```

## Wave 5

### PL-09 The 100% gate (after PL-06, PL-07 and PL-08 are merged)
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"), then the Results of every PL ticket so far. Then do docs/pickup-log/tickets/PL-09.md exactly. First check that PL-06, PL-07 and PL-08 are merged on main; if not, stop and tell me. Attach the private repo joosphotos/maple-captures (read only), clone it and set MAPLE_CAPTURES to its folder. Report the numbers honestly in GATE.md, failures included; fix only small things inside the parts and write follow-up tickets for the rest. When done, fill in the ticket's Results section, open a pull request into main and give me GATE.md's summary to accept or reject.
```

## Wave 6

### PL-10 Live in shadow mode (after you accept the gate and PL-01 is merged)
```
Read CLAUDE.md, docs/CODEBASE.md (especially "The reading pipeline" and shadow mode), docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"), then docs/pickup-log/GATE.md and the Results of PL-01 and PL-09. Then do docs/pickup-log/tickets/PL-10.md exactly. First check that GATE.md is accepted (I said so on PL-09's pull request) and PL-01 is merged; if not, stop and tell me. Set up the Linux test bench as CLAUDE.md says (from PL-01). Nothing the player sees may change, and nothing new goes online. When done, fill in the ticket's Results section (including how I try it on Windows and the Mac) and open a pull request into main.
```

## Wave 7

### PL-11 Health report and release (after PL-10 is merged and you've tried it)
```
Read CLAUDE.md, docs/CODEBASE.md (especially "Kept in sync by hand"), docs/pickup-log/PLAN.md and docs/pickup-log/TICKETS.md (the parts "How a ticket session works" and "Done when"), then the Results of PL-10. Then do docs/pickup-log/tickets/PL-11.md exactly. Step 1 is an owner decision: propose the health report fields to me and wait for my answer before building anything. Counts only, never item names, amounts or pictures. When done, fill in the ticket's Results section (with the release checklist) and open a pull request into main. Don't deploy, tag or release; that's mine.
```

## After release

### YOU-2 Field trial review (after a few days of health reports)
```
Read CLAUDE.md, docs/CODEBASE.md, docs/pickup-log/PLAN.md, docs/pickup-log/GATE.md and the Results of PL-10 and PL-11. I'll paste the output of server/tools/health_summary.mjs for the pickup log fields. Tell me, with the numbers: is the reader at 0 wrong lines and counting every line in the field, how often there are gaps and why, how the EXP check comes out, and its CPU cost. Then recommend what can go live (mesos/hr from the log, a loot tracker, kills) and what must be fixed first, and write those as new ticket files in docs/pickup-log/tickets/ in the same format. Open a pull request into main.
```
