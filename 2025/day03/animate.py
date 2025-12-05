"""
Advent of Code 2025 - Day 3 Animation
"""

from bruhanimate import (
    Screen,
    BaseEffect,
    Buffer,
    EffectRenderer,
    SnowEffect,
    TwinkleEffect,
    FireworkEffect,
    text_to_image,
)

from bruhcolor import bruhcolored


class BatteryBankEffect(BaseEffect):
    def __init__(
        self,
        buffer: Buffer,
        background: str,
        data_file: str = "data",
        batteries_to_select: int = 12,
        second_effect: BaseEffect | None = None,
        second_effect_halt: int = 1,
        selection_pause_frames: int = 15,
        bank_complete_pause_frames: int = 45,
        digit_spacing: int = 4,
        flying_in_frames: int = 30,
        falling_frames: int = 20,
        converging_frames: int = 15,
    ):
        super().__init__(buffer, background)
        self.data_file = data_file
        self.batteries_to_select = batteries_to_select
        self.second_effect = second_effect
        self.second_effect_halt = second_effect_halt
        self.selection_pause_frames = selection_pause_frames
        self.bank_complete_pause_frames = bank_complete_pause_frames
        self.digit_spacing = digit_spacing
        self.flying_in_frames = flying_in_frames
        self.falling_frames = falling_frames
        self.converging_frames = converging_frames
        
        self.current_bank_index = 0
        self.current_position = 0
        self.search_start = 0
        self.selected_indices = []
        self.selected_values = []
        self.is_selecting = False
        self.selection_flash_frames = 0
        self.is_paused = False
        self.pause_frames_remaining = 0
        self.bank_complete_flash_frames = 0
        self.running_total = 0
        self.completed = False
        
        self.is_flying_in = False
        self.is_falling = False
        self.is_converging = False
        self.animation_frame = 0
        self.flying_chars = []
        self.falling_chars = []
        self.converging_chars = []
        
        self.completed_banks = []
        self.current_y = self.buffer.height() // 2
        
        self.banks = []
        self._load_data()
        
        self.digit_images = {
            str(i): text_to_image(str(i), font="doom")
            for i in range(10)
        }
        
        self._start_flying_in_animation()
    
    def _smooth_ease(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)
        
    def _load_data(self):
        with open(self.data_file, 'r') as f:
            data = f.read().strip()
            self.banks = [[int(c) for c in line] for line in data.split("\n")][:25]
    
    def _find_next_selection(self) -> tuple[int, int]:
        bank = self.banks[self.current_bank_index]
        remaining_positions = self.batteries_to_select - self.current_position
        last_viable_spot = len(bank) - remaining_positions
        
        valid_range = bank[self.search_start:last_viable_spot + 1]
        largest_digit = max(valid_range)
        relative_index = valid_range.index(largest_digit)
        absolute_index = self.search_start + relative_index
        
        return absolute_index, largest_digit
    
    def _start_flying_in_animation(self):
        bank = self.banks[self.current_bank_index]
        total_width = len(bank) * self.digit_spacing
        start_x = (self.buffer.width() - total_width) // 2
        
        self.flying_chars = []
        for i, digit in enumerate(bank):
            target_x = start_x + (i * self.digit_spacing)
            current_x = -10 - (i * 2)
            self.flying_chars.append((digit, target_x, current_x))
        
        self.is_flying_in = True
        self.animation_frame = 0
    
    def _start_falling_animation(self):
        bank = self.banks[self.current_bank_index]
        total_width = len(bank) * self.digit_spacing
        start_x = (self.buffer.width() - total_width) // 2
        
        self.falling_chars = []
        for i, digit in enumerate(bank):
            if i not in self.selected_indices:
                x_pos = start_x + (i * self.digit_spacing)
                self.falling_chars.append((digit, x_pos, self.current_y, 0))
        
        self.is_falling = True
        self.animation_frame = 0
    
    def _start_converging_animation(self):
        bank = self.banks[self.current_bank_index]
        total_width = len(bank) * self.digit_spacing
        start_x = (self.buffer.width() - total_width) // 2
        
        num_selected = len(self.selected_indices)
        target_width = num_selected * self.digit_spacing
        target_start_x = (self.buffer.width() - target_width) // 2
        
        self.converging_chars = []
        for idx, bank_idx in enumerate(self.selected_indices):
            digit = bank[bank_idx]
            start_pos = start_x + (bank_idx * self.digit_spacing)
            target_pos = target_start_x + (idx * self.digit_spacing)
            self.converging_chars.append((digit, start_pos, target_pos, start_pos, start_pos))
        
        self.is_converging = True
        self.animation_frame = 0
    
    def _render_flying_in_chars(self):
        progress = self.animation_frame / self.flying_in_frames
        ease_progress = self._smooth_ease(progress)
        
        for digit, target_x, start_x in self.flying_chars:
            current_x = int(start_x + (target_x - start_x) * ease_progress)
            colored = bruhcolored(str(digit), 255).colored
            
            if 0 <= current_x < self.buffer.width() and 0 <= self.current_y < self.buffer.height():
                self.buffer.put_char(current_x, self.current_y, colored)
    
    def _render_falling_chars(self):
        progress = self.animation_frame / self.falling_frames
        
        for digit, start_x, start_y, _ in self.falling_chars:
            if progress < 0.3:
                drop_progress = self._smooth_ease(progress / 0.3)
                y_pos = start_y + int(drop_progress)
                x_pos = start_x
            else:
                move_progress = self._smooth_ease((progress - 0.3) / 0.7)
                y_pos = start_y + 1
                x_offset = int(move_progress * (self.buffer.width() - start_x + 10))
                x_pos = start_x + x_offset
            
            if y_pos < self.buffer.height() and x_pos < self.buffer.width():
                colored = bruhcolored(str(digit), 236).colored
                if 0 <= x_pos < self.buffer.width() and 0 <= y_pos < self.buffer.height():
                    self.buffer.put_char(x_pos, y_pos, colored)
    
    def _render_converging_chars(self):
        progress = self.animation_frame / self.converging_frames
        ease_progress = self._smooth_ease(progress)
        
        updated_chars = []
        for digit, start_x, target_x, current_x, prev_x in self.converging_chars:
            new_x = int(start_x + (target_x - start_x) * ease_progress)
            
            if prev_x != new_x and 0 <= prev_x < self.buffer.width() and 0 <= self.current_y < self.buffer.height():
                self.buffer.put_char(prev_x, self.current_y, self.background)
            
            colored = bruhcolored(str(digit), 46).colored
            if 0 <= new_x < self.buffer.width() and 0 <= self.current_y < self.buffer.height():
                self.buffer.put_char(new_x, self.current_y, colored)
            
            updated_chars.append((digit, start_x, target_x, new_x, new_x))
        
        self.converging_chars = updated_chars
    
    def _render_bank_digits(self):
        for bank_data, selected_indices, y_pos in self.completed_banks:
            if y_pos < 0:
                continue
            self._render_single_bank(bank_data, selected_indices, y_pos, completed=True)
        if not self.is_flying_in and not self.is_falling and not self.is_converging:
            if self.current_bank_index < len(self.banks):
                bank = self.banks[self.current_bank_index]
                self._render_single_bank(bank, self.selected_indices, self.current_y, completed=False)
    
    def _render_single_bank(self, bank, selected_indices, y_pos, completed=False):
        if completed:
            num_selected = len(selected_indices)
            target_width = num_selected * self.digit_spacing
            start_x = (self.buffer.width() - target_width) // 2
            
            for idx, bank_idx in enumerate(selected_indices):
                digit = bank[bank_idx]
                x_pos = start_x + (idx * self.digit_spacing)
                colored = bruhcolored(str(digit), 46).colored
                
                if 0 <= x_pos < self.buffer.width() and 0 <= y_pos < self.buffer.height():
                    self.buffer.put_char(x_pos, y_pos, colored)
        else:
            total_width = len(bank) * self.digit_spacing
            start_x = (self.buffer.width() - total_width) // 2
            
            for i, digit in enumerate(bank):
                x_pos = start_x + (i * self.digit_spacing)
                
                if i in selected_indices:
                    color = 46
                    intensity = 1.0
                elif i < self.search_start:
                    color = 236
                    intensity = 0.3
                elif self.is_selecting and self.selected_indices and i == selected_indices[-1]:
                    color = 226 if self.selection_flash_frames % 2 == 0 else 220
                    intensity = 1.0
                else:
                    remaining_positions = self.batteries_to_select - self.current_position
                    last_viable_spot = len(bank) - remaining_positions
                    
                    if i <= last_viable_spot:
                        color = 255
                        intensity = 1.0
                    else:
                        color = 240
                        intensity = 0.5
                
                digit_str = str(digit)
                colored = bruhcolored(digit_str, color).colored
                
                if 0 <= x_pos < self.buffer.width() and 0 <= y_pos < self.buffer.height():
                    self.buffer.put_char(x_pos, y_pos, colored)
    
    def _render_selection_info(self):
        pos_text = f"Battery {self.current_position}/{self.batteries_to_select}"
        self.buffer.put_at(2, 2, pos_text)
        
        bank_text = f"Bank {self.current_bank_index + 1}/{len(self.banks)}"
        self.buffer.put_at(2, 3, bank_text)
    
    def _render_total(self):
        total_text = f"Total: {self.running_total}"
        self.buffer.put_at(2, 4, text=total_text)

    def render_frame(self, frame_number: int):
        if frame_number % self.second_effect_halt == 0:
            if self.second_effect is not None:
                self.second_effect.render_frame(frame_number=frame_number)
                self.buffer.sync_with(self.second_effect.buffer)
        
        if self.selection_flash_frames > 0:
            self.selection_flash_frames -= 1
        
        if self.bank_complete_flash_frames > 0:
            self.bank_complete_flash_frames -= 1
        
        if self.completed:
            self._render_bank_digits()
            self._render_total()
            return
        
        if self.is_flying_in:
            self.animation_frame += 1
            self._render_selection_info()
            self._render_bank_digits()
            self._render_flying_in_chars()
            self._render_total()
            
            if self.animation_frame >= self.flying_in_frames:
                self.is_flying_in = False
            return
        
        if self.is_falling:
            self.animation_frame += 1
            self._render_selection_info()
            self._render_bank_digits()
            self._render_falling_chars()
            
            bank = self.banks[self.current_bank_index]
            total_width = len(bank) * self.digit_spacing
            start_x = (self.buffer.width() - total_width) // 2
            
            for bank_idx in self.selected_indices:
                digit = bank[bank_idx]
                x_pos = start_x + (bank_idx * self.digit_spacing)
                colored = bruhcolored(str(digit), 46).colored
                if 0 <= x_pos < self.buffer.width() and 0 <= self.current_y < self.buffer.height():
                    self.buffer.put_char(x_pos, self.current_y, colored)
            
            self._render_total()
            
            if self.animation_frame >= self.falling_frames:
                self.is_falling = False
                self._start_converging_animation()
            return
        
        if self.is_converging:
            self.animation_frame += 1
            self._render_selection_info()
            self._render_bank_digits()
            self._render_converging_chars()
            self._render_total()
            
            if self.animation_frame >= self.converging_frames:
                self.is_converging = False
                
                bank_value = int("".join(map(str, self.selected_values)))
                self.running_total += bank_value
                
                self.completed_banks.append((
                    self.banks[self.current_bank_index].copy(),
                    self.selected_indices.copy(),
                    self.current_y
                ))
                
                self.completed_banks = [
                    (bank, indices, y - 1) 
                    for bank, indices, y in self.completed_banks
                ]
                
                self.completed_banks = [
                    (bank, indices, y) 
                    for bank, indices, y in self.completed_banks 
                    if y >= -1
                ]
                
                self.current_bank_index += 1
                if self.current_bank_index >= len(self.banks):
                    self.completed = True
                    return
                
                self.current_position = 0
                self.search_start = 0
                self.selected_indices = []
                self.selected_values = []
                self.is_selecting = False
                
                self._start_flying_in_animation()
            return
        
        if self.is_paused:
            self.pause_frames_remaining -= 1
            if self.pause_frames_remaining <= 0:
                self.is_paused = False
                if self.current_position >= self.batteries_to_select:
                    self._start_falling_animation()
                    return
            
            self._render_selection_info()
            self._render_bank_digits()
            self._render_total()
            return
        
        if not self.is_selecting:
            if self.current_position < self.batteries_to_select:
                index, value = self._find_next_selection()
                self.selected_indices.append(index)
                self.selected_values.append(value)
                self.search_start = index + 1
                self.is_selecting = True
                self.selection_flash_frames = self.selection_pause_frames
                self.is_paused = True
                self.pause_frames_remaining = self.selection_pause_frames
                self.current_position += 1
            else:
                self.bank_complete_flash_frames = self.bank_complete_pause_frames
                self.is_paused = True
                self.pause_frames_remaining = self.bank_complete_pause_frames
        else:
            if self.selection_flash_frames <= 0:
                self.is_selecting = False
        
        self._render_selection_info()
        self._render_bank_digits()
        self._render_total()


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
    fireworks.set_second_effect(second_effect=TwinkleEffect(Buffer(screen.height, screen.width), " "))
    fireworks.set_firework_type("random")
    fireworks.set_firework_color_enabled(True)
    fireworks.set_firework_color_type("twotone")

    snow_effect = SnowEffect(Buffer(screen.height, screen.width), " ")

    renderer.effect = BatteryBankEffect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        data_file="data",
        batteries_to_select=12,
        second_effect=fireworks,
        second_effect_halt=20,
        selection_pause_frames=8,
        bank_complete_pause_frames=30,
        digit_spacing=1,
        flying_in_frames=50,
        falling_frames=50,
        converging_frames=50,
    )

    renderer.run()


if __name__ in ["__main__", "day03_animate"]:
    Screen.show(animate)