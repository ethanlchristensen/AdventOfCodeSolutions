"""
Advent of Code 2025 - Day 4 Animation
"""

import random

from bruhanimate import (
    Screen,
    BaseEffect,
    Buffer,
    EffectRenderer,
    FireworkEffect,
    TwinkleEffect,
    TWINKLE_SPEC,
)

from bruhcolor import bruhcolored as bc


class AdventOfCodeDay04Effect(BaseEffect):
    def __init__(
        self,
        buffer: Buffer,
        background: str,
        part: str = "one",
        data_file: str = "data",
        second_effect: BaseEffect | None = None,
        second_effect_halt: int = 1,
        halt_frames: int = 5,
        check_halt_frames: int = 5,
        board_size: int = 15,
        board_spacing: int = 1,
    ):
        super().__init__(buffer, background)
        self.part = part
        self.data_file = data_file
        self.second_effect = second_effect
        self.second_effect_halt = second_effect_halt
        self.board_a = None
        self.board_b = None
        self.board_height = None
        self.board_width = None
        self.px = None
        self.py = None

        self.board_size = board_size
        self.board_spacing = board_spacing

        self.fork_life_bg = 245
        self.fork_lift_position = (0, 0)

        self.halt_frames = halt_frames
        self.check_halt_frames = check_halt_frames

        self.effective_frames = 0

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

        self.checking_roll = False
        self.rolls_found = 0
        self.checked_directions = 0
        self.checked_changes = {}
        self.check_frames = 0

        self.removeable = {}

        self._load_data()

    def _load_data(self):
        with open(self.data_file, "r") as f:
            self.board_a = [
                [c for c in line][: self.board_size]
                for line in f.read().strip().split("\n")[: self.board_size]
            ]
            self.board_height = len(self.board_a)
            self.board_width = len(self.board_a[0])

            self.px = (
                self.buffer.width() - (self.board_width * self.board_spacing)
            ) // 2
            self.py = (self.buffer.height() - self.board_height) // 2

            for y in range(self.board_height):
                for x in range(self.board_width):
                    if self.board_a[y][x] == ".":
                        self.twinkles[
                            (self.px + (self.board_spacing * x), y + self.py)
                        ] = TWINKLE_SPEC(char=".", value=random.randint(0, 23))
            if self.board_a[0][0] == "@":
                self.checking_roll = True

    def update_twinkles(self):
        for (x, y), twinkle in self.twinkles.items():
            twinkle.next()
            self.changes[(x, y)] = twinkle.fade.colored

    def move(self):
        if self.effective_frames % self.halt_frames != 0:
            self.effective_frames += 1
            return
        fx, fy = self.fork_lift_position

        fx += 1

        if fx >= self.board_width:
            fx = 0
            fy += 1

        if fy >= self.board_height:
            fy = 0

        self.fork_lift_position = (fx, fy)

        if self.board_a[fy][fx] == "@":
            self.checking_roll = True
            self.checked_directions = 0
            self.rolls_found = 0
            self.checked_changes.clear()

    def check(self):
        if self.check_frames % self.check_halt_frames != 0:
            self.check_frames += 1
            return
        dx, dy = self.directions[self.checked_directions]

        fx, fy = self.fork_lift_position

        new_x, new_y = fx + dx, fy + dy
        new_ui_x, new_ui_y = self.px + (self.board_spacing * new_x), new_y + self.py

        if 0 <= new_x < self.board_width and 0 <= new_y < self.board_height:
            piece = self.board_a[new_y][new_x]
            if piece == "@":
                self.changes[(new_ui_x, new_ui_y)] = bc("@", 196, 235).colored
                self.checked_changes[(new_ui_x, new_ui_y)] = "@"
                self.rolls_found += 1
                self.check_frames = 0

        self.check_frames += 1

        self.checked_directions += 1

        if self.checked_directions == len(self.directions):
            self.checking_roll = False
            for (x, y), val in self.checked_changes.items():
                self.changes[(x, y)] = val
            if self.rolls_found < 4:
                fx, fy = self.fork_lift_position
                self.removeable[(self.px + (self.board_spacing * fx), fy + self.py)] = (
                    "X"
                )

    def place_removeable(self):
        for (x, y), val in self.removeable.items():
            self.changes[(x, y)] = bc(val, 196).colored

    def place_fork_lift(self):
        fx, fy = self.fork_lift_position
        self.changes[(self.px + (self.board_spacing * fx), fy + self.py)] = bc(
            "#", 196, 196
        ).colored

    def get_board_changes(self, frame_number: int):
        self.update_twinkles()

        if self.checking_roll:
            self.check()
        else:
            self.move(frame_number=frame_number)

        self.place_removeable()
        self.place_fork_lift()

    def place_changes(self):
        for (x, y), val in self.changes.items():
            self.buffer.put_char(x, y, val)

    def render_frame(self, frame_number: int):
        if frame_number % self.second_effect_halt == 0:
            if self.second_effect is not None:
                self.second_effect.render_frame(frame_number=frame_number)
                self.second_effect.buffer.sync_with(self.buffer)

        self.get_board_changes(frame_number=frame_number)
        self.place_changes()


def animate(screen):
    renderer = EffectRenderer(
        screen=screen,
        frames=float("inf"),
        frame_time=0.005,
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

    renderer.effect = AdventOfCodeDay04Effect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        part="two",
        data_file="data",
        second_effect=fireworks,
        second_effect_halt=2,
        halt_frames=2,
        check_halt_frames=5,
        board_size=20,
        board_spacing=2,
    )

    renderer.run()


if __name__ in ["__main__", "day04_animate"]:
    Screen.show(animate)
