"""
Advent of Code 2025 - Day 7 Animation
"""

import math
import random

from bruhanimate import (
    Screen,
    BaseEffect,
    Buffer,
    EffectRenderer,
    NoiseEffect,
    SnowEffect,
    MatrixEffect,
    TWINKLE_SPEC,
    FireworkEffect,
    TwinkleEffect,
    RainEffect,
)

from bruhcolor import bruhcolored as bc


class AdventOfCodeDay07Effect(BaseEffect):
    def __init__(
        self,
        buffer: Buffer,
        background: str,
        part: str = "one",
        data_file: str = "data",
        second_effect: BaseEffect | None = None,
        second_effect_halt: int = 1,
        effect_halt: int = 1,
        board_spacing: int = 1,
        branch_mode: bool = False,
        twinkle_update_frames: int = 1,
        pulse_speed: int = 1,
        pulse_length: int = 5,
        max_radius: float = 20,
    ):
        super().__init__(buffer, background)
        self.part = part
        self.data_file = data_file
        self.second_effect = second_effect
        self.second_effect_halt = second_effect_halt
        self.effect_halt = effect_halt
        self.board_spacing = board_spacing
        self.branch_mode = branch_mode
        self.twinkle_update_frames = twinkle_update_frames
        self.pulse_speed = pulse_speed
        self.pulse_length = pulse_length
        self.max_radius = max_radius

        self.data = None
        self.board_width = None
        self.board_height = None
        self.px = None
        self.py = None
        self.x = None
        self.y = None

        self.changes = set()
        self.board_positions = set()
        self.virtual_beam_positions = set()
        self.ripple_effects = []
        self.last_ripple_positions = set()

        self.ripple_chars = [" ", ".", "·", ":", "-", "=", "+", "*", "#", "▒", "▓", "█"]
        self.beam_char = "║"
        self.beam_left_char = "╔"
        self.beam_right_char = "╗"
        self.beam_horizontal_char = "═"
        self.splitter_char = "✦"
        self.splitter_left_char = "╝"
        self.splitter_right_char = "╚"
        self.splitter_normal_colors = [196, 208, 190, 76, 21, 93]
        self.beam_color = 45
        self.pulse_color = 45
        self.evergreen_color = 28  # Green color for completed beams

        self.all_branches = []
        self.current_branch_index = 0
        self.current_branch_step = 0
        self.current_branch_path = []

        self.twinkles = {}
        self.twinkle_frame_counter = 0

        self.path_directions = {}
        self.splitter_connections = {}
        self.connector_lines = {}
        self.connector_positions = set()

        self.state = "building"
        self.pulse_position = 0
        self.pulse_frame_counter = 0
        self.pulse_direction = 1

        self.erased_positions = set()
        self.erased_virtual_positions = set()
        self.erased_connector_positions = set()

        self.splitter_colors = {}  # Store permanent colors for each splitter
        self.completed_beam_positions = set()  # Beams that should be evergreen
        self.completed_path_directions = {}  # Store directions for completed beams
        self.completed_connector_lines = {}  # Store connector lines for completed beams

        self._load_data()

    def _load_data(self):
        with open(self.data_file, "r") as f:
            self.data = [[c for c in r] for r in f.read().strip().split("\n")]
            self.board_width = len(self.data[0])
            self.board_height = len(self.data)
            self.paths = [[0] * self.board_width for _ in range(self.board_height)]
            self.px = (
                self.buffer.width() - (self.board_width * self.board_spacing)
            ) // 2
            self.py = (self.buffer.height() - self.board_height) // 2

            for y in range(self.board_height):
                for x in range(self.board_width):
                    if self.data[y][x] == "^":
                        # Assign permanent color to splitter
                        self.splitter_colors[(x, y)] = random.choice(
                            self.splitter_normal_colors
                        )
                    elif self.data[y][x] == ".":
                        ui_x = self.px + (self.board_spacing * x)
                        ui_y = y + self.py
                        self.twinkles[(ui_x, ui_y)] = TWINKLE_SPEC(
                            char="·", value=random.randint(0, 23)
                        )

            if self.branch_mode:
                start_x = self.data[0].index("S")
                self._precompute_branches_extended(start_x, 0)
            else:
                self.x = self.data[0].index("S")
                self.y = 0
                self.paths[self.y][self.x] = 1

    def _precompute_branches_extended(self, start_x, start_y):
        branches_to_process = [[(start_x, start_y)]]

        while branches_to_process:
            path = branches_to_process.pop(0)
            x, y = path[-1]

            if y + 1 >= self.board_height:
                self.all_branches.append(path)
                continue

            cell_below = self.data[y + 1][x]

            if cell_below == ".":
                new_path = path + [(x, y + 1)]
                branches_to_process.append(new_path)
            elif cell_below == "^":
                if x - 1 >= 0:
                    left_path = path + [(x, y + 1), (x - 1, y + 1)]
                    branches_to_process.append(left_path)
                if x + 1 < self.board_width:
                    right_path = path + [(x, y + 1), (x + 1, y + 1)]
                    branches_to_process.append(right_path)
            else:
                self.all_branches.append(path)

        for i, branch in enumerate(self.all_branches):
            extended_branch = []

            start_x_board = branch[0][0]
            ui_start_x = self.px + (self.board_spacing * start_x_board)

            for screen_y in range(0, self.py):
                extended_branch.append(("virtual_top", screen_y, ui_start_x))

            for board_x, board_y in branch:
                extended_branch.append((board_x, board_y, None))

            end_x_board = branch[-1][0]
            ui_end_x = self.px + (self.board_spacing * end_x_board)

            for screen_y in range(self.py + self.board_height, self.buffer.height()):
                extended_branch.append(("virtual_bottom", screen_y, ui_end_x))

            self.all_branches[i] = extended_branch

    def update_twinkles(self):
        if self.twinkle_frame_counter % self.twinkle_update_frames != 0:
            self.twinkle_frame_counter += 1
            return

        for (x, y), twinkle in self.twinkles.items():
            twinkle.next()

        self.twinkle_frame_counter += 1

    def update_board_row_mode(self, frame_number: int):
        if self.x >= self.board_width:
            self.x = 0
            self.y += 1

        if self.y >= self.board_height:
            return

        current_paths = self.paths[self.y][self.x]
        if current_paths == 0:
            self.x += 1
            return

        if self.y + 1 < self.board_height:
            cell_below = self.data[self.y + 1][self.x]

            if cell_below == ".":
                self.paths[self.y + 1][self.x] += current_paths
                self.path_directions[(self.x, self.y + 1)] = "straight"
            elif cell_below == "^":
                ui_x = self.px + (self.board_spacing * self.x)
                ui_y = (self.y + 1) + self.py
                self.ripple_effects.append(
                    {
                        "x": ui_x,
                        "y": ui_y,
                        "radius": 0,
                        "max_radius": self.max_radius,
                        "frame": frame_number,
                    }
                )

                if self.x - 1 >= 0:
                    self.paths[self.y + 1][self.x - 1] += current_paths
                    self.path_directions[(self.x - 1, self.y + 1)] = "left"
                    if self.board_spacing > 1:
                        self.connector_lines[(self.x, self.y + 1, "left")] = True

                if self.x + 1 < self.board_width:
                    self.paths[self.y + 1][self.x + 1] += current_paths
                    self.path_directions[(self.x + 1, self.y + 1)] = "right"
                    if self.board_spacing > 1:
                        self.connector_lines[(self.x, self.y + 1, "right")] = True

        self.x += 1

    def update_board_branch_mode(self, frame_number: int):
        if self.current_branch_index >= len(self.all_branches):
            return

        branch = self.all_branches[self.current_branch_index]

        if self.state == "building":
            if self.current_branch_step >= len(branch):
                self.state = "pulsing"
                self.pulse_position = 0
                self.pulse_direction = 1
                self.pulse_frame_counter = 0
                return

            step = branch[self.current_branch_step]

            if step[0] in ["virtual_top", "virtual_bottom"]:
                self.virtual_beam_positions.add((step[2], step[1]))
            else:
                x, y = step[0], step[1]
                self.paths[y][x] = 1
                self.current_branch_path.append((x, y))

                if self.current_branch_step > 0:
                    prev_step = branch[self.current_branch_step - 1]
                    if prev_step[0] not in ["virtual_top", "virtual_bottom"]:
                        prev_x, prev_y = prev_step[0], prev_step[1]

                        if prev_x < x:
                            self.path_directions[(x, y)] = "right"
                            if self.data[prev_y][prev_x] == "^":
                                self.splitter_connections[(prev_x, prev_y)] = "right"
                                if self.board_spacing > 1:
                                    self.connector_lines[(prev_x, prev_y, "right")] = (
                                        True
                                    )
                        elif prev_x > x:
                            self.path_directions[(x, y)] = "left"
                            if self.data[prev_y][prev_x] == "^":
                                self.splitter_connections[(prev_x, prev_y)] = "left"
                                if self.board_spacing > 1:
                                    self.connector_lines[(prev_x, prev_y, "left")] = (
                                        True
                                    )
                        else:
                            self.path_directions[(x, y)] = "straight"

                        if self.data[y][x] == "^" and prev_y != y:
                            ui_x = self.px + (self.board_spacing * x)
                            ui_y = y + self.py
                            self.ripple_effects.append(
                                {
                                    "x": ui_x,
                                    "y": ui_y,
                                    "radius": 0,
                                    "max_radius": self.max_radius,
                                    "frame": frame_number,
                                }
                            )
                    else:
                        self.path_directions[(x, y)] = "straight"
                else:
                    self.path_directions[(x, y)] = "straight"

            self.current_branch_step += 1

        elif self.state == "pulsing":
            if self.pulse_frame_counter % self.pulse_speed == 0:
                erase_position = self.pulse_position - self.pulse_length - 1
                if 0 <= erase_position < len(branch):
                    step = branch[erase_position]
                    if step[0] in ["virtual_top", "virtual_bottom"]:
                        self.erased_virtual_positions.add((step[2], step[1]))
                        self.buffer.put_char(step[2], step[1], " ")
                    else:
                        x, y = step[0], step[1]

                        # Don't erase if this is a completed beam position
                        if (x, y) not in self.completed_beam_positions:
                            self.erased_positions.add((x, y))

                            ui_x = self.px + (self.board_spacing * x)
                            ui_y = y + self.py
                            if (ui_x, ui_y) in self.twinkles:
                                self.buffer.put_char(
                                    ui_x, ui_y, self.twinkles[(ui_x, ui_y)].fade.colored
                                )
                            else:
                                self.buffer.put_char(ui_x, ui_y, " ")

                            if (x, y, "left") in self.connector_lines:
                                splitter_ui_x = self.px + (self.board_spacing * x)
                                splitter_ui_y = y + self.py
                                for offset in range(1, self.board_spacing):
                                    connector_x = splitter_ui_x - offset
                                    self.erased_connector_positions.add(
                                        (connector_x, splitter_ui_y)
                                    )
                                    self.buffer.put_char(
                                        connector_x, splitter_ui_y, " "
                                    )

                            if (x, y, "right") in self.connector_lines:
                                splitter_ui_x = self.px + (self.board_spacing * x)
                                splitter_ui_y = y + self.py
                                for offset in range(1, self.board_spacing):
                                    connector_x = splitter_ui_x + offset
                                    self.erased_connector_positions.add(
                                        (connector_x, splitter_ui_y)
                                    )
                                    self.buffer.put_char(
                                        connector_x, splitter_ui_y, " "
                                    )

                self.pulse_position += self.pulse_direction

                if self.pulse_position - self.pulse_length - 1 >= len(branch):
                    # Add all positions from this branch to completed set
                    for pos in self.current_branch_path:
                        self.completed_beam_positions.add(pos)
                        # Store the direction permanently
                        if pos in self.path_directions:
                            self.completed_path_directions[pos] = self.path_directions[
                                pos
                            ]

                    # Store connector lines permanently
                    for key in self.connector_lines:
                        self.completed_connector_lines[key] = True

                    for pos in self.connector_positions:
                        if pos not in self.erased_connector_positions:
                            self.buffer.put_char(pos[0], pos[1], " ")

                    for vx, vy in self.virtual_beam_positions:
                        if (vx, vy) not in self.erased_virtual_positions:
                            self.buffer.put_char(vx, vy, " ")

                    self.current_branch_index += 1
                    self.current_branch_step = 0
                    self.current_branch_path = []
                    self.paths = [
                        [0] * self.board_width for _ in range(self.board_height)
                    ]
                    self.path_directions.clear()
                    self.splitter_connections.clear()
                    self.connector_lines.clear()
                    self.connector_positions.clear()
                    self.virtual_beam_positions.clear()
                    self.erased_positions.clear()
                    self.erased_virtual_positions.clear()
                    self.erased_connector_positions.clear()
                    self.state = "building"
                    self.pulse_position = 0
                    self.pulse_direction = 1
                    return

            self.pulse_frame_counter += 1

    def update_board(self, frame_number: int):
        if self.branch_mode:
            self.update_board_branch_mode(frame_number)
        else:
            self.update_board_row_mode(frame_number)

    def update_ripples(self, frame_number: int):
        for x, y in self.last_ripple_positions:
            if (x, y) not in self.board_positions and (
                x,
                y,
            ) not in self.connector_positions:
                self.buffer.put_char(x, y, " ")

        current_ripple_positions = set()
        active_ripples = []

        for ripple in self.ripple_effects:
            age = frame_number - ripple["frame"]
            ripple["radius"] = age * 0.5

            if ripple["radius"] <= ripple["max_radius"]:
                active_ripples.append(ripple)

                for angle in range(0, 360, 10):
                    rad = math.radians(angle)
                    x = int(ripple["x"] + ripple["radius"] * math.cos(rad))
                    y = int(ripple["y"] + ripple["radius"] * math.sin(rad) * 0.5)

                    progress = ripple["radius"] / ripple["max_radius"]
                    color_value = int(255 - (progress * (255 - 232)))

                    char_index = int((1 - progress) * (len(self.ripple_chars) - 1))
                    ripple_char = self.ripple_chars[char_index]

                    if 0 <= x < self.buffer.width() and 0 <= y < self.buffer.height():
                        if (x, y) not in self.board_positions and (
                            x,
                            y,
                        ) not in self.connector_positions:
                            current_ripple_positions.add((x, y))
                            self.buffer.put_char(x, y, bc(ripple_char, color_value))

        self.ripple_effects = active_ripples
        self.last_ripple_positions = current_ripple_positions

    def get_pulse_positions(self):
        pulse_positions = set()
        pulse_screen_positions = set()

        if self.state == "pulsing" and self.current_branch_index < len(
            self.all_branches
        ):
            branch = self.all_branches[self.current_branch_index]

            for i in range(
                max(0, self.pulse_position - self.pulse_length),
                min(len(branch), self.pulse_position + 1),
            ):
                if 0 <= i < len(branch):
                    step = branch[i]
                    if step[0] in ["virtual_top", "virtual_bottom"]:
                        pulse_screen_positions.add((step[2], step[1]))
                    else:
                        pulse_positions.add((step[0], step[1]))

        return pulse_positions, pulse_screen_positions

    def get_board_changes(self):
        pulse_positions, pulse_screen_positions = self.get_pulse_positions()

        for y in range(self.board_height):
            for x in range(self.board_width):
                if (x, y) in self.erased_positions:
                    continue

                val = self.paths[y][x]
                char = self.data[y][x]

                ui_x = self.px + (self.board_spacing * x)
                ui_y = y + self.py

                self.board_positions.add((ui_x, ui_y))

                is_pulsing = (x, y) in pulse_positions
                is_completed = (x, y) in self.completed_beam_positions

                # Determine color: evergreen if completed, pulse color if pulsing, normal otherwise
                if is_completed:
                    color = self.evergreen_color
                elif is_pulsing:
                    color = self.pulse_color
                else:
                    color = self.beam_color

                if char == "^":
                    if (x, y) in self.splitter_connections:
                        connection = self.splitter_connections[(x, y)]
                        if connection == "left":
                            beam_char = self.splitter_left_char
                        else:
                            beam_char = self.splitter_right_char
                        self.changes.add((ui_x, ui_y, bc(beam_char, color)))
                    else:
                        # Use the permanent color assigned to this splitter
                        splitter_color = self.splitter_colors.get(
                            (x, y), self.splitter_normal_colors[0]
                        )
                        self.changes.add(
                            (ui_x, ui_y, bc(self.splitter_char, splitter_color))
                        )
                    continue

                # Render completed beams even if val == 0
                if is_completed:
                    direction = self.completed_path_directions.get((x, y), "straight")
                    if direction == "left":
                        beam_char = self.beam_left_char
                    elif direction == "right":
                        beam_char = self.beam_right_char
                    else:
                        beam_char = self.beam_char
                    self.changes.add((ui_x, ui_y, bc(beam_char, color)))
                    continue

                if val == 0:
                    if (ui_x, ui_y) in self.twinkles:
                        self.changes.add(
                            (ui_x, ui_y, self.twinkles[(ui_x, ui_y)].fade.colored)
                        )
                    else:
                        self.changes.add((ui_x, ui_y, " "))
                    continue

                direction = self.path_directions.get((x, y), "straight")
                if direction == "left":
                    beam_char = self.beam_left_char
                elif direction == "right":
                    beam_char = self.beam_right_char
                else:
                    beam_char = self.beam_char

                self.changes.add((ui_x, ui_y, bc(beam_char, color)))

        # Render current branch connector lines
        for (split_x, split_y, direction), _ in self.connector_lines.items():
            if (split_x, split_y) in self.erased_positions:
                continue

            splitter_ui_x = self.px + (self.board_spacing * split_x)
            splitter_ui_y = split_y + self.py

            is_pulsing = (split_x, split_y) in pulse_positions
            is_completed = (split_x, split_y) in self.completed_beam_positions

            if is_completed:
                color = self.evergreen_color
            elif is_pulsing:
                color = self.pulse_color
            else:
                color = self.beam_color

            if direction == "left":
                for offset in range(1, self.board_spacing):
                    connector_x = splitter_ui_x - offset
                    if (
                        connector_x,
                        splitter_ui_y,
                    ) not in self.erased_connector_positions:
                        self.changes.add(
                            (
                                connector_x,
                                splitter_ui_y,
                                bc(self.beam_horizontal_char, color),
                            )
                        )
                        self.connector_positions.add((connector_x, splitter_ui_y))
            elif direction == "right":
                for offset in range(1, self.board_spacing):
                    connector_x = splitter_ui_x + offset
                    if (
                        connector_x,
                        splitter_ui_y,
                    ) not in self.erased_connector_positions:
                        self.changes.add(
                            (
                                connector_x,
                                splitter_ui_y,
                                bc(self.beam_horizontal_char, color),
                            )
                        )
                        self.connector_positions.add((connector_x, splitter_ui_y))

        # Render completed connector lines
        for (split_x, split_y, direction), _ in self.completed_connector_lines.items():
            splitter_ui_x = self.px + (self.board_spacing * split_x)
            splitter_ui_y = split_y + self.py

            color = self.evergreen_color

            if direction == "left":
                for offset in range(1, self.board_spacing):
                    connector_x = splitter_ui_x - offset
                    self.changes.add(
                        (
                            connector_x,
                            splitter_ui_y,
                            bc(self.beam_horizontal_char, color),
                        )
                    )
                    self.connector_positions.add((connector_x, splitter_ui_y))
            elif direction == "right":
                for offset in range(1, self.board_spacing):
                    connector_x = splitter_ui_x + offset
                    self.changes.add(
                        (
                            connector_x,
                            splitter_ui_y,
                            bc(self.beam_horizontal_char, color),
                        )
                    )
                    self.connector_positions.add((connector_x, splitter_ui_y))

        for screen_x, screen_y in self.virtual_beam_positions:
            if (screen_x, screen_y) in self.erased_virtual_positions:
                continue

            is_pulsing = (screen_x, screen_y) in pulse_screen_positions
            color = self.pulse_color if is_pulsing else self.beam_color
            self.changes.add((screen_x, screen_y, bc(self.beam_char, color)))

    def place_changes(self):
        for x, y, val in self.changes:
            self.buffer.put_char(x, y, val)

    def render_frame(self, frame_number: int):
        if frame_number % self.second_effect_halt == 0:
            if self.second_effect is not None:
                self.second_effect.render_frame(frame_number=frame_number)
                for y in range(self.buffer.height()):
                    for x in range(self.buffer.width()):
                        x_bound = (
                            self.px
                            < x
                            < (self.px + (self.board_width * self.board_spacing))
                        )
                        y_bound = self.py <= y < (self.py + self.board_height)
                        if (
                            (not x_bound or not y_bound)
                            and (
                                x,
                                y,
                            )
                            not in self.virtual_beam_positions
                            and (x, y) not in self.last_ripple_positions
                        ):
                            self.buffer.put_char(
                                x, y, self.second_effect.buffer.get_char(x, y)
                            )

        if frame_number % self.effect_halt == 0:
            self.changes.clear()
            self.update_board(frame_number=frame_number)
            self.get_board_changes()

        self.update_twinkles()

        self.update_ripples(frame_number=frame_number)

        if self.branch_mode:
            self.buffer.put_at(
                1,
                1,
                f"Branch: {self.current_branch_index + 1}/{len(self.all_branches)} Pulse: {self.pulse_position}",
            )
        else:
            self.buffer.put_at(1, 1, f"X: {self.x}, Y: {self.y}")
        self.place_changes()


