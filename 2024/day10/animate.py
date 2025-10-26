from bruhanimate import Screen, Buffer, EffectRenderer, BaseEffect
from bruhcolor import bruhcolored as bc
import time
import uuid
import random


class AdventOfCodeDay10Effect(BaseEffect):
    def __init__(self, buffer: Buffer, background: str):
        super(AdventOfCodeDay10Effect).__init__(buffer, background)
    
    def render_frame(self, frame_number: int):
        pass


class FoundTile:
    def __init__(self, char, x, y, value = 9, hang_time = 20):
        self.char = char
        self.x = x
        self.y = y
        self.value = value
        self.color_mapping = {
            -1: None,
            0: 233,
            1: 234,
            2: 236,
            3: 238,
            4: 240,
            5: 242,
            6: 244,
            7: 247,
            8: 252,
            9: 255,
        }
        self.active = True
        self.hang_time = hang_time
        self.tick = 0

    def _tick(self):
        self.tick += 1
    
    def update(self):
        if not self.tick % self.hang_time == 0:
            return
        if not self.active:
            return
        self.value -= 1
        if self.value == -1:
            self.active = False
    
    def get_colored(self):
        return bc(text=self.char, color=255, on_color=self.color_mapping[self.value]).colored

    def cords(self):
        return (self.x, self.y)
    

def load_data(name="data"):
    with open(name, "r") as file:
        return [list(line.strip()) for line in file.readlines()]


def find_all_trail_heads(data):
    trail_heads = []
    for y in range(len(data)):
        for x in range(len(data[0])):
            if data[y][x] == "0":
                trail_heads.append((x, y))
    return trail_heads


found_tiles = []
paths_hit = 0

