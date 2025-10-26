import time
from bruhanimate import Screen, Buffer
from bruhcolor import bruhcolored


class X:
    def __init__(self, x, y, v, c):
        self.x = x
        self.y = y
        self.v = v
        self.c = c
        self.active = True
        self.vm = {
            255: 253,
            253: 250,
            250: 247,
            247: 245,
            245: 243,
            243: 240,
            240: 237,
            237: 235,
            235: 232,
            232: 232,
        }
    def next_v(self):
        if self.active:
            self.v = self.vm[self.v]
            if self.v == 232:
                self.active = False


def load_data(name='datasmall'):
    file = open(name, 'r')
    data = [[c for c in line.strip()] for line in file.readlines()]
    file.close()
    return data

def get_direction(char: str):
    if char == "^":
        return [0, -1]
    if char == ">":
        return [1, 0]
    if char == "<":
        return [-1, 0]
    if char == "v":
        return [0, 1]

def get_next_guard(current_guard):
    if current_guard == "^":
        return ">"
    if current_guard == ">":
        return "v"
    if current_guard == "v":
        return "<"
    if current_guard == "<":
        return "^"

def get_next_position(position, data, xs):
    current_guard = data[position[1]][position[0]]
    direction = get_direction(data[position[1]][position[0]])
    new_position = (position[0] + direction[0], position[1] + direction[1])
    if not 0 <= new_position[0] < len(data[0]) or not 0 <= new_position[1] < len(data):
            xs.append(X(x=position[0], y=position[1], v=255, c=current_guard))
            data[position[1]][position[0]] = "X"
            return None, data, xs
    if data[new_position[1]][new_position[0]] in ["#", "0"]:
        next_guard = get_next_guard(current_guard)
        data[position[1]][position[0]] = next_guard
        return position, data, xs
    else:
        data[position[1]][position[0]] = "X"
        xs.append(X(x=position[0], y=position[1], v=255, c=current_guard))
        data[new_position[1]][new_position[0]] = current_guard
        return new_position, data, xs

def get_starting_guard_position(data):
    for y in range(len(data)):
        for x in range(len(data[0])):
            if data[y][x] == "^":
                return (x, y)

def run(screen: Screen):
    """
    code to solve part one
    """
    data = load_data()
    for ydx in range(len(data)):
        for xdx in range(len(data[0])):
            xs = []
            guard_position = get_starting_guard_position(data=load_data())
            if xdx == guard_position[0] and ydx == guard_position[1]:
                continue
            if data[ydx][xdx] == "#":
                continue
            screen.clear()
            for y in range(len(data)):
                for x in range(len(data[0])):
                    screen.print_at(data[y][x], x, y, 1)
            this_data = [[data[j][i] for i in range(len(data[0]))] for j in range(len(data))]
            this_data[ydx][xdx] = "0"
            screen.print_at(x=xdx, y=ydx, text=bruhcolored("0", 27).colored, width=1)
            new_position = guard_position
            new_data = this_data
            while True:
                new_position, new_data, new_xs = get_next_position(position=new_position, data=new_data, xs=xs)
                if new_position == None:
                    break
                for erm in new_xs:
                    screen.print_at(x=erm.x, y=erm.y, text=bruhcolored(text=erm.c, color=erm.v).colored, width=1)
                    erm.next_v()
                    if not erm.active:
                        screen.print_at(x=erm.x, y=erm.y, text=" ", width=1)
                new_xs = [erm for erm in new_xs if erm.active]
                screen.print_at(x=new_position[0], y=new_position[1], text=bruhcolored(text=new_data[new_position[1]][new_position[0]], color=220).colored, width=1)
                time.sleep(0.02)
    input()

if __name__ == "__main__":
   Screen.show(run)