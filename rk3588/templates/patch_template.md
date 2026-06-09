# PATCH_TEMPLATE.MD (Authoritative Version)

# Engineering Specification + Patch Generation Specification + Validation Specification + Deployment Specification + AI Agent Operating Manual

Version: 3.0

Target Platforms:

* OpenPilot
* Sunnypilot
* FrogPilot
* OPKR
* KisaPilot

Target Hardware:

* RK3588
* RK3588S
* Orange Pi 5
* Orange Pi 5 Plus

Target Runtime:

* Tinygrad
* ONNX Runtime
* RKNN

Target Camera:

* IMX415
* RKISP
* VisionIPC
* DMA-BUF
* EGLImage

---

# Section A — Patch Engineering Specification

## 1. Objective

This document defines:

* patch generation rules
* patch validation rules
* patch review rules
* deployment rules
* rollback rules
* AI agent patch workflows

Goal:

Generate safe, repeatable, production-quality code changes for OpenPilot-derived repositories.

---

## 2. Patch Philosophy

A patch is not code.

A patch is:

Architecture Understanding
↓
Code Modification
↓
Validation
↓
Performance Verification
↓
Deployment

Without validation:

Patch = Unverified Change

---

## 3. Engineering Principles

Every patch must satisfy:

Correctness

Stability

Observability

Rollback Capability

Performance

Maintainability

Safety

---

## 4. Patch Lifecycle

Repository Discovery
↓
Architecture Analysis
↓
Patch Planning
↓
Implementation
↓
Validation
↓
Performance Testing
↓
Review
↓
Deployment

---

## 5. Patch Ownership

camera.md

owns camera modifications

visionipc.md

owns transport modifications

modeld.md

owns model pipeline modifications

rknn.md

owns runtime modifications

validation.md

owns correctness

performance.md

owns benchmarking

deployment.md

owns production release

patch_template.md

owns change generation

---

## 6. Patch Categories

Category A

Camera

Category B

VisionIPC

Category C

DMA-BUF

Category D

EGLImage

Category E

OpenCL

Category F

Modeld

Category G

Metadata

Category H

RKNN

Category I

Validation

Category J

Performance

Category K

Deployment

---

## 7. Patch Safety Levels

Level 1

Documentation

Level 2

Validation Tooling

Level 3

Runtime Integration

Level 4

Pipeline Modification

Level 5

Planner Impact

Level 6

Controls Impact

Higher level requires greater review.

---

## 8. Production Safety Rule

Never modify:

planner semantics

controlsd semantics

vehicle safety logic

unless explicitly required and separately validated.

---

## 9. Architecture Preservation Rule

Maintain:

Camera Geometry

Tensor Semantics

Metadata Semantics

Message Schemas

Planner Contracts

Unless explicitly migrating versions.

---

## 10. Repository Discovery Requirement

AI agent must discover:

Processes

Messages

Models

Metadata

Camera Pipeline

Runtime

Before generating code.

Discovery first.

Always.

---

# Section B — Repository Discovery Specification

## 11. Repository Inventory

Generate:

architecture_inventory.json

Contents:

Processes

Messages

Models

Metadata

Runtime

Validation Tools

---

## 12. Camera Discovery

Discover:

Camera Driver

Sensor

Format

Buffers

VisionIPC Integration

Generate:

camera_inventory.json

---

## 13. Runtime Discovery

Discover:

Tinygrad

ONNX

RKNN

Backend Selection

Generate:

runtime_inventory.json

---

## 14. Metadata Discovery

Locate:

Metadata Files

Versions

Hashes

Generate:

metadata_inventory.json

---

## 15. Planner Discovery

Discover:

Planner Inputs

Planner Outputs

Message Dependencies

Generate:

planner_inventory.json

---

## 16. Deployment Discovery

Discover:

Build System

Release Artifacts

Validation Reports

Generate:

deployment_inventory.json

---

# Section C — Patch Planning Specification

## 17. Patch Proposal

Every patch begins with:

Objective

Scope

Risk

Validation Plan

Rollback Plan

---

## 18. Scope Definition

Patch must define:

Files Modified

Files Added

Files Removed

Files Renamed

---

## 19. Modification Matrix

For every file:

Path

Reason

Expected Outcome

Validation Method

Rollback Method

---

## 20. Risk Assessment

Low

Medium

High

Critical

Risk must be documented.

---

## 21. Rollback Assessment

Every patch requires:

Rollback Procedure

Rollback Validation

Rollback Artifacts

---

## 22. Dependency Mapping

Patch must identify:

Runtime Dependencies

Metadata Dependencies

Message Dependencies

Build Dependencies

---

## 23. Acceptance Criteria

Patch must define:

Functional Success

Performance Success

Validation Success

Deployment Success

Before implementation begins.

---

# Section D — Patch Generation Specification

## 24. Diff Generation Rule

All patches must be generated as:

Unified Diff

Example:

diff --git a/file.py b/file.py

Never provide vague modification instructions.

---

## 25. Code Generation Rule

Generate:

Minimal Change

Maximum Compatibility

Preserve Existing Behavior

---

## 26. Backward Compatibility Rule

Patch must preserve:

Tinygrad fallback

Existing workflows

Existing deployment paths

unless explicitly deprecated.

---

## 27. Configuration Rule

New features must be:

Feature-gated

Environment-variable controlled

or

Configuration controlled.

---

## 28. Logging Rule

New runtime functionality must emit:

Errors

Warnings

Performance Metrics

Validation Metrics

---

## 29. Reporting Rule

Patch must generate:

Patch Report

Validation Report

Performance Report

Deployment Report

---

## 30. Production Readiness Rule

Patch is not complete until:

Validation PASS

Performance PASS

Deployment PASS

Rollback PASS

Status:

READY FOR REVIEW
