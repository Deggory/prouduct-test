# Openpilot -> Orange Pi 5 (RK3588) AI Port Playbook

## Summary Of What Was Done In This Repo

This fork adds a full RK3588 bring-up path for running openpilot on Orange Pi 5.

Main outcomes:

1. Hardware bring-up path for RK3588 was added, including webcam/camerad integration and manager wiring.
2. `modeld` was extended with an RKNN backend for RK3588 NPU inference.
3. RK3588 model conversion and validation tools were added under `tools/rk3588`.
4. RK3588 ONNX and RKNN model artifacts were added for driving vision and policy.
5. Setup and run documentation for Orange Pi 5 was added.
6. RKNN policy fallback logic was cleaned up and preprocessing was optimized for NHWC path.
7. Submodules were vendored into the repo as regular tracked source (packaging/distribution change).

---

## How To Use This File With Copilot In Another Openpilot Fork

Place this file at the target fork root as `openrknn.md`.

Then ask Copilot Agent:

"Read openrknn.md and apply all steps end-to-end to port this fork to Orange Pi 5 RK3588. Create missing files, edit existing files, and run verification commands."

Important execution rule:

1. If commit hashes from this source fork are available, Copilot may cherry-pick them.
2. If hashes are not available in the target fork, Copilot must implement equivalent code changes manually by following the file-level instructions below.

---

## Commit-Aligned Port Steps

Apply in this exact order.

### Step 1 - RK3588 hardware bring-up and webcam path

Reference commit: `0eece5ae26812c18a6938d9d2d329eca3eaa9b1c`

Goal:

1. Add RK3588 hardware platform detection and integration.
2. Add Orange Pi webcam bring-up path for camera testing.
3. Wire platform-specific process behavior in manager/UI.
4. Preserve required build/runtime environment passthrough in `SConstruct` for RK3588 OpenCL and user-session variables.

Files to create/edit:

1. `system/hardware/__init__.py`
2. `system/hardware/rk3588/__init__.py`
3. `system/hardware/rk3588/hardware.py`
4. `system/manager/process_config.py`
5. `tools/webcam/camera.py`
6. `tools/webcam/camerad.py`
7. `tools/webcam/README.md`
8. `common/transformations/camera.py`
9. `selfdrive/ui/onroad/augmented_road_view.py`
10. `system/ui/lib/application.py`
11. `system/ui/lib/utils.py`
12. `system/ui/widgets/label.py`
13. `SConstruct`

Definition of done:

1. RK3588 platform can be selected/detected without breaking existing boards.
2. Webcam test path runs on Orange Pi 5 without import/runtime crashes.
3. `system/hardware/__init__.py` detects RK3588 from device-tree compatible string (`rockchip,rk3588`) and selects Orange Pi 5 hardware class.
4. `system/manager/process_config.py` keeps Qualcomm `camerad` disabled on RK3588 (`enabled=not WEBCAM and not RK3588`).
5. `SConstruct` preserves environment keys needed by OpenCL/user session (`HOME`, `USER`, `LOGNAME`, `XDG_RUNTIME_DIR`, `OCL_ICD_VENDORS`, `RUSTICL_ENABLE`, `MESA_LOADER_DRIVER_OVERRIDE`).
6. `SConstruct` keeps extras build gating logic (`if GetOption('extras') and arch != "larch64"`).

### Step 2 - Add RKNN backend in modeld

Reference commit: `39166735188a7d5cdc413300cf963c6887e0b2e5`

Goal:

1. Add RKNN inference backend integration into `modeld`.
2. Add compile/runtime routing for RK3588 model backend.
3. Keep tinygrad backend override contract for deterministic bring-up/debug.

Files to edit:

1. `selfdrive/modeld/modeld.py`
2. `selfdrive/modeld/helpers.py`
3. `selfdrive/modeld/compile_modeld.py`
4. `selfdrive/modeld/SConscript`

Definition of done:

1. `modeld` can select RKNN backend on RK3588.
2. Build configuration includes required RKNN path changes.
3. `selfdrive/modeld/SConscript` supports `OPENPILOT_TINYGRAD_DEV` override and OpenCL alias-copy guard (`DISABLE_JIT_ALIAS_COPY=1` when backend is `CL`).
4. `selfdrive/modeld/helpers.py` supports `OPENPILOT_TINYGRAD_IGNORE_COMPILED_FLAGS=1` to bypass compiled backend flags when needed.

### Step 3 - Add RK3588 conversion and validation tooling

Reference commit: `3484c7162d56b0b5692390671e0ff091b77ff35f`

Goal:

1. Add tools to convert, probe, and compare ONNX vs RKNN outputs.
2. Add design docs for RKNN plan and preprocessing/overlay analysis.

Files to add:

