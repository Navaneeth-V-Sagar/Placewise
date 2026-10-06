# PLACEWISE — Technical Failure Analysis & Post-Mortem

This document records genuine engineering failures encountered during the implementation of PLACEWISE, the diagnostic evidence, root cause analysis, corrective actions, and architectural learnings.

---

## Case 1: Ollama Grammar Constraints vs Qwen3 Reasoning Tokens

### Problem
During Phase 3 AI client integration testing, calls to `ai_client.generate_structured` consistently timed out after 60 seconds.

### Evidence
```text
httpcore.ReadTimeout: timed out
E   app.ai.client.OllamaTimeoutError: Inference request to Ollama timed out after 60.0s.
FAILED backend/tests/test_ai_client.py::test_ollama_structured_generation_minimal[asyncio]
```

### Root Cause
`qwen3:4b` is a reasoning model that emits `<think>...</think>` tokens at token step 0 before outputting its final response. When the Ollama API was invoked with `"format": "json"`, Ollama enforced a strict JSON grammar parser from token 0. Because `<think>` starts with `<` (which is invalid at the start of a JSON object or array `{` or `[`), Ollama's constrained grammar sampler became deadlocked trying to reconcile the model's logits with the rigid grammar mask.

### Initial Approach
Passing `"format": "json"` directly in the Ollama request payload and relying on Ollama's internal grammar sampler.

### Fix
1. Removed the conflicting `"format": "json"` parameter from the HTTP request to allow Qwen3's reasoning tokens to emit naturally.
2. Formatted system prompts with explicit JSON schema instructions.
3. Configured `num_predict: 1024` and a resilient `120.0s` timeout.
4. Implemented `OllamaClient.clean_json_text()` with regex stripping:
   ```python
   # Strip reasoning tags
   cleaned = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.DOTALL)
   # Extract pure JSON payload
   fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, flags=re.IGNORECASE)
   ```
5. Enforced validation via Pydantic `model_validate` with an automated 1-step repair fallback.

### Result
Model inference completed with 100% structured schema compliance across all test suites without timeouts.

### Learning
Reasoning LLMs requires token headroom for internal thinking. Post-generation schema extraction and sanitization is significantly more reliable than rigid token-level grammar masks on reasoning architectures.

---

## Case 2: Per-Line Trailing Whitespace in PDF Text Cleaning

### Problem
In Phase 4, the resume text normalization unit test `test_clean_text_normalization` failed with an assertion mismatch on line breaks.

### Evidence
```text
AssertionError: assert 'John Doe \n\n...gineer Python' == 'John Doe\n\n...gineer Python'
  - John Doe 
  ?         -
  + John Doe
```

### Root Cause
The initial text cleaning pipeline used global string substitutions:
`text = re.sub(r'[ ]+', ' ', text)`. While this collapsed consecutive interior spaces, trailing spaces at the end of individual lines prior to `\n` characters remained intact.

### Initial Approach
Document-level global regex replacement.

### Fix
Implemented line-by-line stripping prior to document reassembly:
```python
lines = [re.sub(r'[ ]+', ' ', line).strip() for line in text.splitlines()]
text = '\n'.join(lines)
text = re.sub(r'\n{3,}', '\n\n', text)
```

### Result
Unit tests passed immediately, producing clean, normalized strings for downstream LLM prompts.

### Learning
Unstructured document extraction (especially from PDF streams) contains irregular line-break artifacts; whitespace normalization must enforce per-line boundary sanitization.

---

## Case 3: Tailwind CSS v4 Vite PostCSS Migration

### Problem
During Phase 11 frontend bundling, `npm run build` failed with a PostCSS configuration error.

### Evidence
```text
Error: [postcss] It looks like you're trying to use `tailwindcss` directly as a PostCSS plugin. 
The PostCSS plugin has moved to a separate package...
```

### Root Cause
Tailwind CSS v4 moved away from the legacy `postcss.config.js` plugin architecture and now uses a native Vite compiler plugin `@tailwindcss/vite`.

### Initial Approach
Legacy Tailwind v3 configuration with `tailwind.config.js` and `postcss.config.js`.

### Fix
1. Installed `@tailwindcss/vite`.
2. Registered `tailwindcss()` in `frontend/vite.config.js`.
3. Replaced directive imports with `@import "tailwindcss";` in `src/index.css`.
4. Removed deprecated config files.

### Result
Frontend builds cleanly in 492ms with zero errors.

### Learning
Always utilize modern tooling integrations (e.g., native Vite plugins) to maintain minimal configuration overhead and fast build cycles.
