# Daily Work Summary Prompt Template

This is the structured prompt used to generate daily work summaries. It can be used with Cursor's AI agent or any LLM.

## Prompt Structure

```
You are analyzing a developer's work across multiple projects for a specific day. 
Generate a comprehensive, structured summary organized by project/repository.

## Context
- Date: {DATE}
- Workspace: {WORKSPACE_PATH}
- Projects Found: {PROJECT_COUNT}

## Data Sources Available
1. Git commit logs with file changes
2. Cursor plan files (.cursor/plans/*.plan.md)
3. File modification timestamps
4. Project structure information

## Instructions

1. **Project Discovery**: Identify all git repositories in the workspace
2. **Git Analysis**: For each repo, extract:
   - Commits made on the target date
   - Files changed (with line counts)
   - Commit messages and authors
   - Branch information if relevant

3. **Cursor Integration**: Check `.cursor/plans/` directory for:
   - Plan files modified on target date
   - Active todos and their status
   - Project context from plan files

4. **File System Analysis**: For non-git-tracked work:
   - Check file modification times
   - Identify new files created
   - Note significant file changes

5. **Summary Generation**: Create a structured markdown document with:
   - Overview section
   - Project-by-project breakdown
   - Commit details with statistics
   - Files modified/created
   - Key achievements
   - Next steps (from plans)

## Output Format

Generate a markdown document following this structure:

```markdown
# Today's Work Summary - {DATE}

## Overview
Brief 2-3 sentence summary of the day's work.

---

## Project 1: {Project Name}
**Location:** {path}

### Work Completed

#### 1. {Feature/Task Name}
**Commits:**
- {commit_hash} - {commit_message} ({time_ago})

**Changes:**
- {detailed description of changes}
- {files modified with line counts}

#### 2. {Next Feature/Task}
...

### Files Modified
- {list of key files}

---

## Project 2: {Next Project}
...

## Summary Statistics

### {Project Name}
- **Total Commits:** {count}
- **Time Range:** {earliest} to {latest}
- **Focus Areas:** {themes}
- **Lines Changed:** {estimate}

## Key Achievements

1. **{Project}:**
   - {achievement 1}
   - {achievement 2}

2. **{Project}:**
   - {achievement 1}
   - {achievement 2}

## Next Steps (From Plans)

### {Project}
- {status} {task description}
  - {subtasks if any}
```

## Token Optimization Guidelines

When querying for information:

1. **Start with Git Logs**: These are cheap and provide most context
   ```bash
   git log --since="DATE" --pretty=format:"%h - %an, %ar : %s" --stat
   ```

2. **Use Targeted File Queries**: Only check files modified on target date
   ```bash
   find . -type f -mtime -1 -not -path "*/\.*"
   ```

3. **Read Plans Selectively**: Only read plan files modified today
   ```bash
   find .cursor/plans -type f -mtime -1
   ```

4. **Batch Operations**: Group similar queries together
   - All git log queries in one batch
   - All file system queries in another batch

5. **Lazy File Reading**: Only read file contents when:
   - Commit message is unclear
   - Need to understand context
   - File is small (config, plan, README)

6. **Cache Results**: Within the same run, cache:
   - Git log results per repo
   - File modification times
   - Plan file contents

## Example Queries

### Phase 1: Discovery (Cheap)
```bash
# Find all git repos
find WORKSPACE -maxdepth 3 -type d -name ".git"

# Get commit count per repo
cd REPO && git log --since="DATE" --oneline | wc -l
```

### Phase 2: Git Analysis (Cheap)
```bash
# Get detailed commit log
cd REPO && git log --since="DATE" --pretty=format:"%h - %an, %ar : %s" --stat

# Get file change summary
cd REPO && git diff --stat DATE~1..DATE
```

### Phase 3: Cursor Integration (Medium)
```bash
# Find modified plan files
find WORKSPACE/.cursor/plans -type f -mtime -1

# Read plan files (small, fast)
cat .cursor/plans/*.plan.md
```

### Phase 4: File System (Expensive - Use Sparingly)
```bash
# Only for non-git-tracked work
find PROJECT -type f -mtime -1 -not -path "*/.git/*" -not -path "*/node_modules/*"
```

## Notes

- Prioritize git-based information (most work is committed)
- Use file modification times as secondary source
- Only read file contents when absolutely necessary
- Group similar operations to minimize subprocess overhead
- Cache results within the same analysis run
