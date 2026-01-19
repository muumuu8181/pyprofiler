"""
Call frame data structure
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CallFrame:
    """
    Represents a single function call in the call stack

    Attributes:
        name: Function name
        filename: Source file name
        line_no: Line number in source file
        start_time: Start timestamp (monotonic clock)
        end_time: End timestamp (monotonic clock)
        children: Child call frames (nested calls)
    """

    name: str
    filename: str
    line_no: int
    start_time: float
    end_time: float
    children: List['CallFrame'] = field(default_factory=list)

    @property
    def duration(self) -> float:
        """Total execution time including children"""
        return self.end_time - self.start_time

    @property
    def own_time(self) -> float:
        """Execution time excluding children (self time)"""
        children_time = sum(child.duration for child in self.children)
        return max(0, self.duration - children_time)

    def add_child(self, child: 'CallFrame') -> None:
        """Add a child call frame"""
        self.children.append(child)

    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'filename': self.filename,
            'line_no': self.line_no,
            'duration': self.duration,
            'own_time': self.own_time,
            'children': [child.to_dict() for child in self.children]
        }

    def __repr__(self) -> str:
        return f"CallFrame(name={self.name!r}, duration={self.duration:.6f}s)"
