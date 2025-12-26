"""
Toggle-based side-channel metric extraction from VCD files
with full hierarchical scope support.
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

    symbol_to_signal = {}
    last_value = {}
    toggle_counts = defaultdict(int)

    scope_stack = []
    in_header = True

    with open(vcd_path, "r") as f:
        for line in f:
            line = line.strip()

            # -------------------------------
            # Header parsing (scope aware)
            # -------------------------------
            if in_header:

                if line.startswith("$scope"):
                    # Example: $scope module u_clean $end
                    parts = line.split()
                    scope_stack.append(parts[2])

                elif line.startswith("$upscope"):
                    if scope_stack:
                        scope_stack.pop()

                elif line.startswith("$var"):
                    # Example: $var wire 1 ! noise_reg_a $end
                    parts = line.split()
                    symbol = parts[3]
                    leaf_name = parts[4]

                    full_name = ".".join(scope_stack + [leaf_name])
                    symbol_to_signal[symbol] = full_name
                    last_value[symbol] = None

                elif line == "$enddefinitions $end":
                    in_header = False

                continue

            # -------------------------------
            # Ignore timestamps
            # -------------------------------
            if line.startswith("#"):
                continue

            # -------------------------------
            # Scalar value change
            # -------------------------------
            if line and line[0] in ("0", "1"):
                value = line[0]
                symbol = line[1:]

            # -------------------------------
            # Vector value change
            # -------------------------------
            elif line.startswith("b"):
                try:
                    value, symbol = line[1:].split()
                except ValueError:
                    continue
            else:
                continue

            prev = last_value.get(symbol)

            if prev is not None and prev != value:
                signal = symbol_to_signal.get(symbol)
                if signal:
                    toggle_counts[signal] += 1

            last_value[symbol] = value

    return dict(toggle_counts)