1. `tools/rk3588/convert_model_to_rknn.py`
2. `tools/rk3588/convert_onnx_opset.py`
3. `tools/rk3588/probe_rknn_model.py`
4. `tools/rk3588/compare_onnx_rknn_video.py`
5. `tools/rk3588/compare_hidden_onnx_rknn_video.py`
6. `tools/rk3588/compare_intermediate_rknn_video.py`
7. `tools/rk3588/compare_policy_intermediate_rknn_video.py`
8. `tools/rk3588/dump_model_preprocess_video.py`
9. `tools/rk3588/extract_single_node_onnx.py`
10. `tools/rk3588/rewrite_grouped_conv_to_dense.py`
11. `tools/rk3588/run_live_webcam_rknn.py`
12. `tools/rk3588/tinygrad_rk3588.patch`
13. `docs/rk3588_npu_rknn_plan.md`
14. `docs/rk3588_overlay_preprocess_analysis.md`
15. `docs/rk3588_orangepi5_porting_plan.md`

Definition of done:

1. Conversion and parity-check scripts run without syntax errors.
2. RKNN workflow docs exist and reflect actual scripts.

### Step 3A - Apply tinygrad RK3588 patch (required when tinygrad source is present)

Source artifact: `tools/rk3588/tinygrad_rk3588.patch`

Goal:

1. Apply tinygrad runtime fixes required by RK3588 OpenCL queue replay behavior.

Execution:

1. If repository uses submodules, apply patch inside `tinygrad_repo` submodule.
2. If repository is vendored, apply patch inside tracked `tinygrad_repo` directory.

Definition of done:

1. Patch applies cleanly or equivalent edits already exist.
2. Patched tinygrad files are present in the working tree or already committed.

### Step 4 - Add RK3588 model artifacts

Reference commit: `f782858deb73ef80837240cbad934c6bb00e2079`

Goal:

1. Add RK3588 ONNX and RKNN artifacts used by runtime.

Files to add/edit:

1. `selfdrive/modeld/models/driving_vision_rk3588.onnx`
2. `selfdrive/modeld/models/driving_vision_rk3588.rknn`
3. `selfdrive/modeld/models/driving_policy_rk3588.onnx`
4. `selfdrive/modeld/models/driving_policy_rk3588.rknn`
5. `.gitattributes` (LFS attributes if repo uses Git LFS)

Definition of done:

1. Runtime can resolve RK3588 artifact paths.
2. Artifact tracking strategy (LFS or regular blobs) is consistent with target fork policy.
3. If Git LFS is used, RK3588 model pulls are explicitly documented for the target fork endpoint.

### Step 5 - Add Orange Pi 5 setup runbook

Reference commit: `ab581e68942dca572af70cfaa655c1864afc0264`

Goal:

1. Add complete fresh-setup instructions for Orange Pi 5 RK3588.

File to add:

1. `docs/rk3588_orangepi5_fresh_setup_runbook.md`

### Step 6 - Add large UI run mode documentation

Reference commit: `d054a4f322ccbb80b6740b0a72a5743e9b64ee3b`

Goal:

1. Extend runbook with large UI mode instructions/tuning.

File to edit:

1. `docs/rk3588_orangepi5_fresh_setup_runbook.md`

### Step 7 - Remove policy RKNN abs limit fallback

Reference commit: `175b9ccc1127c7fbae7178bbdd0d0f6e2e152565`

Goal:

1. Remove temporary policy fallback in RKNN path.
2. Update documentation to match runtime behavior.

Files to edit:

1. `selfdrive/modeld/modeld.py`
2. `docs/rk3588_npu_rknn_plan.md`

Definition of done:

1. RKNN policy path no longer uses deprecated abs-limit fallback logic.

### Step 8 - Optimize RK3588 NHWC preprocessing path

Reference commit: `01849906d36ad55ce73c677aca13303703e49f93`

Goal:

1. Optimize preprocessing and tensor path for RK3588 NHWC flow.

Files to edit:

1. `selfdrive/modeld/modeld.py`
2. `selfdrive/modeld/helpers.py`
3. `selfdrive/modeld/compile_modeld.py`
4. `docs/rk3588_npu_rknn_plan.md`
5. `docs/rk3588_orangepi5_fresh_setup_runbook.md`

Definition of done:

1. RK3588 preprocessing route matches model input layout expectations.
2. Docs match current implementation.
3. Runtime guidance includes `MODELD_WARP_OUTPUT_LAYOUT=nhwc` and `MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc` for webcam RKNN path.

### Step 8A - Generate or restore webcam NHWC warp PKL

Goal:

1. Ensure the webcam RKNN prepare artifact exists:
   - `selfdrive/modeld/models/driving_warp_1280x720_webcam_nhwc_tinygrad.pkl`

Definition of done:

1. Warp PKL file exists and is loadable by `modeld` on target board.

### Step 8B - Add runtime environment contract

Goal:

1. Ensure docs and smoke scripts use the required environment values.

