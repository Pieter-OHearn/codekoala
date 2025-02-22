# 🐨 CodeKoala
Your Friendly, Local Code Reviewer (who prefers a nap!)

## 📌 Overview
CodeKoala is your lazy (but effective) local-first, LLM-powered code review tool that gently analyses Git changes and provides AI-driven feedback on code quality, best practices, and design principles. Perfect for the developer who wants to stay comfy without missing important code improvements. The tool is modular, supporting both local execution and future API-based LLMs.

_🐨 From Gum Trees to Git Trees – Reviewing Your Commits with Care!_

## ✨ Features
* 🧠 LLM-Powered Reviews – Get feedback on your commits without the stress of manual reviews.
* 🔍 Git Integration – Automatically ponders over your git diff changes. No need to lift a finger.
* 🚀 Runs Locally – Your code stays close, no external calls needed (privacy first, naps second).
* 🛠 Best Practice Checks – Catches code smells, anti-patterns, and design flaws (so you don't have to).

## 🎯 How It Works
1. Install & Run – CodeKoala scans your staged changes.
2. AI-Powered Review – It lazily processes the code and suggests improvements—without making a fuss.
3. Output Suggestions – See the feedback in your terminal—just like a koala pointing out the obvious.

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
    ollama pull codellama # or your preferred model
    ```
> **Note:** If you use a different model you must set it in the config

## 🛠 Usage

### First-Time Setup

- Verify Ollama is running:
    ```bash
    ollama list
    ```

- Configure your preferred model (default is codellama):
    ```bash
    codekoala config --model codellama
    ```

### Available Commands:
- `review_code`

    Review code changes before committing, comparing them with a specific branch or reviewing staged changes.

    **Example:**
    ```bash
    codekoala review_code --branch main --staged
    ```

- `config`

    Configure codekoala settings, such as selecting the LLM model to use.

    **Example to set the model:**
    ```bash
    codekoala config --model codellama
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
2. **Review PRs or features compared to another branch**
    You can use codekoala to review the differences between your current branch and another branch, such as develop, to ensure your code aligns with the main branch before merging:
    ```bash
    codekoala review_code --branch develop
    ```
    This command compares your current branch to develop and provides suggestions for any detected changes.


_🐨 CodeKoala: Keeping Your Code Cuddly, Not Clunky!_