import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
import requests
import importlib.util
import time


DEFAULT_YEAR = datetime.now().year
SESSION_FILE = ".aoc_session"


SOLUTION_TEMPLATE = '''"""
Advent of Code {year} - Day {day}
"""


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, filename):
        """Load and parse the input data."""
        with open(filename, 'r') as f:
            return f.read().strip()
    
    def part1(self):
        """Solve part 1 of the puzzle."""
        # TODO: Implement part 1
        return None
    
    def part2(self):
        """Solve part 2 of the puzzle."""
        # TODO: Implement part 2
        return None
    
    def solve(self):
        """Run both parts and print results."""
        print(f"Day {day} Solutions:")
        print(f"Part 1: {{self.part1()}}")
        print(f"Part 2: {{self.part2()}}")


if __name__ == "__main__":
    solution = Solution()
    solution.solve()
'''

ANIMATION_TEMPLATE = '''"""
Advent of Code {year} - Day {day} Animation
"""

from bruhanimate import (
    Screen,
    BaseEffect,
    Buffer,
    EffectRenderer,
    SnowEffect
)

from bruhcolor import bruhcolored as bc

class AdventOfCodeDay{day:02d}Effect(BaseEffect):
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
    renderer.effect = AdventOfCodeDay{day:02d}Effect(
        buffer=Buffer(screen.height, screen.width),
        background=" ",
        part="two",
        data_file="data",
        second_effect=snow,
        second_effect_halt=3,
    )

    renderer.run()

if __name__ in ["__main__", "day{day:02d}_animate"]:
    Screen.show(animate)
'''


def get_session_cookie():
    """Read session cookie from file."""
    session_file = Path(SESSION_FILE)
    if not session_file.exists():
        print(f"Error: {SESSION_FILE} not found.")
        print("Please create this file with your AOC session cookie.")
        print("Get it from your browser's cookies after logging into adventofcode.com")
        return None

    with open(session_file, "r") as f:
        return f.read().strip()


def download_input(year, day):
    """Download input data from Advent of Code."""
    session = get_session_cookie()
    if not session:
        return False

    url = f"https://adventofcode.com/{year}/day/{day}/input"
    cookies = {"session": session}

    try:
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading input: {e}")
        return None


def setup_day(year, day, download_data=False, animate=False, verbose=True):
    """Set up folder and files for a specific day."""
    # Create year/day folder structure
    day_folder = Path(f"{year}/day{day:02d}")

    # Create folder (parents=True creates year folder if needed)
    day_folder.mkdir(parents=True, exist_ok=True)
    if verbose:
        print(f"✓ Created folder: {day_folder}")

    # Create solution.py
    solution_file = day_folder / "solution.py"
    file_created = False
    if not solution_file.exists():
        content = SOLUTION_TEMPLATE.format(year=year, day=day)
        solution_file.write_text(content)
        file_created = True
        if verbose:
            print(f"✓ Created {solution_file}")
    else:
        if verbose:
            print(f"⚠ {solution_file} already exists, skipping")

    # Download data if requested
    data_downloaded = False
    if download_data:
        data_file = day_folder / "data"
        if not data_file.exists():
            if verbose:
                print(f"Downloading input for year {year}, day {day}...")
            data = download_input(year, day)
            if data:
                data_file.write_text(data)
                data_downloaded = True
                if verbose:
                    print(f"✓ Downloaded data to {data_file}")
            else:
                if verbose:
                    print(f"✗ Failed to download data")
        else:
            if verbose:
                print(f"⚠ {data_file} already exists, skipping download")

    if verbose:
        print(f"\n✓ Year {year}, Day {day} setup complete!")

    if animate:
        animation_file = day_folder / "animate.py"
        if not animation_file.exists():
            content = ANIMATION_TEMPLATE.format(year=year, day=day)
            animation_file.write_text(content)
            if verbose:
                print(f"✓ Created {animation_file}")
        else:
            if verbose:
                print(f"⚠ {animation_file} already exists, skipping")

    return file_created, data_downloaded


def setup_all_days(year, download_data=False, animate=False):
    """Set up all 25 days for a year."""
    print(f"Setting up all 25 days for year {year}...")
    print("=" * 50)

    created_count = 0
    downloaded_count = 0

    for day in range(1, 26):
        print(f"\nDay {day:02d}:")
        file_created, data_downloaded = setup_day(
            year, day, download_data, animate, verbose=False
        )

        if file_created:
            created_count += 1
            print(f"  ✓ Created solution file")
        else:
            print(f"  ⚠ Solution file already exists")

        if download_data:
            if data_downloaded:
                downloaded_count += 1
                print(f"  ✓ Downloaded data")
            else:
                print(f"  ⚠ Data already exists or download failed")

            # Be nice to the server - small delay between downloads
            if day < 25:
                time.sleep(0.5)

    print(f"\n{'=' * 50}")
    print(f"Setup complete!")
    print(f"  Created {created_count} solution files")
    if download_data:
        print(f"  Downloaded {downloaded_count} data files")


