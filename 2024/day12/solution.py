"""
Advent of Code 2024 - Day 12
"""

import os
import re
import math
import time
from scipy.spatial import ConvexHull


class Solution:
    def __init__(self, data_file="data"):
        self.data = self.load_data(data_file)
    
    def load_data(self, name="data"):
        with open(name, "r") as file:
            return [list(line.strip()) for line in file.readlines()]


    def part1(self):
        """Code to solve part one"""
        start = time.time()

        self.data = self.load_data()
        datastr = "".join([c for row in self.data for c in row])

        crops = {crop: datastr.count(crop) for crop in set(datastr)}
        crop_seen_plots = {crop:set() for crop in crops}
        crop_perimeters = {crop:{} for crop in crops}
        crop_region_totals = {crop:{} for crop in crops}
    
        directions = [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
        ]

        hits = [[" " for _ in range(len(self.data[0]))] for _ in range(len(self.data))]

        def check_dir(crop, point, crop_region):
            x, y = point
            if not 0 <= x < len(self.data[0]) or not 0 <= y < len(self.data):
                crop_seen_plots[crop].add(point)
                crop_perimeters[crop][crop_region] += 1
                return 0
            if self.data[y][x] != crop:
                crop_seen_plots[crop].add(point)
                crop_perimeters[crop][crop_region] += 1
                return 0
            if point in crop_seen_plots[crop]:
                crop_seen_plots[crop].add(point)
                return 0

            crop_seen_plots[crop].add(point)

            plot_hits = 0
            for direction in directions:
                plot_hits += check_dir(crop, (x + direction[0], y + direction[1]), crop_region)
            return plot_hits + 1

        for crop, crop_count in crops.items():
            crops_found = 0
            crop_region = 0
            while crops_found != crop_count:
                if crop_region not in crop_seen_plots[crop]:
                    crop_perimeters[crop][crop_region] = 0
                    crop_region_totals[crop][crop_region] = 0
                region_crops = 0
                crop_start_point = None
                for y in range(len(self.data)):
                    for x in range(len(self.data[0])):
                        if (x, y) in crop_seen_plots[crop]: continue
                        if self.data[y][x] == crop:
                            crop_start_point = (x, y)
                            break
                    else:
                        continue
                    break
                region_crops = check_dir(crop, crop_start_point, crop_region)
                crops_found += region_crops
                crop_region_totals[crop][crop_region] = region_crops
                crop_region += 1
    
        total = 0

        for crop in crop_region_totals:
            region_totals = crop_region_totals[crop]
            region_perimeters = crop_perimeters[crop]
            for region in region_totals:
                total += region_totals[region] * region_perimeters[region]

        end = time.time()
        return total, end - start


    def part2(self):
        """Code to solve part two"""
        start = time.time()

        self.data = self.load_data("datasmall")
        datastr = "".join([c for row in self.data for c in row])

        crops = {crop: datastr.count(crop) for crop in set(datastr)}
        crop_seen_plots = {crop:set() for crop in crops}
        crop_perimeters = {crop:{} for crop in crops}
        crop_region_sides = {crop:{} for crop in crops}
        crop_region_totals = {crop:{} for crop in crops}
        crop_region_plots = {crop:{} for crop in crops}
    
        directions = [
            (1, 0),
            (0, 1),
            (-1, 0),
            (0, -1),
        ]

        hits = [["." for _ in range(len(self.data[0]))] for _ in range(len(self.data))]

        def check_dir(crop, point, crop_region):
            x, y = point
            if not 0 <= x < len(self.data[0]) or not 0 <= y < len(self.data):
                return 0
            if self.data[y][x] != crop:
                return 0
            if point in crop_seen_plots[crop]:
                return 0

            crop_region_plots[crop][crop_region].add(point)
            crop_seen_plots[crop].add(point)

            plot_hits = 0
            for direction in directions:
                plot_hits += check_dir(crop, (x + direction[0], y + direction[1]), crop_region)
            return plot_hits + 1

        for crop, crop_count in crops.items():
            crops_found = 0
            crop_region = 0
            while crops_found != crop_count:
                if crop_region not in crop_seen_plots[crop]:
                    crop_perimeters[crop][crop_region] = 0
                    crop_region_sides[crop][crop_region] = 0
                    crop_region_totals[crop][crop_region] = 0
                    crop_region_plots[crop][crop_region] = set()
                region_crops = 0
                crop_start_point = None
                for y in range(len(self.data)):
                    for x in range(len(self.data[0])):
                        if (x, y) in crop_seen_plots[crop]: continue
                        if self.data[y][x] == crop:
                            crop_start_point = (x, y)
                            break
                    else:
                        continue
                    break
                region_crops = check_dir(crop, crop_start_point, crop_region)
                crops_found += region_crops
                crop_region_totals[crop][crop_region] = region_crops
                crop_region += 1
    
        total = 0

        for target in crop_seen_plots:
            target_points = crop_seen_plots[target].copy()
            for x, y in crop_seen_plots[target]:
                target_points.add((x+1,y))
            if len(target_points) == 2:
                bx, by = list(crop_seen_plots[target])[0]
                target_points.add((bx + 2, by))
                target_points.add((bx + 3, by))
            corners = self.get_sides(list(target_points))
            total += corners

        end = time.time()
        return total, end - start



    def get_sides(self, points):
        from shapely.geometry import Polygon
        polygon = Polygon(points)
        num_sides = len(polygon.exterior.coords) - 1
        return num_sides


    def solve(self):
        """Run solutions for part one and two"""
        part_one_answer, part_one_time_to_complete = self.part1()

        if part_one_answer:
            print(
                f"part one: {part_one_answer}\npart one time: {part_one_time_to_complete:.4f}s"
            )

        part_two_answer, part_two_time_to_complete = self.part2()

        if part_two_answer:
            print(
                f"part two: {part_two_answer}\npart two time: {part_two_time_to_complete:.4f}s"
            )




if __name__ == "__main__":
    solution = Solution()
    solution.solve()
