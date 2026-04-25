"""
Advent of Code 2025 - Day 4 Animation
Updated for bruhanimate 0.2.x
"""

import random
from typing import Optional

from bruhanimate import (
    BaseEffect,
    Buffer,
    EffectRenderer,
    FireworkEffect,
    FireworkSettings,
    Screen,
    TWINKLE_SPEC,
    TwinkleSettings,
    effect_registry,
)
from bruhcolor import bruhcolored as bc


class AdventOfCodeDay04Effect(BaseEffect):
    def __init__(
        self,
        buffer: Buffer,
        background: str,
        part: str = "one",
        data_file: str = "data",
        second_effect: Optional[BaseEffect] = None,
        second_effect_halt: int = 1,
        halt_frames: int = 5,
        check_halt_frames: int = 5,
        board_size: int = 15,
        board_spacing: int = 1,
        fade_frames: int = 50,
        quick_mode: bool = False,
        twinkle_update_frames: int = 1,
        check_fade_frames: int = 30,
    ):
        super().__init__(buffer, background)
        self.part = part
        self.data_file = data_file
        self.second_effect = second_effect
        self.second_effect_halt = second_effect_halt
        self.board_a = None
        self.board_height = None
        self.board_width = None
        self.px = None
        self.py = None

        self.board_size = board_size
        self.board_spacing = board_spacing

        self.fork_life_bg = 245
        self.fork_lift_position = (-1, 0)
        self.previous_fork_lift_position = None

        self.halt_frames = halt_frames
        self.check_halt_frames = check_halt_frames
        self.fade_frames = fade_frames
        self.check_fade_frames = check_fade_frames
        self.quick_mode = quick_mode
        self.twinkle_update_frames = twinkle_update_frames

        self.effective_frames = 0
        self.twinkle_frame_counter = 0

        self.char_to_color = {
            ".": bc(".", 239).colored,
            " ": None,
            "@": bc("@", 91).colored,
        }

        self.directions = [
            (1, 0),
            (1, 1),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
            (0, -1),
            (1, -1),
        ]

        self.changes = {}
        self.twinkles = {}

        # State machine
        self.state = "scanning"
        self.checking_roll = False
        self.rolls_found = 0
        self.checked_directions = 0
        self.checked_changes = {}
        self.check_frames = 0

        # Fading checked cells - stores the starting frame number for each position
        self.fading_checked = {}

        self.removeable = {}
        self.removed = set()

        # Fade animation
        self.fade_progress = {}
        self.fade_frame = 0

        # Global frame counter for fading
        self.global_frame = 0

        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.board_a = [
                    [c for c in line][: self.board_size]
                    for line in f.read().strip().split("\n")[: self.board_size]
                ]
        except FileNotFoundError:
            # Fallback for testing
            self.board_a = [
                [random.choice(["@", ".", ".", "."]) for _ in range(self.board_size)]
                for _ in range(self.board_size)
            ]

        self.board_height = len(self.board_a)
        self.board_width = len(self.board_a[0])

        self.px = (self.buffer.width() - (self.board_width * self.board_spacing)) // 2
        self.py = (self.buffer.height() - self.board_height) // 2

        for y in range(self.board_height):
            for x in range(self.board_width):
                if self.board_a[y][x] == ".":
                    self.twinkles[(self.px + (self.board_spacing * x), y + self.py)] = (
                        TWINKLE_SPEC(char="█", value=random.randint(0, 23))
                    )

    def update_twinkles(self):
        if self.twinkle_frame_counter % self.twinkle_update_frames != 0:
            self.twinkle_frame_counter += 1
            return

        for (x, y), twinkle in self.twinkles.items():
            twinkle.next()
            self.changes[(x, y)] = twinkle.fade.colored

        self.twinkle_frame_counter += 1

    def clear_previous_fork_lift(self):
        if self.previous_fork_lift_position is not None:
            pfx, pfy = self.previous_fork_lift_position
            prev_ui_pos = (self.px + (self.board_spacing * pfx), pfy + self.py)

            if prev_ui_pos in self.twinkles:
                self.changes[prev_ui_pos] = self.twinkles[prev_ui_pos].fade.colored
            elif 0 <= pfy < self.board_height and 0 <= pfx < self.board_width:
                if self.board_a[pfy][pfx] == "@":
                    self.changes[prev_ui_pos] = bc("@", 240).colored

    def clear_board_area(self):
        full_width = self.board_width * self.board_spacing
        full_height = self.board_height

        for y in range(self.py, self.py + full_height):
            for x in range(self.px, self.px + full_width):
                self.buffer.put_char(x, y, " ")

    def fill_spacing(self):
        if self.board_spacing <= 1:
            return

        for y in range(self.board_height):
            for x in range(self.board_width):
                ui_x = self.px + (self.board_spacing * x)
                ui_y = y + self.py

                char = self.board_a[y][x]

                for offset in range(1, self.board_spacing):
                    fill_x = ui_x + offset

                    if char == ".":
                        if (ui_x, ui_y) in self.twinkles:
                            self.changes[(fill_x, ui_y)] = self.twinkles[
                                (ui_x, ui_y)
                            ].fade.colored
                    elif char == "@":
                        if (ui_x, ui_y) in self.changes:
                            self.changes[(fill_x, ui_y)] = self.changes[(ui_x, ui_y)]
                        else:
                            self.changes[(fill_x, ui_y)] = bc("@", 240).colored

    def move(self):
        if self.effective_frames % self.halt_frames != 0:
            self.effective_frames += 1
            return

        if (
            0 <= self.fork_lift_position[0] < self.board_width
            and 0 <= self.fork_lift_position[1] < self.board_height
        ):
            self.previous_fork_lift_position = self.fork_lift_position

        fx, fy = self.fork_lift_position

        fx += 1

        if fx >= self.board_width:
            fx = 0
            fy += 1

        if fy >= self.board_height:
            if len(self.removeable) == 0:
                self.state = "done"
            else:
                self.state = "marking"
            self.fork_lift_position = (0, 0)
            self.previous_fork_lift_position = None
            return

        self.fork_lift_position = (fx, fy)

        if self.board_a[fy][fx] == "@":
            self.checking_roll = True
            self.checked_directions = 0
            self.rolls_found = 0
            self.checked_changes.clear()

        self.effective_frames += 1

    def check(self):
        if not self.quick_mode and self.check_frames % self.check_halt_frames != 0:
            self.check_frames += 1
            return

        dx, dy = self.directions[self.checked_directions]
        fx, fy = self.fork_lift_position

        new_x, new_y = fx + dx, fy + dy
        new_ui_x, new_ui_y = self.px + (self.board_spacing * new_x), new_y + self.py

        if 0 <= new_x < self.board_width and 0 <= new_y < self.board_height:
            piece = self.board_a[new_y][new_x]
            if piece == "@":
                if not self.quick_mode:
                    self.changes[(new_ui_x, new_ui_y)] = bc("@", 91, 255).colored
                    self.checked_changes[(new_ui_x, new_ui_y)] = "@"
                self.rolls_found += 1

        if not self.quick_mode:
            self.check_frames += 1

        self.checked_directions += 1

        if self.checked_directions == len(self.directions):
            self.checking_roll = False

            if self.rolls_found < 4:
                fx, fy = self.fork_lift_position
                pos = (self.px + (self.board_spacing * fx), fy + self.py)
                self.removeable[pos] = (fx, fy)

            for pos in self.checked_changes.keys():
                if pos not in self.removeable:
                    self.fading_checked[pos] = self.global_frame

            self.checked_changes.clear()

    def mark_phase(self):
        if self.effective_frames < 30:
            self.effective_frames += 1
            return

        self.state = "removing"
        self.fade_frame = 0

        for pos in self.removeable.keys():
            self.fade_progress[pos] = 0

        self.effective_frames = 0

    def removing_phase(self):
        if self.fade_frame < self.fade_frames:
            progress = self.fade_frame / self.fade_frames

            for pos in self.removeable.keys():
                if pos not in self.removed:
                    color = int(255 - (255 - 232) * progress)
                    self.fade_progress[pos] = color

            self.fade_frame += 1
        else:
            for pos in self.removeable.keys():
                fx, fy = self.removeable[pos]
                self.board_a[fy][fx] = "."
                self.removed.add(pos)
                self.twinkles[pos] = TWINKLE_SPEC(char="█", value=random.randint(0, 23))

            self.state = "scanning"
            self.fork_lift_position = (-1, 0)
            self.previous_fork_lift_position = None
            self.removeable.clear()
            self.fade_progress.clear()
            self.effective_frames = 0

    def place_board(self):
        for y in range(self.board_height):
            for x in range(self.board_width):
                char = self.board_a[y][x]
                ui_x = self.px + (self.board_spacing * x)
                ui_y = y + self.py

                if char == "@" and (ui_x, ui_y) not in self.removeable:
                    self.changes[(ui_x, ui_y)] = bc("@", 240).colored

    def place_removeable(self):
        if self.state == "scanning":
            for pos in self.removeable.keys():
                self.changes[pos] = bc("█", 196).colored
        elif self.state == "marking":
            color = 255 if (self.effective_frames // 5) % 2 == 0 else 196
            for pos in self.removeable.keys():
                self.changes[pos] = bc("@", color).colored
        elif self.state == "removing":
            for pos, color in self.fade_progress.items():
                self.changes[pos] = bc("@", color).colored

    def place_fork_lift(self):
        if self.state == "scanning":
            self.clear_previous_fork_lift()

            fx, fy = self.fork_lift_position
            if 0 <= fx < self.board_width and 0 <= fy < self.board_height:
                pos = (self.px + (self.board_spacing * fx), fy + self.py)
                self.changes[pos] = bc("█", 27, 27).colored

    def update_fading_checked(self):
        to_remove = []

        for pos, start_frame in list(self.fading_checked.items()):
            elapsed = self.global_frame - start_frame

            if elapsed < self.check_fade_frames:
                progress = elapsed / self.check_fade_frames
                bg_color = int(255 - (255 - 232) * progress)
                self.changes[pos] = bc("@", 91, bg_color).colored
            else:
                self.changes[pos] = bc("@", 240).colored
                to_remove.append(pos)

        for pos in to_remove:
            del self.fading_checked[pos]

    def get_board_changes(self, frame_number: int):
        self.global_frame += 1

        self.update_twinkles()
        self.place_board()
        self.update_fading_checked()

        if self.state != "done":
            if self.state == "scanning":
                if self.checking_roll:
                    self.check()
                else:
                    self.move()
            elif self.state == "marking":
                self.mark_phase()
            elif self.state == "removing":
                self.removing_phase()

            self.place_removeable()
            self.place_fork_lift()

        self.fill_spacing()

    def place_changes(self):
        for (x, y), val in self.changes.items():
            self.buffer.put_char(x, y, val)

    def render_frame(self, frame_number: int):
        if frame_number % self.second_effect_halt == 0:
            if self.second_effect is not None:
                self.second_effect.render_frame(frame_number=frame_number)
                self.buffer.sync_with(self.second_effect.buffer)

        self.clear_board_area()
        self.get_board_changes(frame_number=frame_number)
        self.place_changes()


def animate(screen: Screen):
    renderer = EffectRenderer(
        screen=screen,
        frames=float("inf"),
        frame_time=0,
        effect_type="static",
        background=" ",
        transparent=False,
    )

    twinkle = effect_registry.create(
        "twinkle",
        Buffer(screen.height, screen.width),
        " ",
        settings=TwinkleSettings(density=0.05),
    )

    fireworks = effect_registry.create(
        "firework",
        Buffer(screen.height, screen.width),
        " ",
        settings=FireworkSettings(
            firework_type="random", color_enabled=True, color_type="twotone", rate=0.05
        ),
    )
    if isinstance(fireworks, FireworkEffect):
        fireworks.set_second_effect(twinkle)

    renderer.effect = AdventOfCodeDay04Effect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        part="two",
        data_file="datasmall",
        second_effect=fireworks,
        second_effect_halt=300,
        halt_frames=30,
        check_halt_frames=50,
        board_size=20,
        board_spacing=2,
        fade_frames=1000,
        quick_mode=False,
        twinkle_update_frames=100,
        check_fade_frames=1000,
    )

    renderer.run()


if __name__ in ["__main__", "day04_animate"]:
    Screen.show(animate)
