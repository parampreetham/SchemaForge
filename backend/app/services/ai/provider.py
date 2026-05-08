"""AI Provider Abstraction layer using LiteLLM."""

import os
import structlog
from typing import Tuple
from decimal import Decimal

import litellm
# Optional: litellm.success_callback = ["langfuse"] or similar for observability

logger = structlog.get_logger()

class AIProvider:
    """Wrapper around LiteLLM for text generation and cost calculation."""

    @classmethod
    def generate(cls, model: str, system_prompt: str, user_prompt: str) -> Tuple[str, int, int, Decimal]:
        """Generate response from the LLM.
        
        Args:
            model: The litellm compatible model string (e.g., 'gpt-4o', 'claude-3-opus-20240229').
            system_prompt: System context instructions.
            user_prompt: User prompt content.
            
        Returns:
            Tuple containing:
                - response content (str)
                - input tokens (int)
                - output tokens (int)
                - cost in USD (Decimal)
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            logger.info("Calling LLM", model=model)
            # litellm will use environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY)
            response = litellm.completion(
                model=model,
                messages=messages,
                temperature=0.1, # Low temperature for code translation
                # set mock response if no api key in test environment
                mock_response=cls._get_mock_response() if os.environ.get("TESTING") else None
            )
            
            content = response.choices[0].message.content
            usage = response.usage
            in_tokens = usage.prompt_tokens
            out_tokens = usage.completion_tokens
            
            # litellm cost calculation
            try:
                cost = litellm.completion_cost(completion_response=response)
                cost_usd = Decimal(str(cost)) if cost else Decimal("0.00")
            except Exception:
                cost_usd = Decimal("0.00")
                
            return content, in_tokens, out_tokens, cost_usd
            
        except Exception as e:
            logger.exception("LLM generation failed", model=model, error=str(e))
            raise

    @classmethod
    def _get_mock_response(cls):
        """Used strictly during automated tests when NO API key is available."""
        return "```sql\nCREATE PROCEDURE P1 AS\nBEGIN\nEND;\n```"