Required runtime env for Orange Pi 5 webcam RKNN smoke:

1. `USE_WEBCAM=1`
2. `OPENPILOT_MODELD_BACKEND=rknn`
3. `MODELD_WARP_OUTPUT_LAYOUT=nhwc`
4. `MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc`
5. Webcam format defaults are documented and override-ready (`WEBCAM_WIDTH`, `WEBCAM_HEIGHT`, `WEBCAM_FPS`, `WEBCAM_FOURCC`, `WEBCAM_FLIP`).

Optional tuning env:

1. `RKNN_CORE_MASK`
2. `RKNN_VISION_CORE_MASK`
3. `RKNN_POLICY_CORE_MASK`
4. `MODELD_POLICY_BACKEND` (`rknn`, `tinygrad`, or `auto`)
5. `OPENPILOT_TINYGRAD_DEV`
6. `OPENPILOT_TINYGRAD_IGNORE_COMPILED_FLAGS`
7. `OCL_ICD_VENDORS`
8. `DISABLE_JIT_ALIAS_COPY`

### Step 9 - Vendor submodules into repo (optional packaging step)

Reference commit: `9e8458054c56ebbcf4324768d1464304c208d713`

Goal:

1. Remove external submodule dependency by tracking source directly.

Changes:

1. Remove `.gitmodules` if switching fully to vendored layout.
2. Add full source trees as regular tracked directories:
   - `msgq_repo`
   - `opendbc_repo`
   - `panda`
   - `rednose_repo`
   - `teleoprtc_repo`
   - `tinygrad_repo`

Definition of done:

1. Fresh clone does not require `git submodule update --init --recursive`.

---

## Strict Step Gates And Required Commands

Use this section as hard execution policy.

Global rules:

1. Do not start Step N+1 until Step N gate passes.
2. After each step, run all listed commands and record output in the final report.
3. If any command fails, fix the code and rerun only that step's gate.
4. Commit after each passing step using message: `rk3588-stepN: <short description>`.

### Gate for Step 1

Required commands:

```bash
git checkout -b rk3588-orangepi5-port || git checkout rk3588-orangepi5-port
python3 -m py_compile system/hardware/rk3588/hardware.py tools/webcam/camera.py tools/webcam/camerad.py
python3 - <<'PY'
import importlib
importlib.import_module('system.hardware')
importlib.import_module('system.hardware.rk3588.hardware')
print('ok: rk3588 imports')
PY
grep -n "rockchip,rk3588" system/hardware/__init__.py
grep -n "enabled=not WEBCAM and not RK3588" system/manager/process_config.py
grep -n "OCL_ICD_VENDORS\|RUSTICL_ENABLE\|MESA_LOADER_DRIVER_OVERRIDE" SConstruct
grep -n "GetOption('extras') and arch != \"larch64\"" SConstruct
git diff --name-only -- system/hardware/ tools/webcam/ system/manager/ system/ui/ common/transformations/ SConstruct
```

Pass gate:

1. Compile/import commands return exit code 0.
2. Diff includes expected Step 1 paths.
3. RK3588 detection and camerad gating lines are present.
4. SConstruct env passthrough and extras gating lines are present.

### Gate for Step 2

Required commands:

```bash
python3 -m py_compile selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py
grep -nEi "rknn|rk3588" selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py selfdrive/modeld/SConscript
grep -n "OPENPILOT_TINYGRAD_DEV\|DISABLE_JIT_ALIAS_COPY\|OCL_ICD_VENDORS" selfdrive/modeld/SConscript
grep -n "OPENPILOT_TINYGRAD_IGNORE_COMPILED_FLAGS" selfdrive/modeld/helpers.py
git diff --name-only -- selfdrive/modeld/
```

Pass gate:

1. `py_compile` succeeds.
2. Search output confirms RKNN code paths exist in modeld stack.
3. Tinygrad override and ignore-compiled-flags hooks are present.

### Gate for Step 3

Required commands:

```bash
python3 -m py_compile tools/rk3588/*.py
test -f docs/rk3588_npu_rknn_plan.md && test -f docs/rk3588_overlay_preprocess_analysis.md && test -f docs/rk3588_orangepi5_porting_plan.md
if [ -d tinygrad_repo ]; then (cd tinygrad_repo && git apply --check ../tools/rk3588/tinygrad_rk3588.patch || true); fi
git diff --name-only -- tools/rk3588/ docs/rk3588_npu_rknn_plan.md docs/rk3588_overlay_preprocess_analysis.md docs/rk3588_orangepi5_porting_plan.md
```

Pass gate:

1. All tooling scripts compile.
2. All three docs exist.
3. Tinygrad patch is applicable or equivalent tinygrad changes already exist.

### Gate for Step 4

Required commands:

