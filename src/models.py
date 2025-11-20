from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

@dataclass
class WeatherRecord:
    row: Dict[str, str]
    
@dataclass
class ColumnStats:
    mean: Optional[float]
    median: Optional[float]
    mode: Optional[float]
    data_range: Optional[float]
    count: int
    
    #-------------New----------------        
    count: int = 0

    def asdict(self):
        return {
            'mean': self.mean,
            'median': self.median,
            'mode': self.mode,
            'data_range': self.data_range,
            'count': self.count,
        }
    

@dataclass
class ResultSummary:
    stats_by_column: Dict[str, ColumnStats]
    
    def to_dict(self) -> Dict[str, Any]:
        
        return {
            col: asdict(stat) for col, stat in self.stats_by_column.items()
        }  
