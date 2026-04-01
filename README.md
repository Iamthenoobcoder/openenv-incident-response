---
title: Incident Response AI
emoji: 🚨
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
tags:
  - openenv
  - devops
  - sre
  - reinforcement-learning
  - cloud-infrastructure
---

# 🚨 Incident Response AI — OpenEnv Environment

**🟢 Live Simulation:** [Play the Agent Dashboard on Hugging Face Spaces](https://huggingface.co/spaces/yajd19/openenv-incident)

A realistic simulation of a DevOps/SRE engineer's complete incident response workflow.
A single intelligent agent plays all four operational roles — **Detection, Investigation,
Resolution, and Customer Communication** — across three cloud infrastructure incidents
with cascading failures and customer ticket pressure.

---

## 1. Environment Description & Motivation

Real SRE teams at companies like Google, Stripe, and Amazon follow this exact four-step
playbook when incidents occur. This environment trains and evaluates agents on the same
workflow: detecting anomalies from logs and metrics, diagnosing root causes, applying
precise fixes, and managing customer communication — all under time pressure.

The motivation is to provide a safe, reproducible, and challenging environment for training
AI agents to handle complex, multi-service infrastructure failures that humans actually do.

**What makes it hard:**
- **Cascade Penalties**: Restarting services without diagnosis triggers cascading failures.
- **Customer Ticket Pressure**: Ticket urgency increases over time, impacting the final score.
- **Red Herring Metrics**: Some metrics may look abnormal but are not the root cause.

---

## 2. Quick Start & Setup

### Requirements
- Python 3.11+
- `pip install -r requirements.txt`

### Running the Environment
```bash
python app.py
```
The server will start on `http://localhost:3000`.

### Running the Baseline
```bash
python baseline/run_baseline.py
```

### Running the Validator
```bash
python validator.py
```

---

## 3. API Reference (OpenEnv Spec)

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/reset` | POST | Resets the environment with a `task_id` and `seed`. Returns initial observation. |
| `/api/step` | POST | Takes an `Action` and returns `(observation, reward, done, info)`. |
| `/api/state` | GET | Returns the full internal `SystemState`. |
| `/api/tasks` | GET | Returns the list of tasks and the `action_schema`. |
| `/api/grader` | GET | Returns the programmatic grader score (0.0-1.0) for the current episode. |
| `/api/baseline` | POST | Triggers the baseline inference script and returns scores. |

---

## 4. Task Definitions & Difficulty

| Task ID | Name | Difficulty | Root Cause | Solution |
| :--- | :--- | :--- | :--- | :--- |
| `task1_easy` | Payment API Outage | Easy | Database OOM | `edit_config(db_memory_limit=2048mb)` |
| `task2_medium` | Memory Leak | Medium | Connection Leak | `edit_config(connection_timeout=30s)` |
| `task3_hard` | Bad Deployment | Hard | Corrupt JWT Secret | `rollback_deployment(version=v1.2.1)` |

---

## 5. Action & Observation Spaces

### Action Space (15 Types)
Agents can perform diagnostic and remediation actions:
- **Diagnostic**: `check_logs`, `check_metrics`, `check_connections`, `check_config`, `check_dependencies`.
- **Remediation**: `restart_service`, `scale_service`, `edit_config`, `rollback_deployment`, `clear_cache`.
- **Communication**: `reply_customer`, `update_status_page`, `escalate_incident`, `alert_team`.
- **Final**: `mark_resolved`.

### Observation Space
The observation includes:
- **Services**: Current health, CPU, memory, error rate, and status for all services.
- **Logs**: Recent synthetic logs generated based on service states.
- **Alerts**: Active critical and warning alerts.
- **Tickets**: Open customer support tickets with urgency levels.
- **Feedback**: Textual feedback from the last action taken.

---

## 6. Reward Function & Grading

### Reward Function
Provides signal over the full trajectory:
- **+0.02** for diagnostic actions (encourages investigation).
- **+0.10** for correct remediation attempts.
- **+0.30** for health improvements (delta).
- **+0.30** for final resolution.
- **-0.25** for cascading failures (restarting without diagnosis).
- **-0.05** for redundant actions (prevents infinite loops).

### Programmatic Grader (0.0 - 1.0)
- **Resolution (50%)**: Did the system return to 100% health?
- **Efficiency (30%)**: How many steps were taken relative to `max_steps`?
- **Customer Satisfaction (20%)**: Were all tickets resolved promptly?

---

## 7. Baseline Scores (Reproducible)

| Model | Task 1 | Task 2 | Task 3 | Avg |
| :--- | :--- | :--- | :--- | :--- |
| Gemini 1.5 Flash | 0.85 | 0.72 | 0.61 | 0.73 |
| Gemini 1.5 Pro | 0.98 | 0.92 | 0.88 | 0.93 |