```bash
test -f selfdrive/modeld/models/driving_vision_rk3588.onnx
test -f selfdrive/modeld/models/driving_vision_rk3588.rknn
test -f selfdrive/modeld/models/driving_policy_rk3588.onnx
test -f selfdrive/modeld/models/driving_policy_rk3588.rknn
grep -nEi "rk3588|rknn|onnx" selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py || true
git diff --name-only -- selfdrive/modeld/models/ .gitattributes
```

Pass gate:

1. All four artifact files exist and are tracked.
2. Runtime code references are consistent with artifact names.

### Gate for Step 5

Required commands:

```bash
test -f docs/rk3588_orangepi5_fresh_setup_runbook.md
grep -nE "Orange Pi|RK3588|runbook|setup" docs/rk3588_orangepi5_fresh_setup_runbook.md
git diff --name-only -- docs/rk3588_orangepi5_fresh_setup_runbook.md
```

Pass gate:

1. Runbook file exists.
2. Runbook has concrete setup content.

### Gate for Step 6

Required commands:

```bash
grep -nE "large UI|UI mode|resolution|display" docs/rk3588_orangepi5_fresh_setup_runbook.md
git diff --name-only -- docs/rk3588_orangepi5_fresh_setup_runbook.md
```

Pass gate:

1. Large UI section exists with actionable settings.

### Gate for Step 7

Required commands:

```bash
grep -nEi "abs limit|fallback|policy" selfdrive/modeld/modeld.py docs/rk3588_npu_rknn_plan.md
python3 -m py_compile selfdrive/modeld/modeld.py
git diff --name-only -- selfdrive/modeld/modeld.py docs/rk3588_npu_rknn_plan.md
```

Pass gate:

1. Deprecated fallback logic is removed or documented as removed.
2. `modeld.py` compiles.

### Gate for Step 8

Required commands:

```bash
grep -nE "NHWC|preprocess|layout" selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py docs/rk3588_npu_rknn_plan.md docs/rk3588_orangepi5_fresh_setup_runbook.md
python3 -m py_compile selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py
test -f selfdrive/modeld/models/driving_warp_1280x720_webcam_nhwc_tinygrad.pkl || true
grep -nE "OPENPILOT_MODELD_BACKEND=rknn|MODELD_WARP_OUTPUT_LAYOUT=nhwc|MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc|USE_WEBCAM=1|WEBCAM_WIDTH|WEBCAM_HEIGHT|WEBCAM_FPS|WEBCAM_FOURCC|WEBCAM_FLIP" docs/rk3588_orangepi5_fresh_setup_runbook.md
git diff --name-only -- selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py docs/rk3588_npu_rknn_plan.md docs/rk3588_orangepi5_fresh_setup_runbook.md
```

Pass gate:

1. NHWC/preprocess updates are present in code and docs.
2. All three modeld Python files compile.
3. NHWC webcam warp PKL plan is present (existing file or documented generation path).
4. Runtime env contract for RKNN webcam mode is documented.

### Gate for Step 9 (Optional)

Required commands:

```bash
if [ -f .gitmodules ]; then echo "submodule mode active"; else echo "vendored mode active"; fi
git submodule status || true
git diff --name-only -- .gitmodules msgq_repo opendbc_repo panda rednose_repo teleoprtc_repo tinygrad_repo
```

Pass gate:

1. Chosen dependency strategy is explicit:
   - keep submodules and do not vendor, or
   - remove `.gitmodules` and vendor all required repos.
2. Final clone instructions in docs match the chosen strategy.

---

## Single Copy-Paste Gate Runner (Fail-Fast)

Use this when you want one deterministic command block instead of running each gate manually.

How to use:

1. Run from repository root.
2. Paste the entire block into a shell.
3. Optional: set `RUN_STEP9=1` to execute optional Step 9 gate.

