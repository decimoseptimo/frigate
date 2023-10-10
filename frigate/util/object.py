"""Utils for reading and writing object detetion data."""

import numpy

from frigate.config import CameraConfig
from frigate.models import Event

def get_camera_regions_grid(camera: CameraConfig, grid_size: int = 10) -> list[list[dict[str, any]]]:
    """Get a grid of expected region sizes for a camera."""
    events = Event.select(Event.data).where(Event.camera == camera.name).dicts()

    print(f"There are {len(events)} events for {camera.name}")
    width = camera.detect.width
    height = camera.detect.height

    all_data = [e["data"] for e in events]
    data = filter(lambda i: len(i) > 0, all_data)

    # create a grid
    grid = []
    for x in range(grid_size):
        row = []
        for y in range(grid_size):
            row.append({"sizes": []})
        grid.append(row)

    print(f"The size of grid is {len(grid)} x {len(grid[grid_size - 1])}")
    grid_coef = 1.0 / grid_size

    for d in data:
        if d.get("type") != "object":
            continue

        box = d["box"]

        # calculate centroid position
        x = box[0] + (box[2] / 2)
        y = box[1] + box[3]
        x_pos = int(x * grid_size)
        y_pos = int(y * grid_size)
        grid[x_pos][y_pos]["sizes"].append(d["region"][2] * width)

    for x in range(grid_size):
        for y in range(grid_size):
            cell = grid[x][y]
            print(f"Printing stats for cell {x * grid_coef * width},{y * grid_coef * height} -> {(x + 1) * grid_coef * width},{(y + 1) * grid_coef * height}")
            print(f"Found {len(cell['sizes'])} for this cell")

            if len(cell["sizes"]) == 0:
                print(f"Cell {x}, {y} has no boxes")
                continue

            std_dev = numpy.std(cell["sizes"])
            mean = numpy.mean(cell["sizes"])
            print(f"Std dev: {std_dev} Mean: {mean}")
            cell["std_dev"] = std_dev
            cell["mean"] = mean

    # TODO need to handle filling in missing cells using existing cells
