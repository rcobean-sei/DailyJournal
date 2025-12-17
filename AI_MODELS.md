# AI Model Cost Comparison (Updated December 2025)

This document compares different AI models for generating daily journal entries with current pricing as of December 2025.

## Recommended Models (Cheapest to Most Expensive)

### 1. GPT-4.1-nano ⭐ **CHEAPEST OPTION**
- **Model**: `gpt-4.1-nano`
- **Cost**: $0.10 per 1M input tokens, $0.025 per 1M output tokens
- **Quality**: Basic, suitable for simple tasks
- **Best for**: Ultra-low cost, simple journal entries
- **Provider**: OpenAI
- **Note**: Very new model, may have limited availability

### 2. GPT-4o-mini ⭐ **BEST VALUE**
- **Model**: `gpt-4o-mini`
- **Cost**: $0.15 per 1M input tokens, $0.30 per 1M output tokens (some sources show $0.60)
- **Quality**: Excellent for this task - fast, cheap, good reasoning
- **Best for**: Daily use, cost-conscious users, best overall value
- **Provider**: OpenAI
- **Note**: Most cost-effective quality option

### 3. Claude 3 Haiku ⭐ **RECOMMENDED (Anthropic)**
- **Model**: `claude-3-haiku-20240307`
- **Cost**: $0.25 per 1M input tokens, $1.25 per 1M output tokens
- **Quality**: Excellent for this task - fast, cheap, good reasoning
- **Best for**: Daily use, cost-conscious users, Anthropic ecosystem
- **Provider**: Anthropic
- **Note**: Currently set as default in config

### 4. GPT-4.1-mini
- **Model**: `gpt-4.1-mini`
- **Cost**: $0.40 per 1M input tokens, $0.10 per 1M output tokens
- **Quality**: Good, newer model with optimized output pricing
- **Best for**: When output volume is high
- **Provider**: OpenAI

### 5. GPT-5 mini
- **Model**: `gpt-5-mini`
- **Cost**: $0.25 per 1M input tokens, $2.00 per 1M output tokens
- **Quality**: Better reasoning, newer generation
- **Best for**: When you want latest generation capabilities
- **Provider**: OpenAI

### 6. Claude 3.5 Haiku
- **Model**: `claude-3-5-haiku-20241022` (or similar)
- **Cost**: $0.80 per 1M input tokens, $4.00 per 1M output tokens
- **Quality**: Better than original Haiku, more capable
- **Best for**: When you want better quality than Haiku 3
- **Provider**: Anthropic

### 7. Claude 4.5 Haiku
- **Model**: `claude-4-5-haiku` (or similar)
- **Cost**: $1.00 per 1M input tokens, $5.00 per 1M output tokens
- **Quality**: Latest generation, most capable Haiku
- **Best for**: When you want the latest Claude Haiku model
- **Provider**: Anthropic

### 8. Claude 3 Sonnet
- **Model**: `claude-3-sonnet-20240229`
- **Cost**: $3 per 1M input tokens, $15 per 1M output tokens
- **Quality**: Better reasoning, more nuanced
- **Best for**: When you want higher quality journal entries
- **Provider**: Anthropic

### 9. Claude 3.5 Sonnet
- **Model**: `claude-3-5-sonnet-20241022`
- **Cost**: $3 per 1M input tokens, $15 per 1M output tokens
- **Quality**: Best quality, most nuanced understanding
- **Best for**: When quality is more important than cost
- **Provider**: Anthropic

## Cost Estimation

For a typical daily journal entry:
- **Input**: ~2,000-5,000 tokens (commits, plans, context)
- **Output**: ~500-1,000 tokens (journal entry)

**Daily cost estimates (based on 3,000 input + 750 output tokens):**