```bash
set -euo pipefail

if [[ ! -f openrknn.md ]]; then
   echo "[FAIL] run from repo root (openrknn.md not found)"
   exit 1
fi

log() { echo "[$(date +%H:%M:%S)] $*"; }
run() {
   log "RUN: $*"
   "$@"
}
contains() {
   local file="$1"
   local pattern="$2"
   if ! grep -qE "$pattern" "$file"; then
      echo "[FAIL] pattern not found in $file: $pattern"
      exit 1
   fi
}

log "Step 0 audit evidence"
run git checkout -b rk3588-orangepi5-port || run git checkout rk3588-orangepi5-port
run mkdir -p .ai_rk3588_audit
run sh -c 'git status --porcelain > .ai_rk3588_audit/00_status_before.txt'
run sh -c 'git diff --name-only > .ai_rk3588_audit/01_changed_files_before.txt'
run sh -c 'grep -RInE "rk3588|RK3588|rknn|RKNN|orange ?pi|orangepi|modeld|NHWC|webcam" system/ selfdrive/ tools/ docs/ 2>/dev/null > .ai_rk3588_audit/02_keyword_hits.txt || true'
run sh -c 'git diff > .ai_rk3588_audit/03_backup_before_revert.patch'
run sh -c 'python3 -m py_compile selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py || true'
run sh -c 'python3 -m py_compile system/hardware/rk3588/hardware.py tools/webcam/camera.py tools/webcam/camerad.py || true'
run sh -c 'git diff --name-only > .ai_rk3588_audit/04_changed_files_after_audit.txt'
log "PASS: Step 0 audit"

log "Gate Step 1"
run python3 -m py_compile system/hardware/rk3588/hardware.py tools/webcam/camera.py tools/webcam/camerad.py
run python3 - <<'PY'
import importlib
importlib.import_module('system.hardware')
importlib.import_module('system.hardware.rk3588.hardware')
print('ok: rk3588 imports')
PY
contains system/hardware/__init__.py 'rockchip,rk3588'
contains system/manager/process_config.py 'enabled=not WEBCAM and not RK3588'
contains SConstruct 'OCL_ICD_VENDORS|RUSTICL_ENABLE|MESA_LOADER_DRIVER_OVERRIDE'
contains SConstruct 'GetOption\('\''extras'\''\) and arch != "larch64"'
run git diff --name-only -- system/hardware/ tools/webcam/ system/manager/ system/ui/ common/transformations/ SConstruct
log "PASS: Step 1"

log "Gate Step 2"
run python3 -m py_compile selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py
run grep -nEi 'rknn|rk3588' selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py selfdrive/modeld/SConscript
contains selfdrive/modeld/SConscript 'OPENPILOT_TINYGRAD_DEV|DISABLE_JIT_ALIAS_COPY|OCL_ICD_VENDORS'
contains selfdrive/modeld/helpers.py 'OPENPILOT_TINYGRAD_IGNORE_COMPILED_FLAGS'
run git diff --name-only -- selfdrive/modeld/
log "PASS: Step 2"

log "Gate Step 3"
run sh -c 'python3 -m py_compile tools/rk3588/*.py'
run test -f docs/rk3588_npu_rknn_plan.md
run test -f docs/rk3588_overlay_preprocess_analysis.md
run test -f docs/rk3588_orangepi5_porting_plan.md
if [[ -d tinygrad_repo ]]; then
   (cd tinygrad_repo && git apply --check ../tools/rk3588/tinygrad_rk3588.patch || true)
fi
run git diff --name-only -- tools/rk3588/ docs/rk3588_npu_rknn_plan.md docs/rk3588_overlay_preprocess_analysis.md docs/rk3588_orangepi5_porting_plan.md
log "PASS: Step 3"

log "Gate Step 4"
run test -f selfdrive/modeld/models/driving_vision_rk3588.onnx
run test -f selfdrive/modeld/models/driving_vision_rk3588.rknn
run test -f selfdrive/modeld/models/driving_policy_rk3588.onnx
run test -f selfdrive/modeld/models/driving_policy_rk3588.rknn
run sh -c 'grep -nEi "rk3588|rknn|onnx" selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py || true'
run git diff --name-only -- selfdrive/modeld/models/ .gitattributes
log "PASS: Step 4"

log "Gate Step 5"
run test -f docs/rk3588_orangepi5_fresh_setup_runbook.md
run grep -nE 'Orange Pi|RK3588|runbook|setup' docs/rk3588_orangepi5_fresh_setup_runbook.md
run git diff --name-only -- docs/rk3588_orangepi5_fresh_setup_runbook.md
log "PASS: Step 5"

log "Gate Step 6"
run grep -nE 'large UI|UI mode|resolution|display' docs/rk3588_orangepi5_fresh_setup_runbook.md
run git diff --name-only -- docs/rk3588_orangepi5_fresh_setup_runbook.md
log "PASS: Step 6"

log "Gate Step 7"
run grep -nEi 'abs limit|fallback|policy' selfdrive/modeld/modeld.py docs/rk3588_npu_rknn_plan.md
run python3 -m py_compile selfdrive/modeld/modeld.py
run git diff --name-only -- selfdrive/modeld/modeld.py docs/rk3588_npu_rknn_plan.md
log "PASS: Step 7"

log "Gate Step 8"
run grep -nE 'NHWC|preprocess|layout' selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py docs/rk3588_npu_rknn_plan.md docs/rk3588_orangepi5_fresh_setup_runbook.md
run python3 -m py_compile selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py
if [[ ! -f selfdrive/modeld/models/driving_warp_1280x720_webcam_nhwc_tinygrad.pkl ]]; then
   log "WARN: NHWC warp PKL missing (allowed if generation path is documented)"
fi
run grep -nE 'OPENPILOT_MODELD_BACKEND=rknn|MODELD_WARP_OUTPUT_LAYOUT=nhwc|MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc|USE_WEBCAM=1|WEBCAM_WIDTH|WEBCAM_HEIGHT|WEBCAM_FPS|WEBCAM_FOURCC|WEBCAM_FLIP' docs/rk3588_orangepi5_fresh_setup_runbook.md
run git diff --name-only -- selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py docs/rk3588_npu_rknn_plan.md docs/rk3588_orangepi5_fresh_setup_runbook.md
log "PASS: Step 8"

if [[ "${RUN_STEP9:-0}" == "1" ]]; then
   log "Gate Step 9 (optional)"
   if [[ -f .gitmodules ]]; then echo 'submodule mode active'; else echo 'vendored mode active'; fi
   git submodule status || true
   run git diff --name-only -- .gitmodules msgq_repo opendbc_repo panda rednose_repo teleoprtc_repo tinygrad_repo
   log "PASS: Step 9"
else
   log "SKIP: Step 9 (set RUN_STEP9=1 to enable)"
fi

log "ALL REQUIRED GATES PASSED"
```

