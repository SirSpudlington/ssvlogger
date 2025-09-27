# pylint: disable=C0116, C0114, missing-module-docstring

def seconds_to_ms_or_s(from_log: str):
    """Converts seconds to milliseconds or seconds"""

    try:
        if float(from_log) < 1.5:
            return f"{float(from_log)*1000:.2f} ms"
        return f"{float(from_log):.2f} s"
    except ValueError:
        return f"{from_log}s"
