"""AI Translation Engine."""

import re
import os
from decimal import Decimal
from typing import Tuple
import structlog

from app.services.ai.prompts import get_prompt
from app.services.ai.provider import AIProvider

logger = structlog.get_logger()

class AIEngine:
    """Orchestrates AI translation and response parsing."""
    
    DEFAULT_MODEL = os.environ.get("AI_MODEL", "gpt-4o")
    PROMPT_VERSION = "v1.0"
    
    # Regex to extract code between ```sql and ```
    SQL_BLOCK_PATTERN = re.compile(r"```(?:sql)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)

    @classmethod
    def translate(cls, original_sql: str, object_type: str) -> Tuple[str | None, dict]:
        """Translates DB2 to Azure SQL using LLM.
        
        Returns:
            Tuple containing:
                - converted_sql (str or None)
                - interaction_metrics (dict) with tokens, cost, confidence, prompts
        """
        sys_prompt, usr_prompt = get_prompt(cls.PROMPT_VERSION, object_type, original_sql)
        
        try:
            content, in_tokens, out_tokens, cost = AIProvider.generate(
                model=cls.DEFAULT_MODEL,
                system_prompt=sys_prompt,
                user_prompt=usr_prompt
            )
        except Exception as e:
            logger.error("AIEngine failed to get provider response", error=str(e))
            raise
            
        extracted_sql = cls._extract_sql(content)
        
        if not extracted_sql:
            # Fallback if no block found: assume the whole string is the SQL
            extracted_sql = content.strip()
            
        confidence = cls._calculate_confidence(original_sql, extracted_sql, content)
        
        metrics = {
            "model": cls.DEFAULT_MODEL,
            "prompt_version": cls.PROMPT_VERSION,
            "system_prompt": sys_prompt,
            "user_prompt": usr_prompt,
            "response": content,
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "cost_usd": cost,
            "confidence_score": Decimal(str(confidence)),
            "latency_ms": 0 # Tracked by worker
        }
        
        return extracted_sql, metrics

    @classmethod
    def _extract_sql(cls, response_content: str) -> str | None:
        """Extract SQL from markdown code blocks."""
        match = cls.SQL_BLOCK_PATTERN.search(response_content)
        if match:
            return match.group(1).strip()
        return None

    @classmethod
    def _calculate_confidence(cls, original: str, converted: str, full_response: str) -> float:
        """Naive heuristic for confidence score."""
        score = 0.95
        
        # Deduct for warning phrases
        warnings = ["note:", "warning", "assumed", "attention", "sorry"]
        if any(w in full_response.lower() for w in warnings):
            score -= 0.05
            
        # Deduct for massive length differences (assuming DB2 and T-SQL should be somewhat similar in size)
        orig_len = len(original.strip())
        conv_len = len(converted.strip())
        
        if orig_len > 0:
            ratio = conv_len / orig_len
            if ratio > 3.0 or ratio < 0.3:
                score -= 0.10
                
        return round(max(0.0, score), 2)
