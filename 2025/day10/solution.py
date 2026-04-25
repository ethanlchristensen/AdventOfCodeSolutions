"""
Advent of Code 2025 - Day 10
"""

import re
from collections import deque
import sympy as sp


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)

    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, "r") as f:
            return f.read().strip().split("\n")

    def _extract_lights(self, data):
        match = re.search(r"\[([.#]+)\]", data)
        lights = []
        if match:
            pattern = match.group(1)
            target_mask = 0
            for i, char in enumerate(pattern):
                if char == "#":
                    lights.append(1)
                    target_mask |= 1 << i
                else:
                    lights.append(0)
            return lights, target_mask
        return None, None

    def _extract_schemantics(self, data):
        button_matches = re.findall(r"\(([\d,]+)\)", data)
        buttons = []
        buttons_raw = []
        for match in button_matches:
            indices = [int(x) for x in match.split(",")]
            buttons_raw.append(indices)
            btn_mask = 0
            for index in indices:
                btn_mask |= 1 << index
            buttons.append(btn_mask)
        return buttons, buttons_raw

    def _extract_joltages(self, data):
        joltage_match = re.search(r"\{([\d,]+)\}", data)
        joltages = None
        if joltage_match:
            joltages = [int(x) for x in joltage_match.group(1).split(",")]
        return joltages

    def pasre_line(self, data):
        lights, target_mask = self._extract_lights(data)
        buttons, buttons_raw = self._extract_schemantics(data)
        joltages = self._extract_joltages(data)
        return lights, target_mask, buttons, buttons_raw, joltages

    def press_buttons(self, target, buttons):
        if target == 0:
            return 0

        queue = deque([(0, 0)])
        visited = {0}

        while queue:
            current_state, presses = queue.popleft()

            for button in buttons:
                new_state = current_state ^ button
                if new_state == target:
                    return presses + 1

                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, presses + 1))
        return -1

    def part1(self):
        """Solve part 1 of the puzzle."""
        presses_to_target = []
        for line in self.data:
            _, target_mask, buttons, _, _ = self.pasre_line(line)
            presses = self.press_buttons(target_mask, buttons)
            presses_to_target.append(presses)

        if not presses_to_target:
            return 0
        return sum(presses_to_target)

    def part2(self):
        total_presses = 0
        for line in self.data:
            _, _, _, buttons, joltages = self.pasre_line(line)
            vars = sp.symbols(f"x0:{len(buttons)}")
            equations = []
            for i, target_value in enumerate(joltages):
                relevant_vars = [vars[idx] for idx, b in enumerate(buttons) if i in b]

                if relevant_vars:
                    equations.append(sp.Eq(sp.Add(*relevant_vars), target_value))
                elif target_value > 0:
                    continue
            solution = sp.solve(equations, vars, dict=True)
            if solution:
                sol_dict = solution[0]
                res = []
                for v in vars:
                    val = sol_dict.get(v, 0)
                    if isinstance(val, sp.Expr):
                        val = val.subs({s: 0 for s in val.free_symbols})
                    res.append(int(val))
                total_presses += sum(res)
        return total_presses

    def solve(self):
        """Run both parts and print results."""
        print("Day 10 Solutions:")
        print(f"Part 1: {self.part1()}")
        print(f"Part 2: {self.part2()}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