def animate(screen):
    renderer = EffectRenderer(
        screen=screen,
        frames=float("inf"),
        frame_time=0.01,
        effect_type="static",
        background=" ",
        transparent=False,
    )

    snow = SnowEffect(Buffer(screen.height, screen.width), " ")
    noise = NoiseEffect(Buffer(screen.height, screen.width), " ")
    noise.update_color(True, False)
    matrix = MatrixEffect(Buffer(screen.height, screen.width), " ", gradient_length=2)
    rain = RainEffect(Buffer(screen.height, screen.width), " ")
    rain.update_swells(True)
    rain.update_intensity(1)
    rain.update_wind_direction(direction="east")
    fireworks = FireworkEffect(Buffer(screen.height, screen.width), " ")
    fireworks.set_second_effect(TwinkleEffect(Buffer(screen.height, screen.width), " "))
    fireworks.set_firework_type("random")
    fireworks.set_firework_color_enabled(True)
    fireworks.set_firework_color_type("twotone")

    renderer.effect = AdventOfCodeDay07Effect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        part="two",
        data_file="datasmall",
        second_effect=fireworks,
        second_effect_halt=5,
        board_spacing=2,
        effect_halt=1,
        branch_mode=True,
        twinkle_update_frames=10,
        pulse_speed=1,
        pulse_length=5,
        max_radius=15,
    )

    renderer.run()


if __name__ in ["__main__", "day07_animate"]:
    Screen.show(animate)
