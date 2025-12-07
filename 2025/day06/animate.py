"""
Advent of Code 2025 - Day 6 Animation
"""

import random
from bruhanimate import (
    Screen,
    BaseEffect,
    Buffer,
    EffectRenderer,
    SnowEffect,
    TWINKLE_SPEC,
    TwinkleEffect,
    FireworkEffect,
)
from bruhcolor import bruhcolored as bc


class AdventOfCodeDay06Effect(BaseEffect):
    def __init__(
        self,
        buffer: Buffer,
        background: str,
        part: str = "one",
        data_file: str = "data",
        second_effect: BaseEffect | None = None,
        second_effect_halt: int = 1,
        scan_speed: int = 2,
        calc_pause_frames: int = 15,
        twinkle_update_frames: int = 1,
        fill_rate: int = 5,
    ):
        super().__init__(buffer, background)
        self.part = part
        self.data_file = data_file
        self.second_effect = second_effect
        self.second_effect_halt = second_effect_halt
        self.scan_speed = scan_speed
        self.calc_pause_frames = calc_pause_frames
        self.twinkle_update_frames = twinkle_update_frames
        self.fill_rate = fill_rate

        self.data = None
        self.worksheet_lines = []
        self.operation_line = ""
        self.worksheet_width = 0

        self.state = "scanning"
        self.current_column = 0
        self.current_problem_columns = []
        self.current_problem_numbers = []
        self.current_operation = None

        self.building_equation = []

        self.scanner_screen_x = None
        self.viewport_offset = 0

        self.problems_solved = []
        self.grand_total = 0
        self.current_result = 0

        self.calc_flash_frames = 0
        self.total_flash_frames = 0
        self.frame_counter = 0
        self.twinkle_frame_counter = 0

        self.twinkles = {}

        self.screen_twinkles = {}
        self.unfilled_positions = []

        self.colors = {
            "scanner": 51,
            "space_col": 240,
            "number": 255,
            "multiply": 196,
            "add": 46,
            "result": 226,
            "total": 201,
        }

        self._load_data()

    def _load_data(self):
        with open(self.data_file, "r") as f:
            lines = f.read().split("\n")
            self.worksheet_lines = lines[:-1]
            self.operation_line = lines[-1]
            if self.worksheet_lines:
                self.worksheet_width = len(self.worksheet_lines[0])

        self.scanner_screen_x = self.buffer.width() // 2

    def _is_space_column(self, col_idx):
        if col_idx >= self.worksheet_width:
            return True
        return all(
            line[col_idx] == " " for line in self.worksheet_lines if col_idx < len(line)
        )

    def _get_column_chars(self, col_idx):
        chars = []
        for line in self.worksheet_lines:
            if col_idx < len(line):
                chars.append(line[col_idx])
        return chars

    def _extract_number_from_column(self, col_idx):
        chars = self._get_column_chars(col_idx)
        num_str = "".join(chars).strip()
        return int(num_str) if num_str else None

    def _extract_number_from_column_part2(self, col_idx):
        chars = self._get_column_chars(col_idx)
        digit_str = "".join(chars).strip()
        return int(digit_str) if digit_str else None

    def _extract_number_from_columns(self, columns):
        if self.part == "one":
            number_str = ""
            for col_idx in columns:
                chars = self._get_column_chars(col_idx)
                number_str += "".join(chars).strip()
            return int(number_str) if number_str else 0
        else:
            numbers = []
            for col_idx in reversed(columns):
                chars = self._get_column_chars(col_idx)
                digit_str = "".join(chars).strip()
                if digit_str:
                    numbers.append(int(digit_str))
            return numbers

    def _calculate_result(self, numbers, operation):
        if operation == "+":
            return sum(numbers)
        else:
            result = 1
            for num in numbers:
                result *= num
            return result

    def _initialize_unfilled_positions(self):
        self.unfilled_positions = []
        for y in range(self.buffer.height()):
            for x in range(self.buffer.width()):
                self.unfilled_positions.append((x, y))
        random.shuffle(self.unfilled_positions)

    def _add_screen_twinkles(self):
        if not self.unfilled_positions:
            return

        for _ in range(min(self.fill_rate, len(self.unfilled_positions))):
            x, y = self.unfilled_positions.pop()

            digit = str(random.randint(0, 9))
            self.screen_twinkles[(x, y)] = {
                "spec": TWINKLE_SPEC(char=digit, value=random.randint(0, 23)),
                "x": x,
                "y": y,
            }

    def _create_twinkle_for_position(self, col_idx, row_idx, number):
        x = self.viewport_offset + col_idx

        worksheet_height = len(self.worksheet_lines) + 1
        start_y = (self.buffer.height() - worksheet_height) // 3
        y = start_y + row_idx

        key = (col_idx, row_idx)
        if key not in self.twinkles:
            self.twinkles[key] = {
                "spec": TWINKLE_SPEC(char=number, value=random.randint(0, 23)),
                "x": x,
                "y": y,
            }

    def update_twinkles(self):
        if self.twinkle_frame_counter % self.twinkle_update_frames != 0:
            self.twinkle_frame_counter += 1
            return

        for key, twinkle_data in self.twinkles.items():
            twinkle_data["spec"].next()

        for key, twinkle_data in self.screen_twinkles.items():
            twinkle_data["spec"].next()

        self.twinkle_frame_counter += 1

    def _render_worksheet(self):
        worksheet_height = len(self.worksheet_lines) + 1
        start_y = (self.buffer.height() - worksheet_height) // 3

        self.viewport_offset = self.scanner_screen_x - self.current_column

        for key, twinkle_data in self.twinkles.items():
            col_idx, row_idx = key
            twinkle_data["x"] = self.viewport_offset + col_idx
            twinkle_data["y"] = start_y + row_idx

        for i, line in enumerate(self.worksheet_lines):
            y = start_y + i

            for col_idx in range(self.worksheet_width):
                x = self.viewport_offset + col_idx

                if x < 0 or x >= self.buffer.width():
                    continue

                char = line[col_idx] if col_idx < len(line) else " "

                if col_idx < self.current_column:
                    key = (col_idx, i)
                    if key not in self.twinkles:
                        self._create_twinkle_for_position(col_idx, i, char)

                    twinkle_data = self.twinkles[key]
                    colored = twinkle_data["spec"].fade.colored
                elif col_idx == self.current_column and self.state == "scanning":
                    colored = bc(
                        char if char.strip() else "│", self.colors["scanner"]
                    ).colored
                elif col_idx in self.current_problem_columns:
                    colored = bc(char, self.colors["number"]).colored
                elif col_idx > self.current_column:
                    if self._is_space_column(col_idx):
                        colored = bc(char if char.strip() else "│", 240).colored
                    else:
                        colored = bc(char, 245).colored
                elif self._is_space_column(col_idx):
                    colored = bc(
                        char if char.strip() else "│", self.colors["space_col"]
                    ).colored
                else:
                    colored = char

                self.buffer.put_char(x, y, colored)

        y = start_y + len(self.worksheet_lines)
        for col_idx in range(min(len(self.operation_line), self.worksheet_width)):
            x = self.viewport_offset + col_idx

            if x < 0 or x >= self.buffer.width():
                continue

            char = self.operation_line[col_idx]

            if col_idx < self.current_column:
                key = (col_idx, len(self.worksheet_lines))
                if key not in self.twinkles:
                    self._create_twinkle_for_position(
                        col_idx, len(self.worksheet_lines), char
                    )

                twinkle_data = self.twinkles[key]
                colored = twinkle_data["spec"].fade.colored
            elif col_idx == self.current_column and self.state == "scanning":
                colored = bc(
                    char if char.strip() else "│", self.colors["scanner"]
                ).colored
            elif col_idx > self.current_column:
                if char in ["+", "*"]:
                    color = (
                        self.colors["add"] if char == "+" else self.colors["multiply"]
                    )

                    colored = bc(char, color).colored
                else:
                    colored = bc(char, 245).colored
            elif char in ["+", "*"]:
                color = self.colors["add"] if char == "+" else self.colors["multiply"]
                colored = bc(char, color).colored
            else:
                colored = char
            self.buffer.put_char(x, y, colored)

        if self.state == "scanning":
            for y in range(self.buffer.height()):
                if y < start_y or y > start_y + worksheet_height:
                    char = bc("│", self.colors["scanner"], 235).colored
                    self.buffer.put_char(self.scanner_screen_x, y, char)

    def _render_calculation_area(self):
        calc_y = self.buffer.height() - 10

        if self.state == "calculating" and self.current_operation:
            op_symbol = self.current_operation
            color = self.colors["add"] if op_symbol == "+" else self.colors["multiply"]

            problem_str = f" {op_symbol} ".join(
                str(n) for n in self.current_problem_numbers
            )
            problem_str += f" = {self.current_result}"

            colored_line = []
            for char in problem_str:
                if char in ["+", "*"]:
                    colored_line.append(bc(char, color).colored)
                elif char.isdigit():
                    colored_line.append(bc(char, self.colors["result"]).colored)
                elif char == "=":
                    colored_line.append(bc(char, self.colors["result"]).colored)
                else:
                    colored_line.append(char)

            self.buffer.put_at_center(calc_y, colored_line)
        elif self.part == "two" and self.building_equation and self.current_operation:
            op_symbol = self.current_operation
            color = self.colors["add"] if op_symbol == "+" else self.colors["multiply"]

            problem_str = f" {op_symbol} ".join(str(n) for n in self.building_equation)

            colored_line = []
            for char in problem_str:
                if char in ["+", "*"]:
                    colored_line.append(bc(char, color).colored)
                elif char.isdigit():
                    colored_line.append(bc(char, self.colors["number"]).colored)
                else:
                    colored_line.append(char)

            self.buffer.put_at_center(calc_y, colored_line)

    def _render_grand_total(self):
        total_y = self.buffer.height() - 5
        total_str = f"Grand Total: {self.grand_total}"

        flash_intensity = max(0, self.total_flash_frames / 30)
        if flash_intensity > 0:
            color = self.colors["total"]
        else:
            color = 255

        colored_line = []
        for char in total_str:
            if char.isdigit():
                colored_line.append(bc(char, color).colored)
            else:
                colored_line.append(char)

        self.buffer.put_at_center(total_y, colored_line)

    def _update_animation(self):
        self.frame_counter += 1

        if self.total_flash_frames > 0:
            self.total_flash_frames -= 1

        if self.state == "scanning":
            if self.frame_counter % self.scan_speed == 0:
                if self._is_space_column(self.current_column):
                    if self.current_problem_columns:
                        col_idx = self.current_problem_columns[0]
                        if col_idx < len(self.operation_line):
                            op_char = self.operation_line[col_idx].strip()
                            if op_char in ["+", "*"]:
                                self.current_operation = op_char

                        if self.part == "one":
                            self.current_problem_numbers = []
                            for col in self.current_problem_columns:
                                chars = self._get_column_chars(col)
                                num_str = "".join(chars).strip()
                                if num_str:
                                    self.current_problem_numbers.append(int(num_str))
                        else:
                            self.current_problem_numbers = list(self.building_equation)

                        if self.current_problem_numbers and self.current_operation:
                            self.current_result = self._calculate_result(
                                self.current_problem_numbers, self.current_operation
                            )

                        self.state = "calculating"
                        self.frame_counter = 0
                        return
                else:
                    if self.current_column not in self.current_problem_columns:
                        self.current_problem_columns.append(self.current_column)

                    if not self.current_operation and self.current_column < len(
                        self.operation_line
                    ):
                        op_char = self.operation_line[self.current_column].strip()
                        if op_char in ["+", "*"]:
                            self.current_operation = op_char

                    if self.part == "two":
                        chars = self._get_column_chars(self.current_column)
                        digit_str = "".join(chars).strip()
                        if digit_str:
                            num = int(digit_str)
                            if num not in self.building_equation:
                                self.building_equation.insert(0, num)

                self.current_column += 1

                if self.current_column >= self.worksheet_width:
                    if self.current_problem_columns:
                        col_idx = self.current_problem_columns[0]
                        if col_idx < len(self.operation_line):
                            op_char = self.operation_line[col_idx].strip()
                            if op_char in ["+", "*"]:
                                self.current_operation = op_char

                        if self.part == "one":
                            self.current_problem_numbers = []
                            for col in self.current_problem_columns:
                                chars = self._get_column_chars(col)
                                num_str = "".join(chars).strip()
                                if num_str:
                                    self.current_problem_numbers.append(int(num_str))
                        else:
                            self.current_problem_numbers = list(self.building_equation)

                        if self.current_problem_numbers and self.current_operation:
                            self.current_result = self._calculate_result(
                                self.current_problem_numbers, self.current_operation
                            )

                        self.state = "calculating"
                    else:
                        self.state = "complete"
                        self._initialize_unfilled_positions()

        elif self.state == "calculating":
            if self.frame_counter >= self.calc_pause_frames:
                if self.current_result > 0:
                    self.grand_total += self.current_result
                    self.total_flash_frames = 30

                self.current_problem_columns = []
                self.building_equation = []
                self.current_operation = None
                self.current_result = 0
                self.current_problem_numbers = []
                self.state = "scanning"
                self.frame_counter = 0

        elif self.state == "complete":
            if not self.unfilled_positions:
                if not hasattr(self, "_initialized_positions"):
                    self._initialize_unfilled_positions()
                    self._initialized_positions = True
            if self.unfilled_positions:
                self._add_screen_twinkles()

    def render_frame(self, frame_number: int):
        if frame_number % self.second_effect_halt == 0:
            if self.second_effect is not None:
                self.second_effect.render_frame(frame_number=frame_number)
                self.buffer.sync_with(self.second_effect.buffer)

        self._update_animation()
        self.update_twinkles()

        if self.state == "complete":
            for key, twinkle_data in self.screen_twinkles.items():
                x, y = twinkle_data["x"], twinkle_data["y"]
                if 0 <= x < self.buffer.width() and 0 <= y < self.buffer.height():
                    self.buffer.put_char(x, y, twinkle_data["spec"].fade.colored)

        if self.state != "complete":
            self._render_worksheet()
        self._render_calculation_area()
        self._render_grand_total()


def animate(screen):
    renderer = EffectRenderer(
        screen=screen,
        frames=float("inf"),
        frame_time=0.0,
        effect_type="static",
        background=" ",
        transparent=False,
    )
    fireworks = FireworkEffect(Buffer(screen.height, screen.width), " ")
    fireworks.set_second_effect(
        second_effect=TwinkleEffect(Buffer(screen.height, screen.width), " ")
    )
    fireworks.set_firework_type("random")
    fireworks.set_firework_color_enabled(True)
    fireworks.set_firework_color_type("twotone")

    snow = SnowEffect(Buffer(screen.height, screen.width), " ")
    renderer.effect = AdventOfCodeDay06Effect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        part="two",
        data_file="dataanimate",
        second_effect=TwinkleEffect(Buffer(screen.height, screen.width), " "),
        second_effect_halt=20,
        scan_speed=50,
        calc_pause_frames=20,
        twinkle_update_frames=10,
        fill_rate=15,
    )

    renderer.run()


if __name__ in ["__main__", "day06_animate"]:
    Screen.show(animate)
