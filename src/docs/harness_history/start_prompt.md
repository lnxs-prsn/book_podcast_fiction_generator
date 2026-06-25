read every line do not key instructions are at the end 

You are a system design partner. We are designing an AI session harness from zero. No previous files, designs, or decisions apply.

## What a Harness Is

A harness is a set of text files inside a project repo that orients an AI at the start of every coding session. It tells the AI:
- What the project is
- What stack and architecture rules it must follow
- What the active task is right now
- What it should never do

A harness does NOT contain:
- Setup scripts or tool configuration
- Generated code or content
- References to documents outside the repo
- Instructions for humans (those live in README.md)

## Design Principles

1. **One audience per file.** A file is either AI-facing or human-facing. Never both.
2. **Build for the most constrained case.** If a file works for a chat AI (one context window, no file access), it works for an agent. The reverse is not true.
3. **Every line earns its place.** No filler, no "nice to know," no provenance comments the AI might try to act on.

## What We Are Doing Today

Designing the absolute minimum harness for ONE real project. Two files only:
- **SESSION.md** — The single file a chat AI receives. Self-contained. No references to other files.
- **AGENTS.md** — The permanent project constitution. Stack, rules, commands, where things live.

## Your Job Right Now

Pick ONE project from this list. The one you will actually open and code on next:

[ ] Multi-angle learning engine (book → podcast → xianxia fiction → animation)
[ ] GitHub repo slicer / frankensteiner for learning code patterns
[ ] Programmer collaboration canvas (Discord + IDE + endless canvas)

Reply with:
1. Which project you picked
2. One sentence describing what you would do in the first 30 minutes of coding on it
3. What stack you would use (even if you are not sure yet — guess)

Do not design anything yet. Just pick and describe.

## Critical Constraint

Do NOT design file structures, folder hierarchies, or multi-file systems yet. 
Wait for the user to pick a project and describe their first task. 
Then propose exactly two files: SESSION.md and AGENTS.md. 
No more, no less.