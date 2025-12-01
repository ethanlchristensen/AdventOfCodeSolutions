"""
Advent of Code 2025 - Day 1 Animation
"""

import random

from bruhanimate import (
    Screen,
    BaseEffect,
    Buffer,
    EffectRenderer,
    FireworkEffect,
    TwinkleEffect,
    SnowEffect,
    PlasmaEffect,
    StarEffect,
    text_to_image,
)

from bruhcolor import bruhcolored


class AdventOfCodeDay01Effect(BaseEffect):
    def __init__(
        self,
        buffer: Buffer,
        background: str,
        part: str = "one",
        data_file: str = "data",
        effect_halt: int = 10,
        second_effect: FireworkEffect | StarEffect | SnowEffect | PlasmaEffect | None = None,
        second_effect_halt: int = 1,
        min_transition_frames: int = 2,
        max_transition_frames: int = 20,
        accel_clicks: int = 10,
        curve_intensity: int = 5,
        blur_threshold: int = 3,
        instruction_pause_frames: int = 10,
        show_lines: bool = True,
        exit_rotation_speed: int = 3,
    ):
        super().__init__(buffer, background)
        self.part = part
        self.data_file = data_file
        self.effect_halt = effect_halt
        self.second_effect = second_effect
        self.second_effect_halt = second_effect_halt
        self.min_transition_frames = min_transition_frames
        self.max_transition_frames = max_transition_frames
        self.accel_clicks = accel_clicks
        self.blur_threshold = blur_threshold
        self.instruction_pause_frames = instruction_pause_frames
        self.show_lines = show_lines
        self.exit_rotation_speed =exit_rotation_speed
        self.line_char = "|"
        self.number_images = [
            [[c for c in row] for row in text_to_image(str(i), font="doom")]
            for i in range(100)
        ]
        self.data = None
        self.zeros = 0
        self.position = 50

        # number arch curve
        curve_intensity = max(1, min(10, curve_intensity))
        self.curve_max_offset = 5 + (curve_intensity * 2)
        self.curve_divisor = 6.0 - (curve_intensity * 0.35)
        self.curve_exponent = 1.5 + (curve_intensity * 0.25)

        # transition state tracking
        self.target_position = 0
        self.transition_progress = 0.0
        self.is_transitioning = False
        self.transition_direction = 1
        self.transition_frames = max_transition_frames

        # instruction tracking
        self.current_instruction_index = 0
        self.current_instruction_clicks_remaining = 0
        self.current_instruction_total_clicks = 0
        self.current_instruction_direction = "R"
        self.full_rotations_completed = 0
        self.flash_frames_remaining = 0

        # flash effect for 0 hits
        self.flash_frames_remaining = 0
        self.flash_color = 27
        self.flash_duration = 30

        # zeros counter flash effect
        self.zeros_flash_frames_remaining = 0
        self.zeros_flash_duration = 60
        self.zeros_flash_colors = [196, 226, 46, 51, 201, 165, 129, 93]

        # pause tracking
        self.is_paused = False
        self.pause_frames_remaining = 0
        self.has_completed_instruction = False
        self.has_paused_for_current_instruction = False

        # completion/exit state
        self.all_instructions_completed = False
        self.exit_direction = 1
        self.exit_offset = 0
        self.zeros_y_position = None
        self.zeros_target_y = None

        self._load_data()

    def _load_data(self):
        with open(self.data_file, "r") as f:
            self.data = f.read().strip().split("\n")

    def _rotate(self, position, direction, clicks) -> tuple[int, bool]:
        old_position = position

        passed_through = False

        if direction == "L":
            position += -clicks
        else:
            position += clicks

        if position < 0:
            position = 100 + position
            if position != 0 and old_position != 0:
                passed_through = True
        elif position > 99:
            position = position - 100
            if position != 0 and old_position != 0:
                passed_through = True

        return position, passed_through

    def _get_moves(self, data: str) -> tuple[str, int, int, int]:
        direction = data[0]
        true_clicks = int(data[1:])
        observed_clicks = true_clicks % 100
        times_passed_zero = true_clicks // 100
        return (direction, true_clicks, observed_clicks, times_passed_zero)

    def _start_transition(self, target_pos: int, direction: int):
        self.target_position = target_pos
        self.is_transitioning = True
        self.transition_progress = 0.0
        self.transition_direction = direction
        self.transition_frames = self._calculate_transition_frames()

    def _calculate_transition_frames(self) -> int:
        clicks_done = (
            self.current_instruction_total_clicks
            - self.current_instruction_clicks_remaining
        )

        if clicks_done < self.accel_clicks:
            progress = clicks_done / self.accel_clicks
            base_frames = int(
                self.max_transition_frames
                - (self.max_transition_frames - self.min_transition_frames) * progress
            )
        elif self.current_instruction_clicks_remaining <= self.accel_clicks:
            progress = self.current_instruction_clicks_remaining / self.accel_clicks
            base_frames = int(
                self.max_transition_frames
                - (self.max_transition_frames - self.min_transition_frames) * progress
            )
        else:
            base_frames = self.min_transition_frames

        target = self.target_position
        distance_to_zero = min(target, 100 - target)
        
        proximity_threshold = 5
        if distance_to_zero < proximity_threshold:
            proximity_factor = distance_to_zero / proximity_threshold
            proximity_slowdown = int(self.max_transition_frames * (1 - proximity_factor * 0.7))
            
            return max(base_frames, proximity_slowdown)
        
        return base_frames

    def _place_neighbor_image(
        self,
        neighbor_pos,
        offset,
        center_x,
        center_y,
        image_height,
        image_width,
        horizontal_spacing,
        max_vertical_offset,
    ):
        image = self.get_current_position_image(neighbor_pos)
        if image is None:
            return

        x_pos = center_x + (offset * horizontal_spacing) - image_width // 2

        if offset == 0:
            vertical_offset = 0
        else:
            normalized_offset = abs(offset) / 5.0
            vertical_offset = int(normalized_offset**2 * max_vertical_offset)

        y_pos = center_y - image_height // 2 + vertical_offset

        for i, line in enumerate(image):
            row = y_pos + i

            if row < 0 or row >= self.buffer.height():
                continue

            line_start = 0
            line_end = len(line)
            buffer_col = x_pos

            if x_pos < 0:
                line_start = -x_pos
                buffer_col = 0

            if x_pos + len(line) > self.buffer.width():
                line_end = self.buffer.width() - x_pos

            if line_start < line_end:
                clipped_line = line[line_start:line_end]
                self.buffer.put_at(buffer_col, row, clipped_line)
    
    def _draw_line(self, x1: int, y1: int, x2: int, y2: int, char: str = None):
        if char is None:
            char = self.line_char
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            if 0 <= x < self.buffer.width() and 0 <= y < self.buffer.height():
                if abs(dx) > abs(dy):
                    line_char = '─'
                elif abs(dy) > abs(dx):
                    line_char = '│'
                else:
                    line_char = '/' if (sx * sy) > 0 else '\\'
                
                colored = bruhcolored(line_char, 240).colored
                self.buffer.put_char(x, y, colored)
            
            if x == x2 and y == y2:
                break
            
            e2 = 2 * err
            
            if e2 > -dy:
                err -= dy
                x += sx
            
            if e2 < dx:
                err += dx
                y += sy

    def _trigger_flash(self):
        self.flash_frames_remaining = self.flash_duration

    def _render_flash(self):
        if self.flash_frames_remaining <= 0:
            return
        
        intensity = self.flash_frames_remaining / self.flash_duration
        
        flash_char = "."
        for y in range(self.buffer.height()):
            for x in range(self.buffer.width()):
                if (x + y) % 2 == 0 and intensity > 0.3:
                    colored = bruhcolored(flash_char, self.flash_color).colored
                    self.buffer.put_char(x, y, colored)

    def _trigger_zeros_flash(self):
        """Trigger the colorful flash effect for the zeros counter"""
        self.zeros_flash_frames_remaining = self.zeros_flash_duration

    def get_zero_count_image(self):
        image = text_to_image(str(self.zeros), font="doom")
        
        if self.zeros_flash_frames_remaining > 0:
            colored_image = []
            for y, row in enumerate(image):
                colored_row = []
                for x, char in enumerate(row):
                    if char.strip():
                        color_index = (x + y) % len(self.zeros_flash_colors)
                        color_offset = (self.zeros_flash_duration - self.zeros_flash_frames_remaining) // 3
                        final_color_index = (color_index + color_offset) % len(self.zeros_flash_colors)
                        color = self.zeros_flash_colors[final_color_index]
                        colored_row.append(bruhcolored(char, color).colored)
                    else:
                        colored_row.append(char)
                colored_image.append(colored_row)
            return colored_image
        
        return image
    
    def get_current_position_image(self, position):
        if 0 <= position < 100:
            image = self.number_images[position]
            if position == 0:
                colored_image = []
                for y in range(len(image)):
                    colored_row = []
                    for x in range(len(image[0])):
                        colored_row.append(bruhcolored(image[y][x], 129).colored)
                    colored_image.append(colored_row)
                return colored_image
            return image
        else:
            pos = position % 100
            return self.number_images[pos]
    
    def get_current_instruction_image(self):
        return text_to_image(f"{self.current_instruction_direction} {self.current_instruction_clicks_remaining}", font="doom")

    def place_instruction_image(self):
        image = self.get_current_instruction_image()
        for y, line in enumerate(image):
            self.buffer.put_at_center(y, line)

    def draw_lines_to_numbers(self):
        if not self.show_lines:
            return
        
        center_y = self.buffer.height() // 2
        center_x = self.buffer.width() // 2
        bottom_y = self.buffer.height() - 1
        bottom_x = center_x
        
        horizontal_spacing = 15
        
        transition_offset = 0.0
        if self.is_transitioning:
            t = self.transition_progress
            eased_t = t * t * (3.0 - 2.0 * t)
            transition_offset = eased_t * self.transition_direction
        
        for offset in range(-10, 11):
            visual_offset = offset - transition_offset
            pos = (self.position + offset) % 100
            
            abs_offset = abs(visual_offset)
            normalized_offset = abs_offset / self.curve_divisor
            vertical_offset = int(normalized_offset ** self.curve_exponent * self.curve_max_offset)
            
            image = self.number_images[pos]
            image_height = len(image)
            image_width = len(image[0])
            
            number_x = center_x + int(visual_offset * horizontal_spacing)
            number_y = center_y + vertical_offset
            
            if number_x < 0 or number_x >= self.buffer.width():
                continue
            
            self._draw_line(bottom_x, bottom_y, number_x, number_y)

    def place_zeros_counter_image(self):
        image = self.get_zero_count_image()
        
        if self.zeros_y_position is None:
            self.zeros_y_position = self.buffer.height() - len(image)
        
        if self.all_instructions_completed and self.zeros_target_y is None:
            if abs(self.exit_offset) > 12:
                self.zeros_target_y = (self.buffer.height() - len(image)) // 2
        
        if self.zeros_target_y is not None:
            if abs(self.zeros_y_position - self.zeros_target_y) > 0.5:
                self.zeros_y_position += (self.zeros_target_y - self.zeros_y_position) * 0.1
            else:
                self.zeros_y_position = self.zeros_target_y
        
        for y, line in enumerate(image):
            row = int(self.zeros_y_position) + y
            if 0 <= row < self.buffer.height():
                self.buffer.put_at_center(row, line)
                
    def place_current_position_with_neighbors(self):
        center_y = self.buffer.height() // 2
        center_x = self.buffer.width() // 2

        horizontal_spacing = 15
        max_vertical_offset = 10

        transition_offset = 0.0
        if self.is_transitioning:
            t = self.transition_progress
            eased_t = t * t * (3.0 - 2.0 * t)
            transition_offset = eased_t * self.transition_direction

        if self.all_instructions_completed:
            transition_offset += self.exit_offset

        blur_intensity = 0
        if self.transition_frames <= self.blur_threshold:
            blur_intensity = 1.0 - (self.transition_frames / self.blur_threshold)

        positions_to_show = []
        for offset in range(-10, 11):
            visual_offset = offset - transition_offset
            if self.all_instructions_completed:
                pos = self.position + offset
            else:
                pos = (self.position + offset) % 100
            positions_to_show.append((pos, visual_offset))

        for pos, visual_offset in positions_to_show:
            image = self.get_current_position_image(pos)
            if image is None:
                continue

            image_height = len(image)
            image_width = len(image[0])

            x_pos = (
                center_x + int(visual_offset * horizontal_spacing) - image_width // 2
            )

            if x_pos + image_width < 0 or x_pos >= self.buffer.width():
                continue

            abs_offset = abs(visual_offset)
            normalized_offset = abs_offset / self.curve_divisor
            vertical_offset = int(
                normalized_offset**self.curve_exponent * self.curve_max_offset
            )

            y_pos = center_y - image_height // 2 + vertical_offset

            for i, line in enumerate(image):
                row = y_pos + i

                if row < 0 or row >= self.buffer.height():
                    continue

                line_start = max(0, -x_pos)
                line_end = min(len(line), self.buffer.width() - x_pos)
                buffer_col = max(0, x_pos)

                if line_start < line_end:
                    clipped_line = line[line_start:line_end]

                    if blur_intensity > 0 and visual_offset != 0:
                        distance_factor = min(abs(visual_offset) / 3.0, 1.0)
                        effective_blur = blur_intensity * distance_factor

                        if effective_blur > 0.7:
                            clipped_line = [
                                c if i % 3 == 0 else "·"
                                for i, c in enumerate(clipped_line)
                            ]
                        elif effective_blur > 0.4:
                            clipped_line = [
                                c if i % 2 == 0 else "·"
                                for i, c in enumerate(clipped_line)
                            ]
                        elif effective_blur > 0.2:
                            clipped_line = [
                                c if i % 3 != 1 else "·"
                                for i, c in enumerate(clipped_line)
                            ]

                    self.buffer.put_at(buffer_col, row, clipped_line)

    def render_frame(self, frame_number: int):
        if frame_number % self.second_effect_halt == 0:
            if self.second_effect is not None:
                self.second_effect.render_frame(frame_number=frame_number)
                self.buffer.sync_with(self.second_effect.buffer)

        if self.flash_frames_remaining > 0:
            self.flash_frames_remaining -= 1

        if self.zeros_flash_frames_remaining > 0:
            self.zeros_flash_frames_remaining -= 1

        if self.all_instructions_completed:
            self.exit_offset += self.exit_direction * 0.5
            
            self._render_flash()
            self.draw_lines_to_numbers()
            self.place_current_position_with_neighbors()
            self.place_zeros_counter_image()
            return

        if self.is_paused:
            self.pause_frames_remaining -= 1
            if self.pause_frames_remaining <= 0:
                self.is_paused = False
                self.has_paused_for_current_instruction = True
            self._render_flash()
            self.draw_lines_to_numbers()
            self.place_current_position_with_neighbors()
            self.place_zeros_counter_image()
            return

        if self.is_transitioning:
            self.transition_progress += 1.0 / self.transition_frames

            if self.transition_progress >= 1.0:
                old_position = self.position
                self.position = self.target_position
                self.is_transitioning = False
                self.transition_progress = 0.0
                self.current_instruction_clicks_remaining -= 1
        else:
            if self.current_instruction_clicks_remaining <= 0:
                if (
                    self.has_completed_instruction
                    and self.instruction_pause_frames > 0
                    and not self.has_paused_for_current_instruction
                ):
                    self.is_paused = True
                    self.pause_frames_remaining = self.instruction_pause_frames
                    self._render_flash()
                    self.draw_lines_to_numbers()
                    self.place_current_position_with_neighbors()
                    self.place_zeros_counter_image()
                    return

                if self.current_instruction_index >= len(self.data):
                    self.all_instructions_completed = True
                    if self.position < 50:
                        self.exit_direction = -1
                    else:
                        self.exit_direction = 1
                    return

                direction, true_clicks, observed_clicks, times_passed_through_zero = (
                    self._get_moves(self.data[self.current_instruction_index])
                )

                self.current_instruction_direction = direction
                self.current_instruction_clicks_remaining = true_clicks
                self.current_instruction_total_clicks = true_clicks
                self.full_rotations_completed = 0
                self.current_instruction_index += 1
                self.has_completed_instruction = True
                self.has_paused_for_current_instruction = False

            if self.current_instruction_clicks_remaining > 0:
                if self.current_instruction_direction == "L":
                    target = (self.position - 1) % 100
                    dir_value = -1
                else:
                    target = (self.position + 1) % 100
                    dir_value = 1

                if target == 0 and self.position != 0:
                    self.zeros += 1
                    self._trigger_zeros_flash()

                self._start_transition(target, dir_value)

        self._render_flash()
        self.draw_lines_to_numbers()
        self.place_current_position_with_neighbors()
        self.place_zeros_counter_image()
        self.place_instruction_image()

def animate(screen):
    renderer = EffectRenderer(
        screen=screen,
        frames=float("inf"),
        frame_time=0.01,
        effect_type="static",
        background=" ",
        transparent=False,
    )

    fireworks = FireworkEffect(Buffer(screen.height, screen.width), " ")
    fireworks.set_second_effect(second_effect=TwinkleEffect(Buffer(screen.height, screen.width), " "))
    fireworks.set_firework_type("random")
    fireworks.set_firework_color_enabled(True)
    fireworks.set_firework_color_type("twotone")

    snow = SnowEffect(Buffer(screen.height, screen.width), " ")

    plasma = PlasmaEffect(Buffer(screen.height, screen.width), " ")
    plasma.update_color_properties(True, True, False)

    renderer.effect = AdventOfCodeDay01Effect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        part="two",
        data_file="data1",
        second_effect=fireworks,
        second_effect_halt=3,
        min_transition_frames=2,
        max_transition_frames=20,
        accel_clicks=3,
        curve_intensity=6,
        blur_threshold=3,
        instruction_pause_frames=20,
        show_lines=False,
        exit_rotation_speed=2
    )

    renderer.run()


if __name__ in ["__main__", "day01_animate"]:
    Screen.show(animate)