def run_solution(year, day):
    """Run solution for a specific day."""
    day_folder = Path(f"{year}/day{day:02d}")
    solution_file = day_folder / "solution.py"

    if not solution_file.exists():
        print(f"Error: {solution_file} does not exist")
        return False

    # Dynamically import and run the solution
    spec = importlib.util.spec_from_file_location(f"day{day:02d}", solution_file)
    module = importlib.util.module_from_spec(spec)

    # Change to the day's directory so it can find its data file
    original_dir = os.getcwd()
    os.chdir(day_folder)

    try:
        spec.loader.exec_module(module)
        solution = module.Solution()
        print(f"\n{'=' * 50}")
        print(f"Year {year} - Day {day}")
        print("=" * 50)
        solution.solve()
        return True
    except Exception as e:
        print(f"Error running year {year}, day {day}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        os.chdir(original_dir)


def run_all_solutions(year=None):
    """Run all available solutions for a year or all years."""
    if year:
        # Run all solutions for a specific year
        year_folder = Path(str(year))
        if not year_folder.exists():
            print(f"Error: Year folder {year} does not exist")
            return

        day_folders = sorted(
            [
                d
                for d in year_folder.iterdir()
                if d.is_dir() and d.name.startswith("day")
            ]
        )

        if not day_folders:
            print(f"No solution folders found for year {year}")
            return

        print(f"Running {len(day_folders)} solutions for year {year}...\n")

        for folder in day_folders:
            day = int(folder.name[3:])
            run_solution(year, day)

        print(f"\n{'=' * 50}")
        print(f"Completed {len(day_folders)} solutions for year {year}")

    else:
        # Run all solutions for all years
        year_folders = sorted(
            [d for d in Path(".").iterdir() if d.is_dir() and d.name.isdigit()]
        )

        if not year_folders:
            print("No year folders found")
            return

        total_solutions = 0
        for year_folder in year_folders:
            year_num = int(year_folder.name)
            day_folders = sorted(
                [
                    d
                    for d in year_folder.iterdir()
                    if d.is_dir() and d.name.startswith("day")
                ]
            )

            if day_folders:
                print(f"\n{'#' * 50}")
                print(f"YEAR {year_num}")
                print("#" * 50)

                for folder in day_folders:
                    day = int(folder.name[3:])
                    run_solution(year_num, day)
                    total_solutions += 1

        print(f"\n{'#' * 50}")
        print(
            f"Completed {total_solutions} total solutions across {len(year_folders)} years"
        )


def run_animation(year, day):
    """Run animation for a specific day."""
    day_folder = Path(f"{year}/day{day:02d}")
    animation_file = day_folder / "animate.py"

    if not animation_file.exists():
        print(f"Error: {animation_file} does not exist")
        return False

    # Dynamically import and run the animation
    spec = importlib.util.spec_from_file_location(
        f"day{day:02d}_animate", animation_file
    )
    module = importlib.util.module_from_spec(spec)

    # Change to the day's directory so it can find its data file
    original_dir = os.getcwd()
    os.chdir(day_folder)

    try:
        spec.loader.exec_module(module)
        return True
    except Exception as e:
        print(f"Error running animation for year {year}, day {day}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        os.chdir(original_dir)


def list_animations(year=None):
    """List all solutions that have animation files."""
    if year:
        year_folders = [Path(str(year))]
        if not year_folders[0].exists():
            print(f"Error: Year folder {year} does not exist")
            return
    else:
        year_folders = sorted(
            [d for d in Path(".").iterdir() if d.is_dir() and d.name.isdigit()]
        )

    found_animations = []

    for year_folder in year_folders:
        year_num = int(year_folder.name)
        day_folders = sorted(
            [
                d
                for d in year_folder.iterdir()
                if d.is_dir() and d.name.startswith("day")
            ]
        )

        for folder in day_folders:
            animation_file = folder / "animate.py"
            if animation_file.exists():
                day_num = int(folder.name[3:])
                found_animations.append((year_num, day_num))

    if not found_animations:
        print("No animations found")
        return

    print(f"\nFound {len(found_animations)} animation(s):\n")
    current_year = None
    for year_num, day_num in found_animations:
        if year_num != current_year:
            if current_year is not None:
                print()
            print(f"Year {year_num}:")
            current_year = year_num
        print(f"  Day {day_num:02d}: {year_num}/day{day_num:02d}/animate.py")


def get_current_day():
    """Get the current AOC day (1-25) if we're in December."""
    now = datetime.now()
    if now.month == 12 and 1 <= now.day <= 25:
        return now.day
    return 1  # Default to day 1 if not in AOC season


def get_current_year():
    """Get the current year if in December, otherwise DEFAULT_YEAR."""
    now = datetime.now()
    if now.month == 12:
        return now.year
    return DEFAULT_YEAR


def main():
    parser = argparse.ArgumentParser(
        description="Advent of Code CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Setup commands:
    %(prog)s setup                          # Setup today's puzzle
    %(prog)s setup --day 5                  # Setup day 5 for current year
    %(prog)s setup --day 3 --download       # Setup day 3 and download input
    %(prog)s setup --year 2023 --day 5      # Setup day 5 for 2023
    %(prog)s setup --all                    # Setup all 25 days for current year
    %(prog)s setup --all --download         # Setup all 25 days and download data
    %(prog)s setup --all --year 2023        # Setup all 25 days for 2023
  
  Run commands:
    %(prog)s run                            # Run today's solution
    %(prog)s run --day 5                    # Run day 5 for current year
    %(prog)s run --year 2023 --day 5        # Run day 5 for 2023
    %(prog)s run --all                      # Run all solutions (all years)
    %(prog)s run --all --year 2023          # Run all 2023 solutions

  Animation commands:
    %(prog)s animate                        # Run today's animation
    %(prog)s animate --day 5                # Run animation for day 5
    %(prog)s animate --year 2023 --day 5    # Run animation for 2023 day 5
    %(prog)s list                           # List all available animations
    %(prog)s list --year 2023               # List animations for 2023

Folder structure:
  2024/day01/solution.py
  2024/day01/data
  2024/day01/animate.py
  2024/day02/solution.py
  2023/day01/solution.py
  ...
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup a day's folder and files")
    setup_parser.add_argument(
        "--day",
        type=int,
        default=None,
        help="Day to setup (default: today or 1, ignored if --all is used)",
    )
    setup_parser.add_argument(
        "--year",
        type=int,
        default=get_current_year(),
        help=f"Year (default: current year in December, otherwise {DEFAULT_YEAR})",
    )
    setup_parser.add_argument(
        "--download", action="store_true", help="Download input data"
    )
    setup_parser.add_argument(
        "--all", action="store_true", help="Setup all 25 days for the year"
    )
    setup_parser.add_argument(
        "--animate",
        action="store_true",
        help="Create an animate.py file in the day's folder",
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run solution(s)")
    run_parser.add_argument(
        "--day",
        type=int,
        default=get_current_day(),
        help="Day to run (default: today or 1)",
    )
    run_parser.add_argument(
        "--year",
        type=int,
        default=get_current_year(),
        help=f"Year to run (default: current year in December, otherwise {DEFAULT_YEAR})",
    )
    run_parser.add_argument(
        "--all",
        action="store_true",
        help="Run all available solutions (optionally filter by --year)",
    )

    # Animate command
    animate_parser = subparsers.add_parser("animate", help="Run animation for a day")
    animate_parser.add_argument(
        "--day",
        type=int,
        default=get_current_day(),
        help="Day to animate (default: today or 1)",
    )
    animate_parser.add_argument(
        "--year",
        type=int,
        default=get_current_year(),
        help=f"Year to animate (default: current year in December, otherwise {DEFAULT_YEAR})",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List available animations")
    list_parser.add_argument(
        "--year", type=int, default=None, help="Filter by year (default: all years)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "setup":
        if args.all:
            # Setup all 25 days
            setup_all_days(args.year, args.download, args.animate)
        else:
            # Setup single day
            day = args.day if args.day else get_current_day()
            setup_day(args.year, day, args.download, args.animate)

    elif args.command == "run":
        if args.all:
            # If --year specified with --all, run all for that year only
            year_filter = args.year if args.year != get_current_year() else None
            # Actually, let's always respect --year if --all is used
            year_filter = args.year if hasattr(args, "year") else None
            run_all_solutions(year_filter)
        else:
            run_solution(args.year, args.day)

    elif args.command == "animate":
        run_animation(args.year, args.day)

    elif args.command == "list":
        list_animations(args.year)


if __name__ == "__main__":
    main()
