from pathlib import Path
import json, os, tempfile, uuid

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
    def append_parquet_part(self, relative_directory, records):
        """Append an immutable Parquet part without reopening/replacing prior data.

        A unique destination avoids Windows file locks on a shared ``candles.parquet``
        file. A failed write can leave only an ignored temporary file.
        """
        try:
            import pandas as pd
            directory=self.root/relative_directory; directory.mkdir(parents=True,exist_ok=True)
            final=directory/f"part-{uuid.uuid4().hex}.parquet"
            fd,tmp=tempfile.mkstemp(dir=directory,suffix=".tmp"); os.close(fd)
            try:
                pd.DataFrame(records).to_parquet(tmp,index=False)
                os.replace(tmp,final)
            finally:
                if os.path.exists(tmp): os.unlink(tmp)
            return final
        except ImportError:
            raise RuntimeError("Parquet storage requires pandas and pyarrow")
