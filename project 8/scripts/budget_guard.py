"""Budget Guard: Enforce retry limits and token thresholds."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class BudgetState:
    max_retries: int = 2
    token_threshold: int = 50000
    retry_count: int = 0
    tokens_used: int = 0
    exceeded: bool = False
    log: list[dict] = field(default_factory=list)

    def can_retry(self) -> bool:
        if self.exceeded:
            return False
        return self.retry_count < self.max_retries

    def check_budget(self, estimated_tokens: int) -> bool:
        """Return False if adding these tokens would exceed threshold."""
        if self.tokens_used + estimated_tokens > self.token_threshold:
            self.exceeded = True
            self._log_event("BUDGET_EXCEEDED", {
                "tokens_used": self.tokens_used,
                "attempted": estimated_tokens,
                "threshold": self.token_threshold,
            })
            return False
        return True

    def record_usage(self, tokens: int, operation: str) -> None:
        """Record token usage for an operation."""
        self.tokens_used += tokens
        self._log_event("TOKEN_USAGE", {
            "operation": operation,
            "tokens": tokens,
            "cumulative": self.tokens_used,
        })

    def increment_retry(self) -> None:
        """Increment retry counter (call once per maker-checker attempt)."""
        self.retry_count += 1

    def _log_event(self, event_type: str, details: dict) -> None:
        self.log.append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            **details,
        })

    def needs_human_intervention(self) -> bool:
        """Check if hard stop condition is met."""
        return self.exceeded or not self.can_retry()

    def to_dict(self) -> dict:
        return {
            "max_retries": self.max_retries,
            "token_threshold": self.token_threshold,
            "retry_count": self.retry_count,
            "tokens_used": self.tokens_used,
            "exceeded": self.exceeded,
            "remaining_budget": max(0, self.token_threshold - self.tokens_used),
        }


def load_budget(config_path: Path | None = None) -> BudgetState:
    """Load budget state from config or create default."""
    state = BudgetState()
    if config_path and config_path.exists():
        with open(config_path) as f:
            cfg = json.load(f)
        state.max_retries = cfg.get("max_retries", state.max_retries)
        state.token_threshold = cfg.get("token_threshold", state.token_threshold)
    return state


def save_budget(state: BudgetState, path: Path) -> None:
    """Persist budget state to file."""
    with open(path, "w") as f:
        json.dump(state.to_dict(), f, indent=2)


if __name__ == "__main__":
    bg = BudgetState()
    print(json.dumps(bg.to_dict(), indent=2))
