"""
Advent of Code 2025 - Day 12 Animation
"""

from bruhanimate import Screen, BaseEffect, Buffer, EffectRenderer, SnowEffect



class AdventOfCodeDay12Effect(BaseEffect):
    def __init__(
        self,
        buffer: Buffer,
        background: str,
        part: str = "one",
        data_file: str = "data",
        second_effect: BaseEffect | None = None,
        second_effect_halt: int = 1,
    ):
        super().__init__(buffer, background)
        self.part = part
        self.data_file = data_file
        self.second_effect = second_effect
        self.second_effect_halt = second_effect_halt
        self.data = None

        self._load_data()

    def _load_data(self):
        with open(self.data_file, "r") as f:
            self.data = f.read().strip()

    def render_frame(self, frame_number: int):
        if frame_number % self.second_effect_halt == 0:
            if self.second_effect is not None:
                self.second_effect.render_frame(frame_number=frame_number)
                self.buffer.sync_with(self.second_effect.buffer)


def animate(screen):
    renderer = EffectRenderer(
        screen=screen,
        frames=float("inf"),
        frame_time=0.05,
        effect_type="static",
        background=" ",
        transparent=False,
    )

    snow = SnowEffect(Buffer(screen.height, screen.width), " ")
    renderer.effect = AdventOfCodeDay12Effect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        part="two",
        data_file="data",
        second_effect=snow,
        second_effect_halt=3,
    )

    renderer.run()


if __name__ in ["__main__", "day12_animate"]:
    Screen.show(animate)
