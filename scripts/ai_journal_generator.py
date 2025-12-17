#!/usr/bin/env python3
"""
AI-Powered Daily Journal Generator

Uses AI to transform raw git commits and Cursor activity into natural language
journal entries that learn from your work patterns and understand accomplishments.
"""

import json
import os
import sqlite3
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
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class AIJournalGenerator:
    """AI-powered journal generator that learns from commits and Cursor activity."""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize with configuration."""
        script_dir = Path(__file__).parent.parent
        os.chdir(script_dir)
        
        self.config = self._load_config(config_path)
        self.workspace_root = Path(self.config["workspace_root"]).expanduser()
        self.output_dir = script_dir / self.config["output_dir"]
        self.cache_file = script_dir / self.config["cache_file"]
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # AI client setup
        self.ai_client = self._setup_ai_client()
        
        # Cursor paths
        self.cursor_dir = Path.home() / ".cursor"
        self.cursor_plans_dir = self.cursor_dir / "plans"
        self.cursor_chats_dir = self.cursor_dir / "chats"
        self.cursor_tracking_db = self.cursor_dir / "ai-tracking" / "ai-code-tracking.db"
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        script_dir = Path(__file__).parent.parent
        config_file = script_dir / config_path
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Add AI defaults
        config.setdefault("ai_provider", "anthropic")  # or "openai"
        config.setdefault("ai_model", "claude-3-haiku-20240307")  # Cheapest option that works well
        config.setdefault("ai_temperature", 0.7)
        config.setdefault("use_cursor_logs", True)
        config.setdefault("use_cursor_memory", True)
        
        return config
    
    def _setup_ai_client(self):
        """Setup AI client based on config."""
        provider = self.config.get("ai_provider", "anthropic")
        
        if provider == "anthropic" and HAS_ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY") or self.config.get("anthropic_api_key")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found. Set it in environment or config.")
            return anthropic.Anthropic(api_key=api_key)
        
        elif provider == "openai" and HAS_OPENAI:
            api_key = os.getenv("OPENAI_API_KEY") or self.config.get("openai_api_key")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found. Set it in environment or config.")
            return openai.OpenAI(api_key=api_key)
        
        else:
            raise ValueError(f"AI provider '{provider}' not available. Install anthropic or openai package.")
    
    def get_git_commits(self, repo_path: Path, since_date: str, until_date: Optional[str] = None) -> List[Dict]:
        """Get commits for a date range."""
        try:
            os.chdir(repo_path)
            
            cmd = [
                "git", "log",
                f"--since={since_date} 00:00:00",
                "--all",
                "--pretty=format:%h|%an|%ad|%s|%b",
                "--date=iso",
                "--no-merges"
            ]
            
            if until_date:
                cmd.insert(-2, f"--until={until_date} 23:59:59")
            
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
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line or '|' not in line:
                    continue
                
                parts = line.split('|', 4)
                if len(parts) >= 4:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'date': parts[2],
                        'message': parts[3],
                        'body': parts[4] if len(parts) > 4 else '',
                        'repo': repo_path.name
                    })
            
            return commits
        
        except Exception as e:
            print(f"⚠️  Error getting git log for {repo_path}: {e}")
            return []
        finally:
            os.chdir(self.workspace_root)
    
    def get_cursor_plans(self, target_date: str) -> List[Dict]:
        """Get Cursor plan files for the date."""
        if not self.cursor_plans_dir.exists():
            return []
        
        plans = []
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        
        for plan_file in self.cursor_plans_dir.glob("*.plan.md"):
            try:
                mtime = datetime.fromtimestamp(plan_file.stat().st_mtime)
                if mtime.date() == target_dt.date():
                    content = plan_file.read_text()
                    plans.append({
                        'file': plan_file.name,
                        'path': str(plan_file),
                        'content': content[:2000],  # First 2000 chars
                        'modified': mtime.isoformat()
                    })
            except Exception as e:
                print(f"⚠️  Error reading plan {plan_file}: {e}")
        
        return plans
    
    def get_cursor_activity(self, target_date: str) -> Dict:
        """Get Cursor AI activity from tracking database."""
        if not self.cursor_tracking_db.exists() or not self.config.get("use_cursor_logs", True):
            return {}
        
        activity = {
            'code_generated': [],
            'files_touched': set(),
            'conversations': []
        }
        
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d")
            start_ts = int(target_dt.timestamp())
            end_ts = int((target_dt + timedelta(days=1)).timestamp())
            
            conn = sqlite3.connect(str(self.cursor_tracking_db))
            cursor = conn.cursor()
            
            # Get AI code generation tracking
            cursor.execute("""
                SELECT hash, source, fileName, fileExtension, timestamp, conversationId
                FROM ai_code_hashes
                WHERE timestamp >= ? AND timestamp < ?
                ORDER BY timestamp DESC
            """, (start_ts * 1000, end_ts * 1000))
            
            for row in cursor.fetchall():
                activity['code_generated'].append({
                    'hash': row[0],
                    'source': row[1],
                    'file': row[2],
                    'extension': row[3],
                    'timestamp': row[4],
                    'conversation_id': row[5]
                })
                if row[2]:
                    activity['files_touched'].add(row[2])
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Error reading Cursor tracking: {e}")
        
        activity['files_touched'] = list(activity['files_touched'])
        return activity
    
    def get_cursor_chat_context(self, target_date: str) -> List[Dict]:
        """Extract context from Cursor chat databases."""
        if not self.cursor_chats_dir.exists() or not self.config.get("use_cursor_memory", True):
            return []
        
        chats = []
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        
        # Scan chat databases for relevant conversations
        for chat_dir in self.cursor_chats_dir.iterdir():
            if not chat_dir.is_dir():
                continue
            
            for session_dir in chat_dir.iterdir():
                db_file = session_dir / "store.db"
                if not db_file.exists():
                    continue
                
                try:
                    conn = sqlite3.connect(str(db_file))
                    cursor = conn.cursor()
                    
                    # Try to get messages (schema may vary)
                    try:
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                        tables = [row[0] for row in cursor.fetchall()]
                        
                        # Look for message-like tables
                        for table in tables:
                            if 'message' in table.lower() or 'chat' in table.lower():
                                cursor.execute(f"SELECT * FROM {table} LIMIT 5")
                                # Just note that we have chat data
                                chats.append({
                                    'session': session_dir.name,
                                    'has_data': True
                                })
                                break
                    except:
                        pass
                    
                    conn.close()
                except:
                    pass
        
        return chats
    
    def generate_ai_journal_entry(self, target_date: str, commits: List[Dict], 
                                  plans: List[Dict], cursor_activity: Dict) -> str:
        """Use AI to generate a natural language journal entry."""
        
        # Prepare context for AI
        context = self._prepare_ai_context(target_date, commits, plans, cursor_activity)
        
        # Create the prompt
        prompt = self._create_journal_prompt(context)
        
        # Call AI
        if self.config.get("ai_provider") == "anthropic":
            return self._call_anthropic(prompt)
        else:
            return self._call_openai(prompt)
    
    def _prepare_ai_context(self, target_date: str, commits: List[Dict], 
                           plans: List[Dict], cursor_activity: Dict) -> Dict:
        """Prepare structured context for AI."""
        
        # Group commits by repo
        commits_by_repo = {}
        for commit in commits:
            repo = commit.get('repo', 'unknown')
            if repo not in commits_by_repo:
                commits_by_repo[repo] = []
            commits_by_repo[repo].append(commit)
        
        return {
            'date': target_date,
            'commits': commits,
            'commits_by_repo': commits_by_repo,
            'total_commits': len(commits),
            'cursor_plans': plans,
            'cursor_activity': cursor_activity,
            'workspace': str(self.workspace_root)
        }
    
    def _create_journal_prompt(self, context: Dict) -> str:
        """Create the AI prompt for journal generation."""
        
        prompt = f"""You are helping me write my daily work journal. Today is {context['date']}.

