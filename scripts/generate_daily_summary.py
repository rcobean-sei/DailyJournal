#!/usr/bin/env python3
"""
DailyJournal - Automated daily work summary generator for Cursor-based development.

Token-optimized script that generates structured summaries by analyzing:
1. Git commit logs (cheap, primary source)
2. Cursor plan files (medium cost)
3. File modification times (expensive, use sparingly)

Usage:
    python generate_daily_summary.py [--date YYYY-MM-DD] [--start DATE] [--end DATE]
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

# Try to import optional dependencies
try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None

try:
    import git
    HAS_GITPYTHON = True
except ImportError:
    HAS_GITPYTHON = False


class DailyJournalGenerator:
    """Token-optimized daily work summary generator."""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize with configuration."""
        # Get script directory for relative paths
        script_dir = Path(__file__).parent.parent
        os.chdir(script_dir)  # Change to project root
        
        self.config = self._load_config(config_path)
        self.workspace_root = Path(self.config["workspace_root"]).expanduser()
        
        # Output dir is relative to project root
        self.output_dir = script_dir / self.config["output_dir"]
        self.cache_file = script_dir / self.config["cache_file"]
        self.cursor_plans_dir = Path(self.config["cursor_plans_dir"])
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Cache for this run
        self._git_cache: Dict[str, List[Dict]] = {}
        self._file_cache: Dict[str, Dict] = {}
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        # Config path is relative to project root (script_dir)
        script_dir = Path(__file__).parent.parent
        config_file = script_dir / config_path
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded based on patterns."""
        path_str = str(path)
        for pattern in self.config["exclude_patterns"]:
            # Simple glob-like matching
            if pattern.replace("**/", "").replace("/**", "") in path_str:
                return True
        return False
    
    def find_git_repos(self) -> List[Path]:
        """
        Phase 1: Discovery (Cheap)
        Find all git repositories in workspace.
        """
        repos = []
        max_depth = 3
        
        print(f"🔍 Discovering git repositories in {self.workspace_root}...")
        
        # Use find command (faster than Python walk for large directories)
        try:
            result = subprocess.run(
                ["find", str(self.workspace_root), "-maxdepth", str(max_depth * 2),
                 "-type", "d", "-name", ".git"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            for git_dir in result.stdout.strip().split('\n'):
                if not git_dir:
                    continue
                repo_path = Path(git_dir).parent
                if not self._should_exclude(repo_path):
                    repos.append(repo_path)
        
        except subprocess.TimeoutExpired:
            print("⚠️  Find command timed out, using Python walk...")
            # Fallback to Python walk
            for root, dirs, files in os.walk(self.workspace_root):
                if '.git' in dirs:
                    repo_path = Path(root)
                    if not self._should_exclude(repo_path):
                        repos.append(repo_path)
                    dirs[:] = []  # Don't recurse into subdirectories
        
        # Filter excluded projects
        excluded = set(self.config.get("exclude_projects", []))
        repos = [r for r in repos if r.name not in excluded]
        
        print(f"✅ Found {len(repos)} git repositories")
        return repos
    
    def get_git_commits(self, repo_path: Path, since_date: str, until_date: Optional[str] = None) -> List[Dict]:
        """
        Phase 2: Git Analysis (Cheap)
        Get commits for a date range using git log.
        """
        cache_key = f"{repo_path}:{since_date}:{until_date}"
        if cache_key in self._git_cache:
            return self._git_cache[cache_key]
        
        try:
            os.chdir(repo_path)
            
            # Build git log command
            cmd = [
                "git", "log",
                f"--since={since_date} 00:00:00",
                "--all",
                "--pretty=format:%h|%an|%ar|%s",
                "--stat",
                "--no-merges"
            ]
            
            if until_date:
                cmd.insert(-2, f"--until={until_date} 23:59:59")
            
            # Limit commits
            max_commits = self.config.get("max_commits_per_repo", 50)
            if max_commits:
                cmd.extend(["-n", str(max_commits)])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return []
            
            commits = self._parse_git_log(result.stdout)
            self._git_cache[cache_key] = commits
            return commits
        
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            print(f"⚠️  Error getting git log for {repo_path}: {e}")
            return []
        except Exception as e:
            print(f"⚠️  Unexpected error for {repo_path}: {e}")
            return []
        finally:
            os.chdir(self.workspace_root)
    
    def _parse_git_log(self, log_output: str) -> List[Dict]:
        """Parse git log output into structured data."""
        commits = []
        current_commit = None
        current_files = []
        
        for line in log_output.split('\n'):
            if not line.strip():
                if current_commit:
                    current_commit['files'] = current_files
                    commits.append(current_commit)
                    current_commit = None
                    current_files = []
                continue
            
            # Commit header: hash|author|time|message
            if '|' in line and not line.startswith(' '):
                parts = line.split('|', 3)
                if len(parts) >= 4:
                    current_commit = {
                        'hash': parts[0],
                        'author': parts[1],
                        'time_ago': parts[2],
                        'message': parts[3],
                        'files': []
                    }
                    current_files = []
            
            # File stat line: " file.py | 10 +5 -3"
            elif line.strip().startswith('|') or '|' in line:
                # Parse file change line
                match = re.match(r'\s*([^|]+)\s*\|\s*(\d+)\s*([+-]?\d+)\s*([+-]?\d+)?', line)
                if match:
                    filename = match.group(1).strip()
                    changes = match.group(2)
                    current_files.append({
                        'file': filename,
                        'changes': changes
                    })
        
        # Don't forget the last commit
        if current_commit:
            current_commit['files'] = current_files
            commits.append(current_commit)
        
        return commits
    
    def get_cursor_plans(self, target_date: str) -> List[Dict]:
        """
        Phase 3: Cursor Integration (Medium Cost)
        Get Cursor plan files modified on target date.
        """
        plans_dir = self.workspace_root / self.cursor_plans_dir
        
        if not plans_dir.exists():
            return []
        
        plans = []
        
        try:
            # Find plan files modified on target date
            result = subprocess.run(
                ["find", str(plans_dir), "-type", "f", "-name", "*.plan.md", "-mtime", "-1"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            for plan_file in result.stdout.strip().split('\n'):
                if not plan_file:
                    continue
                
                plan_path = Path(plan_file)
                if plan_path.exists():
                    try:
                        content = plan_path.read_text()
                        # Extract metadata from frontmatter
                        metadata = self._parse_plan_frontmatter(content)
                        plans.append({
                            'file': plan_path.name,
                            'path': str(plan_path),
                            'metadata': metadata,
                            'content_preview': content[:500]  # First 500 chars
                        })
                    except Exception as e:
                        print(f"⚠️  Error reading plan {plan_path}: {e}")
        
        except subprocess.TimeoutExpired:
            print("⚠️  Find command timed out for plans")
        except Exception as e:
            print(f"⚠️  Error getting cursor plans: {e}")
        
        return plans
    
    def _parse_plan_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from plan file."""
        metadata = {}
        
        if content.startswith('---'):
            # Extract frontmatter
            end_idx = content.find('---', 3)
            if end_idx > 0:
                frontmatter = content[3:end_idx].strip()
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        metadata[key] = value
        
        return metadata
    
    def get_file_modifications(self, repo_path: Path, target_date: str) -> List[Dict]:
        """
        Phase 4: File System (Expensive - Use Sparingly)
        Get files modified on target date (for non-git-tracked work).
        """
        # Only check if repo has uncommitted changes or if explicitly needed
        # This is expensive, so we use it sparingly
        
        try:
            os.chdir(repo_path)
            
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Has uncommitted changes, check modification times
                modified_files = []
                for line in result.stdout.strip().split('\n'):
                    if line.startswith(' M') or line.startswith('??'):
                        file_path = line[3:].strip()
                        full_path = repo_path / file_path
                        if full_path.exists():
                            mtime = datetime.fromtimestamp(full_path.stat().st_mtime)
                            if mtime.date() == datetime.strptime(target_date, "%Y-%m-%d").date():
                                modified_files.append({
                                    'file': file_path,
                                    'status': line[0:2].strip(),
                                    'modified': mtime.isoformat()
                                })
                
                return modified_files
        
        except Exception as e:
            print(f"⚠️  Error checking file modifications for {repo_path}: {e}")
        finally:
            os.chdir(self.workspace_root)
        
        return []
    
    def generate_summary(self, target_date: str, end_date: Optional[str] = None) -> str:
        """Generate the daily summary markdown."""
        print(f"\n📝 Generating summary for {target_date}" + (f" to {end_date}" if end_date else ""))
        
        # Phase 1: Discovery
        repos = self.find_git_repos()
        
        # Phase 2: Git Analysis (batch all queries)
        repo_data = {}
        for repo in repos:
            commits = self.get_git_commits(repo, target_date, end_date)
            if commits:
                repo_data[repo] = {
                    'commits': commits,
                    'path': str(repo.relative_to(self.workspace_root))
                }
        
        # Phase 3: Cursor Plans
        plans = self.get_cursor_plans(target_date)
        
        # Phase 4: File modifications (only for repos with commits)
        for repo, data in repo_data.items():
            file_mods = self.get_file_modifications(repo, target_date)
            if file_mods:
                data['file_modifications'] = file_mods
        
        # Generate markdown
        return self._format_summary(target_date, end_date, repo_data, plans)
    
    def _format_summary(self, target_date: str, end_date: Optional[str], 
                       repo_data: Dict, plans: List[Dict]) -> str:
        """Format the summary as markdown."""
        date_range = f"{target_date}" + (f" to {end_date}" if end_date else "")
        
        md = f"# Today's Work Summary - {date_range}\n\n"
        md += f"## Overview\n\n"
        md += f"Work summary generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n"
        md += f"Analyzed {len(repo_data)} repositories with activity.\n\n"
        md += "---\n\n"
        
        # Projects section
        for repo, data in repo_data.items():
            repo_name = repo.name
            repo_path = data['path']
            commits = data['commits']
            
            md += f"## Project: {repo_name}\n"
            md += f"**Location:** `{repo_path}`\n\n"
            
            # Group commits by feature/task (simple heuristic: group by first few words)
            md += "### Work Completed\n\n"
            
            for commit in commits:
                md += f"#### {commit['message']}\n"
                md += f"**Commit:** `{commit['hash']}` - {commit['author']}, {commit['time_ago']}\n\n"
                
                if commit['files']:
                    md += "**Files Changed:**\n"
                    for file_info in commit['files'][:10]:  # Limit to 10 files
                        md += f"- `{file_info['file']}` ({file_info['changes']} changes)\n"
                    if len(commit['files']) > 10:
                        md += f"- ... and {len(commit['files']) - 10} more files\n"
                    md += "\n"
            
            # File modifications (uncommitted)
            if 'file_modifications' in data and data['file_modifications']:
                md += "### Uncommitted Changes\n\n"
                for file_mod in data['file_modifications']:
                    md += f"- `{file_mod['file']}` ({file_mod['status']})\n"
                md += "\n"
            
            md += "---\n\n"
        
        # Cursor Plans section
        if plans:
            md += "## Cursor Plans\n\n"
            for plan in plans:
                md += f"### {plan['metadata'].get('name', plan['file'])}\n"
                md += f"**File:** `{plan['file']}`\n\n"
                if 'overview' in plan['metadata']:
                    md += f"**Overview:** {plan['metadata']['overview']}\n\n"
            md += "---\n\n"
        
        # Statistics
        md += "## Summary Statistics\n\n"
        total_commits = sum(len(data['commits']) for data in repo_data.values())
        md += f"- **Total Repositories:** {len(repo_data)}\n"
        md += f"- **Total Commits:** {total_commits}\n"
        md += f"- **Cursor Plans:** {len(plans)}\n\n"
        
        md += f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return md
    
    def save_summary(self, summary: str, target_date: str) -> Path:
        """Save summary to file."""
        output_file = self.output_dir / f"{target_date}_summary.md"
        output_file.write_text(summary)
        print(f"✅ Summary saved to {output_file}")
        return output_file
    
    def update_cache(self, target_date: str):
        """Update cache with last run timestamp."""
        self.cache_file.write_text(target_date)
    
    def get_last_run_date(self) -> Optional[str]:
        """Get the last run date from cache."""
        if self.cache_file.exists():
            return self.cache_file.read_text().strip()
        return None


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate daily work summary from git commits and Cursor plans"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Target date (YYYY-MM-DD). Defaults to today.",
        default=datetime.now().strftime("%Y-%m-%d")
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start date for range (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date for range (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.json",
        help="Path to config file (relative to script directory)"
    )
    
    args = parser.parse_args()
    
    try:
        generator = DailyJournalGenerator(args.config)
        
        if args.start and args.end:
            # Date range
            summary = generator.generate_summary(args.start, args.end)
            generator.save_summary(summary, f"{args.start}_to_{args.end}")
        else:
            # Single date
            summary = generator.generate_summary(args.date)
            generator.save_summary(summary, args.date)
            generator.update_cache(args.date)
        
        print("\n✨ Summary generation complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
