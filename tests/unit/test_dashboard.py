import json
from kite_strategy_platform.dashboard.server import RuntimeView

def test_dashboard_reads_open_position_and_latest_mark(tmp_path):
    paper=tmp_path/'paper'; ticks=tmp_path/'data'/'raw_ticks'; paper.mkdir(); ticks.mkdir(parents=True)
    events=[
        {'at':'2026-01-01T09:00:00+00:00','event':'paper_session_start','strategies':['calendar']},
        {'at':'2026-01-01T09:01:00+00:00','event':'paper_entry','strategy_id':'calendar','margin_required':50000,'initial_cashflow_rupees':-1000,'margin_details':{'orders':[]}},
        {'at':'2026-01-01T09:02:00+00:00','event':'mark','strategy_id':'calendar','state':'OPEN','pnl_points':2,'gross_pnl_rupees':130},
    ]
    (paper/'events.jsonl').write_text('\n'.join(json.dumps(x) for x in events)+'\n',encoding='utf-8')
    snapshot=RuntimeView(tmp_path).snapshot()
    assert snapshot['positions'][0]['margin_required']==50000
    assert snapshot['positions'][0]['gross_pnl_rupees']==130
