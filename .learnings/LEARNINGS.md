## [LRN-20260218-001] tool_parameter_memory

**Logged**: 2026-02-18T08:20:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Repeatedly forgot to include `file_path` parameter in `write` tool calls, causing 5+ consecutive failures.

### Details
When using the `write` tool to create/update files, I kept passing only `content` and omitting `file_path` (or `path`). This caused:
- Error: "Missing required parameter: path (path or file_path). Supply correct parameters before retrying."
- Wasted 5+ attempts
- User frustration
- Delayed task completion

The tool schema requires:
```json
{
  "file_path": "string",  // OR "path": "string"
  "content": "string"
}
```

I was only passing `content`.

### Root Cause
- Tool calling pattern didn't automatically remind me of required params
- Long context distracted from parameter checklist
- Didn't verify success/failure before retrying same mistake

### Suggested Action
1. **Before every `write` call**: Explicitly verify `file_path` is present
2. **Create mental checklist**: Content? File path? Both present?
3. **Alternative**: Use `exec` with `cat` or `echo` for complex files (more reliable)
4. **Verify**: Check tool response before assuming success

### Metadata
- Source: user_feedback
- Related Files: paper_trader.py
- Tags: tool_usage, parameter_error, repetitive_mistake

---