---

## Adaptive Repo Analysis And Correction Policy

Use this policy before Step 1 so the agent can work with repos where users already attempted an Orange Pi 5 port.

### Objectives

1. Detect what the target repo already changed for RK3588/Orange Pi 5.
2. Keep valid user changes.
3. Revert only invalid/conflicting changes in RK3588-related areas.
4. Continue with missing steps from this playbook.

### Step 0 - Audit Before Applying Changes

Required commands:

```bash
git checkout -b rk3588-orangepi5-port || git checkout rk3588-orangepi5-port
mkdir -p .ai_rk3588_audit
git status --porcelain > .ai_rk3588_audit/00_status_before.txt
git diff --name-only > .ai_rk3588_audit/01_changed_files_before.txt
grep -RInE "rk3588|RK3588|rknn|RKNN|orange ?pi|orangepi|modeld|NHWC|webcam" \
  system/ selfdrive/ tools/ docs/ 2>/dev/null > .ai_rk3588_audit/02_keyword_hits.txt || true
```

Audit result classification:

1. Good change:
   - aligns with this playbook goals,
   - compiles/tests pass for the touched area,
   - does not break expected runtime path.
2. Wrong change:
   - breaks compile/import checks,
   - conflicts with required RKNN/NHWC path,
   - introduces incompatible naming/paths for required artifacts,
   - removes required hardware/process wiring.
3. Unknown change:
   - cannot be validated quickly; treat as keep-by-default and flag in report.

### Safety Rule Before Reverting

Never hard reset the repository.

Before any revert of user code, create a backup patch:

```bash
git diff > .ai_rk3588_audit/03_backup_before_revert.patch
```

Then only revert specific files judged wrong:

```bash
git restore -- <path1> <path2>
```

Do not revert files outside RK3588 port scope unless they directly break the port.

### What To Keep vs Revert

Keep as-is if all checks pass:

1. Existing `system/hardware/rk3588/` implementation that imports cleanly.
2. Existing `modeld` RKNN backend logic that compiles and resolves expected model paths.
3. Existing NHWC preprocessing optimizations consistent with docs.
4. Existing Orange Pi 5 runbook sections with actionable commands.

Revert and replace if failing checks:

1. `modeld` logic that fails `py_compile`.
2. Artifact path references that do not match actual model files.
3. Hardware/process wiring that prevents platform detection/import.
4. Conflicting fallback logic that contradicts Step 7 and Step 8 targets.

### Mandatory Audit Gate

Do not continue to Step 1 until this gate passes.

Required commands:

```bash
python3 -m py_compile selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py || true
python3 -m py_compile system/hardware/rk3588/hardware.py tools/webcam/camera.py tools/webcam/camerad.py || true
git diff --name-only > .ai_rk3588_audit/04_changed_files_after_audit.txt
```

Pass gate:

1. Agent produced `.ai_rk3588_audit/` evidence files.
2. All intentionally reverted files are listed in final report with reason.
3. Remaining good user changes are preserved.

---

## Copilot Execution Script (Recommended)

When Copilot applies this in another fork, it should execute this workflow:

1. Compare target tree to this playbook and create a branch `rk3588-orangepi5-port`.
2. Run Step 0 audit and classify existing RK3588 changes as good/wrong/unknown.
3. Keep good changes, revert wrong scoped files with backup patch, and report unknown items.
4. Apply Steps 1-8 plus Step 3A, Step 8A, and Step 8B for missing or corrected work.
5. Apply Step 9 only if the target project wants vendored dependencies.
6. Run static checks and minimal runtime checks listed below.
7. Produce a final report with:
   - files changed
   - files reverted and why
   - files preserved from user work
   - unresolved TODOs
   - exact verification command outputs

---

## Verification Checklist

Run and record output:

