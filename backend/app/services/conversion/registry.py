"""Extensible conversion rule registry for deterministic translation."""

import abc
from typing import Type

class BaseRule(abc.ABC):
    """Abstract base class for all conversion rules."""
    
    # Priority allows us to order rules. Higher priority runs first.
    priority: int = 100
    
    @classmethod
    @abc.abstractmethod
    def apply(cls, sql: str, metadata: dict) -> tuple[str, bool]:
        """Apply the conversion rule to the SQL string.
        
        Args:
            sql: The SQL string to convert.
            metadata: The metadata dictionary of the chunk.
            
        Returns:
            tuple[str, bool]: 
                - The modified SQL string.
                - A boolean indicating if the rule safely handled everything. 
                  If False, the engine will bail out to AI translation.
        """
        pass

class RuleRegistry:
    """Registry to hold and execute all deterministic conversion rules."""
    
    _rules: list[Type[BaseRule]] = []
    
    @classmethod
    def register(cls, rule_cls: Type[BaseRule]):
        """Register a new conversion rule."""
        cls._rules.append(rule_cls)
        # Sort rules descending by priority so higher runs first
        cls._rules.sort(key=lambda r: r.priority, reverse=True)
        return rule_cls

    @classmethod
    def apply_all(cls, sql: str, metadata: dict) -> tuple[str, bool]:
        """Apply all registered rules sequentially.
        
        Returns:
            tuple[str, bool]:
                - The final SQL string.
                - False if any rule bailed out (meaning AI is needed). True if fully deterministic.
        """
        current_sql = sql
        for rule in cls._rules:
            current_sql, is_safe = rule.apply(current_sql, metadata)
            if not is_safe:
                return current_sql, False
        return current_sql, True
