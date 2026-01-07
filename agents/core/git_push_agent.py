"""
GIT_PUSH_AGENT.PY - Git Push Automation
Automatically commits and pushes generated portfolio to git
"""

import subprocess
import os
from agno.agent import Agent
from agno.run import RunContext


class BaseGitAgent(Agent):
    """Shared git utilities"""

    def _run_git(self, args):
        return subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True
        )

    def _git_add(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        self._run_git(["git", "add", file_path])
        print(f"📝 Added {file_path} to git")

    def _git_commit(self, name: str):
        commit_msg = f"Add portfolio for {name}"

        # Check if there is anything to commit
        status = self._run_git(["git", "status", "--porcelain"])
        if not status.stdout.strip():
            print("ℹ️ No changes to commit")
            return

        self._run_git(["git", "commit", "-m", commit_msg])
        print(f"💾 Committed: {commit_msg}")

    def _git_push(self, branch: str | None = None):
        if branch:
            self._run_git(["git", "push", "-u", "origin", branch])
        else:
            self._run_git(["git", "push"])

        print("🚀 Pushed to remote repository")


class GitPushAgent(BaseGitAgent):
    """Simple commit and push to current branch"""

    name = "git_push_agent"

    def run(self, ctx: RunContext):
        final_output = ctx.state.get("final_output")
        profile = ctx.state.get("profile", {})

        if not final_output:
            raise ValueError("No output file to commit")

        name = profile.get("name", "User")

        try:
            self._git_add(final_output)
            self._git_commit(name)
            self._git_push()

            ctx.state["git_status"] = "✅ Pushed to GitHub"
            print("✅ Portfolio pushed to GitHub successfully!")

        except Exception as e:
            ctx.state["git_status"] = f"❌ Git push failed: {e}"
            print(f"⚠️ Git push failed: {e}")


class GitPushAgentAdvanced(BaseGitAgent):
    """
    Advanced version with branch creation and GitHub Pages deployment
    """

    name = "git_push_agent_advanced"

    def __init__(self, branch_name="portfolio", enable_gh_pages=False):
        super().__init__()
        self.branch_name = branch_name
        self.enable_gh_pages = enable_gh_pages

    def run(self, ctx: RunContext):
        final_output = ctx.state.get("final_output")
        profile = ctx.state.get("profile", {})

        if not final_output:
            raise ValueError("No output file to commit")

        name = profile.get("name", "User").replace(" ", "-").lower()
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

            print(f"✅ Portfolio pushed to branch: {branch}")

        except Exception as e:
            ctx.state["git_status"] = f"❌ Git push failed: {e}"
            print(f"⚠️ Git push failed: {e}")

    def _checkout_branch(self, branch: str):
        branches = self._run_git(["git", "branch", "--list", branch])

        if branches.stdout.strip():
            self._run_git(["git", "checkout", branch])
            print(f"🌿 Switched to branch: {branch}")
        else:
            self._run_git(["git", "checkout", "-b", branch])
            print(f"🌿 Created branch: {branch}")

    def _setup_gh_pages(self, branch: str):
        try:
            subprocess.run(
                ["gh", "pages", "enable", "--branch", branch],
                check=True,
                capture_output=True,
                text=True
            )
            print("🌐 GitHub Pages enabled!")
        except Exception:
            print("⚠️ GitHub Pages setup requires GitHub CLI (`gh`) and repo access")
