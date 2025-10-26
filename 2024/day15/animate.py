import time
import random
from bruhcolor import bruhcolored as bc
from bruhanimate import (
    Screen,
    BaseEffect,
    EffectRenderer,
    Buffer,
    PlasmaEffect,
    TwinkleEffect,
    SnowEffect,
    FireworkEffect,
    text_to_image
)

# DECAY_VALUES = [17, 18, 19, 20, 21]
DECAY_VALUES = list(range(232, 255))
# DECAY_VALUES = [val for val in DECAY_VALUES for _ in range(3)]

class Decay:
    def __init__(
        self, x: int, y: int, char: str, values: list[int] = DECAY_VALUES
    ) -> None:
        self.x = x
        self.y = y
        self.char = char
        self.values = values
        self.life = len(self.values) - 1
        self.active = True
        self.current_value = self.values[self.life]

    def update(self):
        self.life -= 1
        if self.life < 0:
            self.active = False
            return
        self.value = self.values[self.life]

    def get_colored_tile(self):
        return bc(text=self.char, color=self.values[self.life]).colored

class AdventOfCodeDay15Effect(BaseEffect):
    def __init__(
        self,
        buffer: Buffer,
        background: str,
        part: str = "one",
        data_file: str = "data",
        second_effect: PlasmaEffect | TwinkleEffect | SnowEffect = None,
        second_effect_halt: int = 1,
    ):
        super(AdventOfCodeDay15Effect, self).__init__(buffer, background)
        self.part = part
        self.data_file = data_file
        self.board = None
        self.moves = None
        self.char_to_color = {
            "#": 239,
            " ": None,
            "@": 27,
            "[": 91,
            "]": 91,
            "O": 91,
        }
        self.decay_tiles = []
        self.second_effect = second_effect
        self.second_effect_halt = second_effect_halt
        self.processed_move_images = []
        self.__load_data()

    def __load_data(self):
        with open(self.data_file, "r") as file:
            lines = file.readlines()
            if self.part == "two":
                for idx in range(len(lines) - 1):
                    lines[idx] = (
                        lines[idx]
                        .replace("#", "##")
                        .replace("O", "[]")
                        .replace(".", "  ")
                        .replace("@", "@ ")
                    )
            data = [list(line.strip().replace(".", " ")) for line in lines if line.strip() != ""]
            if self.data_file == "datasmall4":
                self.board = data[:-1]
                self.moves = data[-1][:len(data[-1])//4]
            else:
                self.board = data[:-1]
                self.moves = data[-1]

    def get_padding(self):
        return (self.buffer.width() - (len(self.board[0]))) // 2, (
            self.buffer.height() - len(self.board)
        ) // 2

    def get_direction(self, char: str):
        if char == "^":
            return (0, -1)
        if char == ">":
            return (1, 0)
        if char == "<":
            return (-1, 0)
        if char == "v":
            return (0, 1)

    def get_robot_position(self):
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                if self.board[y][x] == "@":
                    return (x, y)

    def get_gps_coordinates(self):
        total = 0
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                if self.board[y][x] in "O[":
                    total += (100 * y) + x
        return total

    def place_board_on_buffer(self):
        px, py = self.get_padding()
        for y in range(len(self.board)):
            for x in range(len(self.board[0])):
                char = self.board[y][x]
                if char == " ":
                    continue
                colored_value = bc(text=char, color=self.char_to_color[char]).colored
                self.buffer.put_char(
                    x=x + px, y=y + py, val=colored_value, transparent=True
                )
        for idx in range(len(self.decay_tiles)):
            tile = self.decay_tiles[idx]
            if self.buffer.get_char(tile.x + px, tile.y + py) == " ":
                self.buffer.put_char(
                    x=tile.x + px,
                    y=tile.y + py,
                    val=tile.get_colored_tile(),
                    transparent=True,
                )
            self.decay_tiles[idx].update()

        self.decay_tiles = [tile for tile in self.decay_tiles if tile.active]

    def generate_next_board_state(self, frame_number: int):
        if frame_number >= len(self.moves):
            return
        move = self.moves[frame_number]
        move_image = text_to_image(text=move)
        self.processed_move_images.append(move_image)
        for y in range(len(move_image)):
            self.buffer.put_at_center(y=self.buffer.height() - len(move_image) + y, text=move_image[y])

        robot_position = self.get_robot_position()
        can_move = True
        cords_to_move = [robot_position]
        iteration = 0
        dx, dy = self.get_direction(move)
        while iteration < len(cords_to_move):
            x, y = cords_to_move[iteration]
            nx, ny = x + dx, y + dy
            if self.board[ny][nx] == "O":
                if (nx, ny) not in cords_to_move:
                    cords_to_move.append((nx, ny))
            elif self.board[ny][nx] in "[]":
                if (nx, ny) not in cords_to_move:
                    cords_to_move.append((nx, ny))
                if self.board[ny][nx] == "]":
                    addition = (nx - 1, ny)
                    if addition not in cords_to_move:
                        cords_to_move.append(addition)
                elif self.board[ny][nx] == "[":
                    addition = (nx + 1, ny)
                    if addition not in cords_to_move:
                        cords_to_move.append(addition)
            elif self.board[ny][nx] == "#":
                can_move = False
                break
            iteration += 1

        if not can_move:
            return
        tmp = [
            [self.board[y][x] for x in range(len(self.board[0]))]
            for y in range(len(self.board))
        ]
        for x, y in cords_to_move:
            tmp[y][x] = " "
        for x, y in cords_to_move:
            tmp[y + dy][x + dx] = self.board[y][x]
            if self.board[y][x] == "@":
                self.decay_tiles.append(Decay(x=x, y=y, char="@"))
        self.board[:] = tmp[:]

    def render_frame(self, frame_number: int):
        if frame_number % self.second_effect_halt == 0:
            if not self.second_effect is None:
                self.second_effect.render_frame(frame_number=frame_number)
                self.buffer.sync_with(self.second_effect.buffer)
        self.place_board_on_buffer()
        self.generate_next_board_state(frame_number)

        gps_score = self.get_gps_coordinates()
        digit_images = []
        for number in list(str(gps_score)):
            digit_images.append(text_to_image(number))
        full_digit_rows = ["" for _ in range(len(digit_images[0]))]
        for digit in digit_images:
            for y in range(len(digit) - 1):
                full_digit_rows[y] += digit[y]
        for idx, row in enumerate(full_digit_rows):
            self.buffer.put_at_center(y=idx, text=row)

def animate(screen: Screen):
    renderer = EffectRenderer(
        screen=screen,
        frames=float("inf"),
        frame_time=0,
        effect_type="static",
        background=" ",
        transparent=False,
    )

    twinke_effect = TwinkleEffect(Buffer(screen.height, screen.width), " ")

    firework_effect = FireworkEffect(Buffer(screen.height, screen.width), " ")
    firework_effect.set_firework_color_enabled(True)
    firework_effect.set_firework_color_type("twotone")
    firework_effect.set_second_effect(second_effect=twinke_effect)
    firework_effect.set_firework_type("random")

    renderer.effect = AdventOfCodeDay15Effect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        part="two",
        data_file="datasmall4", # from advent of code
        second_effect=firework_effect,
        second_effect_halt=3,
    )

    renderer.run()


if __name__ == "__main__":
    Screen.show(animate)
