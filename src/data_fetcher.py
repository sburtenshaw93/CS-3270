from abc import ABC, abstractmethod
from pathlib import Path
import csv, logging
import aiofiles
from typing import List, Dict, Iterator, Union

try:
    from .models import WeatherRecord
except ImportError:
    from models import WeatherRecord

class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self) -> List[WeatherRecord]:
        pass

class CSVFetcher(BaseFetcher):
    def __init__(self, path: str | Path, encoding: str = "utf-8") -> None:
        self.path = Path(path)
        self.encoding = encoding

    def fetch(self) -> List[WeatherRecord]:
        if not self.path.exists():
            raise FileNotFoundError(f"CSV not found: {self.path}")
        records: List[WeatherRecord] = []
        with self.path.open("r", encoding=self.encoding, newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header row.")
            for row in reader:
                records.append(WeatherRecord(row=row))
        return records

#--------------------New--------------------
log = logging.getLogger(__name__)
PathLike = Union[str, Path]
# Added generator to yield one row at a time
def iter_csv_records(path: PathLike, *, encoding: str ='utf-8', dialect: str ='excel') -> Iterator[Dict[str, str]]:
    path = Path(path)
    if not path.exists():
        log.error("CSV file not found: %s", path)
        raise FileNotFoundError(f"CSV not found: {path}")
    
    try:
        with path.open('r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f, dialect=dialect)
            if not reader.fieldnames:
                raise ValueError("CSV header row is missing or unreadable.")
            
            reader.fieldnames = [h.strip() if isinstance(h, str) else h for h in reader.fieldnames]
            
            for i, row in enumerate(reader, start=2):
                if not any((v or "").strip() for v in row.values()):
                    log.warning("Skipping empty row at line %d", i)
                    continue
                
                clean = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
                yield clean
                
    except UnicodeDecodeError:
        log.exception("Encoding error reading %s", path)
        raise
    except csv.Error as e:
        log.exception("CSV parse error in %s: %s", path, e)
        raise
    
# ------------------------- New for phase 7----------------------------------------
async def async_read_csv_records(path: PathLike, *, encoding: str ='utf-8', dialect: str ='excel') -> Iterator[Dict[str, str]]:
    """Added the async version for reading a csv file"""
    path = Path(path)
    if not path.exists():
        log.error("CSV file not found: %s", path)
        raise FileNotFoundError(f"CSV not found: {path}")
    
    try:
        async with aiofiles.open(path, 'r', encoding=encoding, newline='') as f:
            contents = await f.read()
        
        # Splitting the contents into lines and parse as CSV
        lines = contents.splitlines()
        reader = csv.DictReader(lines, dialect=dialect)
        
        #Validate header row
        if not reader.fieldnames:
            raise ValueError("CSV header row is missing or unreadable")
            
        reader.fieldnames = [h.strip() if isinstance(h, str) else h for h in reader.fieldnames]
        
        records = []
            
        for i, row in enumerate(reader, start=2):
            if not any((v or "").strip() for v in row.values()):
                log.warning("Skipping empty row at line %d", i)
                continue
            
            clean = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            records.append(clean)
        
        log.info("Successfully read %d records from %s, len(records), path")
        return records
                
    except UnicodeDecodeError:
        log.exception("Encoding error reading %s", path)
        raise
    except csv.Error as e:
        log.exception("CSV parse error in %s: %s", path, e)
        raise