1. `python3 -m py_compile selfdrive/modeld/modeld.py selfdrive/modeld/helpers.py selfdrive/modeld/compile_modeld.py`
2. `python3 -m py_compile tools/rk3588/*.py` (if tools added)
3. `git diff --name-only -- docs/ selfdrive/modeld/ system/hardware/ tools/rk3588/`
4. Platform smoke checks:
   - RK3588 hardware import path loads.
   - modeld chooses RKNN backend on RK3588.
   - webcam/camera test utilities start.
5. Runtime env smoke check (documented and executable):
   - `USE_WEBCAM=1`
   - `OPENPILOT_MODELD_BACKEND=rknn`
   - `MODELD_WARP_OUTPUT_LAYOUT=nhwc`
   - `MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc`

If a check fails, fix code and rerun until all checks pass.

---

## Notes For Upstream Sync

This fork is ahead by 9 RK3588-focused commits and behind upstream by many commits.
When porting to a newer upstream state, rebase logically in this order:

1. hardware bring-up
2. modeld RKNN backend
3. tooling/docs
4. artifacts
5. preprocessing/fallback cleanup
6. packaging choice (submodule vs vendored)

This order minimizes conflict risk in `modeld` and platform wiring.

---

## What Changed By Folder And How Orange Pi 5 Runs

This section explains what each modified area does in runtime terms.

### Platform and hardware identity

1. `system/hardware/__init__.py`
   - Detects RK3588/Orange Pi 5 from device-tree strings.
   - Selects `Rk3588()` hardware class instead of comma device classes.
2. `system/hardware/rk3588/hardware.py`
   - Adds thermal zone mapping for RK3588 sensors.
3. `system/manager/process_config.py`
   - Prevents Qualcomm `camerad` path on RK3588.
   - Keeps webcam bring-up path active for Orange Pi 5 bench usage.

### Camera and UI path

1. `tools/webcam/camera.py`, `tools/webcam/camerad.py`, `tools/webcam/README.md`
   - Adds robust webcam pipeline with env-configurable resolution/fps/fourcc/flip.
2. `common/transformations/camera.py`
   - Injects webcam camera config from env values.
3. `selfdrive/ui/onroad/augmented_road_view.py`, `system/ui/lib/application.py`, `system/ui/lib/utils.py`, `system/ui/widgets/label.py`
   - UI/render fixes for this platform and desktop-based bring-up.

### Model path and acceleration

1. `selfdrive/modeld/modeld.py`
   - Adds RKNN runtime loading and inference path.
   - Adds policy backend mode (`rknn`, `tinygrad`, `auto`).
   - Adds runtime env controls for RKNN model paths, core masks, and layouts.
2. `selfdrive/modeld/compile_modeld.py`
   - Adds NHWC preprocessing path and output layout controls for RKNN webcam flow.
3. `selfdrive/modeld/helpers.py`
   - Adds compiled backend env loading and webcam NV12 handling.
4. `selfdrive/modeld/SConscript`
   - Adds tinygrad backend override controls and OpenCL safety flags.

### Tools, artifacts, docs

1. `tools/rk3588/*`
   - ONNX->RKNN conversion, probing, and parity-check tooling.
2. `selfdrive/modeld/models/*rk3588*`
   - RK3588 ONNX and RKNN artifacts for vision and policy models.
3. `docs/rk3588_*`
   - Setup/runbook, performance notes, and porting analysis.

### Packaging

1. `9e8458054` vendored submodule sources into repo.
2. This removes hard dependency on recursive submodule init for clone/build.

---

## CPU, GPU, NPU Responsibilities In This Port

### CPU

1. Process orchestration, messaging, model output parsing, and control-loop plumbing.
2. Fallback compute path when policy backend is tinygrad/CPU.
3. Host-side memory movement and part of preprocessing overhead.

### GPU (OpenCL through tinygrad)

1. Used by tinygrad preprocessing/graph execution paths when OpenCL backend is active.
2. Tinygrad patch and env guards reduce problematic queue replay/alias-copy behavior.

### NPU (RKNN)

1. Runs `driving_vision_rk3588.rknn` and `driving_policy_rk3588.rknn` when RKNN backend is selected.
2. Core-mask env values steer NPU core use.

---

## ONNX vs RKNN In Runtime

1. ONNX is used as source/intermediate format and for some tinygrad/fallback/tool flows.
2. RKNN is the target runtime format for Orange Pi 5 NPU inference path.
3. In RKNN mode, vision and policy inference are expected to run on RKNN, with optional tinygrad fallback depending on policy backend mode.

---

## Tinygrad RK3588 Patch (What It Is)

Patch file: `tools/rk3588/tinygrad_rk3588.patch`

Purpose:

1. Adjust tinygrad OpenCL/JIT behavior used in this pipeline for RK3588 stability.
2. Reduce queue replay and alias-copy issues seen during preprocessing path execution.
3. Keep preprocessing behavior consistent with RKNN-oriented runtime expectations.

