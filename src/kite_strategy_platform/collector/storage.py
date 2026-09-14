from pathlib import Path
import json, os, tempfile

class AppendOnlyStore:
    def __init__(self, root="runtime"): self.root=Path(root)
    def append_jsonl(self, relative, records):
        path=self.root/relative; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            for record in records: f.write(json.dumps(record, default=str, separators=(",", ":"))+"\n")
    def write_table(self, relative, records):
        path=self.root/relative; path.parent.mkdir(parents=True, exist_ok=True)
        try:
            import pandas as pd
            frame=pd.DataFrame(records); fd,tmp=tempfile.mkstemp(dir=path.parent, suffix=".tmp"); os.close(fd)
            frame.to_parquet(tmp, index=False); os.replace(tmp,path)
        except ImportError:
            raise RuntimeError("Parquet storage requires pandas and pyarrow")
    def append_table(self, relative, records):
        try:
            import pandas as pd
            path=self.root/relative
            old=pd.read_parquet(path) if path.exists() else pd.DataFrame()
            self.write_table(relative,pd.concat([old,pd.DataFrame(records)],ignore_index=True).to_dict("records"))
        except ImportError:
            raise RuntimeError("Parquet storage requires pandas and pyarrow")
