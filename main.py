"""Main game file for the libtcod roguelike."""
import tcod
import random
from entity import Entity
from game_map import GameMap
from camera import Camera


# Screen dimensions
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

# Map dimensions (larger than screen)
MAP_WIDTH = 120
MAP_HEIGHT = 80

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
BLUE = (100, 149, 237)  # Cornflower blue
YELLOW = (255, 255, 0)


class Game:
    """Main game class."""

    def __init__(self):
        # Initialize console
        self.tileset = tcod.tileset.load_tilesheet(
            tcod.tileset.CHARMAP_CP437, 16, 16, tcod.tileset.CHARMAP_CP437
        )
        self.console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")
        self.context = tcod.context.new(
            console=self.console,
            tileset=self.tileset,
            title="Roguelike Game",
            vsync=True
        )

        # Initialize game map
        self.game_map = GameMap(MAP_WIDTH, MAP_HEIGHT)

        # Find a walkable starting position for the player
        player_x, player_y = self.find_walkable_position()

        # Initialize player
        self.player = Entity(
            x=player_x,
            y=player_y,
            char="@",
            color=WHITE,
            name="Player",
            blocks_movement=True
        )

        # Initialize camera
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
        self.camera.update(self.player.x, self.player.y)

        # Initialize entities
        self.entities = [self.player]
        self.spawn_enemies(10)
        self.spawn_neutrals(15)

    def find_walkable_position(self) -> tuple[int, int]:
        """Find a random walkable position on the map."""
        while True:
            x = random.randint(0, MAP_WIDTH - 1)
            y = random.randint(0, MAP_HEIGHT - 1)
            if self.game_map.is_walkable(x, y):
                return x, y

    def spawn_enemies(self, count: int) -> None:
        """Spawn static enemy entities in red."""
        enemy_chars = ['G', 'O', 'T', 'K', 'D']  # Goblin, Orc, Troll, Kobold, Dragon
        for _ in range(count):
            x, y = self.find_walkable_position()
            # Make sure we don't spawn on the player
            while x == self.player.x and y == self.player.y:
                x, y = self.find_walkable_position()

            enemy = Entity(
                x=x,
                y=y,
                char=random.choice(enemy_chars),
                color=RED,
                name="Enemy",
                blocks_movement=True
            )
            self.entities.append(enemy)

    def spawn_neutrals(self, count: int) -> None:
        """Spawn neutral entities in blue or yellow."""
        neutral_chars = ['N', 'V', 'M', 'P']  # NPC, Vendor, Merchant, Person
        colors = [BLUE, YELLOW]

        for _ in range(count):
            x, y = self.find_walkable_position()
            # Make sure we don't spawn on the player
            while x == self.player.x and y == self.player.y:
                x, y = self.find_walkable_position()

            neutral = Entity(
                x=x,
                y=y,
                char=random.choice(neutral_chars),
                color=random.choice(colors),
                name="Neutral",
                blocks_movement=False
            )
            self.entities.append(neutral)

    def handle_input(self) -> bool:
        """Handle keyboard input. Returns False if game should quit."""
        for event in tcod.event.wait():
            if event.type == "QUIT":
                return False
            elif event.type == "KEYDOWN":
                if event.sym == tcod.event.KeySym.ESCAPE:
                    return False

                # Movement keys
                dx, dy = 0, 0
                if event.sym == tcod.event.KeySym.UP or event.sym == tcod.event.KeySym.k:
                    dy = -1
                elif event.sym == tcod.event.KeySym.DOWN or event.sym == tcod.event.KeySym.j:
                    dy = 1
                elif event.sym == tcod.event.KeySym.LEFT or event.sym == tcod.event.KeySym.h:
                    dx = -1
                elif event.sym == tcod.event.KeySym.RIGHT or event.sym == tcod.event.KeySym.l:
                    dx = 1
                # Diagonal movement
                elif event.sym == tcod.event.KeySym.y:
                    dx, dy = -1, -1
                elif event.sym == tcod.event.KeySym.u:
                    dx, dy = 1, -1
                elif event.sym == tcod.event.KeySym.b:
                    dx, dy = -1, 1
                elif event.sym == tcod.event.KeySym.n:
                    dx, dy = 1, 1

                # Move player if valid
                if dx != 0 or dy != 0:
                    new_x = self.player.x + dx
                    new_y = self.player.y + dy
                    if self.game_map.is_walkable(new_x, new_y):
                        self.player.move(dx, dy)
                        self.camera.update(self.player.x, self.player.y)

        return True

    def render(self) -> None:
        """Render the game."""
        self.console.clear()

        # Render map
        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                world_x = x + self.camera.x
                world_y = y + self.camera.y

                if self.game_map.is_in_bounds(world_x, world_y):
                    if self.game_map.is_walkable(world_x, world_y):
                        self.console.print(x, y, ".", fg=GRAY)
                    else:
                        self.console.print(x, y, "#", fg=DARK_GRAY)

        # Render entities
        for entity in self.entities:
            if self.camera.is_visible(entity.x, entity.y):
                screen_x, screen_y = self.camera.get_screen_position(entity.x, entity.y)
                self.console.print(screen_x, screen_y, entity.char, fg=entity.color)

        # Render UI info
        info_text = f"Player: ({self.player.x}, {self.player.y}) | Camera: ({self.camera.x}, {self.camera.y})"
        self.console.print(0, 0, info_text, fg=WHITE, bg=BLACK)

        # Present the console
        self.context.present(self.console)

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            self.render()
            running = self.handle_input()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
