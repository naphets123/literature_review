"""Game map generation and management."""
import numpy as np
from typing import Tuple
import random


class GameMap:
    """A rectangular map with walls and floors."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # True = walkable, False = wall
        self.tiles = np.zeros((width, height), dtype=bool)
        self.generate_dungeon()

    def generate_dungeon(self) -> None:
        """Generate a simple dungeon with rooms and corridors."""
        # Start with all walls
        self.tiles.fill(False)

        # Create some random rooms
        rooms = []
        max_rooms = 10
        min_room_size = 6
        max_room_size = 12

        for _ in range(max_rooms):
            # Random room dimensions
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            # Random position
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)

            # Check if room overlaps with existing rooms
            new_room = (x, y, w, h)
            overlaps = False
            for room in rooms:
                if self.rooms_overlap(new_room, room):
                    overlaps = True
                    break

            if not overlaps:
                # Carve out the room
                self.create_room(x, y, w, h)
                rooms.append(new_room)

                # Connect to previous room with a corridor
                if len(rooms) > 1:
                    prev_room = rooms[-2]
                    # Get centers of both rooms
                    prev_center = (prev_room[0] + prev_room[2] // 2, prev_room[1] + prev_room[3] // 2)
                    new_center = (x + w // 2, y + h // 2)

                    # Create L-shaped corridor
                    if random.random() < 0.5:
                        self.create_h_corridor(prev_center[0], new_center[0], prev_center[1])
                        self.create_v_corridor(prev_center[1], new_center[1], new_center[0])
                    else:
                        self.create_v_corridor(prev_center[1], new_center[1], prev_center[0])
                        self.create_h_corridor(prev_center[0], new_center[0], new_center[1])

    def create_room(self, x: int, y: int, w: int, h: int) -> None:
        """Create a rectangular room."""
        self.tiles[x:x+w, y:y+h] = True

    def create_h_corridor(self, x1: int, x2: int, y: int) -> None:
        """Create a horizontal corridor."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[x, y] = True

    def create_v_corridor(self, y1: int, y2: int, x: int) -> None:
        """Create a vertical corridor."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[x, y] = True

    def rooms_overlap(self, room1: Tuple[int, int, int, int], room2: Tuple[int, int, int, int]) -> bool:
        """Check if two rooms overlap."""
        x1, y1, w1, h1 = room1
        x2, y2, w2, h2 = room2
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a position is walkable."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x, y]
        return False

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Check if a position is within map bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
