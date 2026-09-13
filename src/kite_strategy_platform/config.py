from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

class TriggerConfig(BaseModel):
    percentage: float = Field(gt=0)
    scan_start: str = "10:00:00"
    entry_cutoff: str = "14:30:00"
    ambiguous_candle_action: str = "skip"

class ExitRule(BaseModel):
    enabled: bool = True
    type: str = "percentage_of_initial_credit"
    value: float = Field(ge=0)

class StrategyConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    underlying: str
    quantity: dict[str, int] = {"lots": 1}
    trigger: TriggerConfig
    exits: dict[str, Any]

class AppConfig(BaseModel):
    strategy: StrategyConfig
    trading: dict[str, str] = {"mode": "paper"}
    runtime: dict[str, str] = {"root": "runtime"}

    @field_validator("trading")
    @classmethod
    def paper_only(cls, value):
        if value.get("mode") != "paper":
            raise ValueError("only trading.mode=paper is implemented; failing closed")
        return value

def load_config(strategy_path: str | Path, trading_path: str | Path | None = None) -> AppConfig:
    data = yaml.safe_load(Path(strategy_path).read_text(encoding="utf-8"))
    if trading_path:
        data.update(yaml.safe_load(Path(trading_path).read_text(encoding="utf-8")) or {})
    return AppConfig.model_validate(data)
