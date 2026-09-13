import pytest
from kite_strategy_platform.config import load_config

def test_config_loads_and_fails_closed_for_live_mode(tmp_path):
    config=load_config("config/strategy_reversal_credit.yaml", "config/paper_trading.yaml")
    assert config.trading["mode"] == "paper"
    bad=tmp_path/"bad.yaml"; bad.write_text("trading:\n  mode: live\n")
    with pytest.raises(ValueError, match="only trading.mode=paper"):
        load_config("config/strategy_reversal_credit.yaml", bad)
