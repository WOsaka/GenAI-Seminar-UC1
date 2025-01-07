from PIL import Image, ImageDraw
import json

# Load the image
image_path = "image.png"
image = Image.open(image_path)

# Load the coordinates from the JSON file
with open("coordinates.json", "r") as file:
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

# Save the modified image
output_path = "output.png"
image.save(output_path)

print(f"Image saved to {output_path}")