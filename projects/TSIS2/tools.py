import pygame
from datetime import datetime
from collections import deque


def pencil_tool(surface, prev_pos, curr_pos, color, size):
    """Draw a continuous line between previous and current mouse positions."""
    if prev_pos:
        pygame.draw.line(surface, color, prev_pos, curr_pos, size)


def line_preview(surface, start_pos, end_pos, color, size):
    """Draw a temporary preview line while dragging (straight line tool)."""
    pygame.draw.line(surface, color, start_pos, end_pos, size)


def flood_fill(surface, start_pos, fill_color):
    """
    Flood-fill algorithm using BFS (Breadth-First Search).
    Starts at start_pos, fills all connected pixels of the same color
    with fill_color. Stops at pixels of a different color.
    """
    x, y = start_pos
    width, height = surface.get_size()

    # Get the color of the pixel where user clicked (target color)
    target_color = surface.get_at((x, y))[:3]  # ignore alpha channel
    fill_rgb      = fill_color[:3]

    # If target is already the fill color — nothing to do
    if target_color == fill_rgb:
        return

    # BFS queue: start from clicked pixel
    queue = deque()
    queue.append((x, y))
    visited = set()
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()

        # Skip if out of bounds
        if cx < 0 or cx >= width or cy < 0 or cy >= height:
            continue

        # Skip if this pixel doesn't match the target color
        if surface.get_at((cx, cy))[:3] != target_color:
            continue

        # Paint the pixel
        surface.set_at((cx, cy), fill_color)

        # Add 4 neighbours (up, down, left, right)
        for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
            if (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))


def save_canvas(surface):
    """
    Save the canvas as a PNG file.
    Filename includes a timestamp so saves never overwrite each other.
    Example: canvas_2024-05-21_14-30-55.png
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename  = f"canvas_{timestamp}.png"
    pygame.image.save(surface, filename)
    print(f"Canvas saved as: {filename}")
    return filename