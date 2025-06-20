---
description: Automatically process a PRD into tasks with complexity analysis and breakdown
---

# Automated TaskMaster Workflow

This workflow automatically processes a Product Requirements Document (PRD) through TaskMaster AI to generate tasks, analyze their complexity, and break down complex tasks into manageable subtasks.

## Run the workflow

```bash
// turbo-all
./scripts/taskmaster_workflow.sh --prd=<path-to-prd-file> [--threshold=<complexity-threshold>]
```

### Parameters:

- `--prd=<path>`: (Required) Path to your PRD document
- `--threshold=<num>`: (Optional) Complexity threshold for task breakdown (default: 7)

### Example:

```bash
./scripts/taskmaster_workflow.sh --prd=pedigree-tracker-prd.txt --threshold=6
```

## What this workflow does:

1. Initializes TaskMaster in your project (if not already done)
2. Parses the PRD document and generates tasks
3. Analyzes task complexity with research-backed insights
4. Automatically identifies tasks above the complexity threshold
5. Breaks down complex tasks into appropriate subtasks
6. Regenerates task files
7. Shows the next task to work on

## After running:

- View all tasks with: `npx task-master list`
- See task details with: `npx task-master show <task-id>`
- Find the next task to work on: `npx task-master next`
