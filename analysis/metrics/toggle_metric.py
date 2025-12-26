"""
Toggle-based side-channel metric extraction from VCD files.
"""

from pathlib import Path
from collections import defaultdict


def extract_toggle_counts(vcd_path: Path) -> dict:
    """
    Parse a VCD file and count value toggles per signal.

    Returns:
        dict: { "hierarchical.signal.name": toggle_count }
    """

    if not vcd_path.exists():
        raise FileNotFoundError(f"VCD file not found: {vcd_path}")

    # --------------------------------------------------
    # VCD symbol → signal name mapping
    # --------------------------------------------------
    symbol_to_signal = {}

    # --------------------------------------------------
    # Last seen value per symbol
    # --------------------------------------------------
    last_value = {}

    # --------------------------------------------------
    # Toggle counters per signal
    # --------------------------------------------------
    toggle_counts = defaultdict(int)

    in_header = True

    with open(vcd_path, "r") as f:
        for line in f:
            line = line.strip()

            # ------------------------------------------
            # Header parsing
            # ------------------------------------------
            if in_header:
                if line.startswith("$var"):
                    # Example:
                    # $var wire 1 ! u_clean.noise_reg_a $end
                    parts = line.split()
                    symbol = parts[3]
                    signal_name = parts[4]

                    symbol_to_signal[symbol] = signal_name
                    last_value[symbol] = None

                elif line == "$enddefinitions $end":
                    in_header = False

                continue

            # ------------------------------------------
            # Ignore timestamps
            # ------------------------------------------
            if line.startswith("#"):
                continue

            # ------------------------------------------
            # Scalar value change: 0!, 1!
            # ------------------------------------------
            if line and line[0] in ("0", "1"):
                value = line[0]
                symbol = line[1:]

            # ------------------------------------------
            # Vector value change: b1010 !
            # ------------------------------------------
            elif line.startswith("b"):
                try:
                    value, symbol = line[1:].split()
                except ValueError:
                    continue

            else:
                continue

            # ------------------------------------------
            # Toggle detection
            # ------------------------------------------
            prev = last_value.get(symbol)

            if prev is not None and prev != value:
                signal = symbol_to_signal.get(symbol)
                if signal:
                    toggle_counts[signal] += 1

            last_value[symbol] = value

    return dict(toggle_counts)
