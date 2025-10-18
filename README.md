# 🐨 CodeKoala
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-%23FE5196?logo=conventionalcommits&logoColor=white)](https://conventionalcommits.org)
[![Koala Approved](https://img.shields.io/badge/Koala-Approved-%23a67c52)](https://github.com/POH8479/codekoala)


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
Ready to get started? Here’s how to bring CodeKoala into your project—without waking up the koala:

### 1. Install the package

You can install `codekoala` locally using pip in editable mode:

```bash
pip install -e .
```
### 2. Install dependencies
Ensure all necessary dependencies are installed:
```bash
pip install click ollama GitPython rich
```

### 3. Ollama Installation Required
- Install Ollama from [ollama.ai](https://ollama.com/)
- After installation, pull the desired model:
    ```bash
    ollama pull mistral-nemo:12b # recommended default model
    ```
> **Note:** If you use a different model you must set it in the config

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
