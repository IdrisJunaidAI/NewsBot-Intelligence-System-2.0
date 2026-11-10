"""Report export. Caller chooses destination; no silent publication."""
import json
from pathlib import Path

def export_json(payload,destination):
    p=Path(destination);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(payload,indent=2,ensure_ascii=False,default=str),encoding='utf8')
    return p