---

## Performance Numbers Recorded In This Repo

These values come from repo docs and validation notes in this fork.

1. Raw RKNN probes (standalone):
   - vision: about `0.028 s`
   - policy: about `0.0043 s`
   - combined: about `0.032 s`
2. Live webcam RKNN run (reported):
   - average model execution: about `0.083 s`
   - median: about `0.078 s`
   - effective publish rate: about `5.0 FPS`
3. Earlier CPU tinygrad baseline in same docs: about `1.0 s` per inference.

Interpretation:

1. RKNN path is clearly faster than the earlier CPU-only path in this fork.
2. It is not yet a strict proof against comma device speed without controlled apples-to-apples replay.

---

## Strict Apples-To-Apples Benchmark Plan

Use this plan to compare Orange Pi 5 and comma device fairly.

### Fairness rules (must follow)

1. Same git commit on both devices.
2. Same model artifacts revision and metadata files.
3. Same replay input segment and frame window.
4. Same process replay script and python version as much as possible.
5. No background heavy jobs during benchmark.
6. Capture full command output and environment for each run.

### Metrics to compare

1. `modelV2.modelExecutionTime` max and average.
2. `driverStateV2.modelExecutionTime` max and average (optional but recommended).
3. Stability indicators: crashes/timeouts/replay failures.

### Benchmark modes

1. Mode A (common path):
   - run both devices with tinygrad backend.
   - answers: raw platform compute difference under same backend family.
2. Mode B (best practical path):
   - Orange Pi 5: RKNN backend.
   - comma device: its normal optimized backend path.
   - answers: practical real-world per-platform throughput.

### Commands: prepare both devices

Run on both devices:

```bash
cd /path/to/openpilot
git fetch --all --tags
git checkout <same_commit_hash>

python3 --version
uname -a

mkdir -p /tmp/openpilot_bench
env | sort > /tmp/openpilot_bench/env.before.txt
```

### Commands: Mode A (tinygrad on both)

Run on both devices:

```bash
cd /path/to/openpilot

env -u DEBUG \
  OPENPILOT_MODELD_BACKEND=tinygrad \
  OPENPILOT_TINYGRAD_IGNORE_COMPILED_FLAGS=1 \
  python3 selfdrive/test/process_replay/model_replay.py \
  | tee /tmp/openpilot_bench/model_replay_modeA.log
```

Extract summary row from output table:

```bash
grep -n "modelV2\|driverStateV2\|Model Timing" /tmp/openpilot_bench/model_replay_modeA.log \
  > /tmp/openpilot_bench/model_replay_modeA.summary.txt
cat /tmp/openpilot_bench/model_replay_modeA.summary.txt
```

### Commands: Mode B (best practical path)

Run on Orange Pi 5:

```bash
cd /path/to/openpilot

env -u DEBUG \
  OPENPILOT_MODELD_BACKEND=rknn \
  MODELD_POLICY_BACKEND=auto \
  MODELD_WARP_OUTPUT_LAYOUT=nhwc \
  MODELD_VISION_RKNN_INPUT_LAYOUT=nhwc \
  python3 selfdrive/test/process_replay/model_replay.py \
  | tee /tmp/openpilot_bench/model_replay_modeB_pi.log
```

Run on comma device:

```bash
cd /path/to/openpilot

env -u DEBUG \
  python3 selfdrive/test/process_replay/model_replay.py \
  | tee /tmp/openpilot_bench/model_replay_modeB_comma.log
```

Extract summary rows:

```bash
grep -n "modelV2\|driverStateV2\|Model Timing" /tmp/openpilot_bench/model_replay_modeB_*.log \
  > /tmp/openpilot_bench/model_replay_modeB.summary.txt
cat /tmp/openpilot_bench/model_replay_modeB.summary.txt
```

### Optional: structured parse from logs

Run on each device for each mode log file:

```bash
python3 - <<'PY'
import re, json, pathlib
log = pathlib.Path('/tmp/openpilot_bench/model_replay_modeA.log').read_text(errors='ignore')
rows = []
for line in log.splitlines():
  if 'modelV2' in line or 'driverStateV2' in line:
    cols = [c.strip() for c in line.split('|') if c.strip()]
    if len(cols) >= 6 and cols[0] in ('modelV2','driverStateV2'):
      rows.append({
        'model': cols[0],
        'max_instant': cols[1],
        'max_allowed': cols[2],
        'avg': cols[3],
        'avg_allowed': cols[4],
        'result': cols[5],
      })
print(json.dumps(rows, indent=2))
PY
```

### How to conclude fairly

1. Compare Mode A first to isolate hardware/platform difference with same backend family.
2. Compare Mode B second to evaluate practical deployment speed per platform.
3. Do not claim "faster than comma" unless both modes and logs are archived and reproducible.