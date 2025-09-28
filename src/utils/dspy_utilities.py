import dspy
from dotenv import load_dotenv
import os

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY:
    raise ValueError("Please set the FIREWORKS_API_KEY environment variable.")
# fireworks_model="accounts/fireworks/models/llama-v3p1-70b-instruct"
# fireworks_model="accounts/fireworks/models/deepseek-r1"
# model = f"openai/{fireworks_model}"
r1 = "fireworks_ai/accounts/fireworks/models/deepseek-r1-0528"
v3 = "fireworks_ai/accounts/fireworks/models/deepseek-v3-0324"
qwen3 = "fireworks_ai/accounts/fireworks/models/qwen3-235b-a22b-instruct-2507"
# Default text model used across the app (non-vision)
model = qwen3

# Vision-capable model (Fireworks VLM), defined like other models (string only)
# Ref: https://fireworks.ai/docs/guides/querying-vision-language-models#best-practices
qwen2p5_vl = "fireworks_ai/accounts/fireworks/models/qwen2p5-vl-32b-instruct"
base_url = os.getenv("FIREWORKS_BASE_URL")
if not base_url:
    raise ValueError("Please set the FIREWORKS_BASE_URL environment variable.")

# lm = dspy.LM(model, api_base=base_url, api_key=FIREWORKS_API_KEY)
lm = dspy.LM(
    model,
    api_key=FIREWORKS_API_KEY,
    max_tokens=128000,
    temperature=0.7,
    cache=True,
    num_retries=8,
)

# Dedicated vision LM (for consistency of import/use)
lm_vision = dspy.LM(
    qwen2p5_vl,
    api_key=FIREWORKS_API_KEY,
    max_tokens=128000,
    temperature=0.3,
    cache=True,
    num_retries=8,
)

# test = lm("Say this is a test!")
# print(test)