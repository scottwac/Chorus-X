# Chorus - Supported AI Models

This document lists all AI models currently supported by Chorus.

## OpenAI Models

### GPT-5 Series (Latest)
- **gpt-5-2025-08-07** - GPT-5 snapshot from August 2025
- **gpt-5-nano** - Compact, efficient GPT-5 variant
- **gpt-5-nano-2025-08-07** - GPT-5 nano snapshot from August 2025

### GPT-4 Series
- **gpt-4o** - GPT-4 Optimized (with vision capabilities)
- **gpt-4o-mini** - Compact GPT-4o variant
- **gpt-4-turbo** - Enhanced GPT-4 with better speed
- **gpt-4** - Standard GPT-4

### GPT-3.5 Series
- **gpt-3.5-turbo** - Fast and efficient GPT-3.5

---

## Anthropic Claude Models

### Claude 3.7 (Newest)
- **claude-3-7-sonnet-20250219** - Latest Claude 3.7 Sonnet

### Claude 3.5
- **claude-3-5-sonnet-20241022** - Claude 3.5 Sonnet (October 2024)
- **claude-3-5-sonnet-20240620** - Claude 3.5 Sonnet (June 2024)
- **claude-3-5-haiku-20241022** - Claude 3.5 Haiku (fast)

### Claude 3
- **claude-3-opus-20240229** - Most capable Claude 3 model
- **claude-3-sonnet-20240229** - Balanced Claude 3 model
- **claude-3-haiku-20240307** - Fastest Claude 3 model

---

## Groq Models

### Llama Series
- **llama-3.3-70b-versatile** - Llama 3.3 70B parameter model
- **llama-3.1-70b-versatile** - Llama 3.1 70B parameter model
- **llama-3.1-8b-instant** - Fast Llama 3.1 8B model

### Other Models
- **mixtral-8x7b-32768** - Mixtral mixture of experts model
- **gemma2-9b-it** - Google's Gemma 2 instruction-tuned

---

## Model Selection Tips

### For Responder LLMs (Generating Answers)
- **Best Quality**: GPT-5 series, Claude 3.7 Sonnet, Claude 3.5 Sonnet
- **Balanced**: GPT-4o, Claude 3.5 Haiku, Llama 3.3 70B
- **Fast & Efficient**: GPT-4o-mini, GPT-5 nano, Llama 3.1 8B

### For Evaluator LLMs (Voting on Best Answer)
- **Recommended**: Claude 3.7 Sonnet, Claude 3.5 Sonnet, GPT-5
- **Alternative**: GPT-4o, Claude 3.5 Haiku
- **Budget-Friendly**: GPT-4o-mini, Llama 3.1 70B

### Chorus Configuration Examples

**Premium Setup** (Best Quality)
- Responders: GPT-5, Claude 3.7 Sonnet, Claude 3.5 Sonnet
- Evaluators: Claude 3.7 Sonnet, GPT-5

**Balanced Setup** (Quality + Speed)
- Responders: GPT-4o, Claude 3.5 Sonnet, Llama 3.3 70B
- Evaluators: Claude 3.5 Sonnet, GPT-4o

**Fast Setup** (Speed Priority)
- Responders: GPT-4o-mini, GPT-5 nano, Llama 3.1 8B
- Evaluators: GPT-4o-mini, Claude 3.5 Haiku

**Diverse Setup** (Multiple Perspectives)
- Responders: GPT-5, Claude 3.7 Sonnet, Llama 3.3 70B, Mixtral
- Evaluators: Claude 3.7 Sonnet, GPT-5, Claude 3.5 Sonnet

---

## API Requirements

Make sure your `.env` file contains valid API keys:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
```

**Note**: You only need API keys for the providers you plan to use.

---

## Model Updates

Models are regularly updated by their providers. This list reflects the models available as of the latest Chorus update. Check the provider documentation for the most current model information:

- **OpenAI**: https://platform.openai.com/docs/models
- **Anthropic**: https://docs.anthropic.com/claude/docs/models-overview
- **Groq**: https://console.groq.com/docs/models

