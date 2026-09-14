from kite_strategy_platform.collector.live import LiveCollector
def test_expand_updates_contract_mapping_without_live_socket(tmp_path):
    c=LiveCollector([1],tmp_path); c.expand([(2,"contract-2")])
    assert c.tokens==[1,2] and c.token_to_contract[2]=="contract-2"
