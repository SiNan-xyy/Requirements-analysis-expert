# Git Skill Package

Use the repository root as the Git Skill source because `SKILL.md` lives at the root and references `agent_modules/`.

The Agent platform should download this repository as a skill:

```text
https://github.com/SiNan-xyy/Requirements-analysis-expert.git
```

Recommended branch:

```text
master
```

The skill uses:

- `SKILL.md`
- `agent_modules/interaction_schema/`
- `agent_modules/requirement_clarification/`
- `agent_modules/rpa_boundary_check/`
- `agent_modules/process_breakdown/`
- `agent_modules/exception_design/`
- `agent_modules/solution_packaging/`

The platform should separately upload the files in `agent_platform_package/rag_upload/` as RAG material and copy `agent_platform_package/system_prompt/agent-system-prompt.md` into the system prompt editor.