I want a natural, personal journal entry that:
1. Understands what I actually accomplished (not just what I committed)
2. Learns from my commit patterns to infer the bigger picture
3. Reads like a personal reflection, not a technical report
4. Connects my work to goals and accomplishments

Here's what I did today:

## Git Commits ({context['total_commits']} total)

"""
        
        # Add commits grouped by repo
        for repo, repo_commits in context['commits_by_repo'].items():
            prompt += f"\n### {repo} ({len(repo_commits)} commits)\n\n"
            for commit in repo_commits[:10]:  # Limit to 10 per repo
                prompt += f"- `{commit['hash']}`: {commit['message']}\n"
                if commit.get('body'):
                    prompt += f"  {commit['body'][:200]}\n"
        
        # Add Cursor plans
        if context['cursor_plans']:
            prompt += f"\n## Cursor Plans ({len(context['cursor_plans'])} active)\n\n"
            for plan in context['cursor_plans'][:5]:
                prompt += f"- {plan['file']}: {plan['content'][:300]}...\n"
        
        # Add Cursor AI activity
        if context['cursor_activity'].get('code_generated'):
            prompt += f"\n## Cursor AI Activity\n\n"
            prompt += f"- Generated code for {len(context['cursor_activity']['code_generated'])} files\n"
            if context['cursor_activity'].get('files_touched'):
                prompt += f"- Files touched: {', '.join(context['cursor_activity']['files_touched'][:10])}\n"
        
        prompt += """

## Instructions

Write a personal journal entry (2-3 paragraphs) that:

1. **Understands accomplishments**: Look at the commits and infer what problems I was solving or features I was building. Don't just list commits - explain what I achieved.

