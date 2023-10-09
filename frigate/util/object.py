"""Utils for reading and writing object detetion data."""

import numpy

from frigate.config import CameraConfig
from frigate.models import Event

def get_camera_regions_grid(camera: CameraConfig) -> list[list[dict[str, any]]]:
    """Get a 5x5 grid of expected region sizes for a camera."""
    events = Event.select(Event.data).where(Event.camera == camera.name).dicts()

    print(f"There are {len(events)} events for {camera.name}")
    width = camera.detect.width
    height = camera.detect.height

    all_data = [e["data"] for e in events]
    data = filter(lambda i: len(i) > 0, all_data)

    # create 5x5 grid
    grid = []
    for x in range(5):
        row = []
        for y in range(5):
            row.append({"sizes": []})
        grid.append(row)

    print(f"The size of grid is {len(grid)} x {len(grid[4])}")

    for d in data:
        if d.get("type") != "object":
            continue

        box = d["box"]

        # calculate centroid position
        x = box[0] + (box[2] / 2)
        y = box[1] + box[3]
        x_pos = int(x * 5)
        y_pos = int(y * 5)
        grid[x_pos][y_pos]["sizes"].append(d["region"][2] * width)

    print(f"The grid is {grid}")

    for x in range(5):
        for y in range(5):
            cell = grid[x][y]
            print(f"Printing stats for cell {x * 0.2 * width},{y * 0.2 * height} -> {(x + 1) * 0.2 * width},{(y + 1) * 0.2 * height}")
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