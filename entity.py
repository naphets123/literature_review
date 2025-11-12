"""Entity class for game objects."""
from typing import Tuple


class Entity:
    """A generic entity that can be placed on the map."""

    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: Tuple[int, int, int],
        name: str,
        blocks_movement: bool = False
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    def move(self, dx: int, dy: int) -> None:
        """Move the entity by a given amount."""
        self.x += dx
        self.y += dy
