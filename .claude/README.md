# 🛠️ Naveed-Tech-Lab Skills (Anthropic Implementation)

> **Note:** This repository contains Anthropic's implementation of skills for Claude. For information about the Agent Skills standard, visit [agentskills.io](http://agentskills.io).

---

## 🌟 Overview
**Skills** are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. They teach Claude how to complete tasks in a repeatable way.

### 🚀 Key Capabilities
* **Creative:** Art, music, and design.
* **Technical:** Testing web apps and MCP server generation.
* **Enterprise:** Branding, communications, and workflows.
* **Document:** Native document capabilities for Word, PDF, Excel, and PPT.

---

## 📁 Repository Structure

| Path | Purpose |
| :--- | :--- |
| [`./skills`](./skills) | Creative, Technical, and Enterprise examples. |
| [`./spec`](./spec) | The Agent Skills specification. |
| [`./template`](./template) | Basic template for creating new skills. |
| [`./skills/docx`](./skills/docx) | Document creation & editing skills. |

---

## 🛠️ How to Use

### 1️⃣ Claude Code
Run the following command in Claude Code to add the marketplace:
```bash
/plugin marketplace add anthropics/skills
