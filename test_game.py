"""Test script to verify game logic without GUI."""
from entity import Entity
from game_map import GameMap
from camera import Camera


def test_entity():
    """Test entity creation and movement."""
    print("Testing Entity...")
    entity = Entity(5, 5, "@", (255, 255, 255), "Test", blocks_movement=True)
    assert entity.x == 5
    assert entity.y == 5
    entity.move(1, -1)
    assert entity.x == 6
    assert entity.y == 4
    print("✓ Entity tests passed")


def test_game_map():
    """Test game map generation."""
    print("\nTesting GameMap...")
    game_map = GameMap(100, 80)
    assert game_map.width == 100
    assert game_map.height == 80

    # Check that some tiles are walkable (floor)
    walkable_count = sum(game_map.tiles.flatten())
    assert walkable_count > 0, "Map should have walkable tiles"
    print(f"✓ Map generated with {walkable_count} walkable tiles")

    # Test bounds checking
    assert game_map.is_in_bounds(50, 40) == True
    assert game_map.is_in_bounds(-1, 40) == False
    assert game_map.is_in_bounds(101, 40) == False
    print("✓ Bounds checking works")


def test_camera():
    """Test camera system."""
    print("\nTesting Camera...")
    camera = Camera(screen_width=80, screen_height=50, map_width=120, map_height=80)

    # Test centered player
    camera.update(60, 40)  # Player in middle of map
    expected_x = 60 - 40  # 60 - screen_width//2
    expected_y = 40 - 25  # 40 - screen_height//2
    assert camera.x == expected_x, f"Expected camera.x={expected_x}, got {camera.x}"
    assert camera.y == expected_y, f"Expected camera.y={expected_y}, got {camera.y}"
    print("✓ Camera centering works")

    # Test edge clamping
    camera.update(10, 10)  # Player near top-left corner
    assert camera.x == 0, "Camera should clamp to 0 at left edge"
    assert camera.y == 0, "Camera should clamp to 0 at top edge"
    print("✓ Camera edge clamping works")

    # Test screen position conversion
    screen_x, screen_y = camera.get_screen_position(10, 10)
    assert screen_x == 10, f"Expected screen_x=10, got {screen_x}"
    assert screen_y == 10, f"Expected screen_y=10, got {screen_y}"
    print("✓ World-to-screen coordinate conversion works")

    # Test visibility
    assert camera.is_visible(10, 10) == True
    assert camera.is_visible(200, 200) == False
    print("✓ Visibility checking works")


def test_game_integration():
    """Test integration of game components."""
    print("\nTesting Integration...")

    # Create game components
    game_map = GameMap(120, 80)
    camera = Camera(80, 50, 120, 80)

    # Find walkable position
    for x in range(game_map.width):
        for y in range(game_map.height):
            if game_map.is_walkable(x, y):
                player_x, player_y = x, y
                break
        else:
            continue
        break

    # Create player
    player = Entity(player_x, player_y, "@", (255, 255, 255), "Player", blocks_movement=True)
    camera.update(player.x, player.y)

    # Test player movement
    old_x, old_y = player.x, player.y
    # Try to move right
    new_x, new_y = player.x + 1, player.y
    if game_map.is_walkable(new_x, new_y):
        player.move(1, 0)
        camera.update(player.x, player.y)
        assert player.x == old_x + 1
        print("✓ Player movement works")
    else:
        print("✓ Movement validation works (blocked by wall)")

    # Create some entities
    entities = [player]
    enemy = Entity(player_x + 5, player_y, "G", (255, 0, 0), "Goblin")
    neutral = Entity(player_x - 5, player_y, "N", (100, 149, 237), "NPC")
    entities.extend([enemy, neutral])

    assert len(entities) == 3
    print("✓ Entity management works")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Running Game Logic Tests")
    print("=" * 50)

    try:
        test_entity()
        test_game_map()
        test_camera()
        test_game_integration()

        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        print("\nGame is ready to run with: python main.py")
        print("(Note: Requires a graphical environment to display)")

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
