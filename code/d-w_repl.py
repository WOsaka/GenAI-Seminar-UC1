from PIL import Image, ImageDraw
from shapely.geometry import Point, Polygon
import json

# Load the image
image_path = r"data\segment_floorplan.jpg"
image = Image.open(image_path)

# Load the coordinates from the JSON file
with open(r"data\segment_floorplan.json", "r") as file:
    data = json.load(file)

# Create a drawing context
draw = ImageDraw.Draw(image)

# Fill the specified areas for "door" or "window" classes
for prediction in data["predictions"]:
    if prediction["class"] in ["door", "window"]:
        points = [tuple(point.values()) for point in prediction["points"]]
        color = (
            255,
            255,
            255,
        )  # Using white color for filling, you can change it as needed
        draw.polygon(points, fill=color)

# Confidence for door/window that are added back into the image
confidence = 0

# Fill the specified areas for "door" or "window" classes
for prediction in data["predictions"]:
    if (
        prediction["class"] in ["door", "window"]
        and prediction["confidence"] > confidence
    ):
        # Extract points
        points = [tuple(point.values()) for point in prediction["points"]]
        # Get min and max coordinates
        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)
        min_y = min(point[1] for point in points)
        max_y = max(point[1] for point in points)

        fill_color = (
            255,
            255,
            255,
        )  # White color for filling
        outline_color = (
            0,
            0,
            0,
        )  # Black color for outline

        if prediction["class"] == "window":
            # Draw a rectangle using min and max coordinates with fill and outline
            draw.rectangle(
                [min_x, min_y, max_x, max_y],
                fill=fill_color,
                outline=outline_color,
                width=3,
            )

            # Draw a horizontal line in the middle of the rectangle

            length_x = max_x - min_x
            length_y = max_y - min_y
            if length_x > length_y:
                middle_y = (min_y + max_y) // 2
                draw.line(
                    [min_x, middle_y, max_x, middle_y], fill=outline_color, width=2
                )
            else:
                middle_x = (min_x + max_x) // 2
                draw.line(
                    [middle_x, min_y, middle_x, max_y], fill=outline_color, width=2
                )

        elif prediction["class"] == "door":
            polygon = Polygon(points)

            # Padding to check orientation of door
            padding = 10

            # Define the point to check
            corner_points = {
                "upper_left": (min_x + padding, min_y + padding),
                "lower_left": (min_x + padding, max_y - padding),
                "upper_right": (max_x - padding, min_y + padding),
                "lower_right": (max_x - padding, max_y - padding),
            }

            for point_to_check in corner_points:
                point = Point(corner_points[point_to_check])

                # Check if the point is inside the polygon
                is_inside = polygon.contains(point)

                if not is_inside:
                    # Width of line for doors
                    width = 2

                    if point_to_check == "upper_left":
                        draw.line(
                            [max_x, min_y, max_x, max_y],
                            fill=outline_color,
                            width=width,
                        )
                        draw.line(
                            [max_x, max_y, min_x, max_y],
                            fill=outline_color,
                            width=width,
                        )
                        draw.line(
                            [max_x, min_y, min_x, max_y],
                            fill=outline_color,
                            width=width,
                        )
                    elif point_to_check == "lower_left":
                        draw.line(
                            [min_x, min_y, max_x, min_y],
                            fill=outline_color,
                            width=width,
                        )
                        draw.line(
                            [max_x, min_y, max_x, max_y],
                            fill=outline_color,
                            width=width,
                        )
                        draw.line(
                            [min_x, min_y, max_x, max_y],
                            fill=outline_color,
                            width=width,
                        )
                    elif point_to_check == "upper_right":
                        draw.line(
                            [min_x, min_y, min_x, max_y],
                            fill=outline_color,
                            width=width,
                        )
                        draw.line(
                            [min_x, max_y, max_x, max_y],
                            fill=outline_color,
                            width=width,
                        )
                        draw.line(
                            [min_x, min_y, max_x, max_y],
                            fill=outline_color,
                            width=width,
                        )
                    elif point_to_check == "lower_right":
                        draw.line(
                            [min_x, max_y, min_x, min_y],
                            fill=outline_color,
                            width=width,
                        )
                        draw.line(
                            [min_x, min_y, max_x, min_y],
                            fill=outline_color,
                            width=width,
                        )
                        draw.line(
                            [max_x, min_y, min_x, max_y],
                            fill=outline_color,
                            width=width,
                        )


# Save the modified image
output_path = r"data/output.png"
image.save(output_path)
print(f"Image saved to {output_path}")
