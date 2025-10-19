# 🐨 CodeKoala
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![Koala Approved](https://img.shields.io/badge/Koala-Approved-%23a67c52)](https://github.com/pieter-ohearn/codekoala)


Your Friendly, Local Code Reviewer (who prefers a nap!)

## 📌 Overview
CodeKoala is your lazy (but effective) local-first, LLM-powered code review tool that gently analyses Git changes and provides AI-driven feedback on code quality, best practices, and design principles. Perfect for the developer who wants to stay comfy without missing important code improvements. The tool is modular, supporting both local execution and future API-based LLMs.

_🐨 From Gum Trees to Git Trees – Reviewing Your Commits with Care!_

## ✨ Features
* 🧠 LLM-Powered Reviews – Get feedback on your commits without the stress of manual reviews.
* 🔍 Git Integration – Automatically ponders over your git diff changes. No need to lift a finger.
* 🚀 Runs Locally – Your code stays close, no external calls needed (privacy first, naps second).
* 🛠 Best Practice Checks – Catches code smells, anti-patterns, and design flaws (so you don't have to).
* 🗒️ Conventional Commits – Automatically generate commit messages that follow the [Conventional Commits](https://www.conventionalcommits.org/) spec.

## 🚀 Installation
Pick the option that fits your workflow—each installs the `codekoala` CLI so you can call it from any repository.

### Install from a GitHub Release (recommended)
1. Download the latest `codekoala-*.whl` from the [Releases](https://github.com/pieter-ohearn/codekoala/releases) page.
2. Install it with pip:
   ```bash
   pip install path/to/codekoala-<version>-py3-none-any.whl
   ```

### Requirements
- Python 3.10 or newer
- [Ollama](https://ollama.com/) installed locally
- Pull the recommended model:  
  ```bash
  ollama pull mistral-nemo:12b
  ```
  If you prefer a different model, set it after install with `codekoala config --model <name>`.

## 🛠 Usage

### First-Time Setup

- Verify Ollama is running:
    ```bash
    ollama list
    ```

- Configure your preferred model (default is mistral-nemo:12b):
    ```bash
    codekoala config --model mistral-nemo:12b
    ```

### Available Commands:
- `review_code`

    Review code changes before committing, comparing them with a specific branch or reviewing staged changes.

    **Example:**
    ```bash
    codekoala review_code --branch main --staged
    ```

- `generate-message`

    Automatically generate a commit message following the [Conventional Commits](https://www.conventionalcommits.org/) specification based on your Git changes.

    **Example:**
    ```bash
    codekoala generate-message --ticket 54321 --context "Refines onboarding flow" --context-file docs/release-notes.md
    ```
    This analyses staged changes, blends in any optional context, and suggests a structured commit message. Use `--prompt-only` to copy the prompt instead of calling the local model directly.

    **Helpful flags**
    - `--ticket`: Provide a ticket number upfront (e.g. `--ticket 54321`).
    - `--context`: Add free-form context; repeat for multiple notes.
    - `--context-file`: Merge the contents of supporting files into the prompt.
    - `--prompt-only`: Copy the full prompt (diff + context) to your clipboard.

- `config`

    Configure CodeKoala settings, such as selecting the LLM model to use.

    **Example to set the model:**
    ```bash
    codekoala config --model mistral-nemo:12b
    ```

    **Example to show current configuration:**
    ```bash
    codekoala config --show
    ```

### Example Workflow

1. **Check your own code before committing**  
    You can review the changes you've staged for commit using:
    ```bash
    codekoala review_code --staged
    ```
    Or, if you want to check all changes (not just staged ones), run:
    ```bash
    codekoala review_code
    ```

2. **Generate a commit message based on changes**
    Instead of manually writing a commit message, let CodeKoala handle it:
    ```bash
    codekoala generate-message --ticket 54321
    ```
    This ensures consistency and adherence to Conventional Commits.

3. **Review PRs or features compared to another branch**
    You can use CodeKoala to review the differences between your current branch and another branch, such as `develop`, to ensure your code aligns with the main branch before merging:
    ```bash
    codekoala review_code --branch develop
    ```
    This command compares your current branch to `develop` and provides suggestions for any detected changes.


_🐨 CodeKoala: Keeping Your Code Cuddly, Not Clunky!_

## 🔁 Release Workflow
Releases are automated through GitHub Actions whenever you push a tag that matches `v*.*.*`.

1. Make sure the version in `pyproject.toml` is up to date.
2. Create a tag and push it, e.g.:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
3. The `release` workflow will:
   - lint the codebase with Flake8,
   - build and upload wheel/sdist artifacts,
   - create a GitHub Release (shows up in the repository sidebar automatically).
