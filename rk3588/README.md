# AI PACK README (Authoritative Version)

# Start Here

If you are reading this file, start here.

This folder contains a complete AI Engineering Pack for:

* OpenPilot
* Sunnypilot
* FrogPilot
* OPKR
* KisaPilot

running on:

* RK3588
* Orange Pi 5
* IMX415
* RKNN

---

# What Is This?

Think of this folder as a complete engineering school.

Normally an engineer needs:

* documentation
* architecture knowledge
* validation knowledge
* deployment knowledge

before changing code.

This AI Pack contains all of that.

Instead of teaching an engineer,

it teaches an AI.

---

# What Happens If I Put This Folder Into My Repository?

Example:

```text
my_repo/

├── selfdrive/
├── common/
├── system/
├── cereal/

└── ai/
```

Now an AI agent can read:

```text
ai/
```

before modifying code.

The AI learns:

* how camera works
* how modeld works
* how RKNN works
* how validation works
* how deployment works

before touching source code.

This dramatically reduces AI mistakes.

---

# Think Of It Like This

Normal AI:

```text
See code
↓
Guess
↓
Modify code
```

AI With This Pack:

```text
Read architecture
↓
Understand system
↓
Read validation rules
↓
Read deployment rules
↓
Modify code
↓
Validate
↓
Deploy
```

Much safer.

---

# Folder Structure

```text
ai/

camera.md
visionipc.md
modeld.md
rknn.md
validation.md
performance.md
deployment.md

references/
templates/
checklists/
examples/
diagrams/

README.md
```

---

# Read These First

Always read in this order:

```text
1. README.md

2. references/openpilot_architecture.md

3. references/rk3588.md

4. references/imx415.md

5. references/model_metadata.md

6. camera.md

7. visionipc.md

8. modeld.md

9. rknn.md

10. validation.md

11. performance.md

12. deployment.md
```

This gives the AI complete understanding.

---

# What Each File Does

## camera.md

Teaches:

```text
IMX415
RKISP
V4L2
NV12
DMA-BUF
camera geometry
warp generation
```

---

## visionipc.md

Teaches:

```text
frame transport
stream ownership
timestamps
buffer ownership
EGLImage
GPU preview path
```

---

## modeld.md

Teaches:

```text
OpenCL preprocessing

loadyuv.cl

transform.cl

tensor generation

modelV2 publishing
```

---

## rknn.md

Teaches:

```text
RKNN

NPU

Core assignment

Vision model

Policy model

validation
```

---

## validation.md

Teaches:

```text
how to prove code works
```

---

## performance.md

Teaches:

```text
how to measure speed
```

---

## deployment.md

Teaches:

```text
how to release safely
```

---

# References Folder

Contains deep knowledge.

```text
references/

rk3588.md
imx415.md
model_metadata.md
openpilot_architecture.md
```

These files explain:

```text
how everything works
```

---

# Templates Folder

Contains reusable formats.

```text
templates/
```

These tell AI:

```text
how to write reports
how to write patches
how to write deployments
```

---

# Checklists Folder

Contains:

```text
camera_checklist.md

rknn_checklist.md

validation_checklist.md

production_checklist.md
```

These tell AI:

```text
what must be verified
before saying PASS
```

---

# Examples Folder

Contains:

```text
real examples
```

Examples show:

```text
how to implement

how to validate

how to deploy
```

---

# Diagrams Folder

Contains:

```text
architecture diagrams
```

These help AI understand:

```text
how data flows
```

---

# If You Want To Start A New Project

Step 1

Place:

```text
ai/
```

inside repository.

---

Step 2

Ask AI:

```text
Read README.md

Then read every file referenced by README.md

Build a complete architecture inventory.
```

---

Step 3

Ask AI:

```text
Explain repository architecture.
```

If AI cannot explain architecture:

```text
DO NOT MODIFY CODE YET.
```

---

Step 4

Ask AI:

```text
Generate architecture_inventory.json
```

---

Step 5

Ask AI:

```text
Find camera pipeline.
```

---

Step 6

Ask AI:

```text
Find model pipeline.
```

---

Step 7

Ask AI:

```text
Find metadata.
```

---

Step 8

Ask AI:

```text
Generate implementation plan.
```

---

Step 9

Ask AI:

```text
Generate validation plan.
```

---

Step 10

Only now:

```text
modify code
```

---

# For VSCode AI Agents

When using:

* Claude Code
* ChatGPT Agent
* Cursor
* Windsurf
* Continue.dev

always do:

```text
Read README.md first.
```

Then:

```text
Read every document referenced by README.md.
```

Never skip.

---

# AI Rules

Before changing code:

Must understand:

```text
camera

visionipc

modeld

metadata

rknn

planner
```

---

Before saying PASS:

Must complete:

```text
validation

performance

stress

recovery
```

---

Before deployment:

Must verify:

```text
rollback
```

---

# Golden Rule

Never modify code first.

Always:

```text
Understand
↓
Plan
↓
Validate
↓
Implement
↓
Verify
↓
Deploy
```

Never:

```text
Implement
↓
Hope
```

---

# Special Rule For RK3588 Projects

Preferred Production Pipeline:

```text
IMX415
↓
RKISP
↓
NV12 DMA-BUF
├── VisionIPC
│      ↓
│   OpenCL
│      ↓
│   RKNN Vision Core 0
│      ↓
│   RKNN Policy Core 1
│      ↓
│   modelV2
│      ↓
│   planner
│
└── EGLImage
       ↓
    Mali GPU
       ↓
    UI Preview
```

Target:

```text
Camera → modelV2

15–30 ms

Camera → UI

20–35 ms
```

---

# Final Message To The AI

If you are an AI agent reading this:

Do not start coding.

Read:

```text
README.md
```

Then read:

```text
references/
```

Then read:

```text
core documents
```

Then read:

```text
templates
```

Then read:

```text
checklists
```

Then read:

```text
examples
```

Then read:

```text
diagrams
```

Only after understanding the entire system may you modify code.

Architecture first.

Code second.
