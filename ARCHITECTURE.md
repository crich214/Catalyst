# Catalyst Architecture

Version: 0.2

---

# Philosophy

Catalyst is not a stock screener.

Catalyst is an AI Investment Operating System.

Every architectural decision must support one principle:

> Make it easy to add new investment intelligence without changing the core platform.

Catalyst is designed to evolve for decades.

---

# Core Principles

1. Small independent modules.

2. Every intelligence source is an Engine.

3. The Dashboard never contains business logic.

4. APIs expose information only.

5. Business logic belongs in Services.

6. Every Engine follows the same interface.

7. Every sprint must leave Catalyst in a working state.

---

# High-Level Architecture

Catalyst

├── backend
│
├── frontend
│
├── signal_engines
│
├── data
│
├── docs
│
├── scripts
│
└── tests

---

# Backend

The backend owns the business logic.

backend/

api/
FastAPI routes

services/
Business logic

models/
Data models

config/
Configuration

main.py
Application entry point

Rule:

main.py should remain extremely small.

Its job is to start the application—not perform analysis.

---

# Frontend

The frontend owns presentation only.

It should never calculate investment scores.

Its responsibilities:

• Dashboard
• Charts
• Tables
• User interaction

Nothing more.

---

# Signal Engines

The heart of Catalyst.

Every investment signal is implemented as an Engine.

Examples

Macro Engine

Valuation Engine

Quality Engine

Insider Engine

Congress Engine

Institutional Engine

Options Engine

News Engine

AI Committee

Every Engine must inherit from:

SignalEngine

Every Engine must implement:

collect()

analyze()

score()

summarize()

No exceptions.

---

# Registry

The registry discovers all Engines.

Example

Dashboard

↓

Registry

↓

Macro

↓

Valuation

↓

Quality

↓

Insider

↓

Congress

↓

AI Committee

Adding a new Engine should require:

1. Create folder.

2. Register Engine.

3. Done.

No dashboard changes.

No API changes.

---

# Services

Services perform business logic.

Examples

MarketService

ScoringService

PortfolioService

MacroService

InsiderService

CongressService

Services may call Engines.

Routes never call Engines directly.

---

# Models

Models describe data.

Examples

Opportunity

Signal

Portfolio

Holding

Company

Recommendation

Models never contain business logic.

---

# Configuration

Configuration belongs in:

backend/config

Examples

API Keys

Environment

Logging

Application Settings

No hardcoded values.

---

# Dashboard Flow

User

↓

Dashboard

↓

API

↓

Services

↓

Signal Registry

↓

Signal Engines

↓

Scoring

↓

Response

↓

Dashboard

---

# Data Flow

Market Data

↓

Normalizer

↓

Signal Engine

↓

Signal Score

↓

Composite Score

↓

AI Committee

↓

Investment Memo

---

# Testing

Every sprint must pass:

Dashboard launches.

API loads.

Signal registry loads.

Every Engine returns a valid score.

No existing feature breaks.

---

# Coding Standards

Readable over clever.

Simple over complex.

Composition over inheritance.

Small files.

Small classes.

Small functions.

Every commit must compile.

---

# Git Workflow

main

Always deployable.

feature/*

New development.

Pull Request

Required.

Merge

Only after testing.

---

# Release Philosophy

Every sprint delivers visible value.

Never leave Catalyst partially working.

Architecture evolves slowly.

Investment intelligence evolves continuously.

---

# Long-Term Goal

Catalyst should become the operating system for investment decision making.

Every future capability should plug into the existing architecture—not require rewriting it.

The architecture should make future development easier every month.

Not harder.
Raw Data
     │
     ▼
Normalized Data
     │
     ▼
Signal
     │
     ▼
Engine
     │
     ▼
Composite Score
     │
     ▼
AI Committee
     │
     ▼
Investment Thesis
     │
     ▼
Portfolio Decision