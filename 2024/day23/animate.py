import time
import string
import random
import networkx
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
    text_to_image,
    DrawLinesEffect,
    Line,
)

class AdventOfCodeDay23Effect(BaseEffect):
    def __init__(
        self,
        buffer: Buffer,
        background: str,
        part: str = "one",
        data_file: str = "data",
        second_effect: DrawLinesEffect = None,
        second_effect_halt: int = 1,
        third_effect: SnowEffect |  PlasmaEffect | FireworkEffect | TwinkleEffect = None
    ):
        super(AdventOfCodeDay23Effect, self).__init__(buffer, background)
        self.part = part
        self.data_file = data_file
        self.second_effect = second_effect
        self.second_effect_halt = second_effect_halt
        self.third_effect = third_effect
        self.network = 0
        self.N = 26
        self.board = [[bc(text=".", color="232").colored for _ in range(self.N)] for _ in range(self.N)]
        self.nodes = set()
        self.edges = set()
        self.graph = None
        self.valid_networks = None
        self.__load_data()

    def __load_data(self):
        with open(self.data_file, "r") as file:
            data = [tuple(line.strip().split("-")) for line in file if line.strip() != ""]
            for c1, c2 in data:
                self.nodes.add(c1)
                self.nodes.add(c2)
                self.edges.add((c1, c2))
                self.edges.add((c2, c1))
            self.graph = networkx.Graph()
            self.graph.add_nodes_from(self.nodes)
            self.graph.add_edges_from(self.edges)

    def get_padding(self):
        return (self.buffer.width() - (len(self.board[0]) * 2)) // 2, (
            self.buffer.height() - len(self.board)
        ) // 2

    def place_board_on_buffer(self):
        px, py = self.get_padding()
        for y in range(len(self.board)):
            self.buffer.put_char(x=px-2, y=y+py, val=string.ascii_uppercase[y])
        x_offset = 0
        for x in range(len(self.board[0])):
            self.buffer.put_char(x=x+px+x_offset, y=py-1, val=string.ascii_uppercase[x])
            x_offset += 1
        for y in range(len(self.board)):
            x_offset = 0
            for x in range(len(self.board[0])):
                char = self.board[y][x]
                if char == " ":
                    x_offset += 1
                    continue
                self.buffer.put_char(
                    x=x + px + x_offset, y=y + py, val=char, transparent=True
                )
                x_offset += 1

    def computer_to_coordinate(self, computer):
        x, y = computer[0], computer[1]
        x = string.ascii_lowercase.index(x)
        y = string.ascii_lowercase.index(y)
        return (x, y)

    def render_frame(self, frame_number: int):
        if self.third_effect:
            self.third_effect.render_frame(frame_number=frame_number)
        
        if frame_number % self.second_effect_halt == 0:
            px, py = self.get_padding()
            if not self.valid_networks:
                networks = list(networkx.enumerate_all_cliques(self.graph))
                triples = [network for network in networks if len(network) == 3]
                self.valid_networks = [network for network in triples if any([node.startswith("t") for node in network])]
            
            # Clear buffer and lines each time
            self.buffer.clear_buffer()
            self.second_effect.buffer.clear_buffer()
            self.second_effect.lines = []
            
            # Process past networks (gray)
            for idx, network in enumerate(self.valid_networks[:self.network]):
                coords = [self.computer_to_coordinate(computer) for computer in network]
                for x, y in coords:
                    self.board[y][x] = bc(text="@", color=240).colored
            
            # Process current network (green with lines)
            if self.network < len(self.valid_networks):
                network = self.valid_networks[self.network]
                coords = [self.computer_to_coordinate(computer) for computer in network]
                
                # Mark nodes
                for x, y in coords:
                    self.board[y][x] = bc(text="@", color=76).colored
                
                # Add lines between all nodes in the current triangle
                if len(coords) >= 2:  # Need at least 2 points for a line
                    for i in range(len(coords)):
                        for j in range(i+1, len(coords)):
                            x1, y1 = coords[i]
                            x2, y2 = coords[j]
                            # Convert to screen coordinates
                            screen_x1 = x1 * 2 + px
                            screen_x2 = x2 * 2 + px
                            screen_y1 = y1 + py
                            screen_y2 = y2 + py
                            
                            # Add the line to second_effect
                            self.second_effect.add_line(
                                start_point=(screen_x1, screen_y1), 
                                end_point=(screen_x2, screen_y2)
                            )
            
            # If we're at the end, just show all nodes in gray
            elif self.network == len(self.valid_networks):
                for network in self.valid_networks:
                    coords = [self.computer_to_coordinate(computer) for computer in network]
                    for x, y in coords:
                        self.board[y][x] = bc(text="@", color=240).colored
            
            # Apply third effect if present
            if self.third_effect:
                self.buffer.sync_with(self.third_effect.buffer)
            
            # Place the board on the buffer
            self.place_board_on_buffer()
            
            # Render the lines
            self.second_effect.render_frame(frame_number=0)  # Always use frame 0
            
            # Merge the line effects onto the main buffer
            for y in range(self.buffer.height()):
                for x in range(self.buffer.width()):
                    effect_char = self.second_effect.buffer.get_char(x, y)
                    main_char = self.buffer.get_char(x, y)
                    if effect_char != " " and main_char != bc(text="@", color=76).colored:
                        self.buffer.put_char(x, y, effect_char)
            
            # Show stats
            text = f"Total Triples: {self.network + 1} / {len(self.valid_networks)}"
            self.buffer.put_at(x=0, y=0, text=text)
            
            # Move to next network for next frame
            self.network += 1
        else:
            # Non-update frame, just redraw current state
            # Keep the current visualization without advancing
            self.buffer.clear_buffer()
            if self.third_effect:
                self.buffer.sync_with(self.third_effect.buffer)
            self.place_board_on_buffer()
            self.second_effect.render_frame(frame_number=0)  # Always use frame 0
            
            for y in range(self.buffer.height()):
                for x in range(self.buffer.width()):
                    effect_char = self.second_effect.buffer.get_char(x, y)
                    main_char = self.buffer.get_char(x, y)
                    if effect_char != " " and main_char != bc(text="@", color=76).colored:
                        self.buffer.put_char(x, y, effect_char)
            
            text = f"Total Triples: {self.network} / {len(self.valid_networks) if self.valid_networks else 0}"
            self.buffer.put_at(x=0, y=0, text=text)

def animate(screen: Screen):
    renderer = EffectRenderer(
        screen=screen,
        frames=float("inf"),
        frame_time=0.05,
        effect_type="static",
        background=" ",
        transparent=False,
    )

    second_effect = DrawLinesEffect(buffer=Buffer(screen.height, screen.width), background=" ", thin=False)
    twinke_effect = TwinkleEffect(Buffer(screen.height, screen.width), " ")
    firework_effect = FireworkEffect(Buffer(screen.height, screen.width), " ")
    firework_effect.set_firework_color_enabled(True)
    firework_effect.set_firework_color_type("twotone")
    firework_effect.set_second_effect(second_effect=twinke_effect)
    firework_effect.set_firework_type("random")
    plasma_effect = PlasmaEffect(Buffer(screen.height, screen.width), " ")
    plasma_effect.update_color_properties(True, True, False)

    renderer.effect = AdventOfCodeDay23Effect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        part="two",
        data_file="data", # from advent of code
        second_effect=second_effect,
        second_effect_halt=1,
        third_effect=firework_effect
    )

    renderer.run()


if __name__ == "__main__":
    Screen.show(animate)
