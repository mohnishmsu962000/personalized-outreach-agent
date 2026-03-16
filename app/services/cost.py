# Pricing as of 2024 per 1M tokens
PRICING = {
    "gpt-4o-mini": {
        "input": 0.150 / 1_000_000,
        "output": 0.600 / 1_000_000,
    },
    "gpt-4o": {
        "input": 5.00 / 1_000_000,
        "output": 15.00 / 1_000_000,
    },
}

# Rough estimate: ~200 tokens prompt + ~100 tokens output per message
ESTIMATED_INPUT_TOKENS = 200
ESTIMATED_OUTPUT_TOKENS = 100


def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    pricing = PRICING.get(model, PRICING["gpt-4o-mini"])
    return (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])


def estimate_cost(researcher_count: int, model: str) -> dict:
    estimated_input = ESTIMATED_INPUT_TOKENS * researcher_count
    estimated_output = ESTIMATED_OUTPUT_TOKENS * researcher_count
    estimated_total_tokens = estimated_input + estimated_output
    estimated_cost = calculate_cost(estimated_input, estimated_output, model)

    return {
        "researcher_count": researcher_count,
        "estimated_tokens": estimated_total_tokens,
        "estimated_cost_usd": round(estimated_cost, 6),
        "model": model,
    }