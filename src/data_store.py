from pathlib import Path
import json, logging
from typing import Union
import aiofiles

log = logging.getLogger(__name__)

try:
    from .models import ResultSummary
except ImportError:
    from models import ResultSummary


class FileStore:
    def __init__(self, output_path: Union[str, Path]) -> None:
        p = Path(output_path)
        self.out_file = p if p.suffix else (p / "summary.json")
        # Ensure the parent directory exists
        self.out_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Original
    def save_summary(self, summary: ResultSummary) -> Path:
        """Original synchronous version - kept for comparison"""
        out = self.out_file
        tmp = out.with_name(out.name + ".tmp")  

        payload = {col: stats.asdict() for col, stats in summary.stats_by_column.items()}

        try:
            with tmp.open('w', encoding='utf-8') as f:  
                json.dump(payload, f, indent=2)
            tmp.replace(out)
            log.info("Wrote summary to %s", out.resolve())
            return out
        except OSError:
            log.exception("Failed to write summary to %s", out)
            raise
    
#------------------------------New for phase 7-----------------------------------------
    async def async_save_summary(self, summary: ResultSummary) -> Path:
        '''Async save_memory version'''
        out = self.out_file
        tmp = out.with_name(out.name + ".tmp")  

        payload = {col: stats.asdict() for col, stats in summary.stats_by_column.items()}
        json_string = json.dumps(payload, indent=2)
        
        try:
            async with aiofiles.open(tmp, mode='w', encoding='utf-8') as f:  
                await f.write(json_string)
            tmp.replace(out)
            log.info("Wrote summary to %s", out.resolve())
            return out
        except OSError:
            log.exception("Failed to write summary to %s", out)
            raise
        