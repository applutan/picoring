from patterns import PATTERNS

class RingController:
    def __init__(self):
        self.patterns = PATTERNS
        self.state = {
            "idx": 0,
            "pat": self.patterns[0],   # The raw pattern from the list
            "disp": self.patterns[0],  # The effectively displayed (rotated) pattern
            "bri": 0.2,
            "rate": 0.5,
            "running": True,
            "align_target": "0"        # The digit that must be at Index 0
        }
        self.palette = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (255, 128, 0), (255, 255, 255)
        ]
        self._update_display_pattern()

    def _update_display_pattern(self):
        """Updates 'disp' by rotating 'pat' to align 'align_target' to index 0."""
        pat = self.state["pat"]
        target = self.state["align_target"]
        
        # Find first occurrence of target
        try:
            rotate_by = pat.index(target)
            # Rotate left by 'rotate_by'
            self.state["disp"] = pat[rotate_by:] + pat[:rotate_by]
        except ValueError:
            # Target not found in pattern (shouldn't happen with valid pats), keep raw
            self.state["disp"] = pat

    def advance(self):
        """Advance to the next pattern in the cycle."""
        self.state["idx"] = (self.state["idx"] + 1) % len(self.patterns)
        self.state["pat"] = self.patterns[self.state["idx"]]
        self._update_display_pattern()

    def manual_change(self, direction):
        """Manually change pattern (prev/next) and pause auto-cycle."""
        self.state["idx"] = (self.state["idx"] + direction) % len(self.patterns)
        self.state["pat"] = self.patterns[self.state["idx"]]
        self._update_display_pattern()
        self.state["running"] = False

    def toggle(self):
        self.state["running"] = not self.state["running"]

    def set_config(self, bri=None, rate=None):
        if bri is not None:
            self.state["bri"] = max(0.0, min(1.0, float(bri)))
        if rate is not None:
            self.state["rate"] = max(0.01, float(rate))

    def set_alignment(self, target_digit):
        """Sets the global alignment target (0-7)."""
        # If we click the SAME target again, maybe we want to toggle to the 2nd instance?
        # For now, let's keep it simple: Always align to the FIRST instance of the target.
        self.state["align_target"] = str(target_digit)
        self._update_display_pattern()