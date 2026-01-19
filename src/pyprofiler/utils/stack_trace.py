"""
Stack trace utilities for profiling
"""
import inspect
from typing import Optional, Tuple


class StackTrace:
    """Utilities for extracting and managing stack traces"""

    @staticmethod
    def get_current_frame_info() -> Tuple[str, str, int]:
        """
        Get information about the current function call

        Returns:
            Tuple of (function_name, filename, line_number)
        """
        frame = inspect.currentframe()

        # Skip this function's frame and the caller's frame
        # to get the actual function being profiled
        if frame is not None:
            frame = frame.f_back
            if frame is not None:
                frame = frame.f_back

        if frame is None:
            return ("unknown", "unknown", 0)

        code = frame.f_code
        function_name = code.co_name
        filename = code.co_filename
        line_no = frame.f_lineno

        return (function_name, filename, line_no)

    @staticmethod
    def get_frame_info(depth: int = 1) -> Tuple[str, str, int]:
        """
        Get frame information at specified depth

        Args:
            depth: Stack depth (0 = current function, 1 = caller, etc.)

        Returns:
            Tuple of (function_name, filename, line_number)
        """
        frame = inspect.currentframe()

        # Navigate to the desired depth
        # depth + 1 to skip get_frame_info itself
        for _ in range(depth + 1):
            if frame is not None:
                frame = frame.f_back

        if frame is None:
            return ("unknown", "unknown", 0)

        code = frame.f_code
        return (code.co_name, code.co_filename, frame.f_lineno)

    @staticmethod
    def format_frame(name: str, filename: str, line_no: int) -> str:
        """Format frame information as a string"""
        # Shorten filename if it's too long
        if len(filename) > 30:
            filename = "..." + filename[-27:]
        return f"{name} ({filename}:{line_no})"
