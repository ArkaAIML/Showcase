"""
GIT_PUSH_AGENT.PY - Git Push Automation
Automatically commits and pushes generated portfolio to git
"""

import subprocess
import os
from pathlib import Path
from agno.agent import Agent
from agno.run import RunContext


class BaseGitAgent(Agent):
    """Shared git utilities"""

    def _run_git(self, args):
        return subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
        )

    def _ensure_git_repo(self):
        try:
            self._run_git(["git", "rev-parse", "--is-inside-work-tree"])
        except subprocess.CalledProcessError:
            raise RuntimeError("Not inside a git repository")

    def _git_add(self, path: str | Path):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File or directory not found: {path}")

        self._run_git(["git", "add", str(path)])

    def _git_commit(self, name: str):
        commit_msg = f"Add portfolio for {name}"

        status = self._run_git(["git", "status", "--porcelain"])
        if not status.stdout.strip():
            return False

        self._run_git(["git", "commit", "-m", commit_msg])
        return True

    def _git_push(self, branch: str | None = None):
        if branch:
            self._run_git(["git", "push", "-u", "origin", branch])
        else:
            self._run_git(["git", "push"])


class GitPushAgent(BaseGitAgent):
    """Simple commit and push to current branch"""

    name = "git_push_agent"

    def run(self, ctx: RunContext):
        self._ensure_git_repo()

        final_output = ctx.state.get("final_output")
        profile = ctx.state.get("profile", {})

        if not final_output:
            raise ValueError("No output file to commit")

        name = profile.get("name", "User")

        try:
            self._git_add(final_output)
            committed = self._git_commit(name)

            if committed:
                self._git_push()
                ctx.state["git_status"] = "✅ Pushed to GitHub"
            else:
                ctx.state["git_status"] = "ℹ️ No changes to commit"

        except Exception as e:
            ctx.state["git_status"] = f"❌ Git push failed: {e}"
            raise


class GitPushAgentAdvanced(BaseGitAgent):
    """
    Advanced version with branch creation and optional GitHub Pages deployment
    """

    name = "git_push_agent_advanced"

    def __init__(self, branch_name="portfolio", enable_gh_pages=False):
        super().__init__()
        self.branch_name = branch_name
        self.enable_gh_pages = enable_gh_pages

    def run(self, ctx: RunContext):
        self._ensure_git_repo()

        final_output = ctx.state.get("final_output")
        profile = ctx.state.get("profile", {})

        if not final_output:
            raise ValueError("No output file to commit")

        name = profile.get("name", "user").replace(" ", "-").lower()
        branch = f"{self.branch_name}-{name}"

        try:
            self._checkout_branch(branch)
            self._git_add(final_output)
            self._git_commit(name)
            self._git_push(branch)

            if self.enable_gh_pages:
                self._setup_gh_pages(branch)

            ctx.state["git_status"] = f"✅ Pushed to branch: {branch}"
            ctx.state["git_branch"] = branch

        except Exception as e:
            ctx.state["git_status"] = f"❌ Git push failed: {e}"
            raise

    def _checkout_branch(self, branch: str):
        branches = self._run_git(["git", "branch", "--list", branch])

        if branches.stdout.strip():
            self._run_git(["git", "checkout", branch])
        else:
            self._run_git(["git", "checkout", "-b", branch])

    def _setup_gh_pages(self, branch: str):
        try:
            subprocess.run(
                ["gh", "pages", "enable", "--branch", branch],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "GitHub Pages setup failed. Ensure `gh` CLI is installed and authenticated."
            ) from e
