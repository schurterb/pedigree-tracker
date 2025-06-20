---
description: Set up and manage project tasks with TaskMaster AI
---

# TaskMaster AI Project Setup and Task Management

This workflow guides you through setting up and managing tasks for a project using TaskMaster AI, from initializing the project to breaking down complex tasks.

## 1. Initialize TaskMaster in your project

Initialize TaskMaster to create the necessary configuration files:

```bash
# Initialize TaskMaster in the current project
npx task-master init
```

## 2. Create or identify a PRD document

Create a Product Requirements Document (PRD) or use an existing one. This document should outline the project's requirements, features, and specifications.

Example PRD location: `<project-root>/scripts/prd.txt`

## 3. Generate tasks from the PRD

Parse the PRD to automatically generate initial tasks:

```bash
# Parse PRD and create tasks (adjust path as needed)
npx task-master parse-prd --input=<path-to-prd>.txt
```

## 4. Analyze task complexity

Analyze the complexity of generated tasks to identify which ones need further breakdown:

```bash
# Analyze task complexity and generate a report
npx task-master analyze-complexity --research
```

## 5. Review the complexity report

View the analysis results in a readable format:

```bash
# View the complexity report
npx task-master complexity-report
```

## 6. Break down complex tasks

For each high-complexity task (generally score 7+), break it down into subtasks:

```bash
# Expand a specific task with subtasks
npx task-master expand --id=<task-id> --num=<number-of-subtasks> --research --prompt="<breakdown-guidance>"
```

Example breakdown prompts:
- "Break down the implementation into logical steps including data modeling, API endpoints, UI components, and testing"
- "Divide this feature into smaller components covering setup, core functionality, error handling, and optimization"

## 7. Set task dependencies

Establish dependencies between tasks to create a logical workflow:

```bash
# Add dependency between tasks
npx task-master add-dependency --id=<task-id> --dependsOn=<dependency-id>
```

## 8. Generate individual task files

After updating tasks or dependencies, generate the individual task files:

```bash
# Generate task files from tasks.json
npx task-master generate
```

## 9. Find the next task to work on

Identify the next task to work on based on dependencies and status:

```bash
# Find next task
npx task-master next
```

## 10. Update task status as you progress

As you complete tasks, update their status:

```bash
# Set task status
npx task-master set-status --id=<task-id> --status=done
```

## 11. Modify future tasks based on implementation changes

If your implementation differs significantly from the original plan, update future tasks:

```bash
# Update future tasks based on changes
npx task-master update --from=<task-id> --prompt="<explanation-of-changes>"
```

## 12. Additional helpful commands

Other useful TaskMaster commands:

```bash
# List all tasks
npx task-master list

# View specific task details
npx task-master show <task-id>

# Clear existing subtasks before regenerating
npx task-master clear-subtasks --id=<task-id>

# Fix dependency issues
npx task-master fix-dependencies
```