2. **Natural language**: Write in first person, like I'm reflecting on my day. Use phrases like "I worked on...", "I figured out...", "I made progress on..."

3. **Connect the dots**: If I made multiple commits to the same feature, group them together. If I worked across multiple projects, explain how they relate.

4. **Learning from patterns**: Notice patterns in commit messages - if I'm fixing bugs, building features, refactoring, etc. Reflect that in the narrative.

5. **Personal tone**: This is MY journal. Make it feel authentic and reflective, not like a changelog.

Example style:
"Today I focused on improving the authentication system. I spent time debugging some edge cases that were causing issues for users, and then refactored the login flow to make it more robust. I also started exploring a new feature for the dashboard, though that's still in early stages."

Write the journal entry now:"""
        
        return prompt
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude API."""
        model = self.config.get("ai_model", "claude-3-haiku-20240307")
        
        message = self.ai_client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=self.config.get("ai_temperature", 0.7),
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return message.content[0].text
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        model = self.config.get("ai_model", "gpt-4")
        
        response = self.ai_client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=self.config.get("ai_temperature", 0.7),
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def find_git_repos(self) -> List[Path]:
        """Find all git repositories."""
        repos = []
        max_depth = 3
        
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
            print("⚠️  Find command timed out")
        
        excluded = set(self.config.get("exclude_projects", []))
        repos = [r for r in repos if r.name not in excluded]
        
        return repos
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        path_str = str(path)
        for pattern in self.config.get("exclude_patterns", []):
            if pattern.replace("**/", "").replace("/**", "") in path_str:
                return True
        return False
    
    def generate_journal(self, target_date: str, end_date: Optional[str] = None) -> str:
        """Generate the complete journal entry."""
        print(f"\n📝 Generating AI-powered journal for {target_date}")
        
        # Find repos
        repos = self.find_git_repos()
        print(f"✅ Found {len(repos)} git repositories")
        
        # Get commits
        all_commits = []
        for repo in repos:
            commits = self.get_git_commits(repo, target_date, end_date)
            all_commits.extend(commits)
        
        print(f"✅ Found {len(all_commits)} commits")
        
        # Get Cursor data
        plans = self.get_cursor_plans(target_date)
        print(f"✅ Found {len(plans)} Cursor plans")
        
        cursor_activity = self.get_cursor_activity(target_date)
        print(f"✅ Analyzed Cursor activity")
        
        # Generate AI journal entry
        print("🤖 Generating natural language journal entry...")
        journal_entry = self.generate_ai_journal_entry(target_date, all_commits, plans, cursor_activity)
        
        # Format final output
        return self._format_journal(target_date, journal_entry, all_commits, plans, cursor_activity)
    
    def _format_journal(self, target_date: str, journal_entry: str, 
                        commits: List[Dict], plans: List[Dict], 
                        cursor_activity: Dict) -> str:
        """Format the final journal entry."""
        
        md = f"# Daily Journal - {target_date}\n\n"
        md += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        md += "---\n\n"
        
        # AI-generated journal entry
        md += "## Today's Reflection\n\n"
        md += journal_entry
        md += "\n\n---\n\n"
        
        # Technical details (collapsible/optional)
        md += "## Technical Details\n\n"
        md += f"**Total Commits:** {len(commits)}\n"
        md += f"**Cursor Plans:** {len(plans)}\n"
        if cursor_activity.get('code_generated'):
            md += f"**AI-Generated Code:** {len(cursor_activity['code_generated'])} files\n"
        md += "\n"
        
        # Quick commit summary
        if commits:
            md += "### Commits\n\n"
            for commit in commits[:20]:  # Limit to 20
                md += f"- `{commit['hash']}`: {commit['message']} ({commit.get('repo', 'unknown')})\n"
            if len(commits) > 20:
                md += f"- ... and {len(commits) - 20} more commits\n"
        
        md += "\n"
        return md
    
    def save_journal(self, journal: str, target_date: str) -> Path:
        """Save journal to file."""
        output_file = self.output_dir / f"{target_date}_journal.md"
        output_file.write_text(journal)
        print(f"✅ Journal saved to {output_file}")
        return output_file


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate AI-powered daily journal from git commits and Cursor activity"
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
        help="Path to config file"
    )
    
    args = parser.parse_args()
    
    try:
        generator = AIJournalGenerator(args.config)
        
        if args.start and args.end:
            # For date ranges, generate for each day
            start = datetime.strptime(args.start, "%Y-%m-%d")
            end = datetime.strptime(args.end, "%Y-%m-%d")
            current = start
            while current <= end:
                date_str = current.strftime("%Y-%m-%d")
                journal = generator.generate_journal(date_str)
                generator.save_journal(journal, date_str)
                current += timedelta(days=1)
        else:
            journal = generator.generate_journal(args.date)
            generator.save_journal(journal, args.date)
        
        print("\n✨ Journal generation complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
