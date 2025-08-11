#!/usr/bin/env python3
"""
UHL Auto-Commit Script
Automated commit, push, and release workflow for UHL operations
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

class GitAutoCommit:
    """Automated git workflow manager for UHL operations"""
    
    def __init__(self, repo_path: Optional[str] = None):
        """Initialize the auto-commit manager"""
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        while not (self.repo_path / '.git').exists() and self.repo_path.parent != self.repo_path:
            self.repo_path = self.repo_path.parent
            
        if not (self.repo_path / '.git').exists():
            raise ValueError("Not in a git repository!")
            
        os.chdir(self.repo_path)
        self.ops_dir = self.repo_path / 'ops'
        
    def print_status(self, message: str) -> None:
        """Print success message"""
        print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
        
    def print_warning(self, message: str) -> None:
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")
        
    def print_error(self, message: str) -> None:
        """Print error message"""
        print(f"{Colors.RED}❌ {message}{Colors.NC}")
        
    def print_info(self, message: str) -> None:
        """Print info message"""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")
        
    def print_header(self, title: str) -> None:
        """Print section header"""
        print(f"\n{Colors.CYAN}{title}{Colors.NC}")
        print("=" * len(title))
        
    def run_git_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """Run a git command and return success status and output"""
        try:
            result = subprocess.run(['git'] + cmd, 
                                  capture_output=capture_output, 
                                  text=True, 
                                  check=True)
            return True, result.stdout.strip() if capture_output else ""
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            return False, error_msg
            
    def check_git_status(self) -> Dict[str, any]:
        """Check current git repository status"""
        status = {
            'has_changes': False,
            'branch': '',
            'changed_files': [],
            'staged_files': [],
            'untracked_files': []
        }
        
        # Get current branch
        success, branch = self.run_git_command(['branch', '--show-current'])
        if success:
            status['branch'] = branch
            
        # Check for changes
        success, output = self.run_git_command(['status', '--porcelain'])
        if success:
            lines = output.strip().split('\n') if output.strip() else []
            for line in lines:
                if line:
                    status['has_changes'] = True
                    file_status = line[:2]
                    filename = line[3:]
                    
                    if file_status[0] in ['M', 'A', 'D', 'R', 'C']:
                        status['staged_files'].append(filename)
                    if file_status[1] in ['M', 'D']:
                        status['changed_files'].append(filename)
                    if file_status == '??':
                        status['untracked_files'].append(filename)
                        
        return status
        
    def analyze_changes(self) -> Dict[str, any]:
        """Analyze the type of changes being committed"""
        analysis = {
            'type': 'feat',
            'scope': '',
            'description': '',
            'is_gameday': False,
            'is_ops': False,
            'is_refactor': False,
            'is_docs': False,
            'changed_files': [],
            'data_stats': {}
        }
        
        # Get list of changed files
        status = self.check_git_status()
        all_changed = status['changed_files'] + status['staged_files'] + status['untracked_files']
        analysis['changed_files'] = all_changed
        
        # Analyze file patterns to determine change type
        scripts_changes = [f for f in all_changed if 'scripts/' in f or f.endswith('.py') and 'ops/' in f]
        config_changes = [f for f in all_changed if 'config/' in f or f.endswith('.env') or f.endswith('settings.py')]
        docs_changes = [f for f in all_changed if f.endswith('.md') or 'docs/' in f or 'README' in f]
        data_changes = [f for f in all_changed if f.endswith('.json') and 'output/' in f]
        refactor_changes = [f for f in all_changed if 'src/' in f or '__init__.py' in f]
        
        # Determine primary change type based on file patterns
        if data_changes and self._are_data_files_fresh():
            analysis['is_gameday'] = True
            analysis['type'] = 'gameday'
            analysis['scope'] = 'data'
            analysis['description'] = 'gameday data update'
            analysis = self._extract_data_stats(analysis)
            
        elif scripts_changes and len(scripts_changes) > len(all_changed) * 0.3:
            analysis['is_ops'] = True
            analysis['type'] = 'ops'
            analysis['scope'] = 'automation'
            if 'auto_commit' in str(scripts_changes):
                analysis['description'] = 'automated commit system'
            elif 'weekly_update' in str(scripts_changes):
                analysis['description'] = 'update automation'
            else:
                analysis['description'] = 'operations improvements'
                
        elif refactor_changes and len(refactor_changes) > len(all_changed) * 0.4:
            analysis['is_refactor'] = True
            analysis['type'] = 'refactor'
            analysis['scope'] = 'structure'
            analysis['description'] = 'code organization and structure'
            
        elif docs_changes and len(docs_changes) > len(all_changed) * 0.5:
            analysis['is_docs'] = True
            analysis['type'] = 'docs'
            analysis['scope'] = 'documentation'
            analysis['description'] = 'documentation updates'
            
        elif config_changes:
            analysis['type'] = 'config'
            analysis['scope'] = 'settings'
            analysis['description'] = 'configuration updates'
            
        return analysis
        
    def _are_data_files_fresh(self) -> bool:
        """Check if data files were recently modified (within last hour)"""
        output_dir = self.ops_dir / 'output'
        data_files = ['schedule.json', 'players.json', 'standings.json', 'goalie_stats.json']
        
        if not all((output_dir / f).exists() for f in data_files):
            return False
            
        import time
        current_time = time.time()
        for filename in data_files:
            file_path = output_dir / filename
            if file_path.exists():
                file_mtime = file_path.stat().st_mtime
                # If file was modified within the last hour, consider it fresh
                if current_time - file_mtime < 3600:
                    return True
        return False
        
    def _extract_data_stats(self, analysis: Dict[str, any]) -> Dict[str, any]:
        """Extract statistics from data files"""
        output_dir = self.ops_dir / 'output'
        try:
            schedule_path = output_dir / 'schedule.json'
            players_path = output_dir / 'players.json'
            goalies_path = output_dir / 'goalie_stats.json'
            
            if schedule_path.exists():
                with open(schedule_path) as f:
                    schedule_data = json.load(f)
                    if isinstance(schedule_data, list):
                        analysis['data_stats']['games'] = len(schedule_data)
                    else:
                        analysis['data_stats']['games'] = len(schedule_data.get('games', []))
                    
            if players_path.exists():
                with open(players_path) as f:
                    players_data = json.load(f)
                    if isinstance(players_data, list):
                        analysis['data_stats']['players'] = len(players_data)
                    else:
                        analysis['data_stats']['players'] = len(players_data.get('players', []))
                    
            if goalies_path.exists():
                with open(goalies_path) as f:
                    goalies_data = json.load(f)
                    if isinstance(goalies_data, list):
                        analysis['data_stats']['goalies'] = len(goalies_data)
                    else:
                        analysis['data_stats']['goalies'] = len(goalies_data.get('goalies', []))
                    
        except (json.JSONDecodeError, FileNotFoundError):
            pass
            
        return analysis
        
    def generate_commit_message(self, analysis: Dict[str, any], custom_msg: Optional[str] = None) -> str:
        """Generate appropriate commit message based on changes"""
        if custom_msg:
            return custom_msg
            
        commit_type = analysis['type']
        scope = analysis['scope']
        description = analysis['description']
        
        if analysis['is_gameday']:
            stats = analysis['data_stats']
            games = stats.get('games', 0)
            players = stats.get('players', 0)
            goalies = stats.get('goalies', 0)
            return f"gameday: Update UHL data - {games} games, {players} players, {goalies} goalies"
            
        elif analysis['is_ops']:
            if 'automated commit system' in description:
                return "ops: Add Python-based automated commit workflow"
            elif 'update automation' in description:
                return "ops: Improve update automation scripts"
            else:
                return f"ops: {description.title()}"
                
        elif analysis['is_refactor']:
            return f"refactor({scope}): {description}"
            
        elif analysis['is_docs']:
            return f"docs: Update {description}"
            
        elif commit_type == 'config':
            return f"config: Update {description}"
            
        else:
            # Fallback - try to be smart about what changed
            changed_files = analysis.get('changed_files', [])
            if any('python' in f.lower() or f.endswith('.py') for f in changed_files):
                return "feat: Add new Python automation tools"
            elif any('script' in f.lower() for f in changed_files):
                return "feat: Add new automation scripts"
            else:
                return "feat: Update hockey league system"
            
    def get_current_version(self) -> Tuple[int, int, int]:
        """Get current version from git tags"""
        success, output = self.run_git_command(['describe', '--tags', '--abbrev=0'])
        if not success:
            return (0, 0, 0)
            
        # Parse version (remove 'v' prefix if present)
        version_str = output.lstrip('v')
        try:
            parts = version_str.split('.')
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except (ValueError, IndexError):
            return (0, 0, 0)
            
    def bump_version(self, current: Tuple[int, int, int], bump_type: str) -> str:
        """Bump version based on type"""
        major, minor, patch = current
        
        if bump_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        elif bump_type == 'patch':
            patch += 1
            
        return f"v{major}.{minor}.{patch}"
        
    def generate_release_notes(self, version: str, analysis: Dict[str, any], commit_msg: str) -> str:
        """Generate release notes"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if analysis['is_gameday']:
            stats = analysis['data_stats']
            games = stats.get('games', 0)
            players = stats.get('players', 0)
            goalies = stats.get('goalies', 0)
            
            return f"""🏒 Gameday Update {version}

## Data Updates
- Updated schedule with {games} games
- Processed {players} player records  
- Calculated statistics for {goalies} goalies

## Files Updated
- `schedule.json` - Complete game schedule with lineups
- `players.json` - Player data and season statistics
- `standings.json` - Team standings and records
- `goalie_stats.json` - Goalie performance metrics

Generated: {timestamp}"""
            
        elif analysis['is_ops']:
            return f"""🔧 Operations Update {version}

## System Improvements
- Enhanced UHL operations workflow
- Improved automation scripts
- Better error handling and logging

## Technical Updates
- Streamlined data processing
- Updated configuration management
- Enhanced reliability and performance

Generated: {timestamp}"""
            
        else:
            return f"""🚀 UHL System Update {version}

## Updates
{commit_msg}

Generated: {timestamp}"""
            
    def interactive_commit(self, dry_run: bool = False) -> bool:
        """Interactive commit workflow"""
        self.print_header("🏒 UHL Auto-Commit Workflow")
        
        print(f"Repository: {self.repo_path.name}")
        
        # Check git status
        status = self.check_git_status()
        print(f"Current branch: {status['branch']}")
        
        if not status['has_changes']:
            self.print_warning("No changes to commit")
            if not self._confirm("Continue anyway?"):
                return False
                
        # Show current status
        if status['changed_files'] or status['staged_files'] or status['untracked_files']:
            self.print_info("Changed files:")
            for f in status['changed_files'] + status['staged_files'] + status['untracked_files']:
                print(f"  {f}")
        print()
        
        # Analyze changes
        analysis = self.analyze_changes()
        
        # Generate commit message
        suggested_msg = self.generate_commit_message(analysis)
        print(f"{Colors.YELLOW}Suggested commit message:{Colors.NC}")
        print(f"  {suggested_msg}")
        
        if self._confirm("Use this message?"):
            commit_msg = suggested_msg
        else:
            commit_msg = input("Enter your commit message: ").strip()
            if not commit_msg:
                commit_msg = suggested_msg
                
        # Ask about version bump
        print(f"\n{Colors.YELLOW}Release version bump:{Colors.NC}")
        print("1) patch (1.0.1 -> 1.0.2) - Bug fixes, data updates")
        print("2) minor (1.0.1 -> 1.1.0) - New features, improvements")  
        print("3) major (1.0.1 -> 2.0.0) - Breaking changes")
        print("4) skip - No release, just commit and push")
        
        choice = input("\nSelect version bump (1-4) [default: 1]: ").strip()
        version_map = {'1': 'patch', '2': 'minor', '3': 'major', '4': 'skip'}
        version_type = version_map.get(choice, 'patch')
        
        if dry_run:
            self.print_info("DRY RUN - would execute:")
            print(f"  Commit: {commit_msg}")
            print(f"  Version bump: {version_type}")
            if version_type != 'skip':
                current_version = self.get_current_version()
                new_version = self.bump_version(current_version, version_type)
                print(f"  New version: {new_version}")
            return True
            
        # Execute workflow
        return self._execute_workflow(commit_msg, version_type, analysis)
        
    def _confirm(self, question: str, default: bool = True) -> bool:
        """Ask for user confirmation"""
        suffix = " (Y/n): " if default else " (y/N): "
        response = input(question + suffix).strip().lower()
        
        if not response:
            return default
        return response.startswith('y')
        
    def _execute_workflow(self, commit_msg: str, version_type: str, analysis: Dict[str, any]) -> bool:
        """Execute the complete workflow"""
        try:
            # Stage changes
            self.print_info("Staging changes...")
            success, output = self.run_git_command(['add', '.'])
            if not success:
                self.print_error(f"Failed to stage changes: {output}")
                return False
            self.print_status("Changes staged")
            
            # Commit changes
            self.print_info("Committing changes...")
            success, output = self.run_git_command(['commit', '-m', commit_msg])
            if not success:
                self.print_error(f"Commit failed: {output}")
                return False
            self.print_status("Changes committed")
            
            # Push changes
            self.print_info("Pushing to origin...")
            success, output = self.run_git_command(['push'], capture_output=False)
            if not success:
                self.print_error(f"Push failed: {output}")
                return False
            self.print_status("Changes pushed to remote")
            
            # Create release if requested
            if version_type != 'skip':
                return self._create_release(version_type, analysis, commit_msg)
                
            return True
            
        except Exception as e:
            self.print_error(f"Workflow failed: {e}")
            return False
            
    def _create_release(self, version_type: str, analysis: Dict[str, any], commit_msg: str) -> bool:
        """Create a new release"""
        try:
            self.print_info("Creating release...")
            
            current_version = self.get_current_version()
            new_version = self.bump_version(current_version, version_type)
            release_notes = self.generate_release_notes(new_version, analysis, commit_msg)
            
            # Create and push tag
            success, output = self.run_git_command(['tag', '-a', new_version, '-m', release_notes])
            if not success:
                self.print_error(f"Failed to create tag: {output}")
                return False
            self.print_status(f"Tag {new_version} created")
            
            success, output = self.run_git_command(['push', 'origin', new_version], capture_output=False)
            if not success:
                self.print_error(f"Failed to push tag: {output}")
                return False
            self.print_status("Tag pushed to remote")
            
            # Create GitHub release if gh CLI is available
            if subprocess.run(['which', 'gh'], capture_output=True).returncode == 0:
                self.print_info("Creating GitHub release...")
                try:
                    subprocess.run(['gh', 'release', 'create', new_version, 
                                  '--title', new_version, '--notes', release_notes], 
                                 check=True, capture_output=True)
                    self.print_status(f"GitHub release created: {new_version}")
                except subprocess.CalledProcessError:
                    self.print_warning("GitHub release creation failed (tag still created)")
            else:
                self.print_warning("GitHub CLI not available - tag created but no release")
                
            return True
            
        except Exception as e:
            self.print_error(f"Release creation failed: {e}")
            return False
            
    def quick_gameday_commit(self) -> bool:
        """Quick gameday commit with sensible defaults"""
        analysis = self.analyze_changes()
        if not analysis['is_gameday']:
            self.print_error("No gameday data found!")
            return False
            
        commit_msg = self.generate_commit_message(analysis)
        return self._execute_workflow(commit_msg, 'patch', analysis)
        
    def quick_ops_commit(self) -> bool:
        """Quick ops commit with sensible defaults"""
        analysis = self.analyze_changes()
        commit_msg = self.generate_commit_message(analysis)
        version_type = 'minor' if analysis['is_ops'] else 'patch'
        return self._execute_workflow(commit_msg, version_type, analysis)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='UHL Auto-Commit Workflow')
    parser.add_argument('--quick-gameday', action='store_true', 
                       help='Quick gameday commit with defaults')
    parser.add_argument('--quick-ops', action='store_true',
                       help='Quick ops commit with defaults')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without executing')
    parser.add_argument('--repo-path', type=str,
                       help='Path to git repository (default: current directory)')
    
    args = parser.parse_args()
    
    try:
        auto_commit = GitAutoCommit(args.repo_path)
        
        if args.quick_gameday:
            success = auto_commit.quick_gameday_commit()
        elif args.quick_ops:
            success = auto_commit.quick_ops_commit()
        else:
            success = auto_commit.interactive_commit(args.dry_run)
            
        if success:
            auto_commit.print_header("🎉 Auto-commit workflow complete!")
            status = auto_commit.check_git_status()
            auto_commit.print_status(f"Repository: {auto_commit.repo_path.name}")
            auto_commit.print_status(f"Branch: {status['branch']}")
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
        sys.exit(1)

if __name__ == '__main__':
    main()
