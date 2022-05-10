from dataclasses import dataclass
from typing import List



@dataclass
class TimeSlotTableData:
    start_time: str
    end_time: str
    day_id: int

@dataclass
class SemesterOfferTableData:

    section: str
    capacity: int
    classroom: str
    professor: List[str]
    slots: List[TimeSlotTableData]






