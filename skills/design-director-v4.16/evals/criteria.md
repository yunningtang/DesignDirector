# Evaluation (two layers)

## Auto layer (radar + screenshots; never shown to the model)
| metric | gate |
|---|---|
| AI 味 (dashboard radar algorithm: corners by the most common bucket) | ≤ 1.0 per page on average |
| heading fonts across 10 pages | ≥ 7 kinds |
| Archivo heading | 0 |
| phone overflow (375px) | ≤ 1 page |
| JS errors | 0 |
| direction collisions with config/used.json | 0 |

## Judge layer (blind, all variants of a task side by side)
Score 1–5 on usable, looks, fit; then rank. One judge per task, positions balanced by a Latin square.

## Decision rule
Pass the auto gate first; among versions that pass, compare judge scores with paired tests (Wilcoxon over tasks). v1 targets: looks and rank not significantly below Style Director v1.1, and significantly above Design Director v0.2.