| Model | Daily Cost | Monthly Cost (30 days) | Yearly Cost |
|-------|------------|------------------------|-------------|
| GPT-4.1-nano | **$0.0003** | **$0.009** | **$0.11** |
| GPT-4o-mini | **$0.0005** | **$0.015** | **$0.18** |
| Claude 3 Haiku | **$0.0009** | **$0.027** | **$0.33** |
| GPT-4.1-mini | **$0.0012** | **$0.036** | **$0.43** |
| GPT-5 mini | **$0.0015** | **$0.045** | **$0.54** |
| Claude 3.5 Haiku | **$0.0034** | **$0.102** | **$1.22** |
| Claude 4.5 Haiku | **$0.0043** | **$0.129** | **$1.55** |
| Claude 3 Sonnet | **$0.0105** | **$0.315** | **$3.78** |
| Claude 3.5 Sonnet | **$0.0105** | **$0.315** | **$3.78** |

## Recommendation

**For this task, use GPT-5 mini** - Latest generation with excellent value:

- **GPT-5 mini**: Latest GPT generation, best value for latest models ($0.0015/day)
- **GPT-4o-mini**: Cheapest quality option ($0.0005/day) - use if cost is primary concern
- **Claude 3 Haiku**: Great Anthropic option ($0.0009/day) - use if you prefer Anthropic

**Current default: GPT-5 mini** - Latest generation capabilities at reasonable cost. At these prices, you could generate 1,000 journal entries for less than $1!

## How to Change Models

Edit `config/config.json`:

**For GPT-4o-mini (cheapest quality option):**
```json
{
  "ai_provider": "openai",
  "ai_model": "gpt-4o-mini"
}
```

**For Claude 3 Haiku (current default):**
```json
{
  "ai_provider": "anthropic",
  "ai_model": "claude-3-haiku-20240307"
}
```

**For GPT-4.1-nano (ultra-cheap):**
```json
{
  "ai_provider": "openai",
  "ai_model": "gpt-4.1-nano"
}
```

## Model Comparison for This Task

| Model | Cost/Day | Quality | Speed | Recommendation |
|-------|----------|---------|-------|----------------|
| GPT-4.1-nano | $0.0003 | ⭐⭐⭐ | ⚡⚡⚡ | ✅ Cheapest |
| GPT-4o-mini | $0.0005 | ⭐⭐⭐⭐ | ⚡⚡⚡ | ✅ **Best value** |
| Claude 3 Haiku | $0.0009 | ⭐⭐⭐⭐ | ⚡⚡⚡ | ✅ Great option |
| GPT-4.1-mini | $0.0012 | ⭐⭐⭐⭐ | ⚡⚡⚡ | ✅ Good for high output |
| GPT-5 mini | $0.0015 | ⭐⭐⭐⭐ | ⚡⚡⚡ | ✅ Latest gen |
| Claude 3.5 Haiku | $0.0034 | ⭐⭐⭐⭐ | ⚡⚡⚡ | 💎 Better quality |
| Claude 4.5 Haiku | $0.0043 | ⭐⭐⭐⭐ | ⚡⚡⚡ | 💎 Latest Claude |
| Claude 3 Sonnet | $0.0105 | ⭐⭐⭐⭐⭐ | ⚡⚡ | 💎 Premium quality |
| Claude 3.5 Sonnet | $0.0105 | ⭐⭐⭐⭐⭐ | ⚡⚡ | 💎 Premium quality |

## Notes

- Prices are per million tokens (1M = 1,000,000)
- Prices may vary slightly by region and provider
- Some models may have minimum charges or rate limits
- Always check official pricing pages for most current rates:
  - Anthropic: https://platform.claude.com/docs/about-claude/pricing
  - OpenAI: https://platform.openai.com/docs/pricing

## Cost Savings Tips

1. **Use GPT-4o-mini** - Best balance of cost and quality
2. **Limit context** - Only include relevant commits/plans
3. **Cache results** - Don't regenerate for same date
4. **Batch processing** - Process multiple days in one API call if possible
