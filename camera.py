"""Camera system for following the player."""
from typing import Tuple


class Camera:
    """Camera that follows the player with centered view and border logic."""

    def __init__(self, screen_width: int, screen_height: int, map_width: int, map_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        self.x = 0  # Top-left corner of camera in world coordinates
        self.y = 0

    def update(self, target_x: int, target_y: int) -> None:
        """
        Update camera position to follow the target (player).

        The player stays centered unless we're near map edges.
        When near edges, player can move within 20% of screen border.
        """
        # Calculate the ideal centered position (player at center of screen)
        ideal_camera_x = target_x - self.screen_width // 2
        ideal_camera_y = target_y - self.screen_height // 2

        # Calculate the border zone (20% of screen size)
        border_x = int(self.screen_width * 0.2)
        border_y = int(self.screen_height * 0.2)

        # Clamp camera position to map boundaries
        # The camera should show as much map as possible
        min_camera_x = 0
        max_camera_x = max(0, self.map_width - self.screen_width)
        min_camera_y = 0
        max_camera_y = max(0, self.map_height - self.screen_height)

        # Set camera position
        self.x = max(min_camera_x, min(ideal_camera_x, max_camera_x))
        self.y = max(min_camera_y, min(ideal_camera_y, max_camera_y))

    def get_screen_position(self, world_x: int, world_y: int) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return screen_x, screen_y

    def is_visible(self, world_x: int, world_y: int) -> bool:
        """Check if a world position is visible on screen."""
        screen_x, screen_y = self.get_screen_position(world_x, world_y)
        return 0 <= screen_x < self.screen_width and 0 <= screen_y < self.screen_height
