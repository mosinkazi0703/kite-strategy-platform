from kite_strategy_platform.runtime.synthetic import run_synthetic_paper
def test_end_to_end_synthetic_paper_session(tmp_path):
    report=run_synthetic_paper(tmp_path)
    assert report["trades"]==1 and report["resolved"]==1