def run(screen: Screen):
    global found_tiles, paths_hit

    directions = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    
    data = load_data()

    tiles_traversed = {}

    def get_total_trail_heads():
        output = 0
        for k, v in tiles_traversed.items():
            output += v["trail_heads"]
        return output

    def get_total_found_paths():
        output = 0
        for k, v in tiles_traversed.items():
            output += v["paths_found"]
        return output

    def get_padding_x_y():
        return((screen.width - (len(data[0]) * 2)) // 2, (screen.height - len(data)) // 2)
    
    padding_x, padding_y = get_padding_x_y()

    for y in range(len(data)):
        offset_x = 0
        for x in range(len(data[0])):
            # screen.print_at(
            #     text=bc(text=" ", on_color=color_mapping[data[y][x]]).colored,
            #     x=x + padding_x + x,
            #     y=y + padding_y,
            #     width=1
            # )
            screen.print_at(
                text=bc(text=data[y][x]).colored,
                x=x + padding_x + x,
                y=y + padding_y,
                width=1
            )
            screen.print_at(
                text=" ",
                x=x + padding_x + x + 1,
                y=y + padding_y,
                width=1
            )
            offset_x += 1
    
    def update_found_tiles():
        global found_tiles
        for idx in range(len(found_tiles)):
            found_tiles[idx]._tick()
            found_tiles[idx].update()
            screen.print_at(text=found_tiles[idx].get_colored(), x=found_tiles[idx].x, y=found_tiles[idx].y, width=1)
        found_tiles = [tile for tile in found_tiles if tile.active]

    def check_dir(value, x, y, dir, trail_head_id, placed_x, mode="part1"):
        global found_tiles, paths_hit
        ppx,ppy = get_padding_x_y()
        dx, dy = x + dir[0], y + dir[1]
        if 0 <= dy < len(data) and 0 <= dx < len(data[0]):
            if data[dy][dx] != ".":
                if int(data[dy][dx]) == int(value) + 1:
                    if (dx, dy) not in tiles_traversed[trail_head_id]["seen_xy"]:
                        tiles_traversed[trail_head_id]["seen_xy"].append((dx, dy))
                        if data[dy][dx] == "9":
                            screen.print_at(text=bc(text=" ", on_color=76).colored, x=dx + padding_x + dx, y=dy + padding_y, width=1)
                            tiles_traversed[trail_head_id]["trail_heads"] += 1
                            # tiles_traversed[trail_head_id]["paths_found"] += 1
                            paths_hit += 1
                            return placed_x
                        new_value = data[dy][dx]

                        screen.print_at("┗", 0, screen.height-1, 1)
                        screen.print_at("┛", screen.width-1, screen.height-1, 1)
                        screen.print_at("┓", screen.width-1, 0, 1)
                        screen.print_at("┏", 0, 0, 1)
                        px, py = get_padding_x_y()
                        # text = f"Total Valid Paths Score: {get_total_found_paths()}"
                        text_nine_hit = f"Total Reachable Trail 9's Score: {paths_hit}"
                        text_2 = f"┃Checking trailhead: {trail_head_id}"
                        for xx in range(1, screen.width - 1):
                            if xx > len(text_nine_hit) + 2:
                                screen.print_at(text="━", x=xx, y=0, width=1)
                        screen.print_at(text=f"┏{'━'*len(text_nine_hit)}┳", x=0, y=0, width=len(text_nine_hit) + 2)
                        screen.print_at(text=f"┃{text_nine_hit}┃", x=0, y=1, width=len(text_nine_hit) + 2)
                        screen.print_at(text=f"┣{'━'*len(text_nine_hit)}┛", x=0, y=2, width=len(text_nine_hit) + 2)
                        screen.print_at(text=text_2, x=0, y=3, width=len(text_2))
                        screen.print_at(text="┃", x=0, y=4, width=1)
                        screen.print_at(text="┃Trail Head Stats: <Trail Head Id>: <9's Reachable>", x=0, y=5, width=len("┃Trail Head Stats: <Trail Head Id>: <9's Reachable>"))
                        offset_y = 0
                        offset_x = 0
                        for idx, k in enumerate(tiles_traversed):
                            if idx % (screen.height - 7) == 0 and idx != 0:
                                offset_x += 1
                                offset_y = 0
                            if offset_x == 0:
                                text_3 = f"┃{k[:4]}: {tiles_traversed[k]['trail_heads']: >1d}"
                            else:
                                text_3 = f" {k[:4]}: {tiles_traversed[k]['trail_heads']: >1d}"
                            screen.print_at(text=text_3, x=offset_x * 8, y=6 + offset_y, width=len(text_3))
                            offset_y += 1
                        seen_tiles = [tile.cords() for tile in found_tiles]
                        if not (x + px + x, y + py + y) in seen_tiles:
                            found_tiles.append(FoundTile(
                                char=new_value, x=x + px + x, y=y + py
                            ))
                        # time.sleep(0.1)
                        placed_x = check_dir(new_value, dx, dy, directions[0], trail_head_id, placed_x)
                        placed_x = check_dir(new_value, dx, dy, directions[1], trail_head_id, placed_x)
                        placed_x = check_dir(new_value, dx, dy, directions[2], trail_head_id, placed_x)
                        placed_x = check_dir(new_value, dx, dy, directions[3], trail_head_id, placed_x)
        else:
            placed_x.append((dx + ppx + dx, dy + ppy))
            screen.print_at(text=bc(text="X", color="red", on_color=None).colored, x=dx + ppx + dx, y=dy + ppy, width=1) 
        update_found_tiles()
        return placed_x
    trail_heads = find_all_trail_heads(data=data)

    for trail_head in trail_heads:
        placed_x = []
        trail_head_id = str(uuid.uuid4())
        tiles_traversed[trail_head_id] = {"trail_heads": 0, "paths_found": 0, "seen_xy": [], "color": random.randint(0, 231)}
        padding_x, padding_y = get_padding_x_y()
        for yy in range(1, screen.height - 1):
            if yy != 2:
                screen.print_at(text="┃", x=0, y=yy, width=1)
            screen.print_at(text="┃", x=screen.width - 1, y=yy, width=1)
        for xx in range(1, screen.width - 1):
            screen.print_at(text="━", x=xx, y=screen.height - 1, width=1)
        found_tiles.append(FoundTile(
            char="0", x=trail_head[0] + padding_x + trail_head[0], y=trail_head[1] + padding_y
        ))
        placed_x= check_dir("0", trail_head[0], trail_head[1], directions[0], trail_head_id, placed_x)
        placed_x= check_dir("0", trail_head[0], trail_head[1], directions[1], trail_head_id, placed_x)
        placed_x= check_dir("0", trail_head[0], trail_head[1], directions[2], trail_head_id, placed_x)
        placed_x= check_dir("0", trail_head[0], trail_head[1], directions[3], trail_head_id, placed_x)
        for X in placed_x:
            screen.print_at(" ", x=X[0], y=X[1], width=1)
    while found_tiles:
        update_found_tiles()
    text_nine_hit = f"Total Reachable Trail 9's Score: {paths_hit}"
    screen.print_at(text=f"┃{text_nine_hit}┃", x=0, y=1, width=len(text_nine_hit) + 2)
    input()


if __name__ == "__main__":
    Screen.show(run)
