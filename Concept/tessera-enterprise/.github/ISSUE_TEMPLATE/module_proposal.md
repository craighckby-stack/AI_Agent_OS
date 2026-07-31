---
name: Module proposal
about: Propose a new module for Tessera
title: "[MODULE] "
labels: module-proposal
assignees: ''
---

## Module name
A short, snake_case name (e.g. `qrcode_reader`, `pdf_text_extractor`).

## Purpose
One sentence describing what this module does. This will be in the README.md
and used by the LLM router to decide when to pick this module.

## Cluster key strategy
- [ ] `static` — always returns the same answer
- [ ] `request` — each unique phrasing gets its own slot
- [ ] `extract:image` — one slot per image filename
- [ ] `extract:url` — one slot per URL
- [ ] other (describe below)

## What real computation does this module do?
Tessera modules should do work an LLM cannot do reliably in a single call.
What does this module compute?

## Inputs
What inputs does the module expect? (Extracted from AI_AGENT_REQUEST)

## Outputs
What does the module return? (Plain text? JSON? Structured data?)

## Dependencies
What packages/system tools does this module require? (e.g. PIL, numpy, tesseract)

## Why should this be in the standard library?
Why shouldn't this be a user's custom module? What makes it broadly useful?
