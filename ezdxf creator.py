import ezdxf

# Create a new DXF document
doc = ezdxf.new()

# Add a modelspace to the DXF document
msp = doc.modelspace()

# Define room details extracted from the floor plan image with manual text positions
rooms = [
    {"name": "Wohnzimmer", "x": 0, "y": 4.0, "width": 4.0, "height": 6.5, "text_pos": (2.0, 7.25)},
    {"name": "Windfang", "x": 0, "y": 2.8, "width": 4.0, "height": 1.2, "text_pos": (2.0, 3.4)},
    {"name": "Flur", "x": 0, "y": 2.0, "width": 4.0, "height": 0.8, "text_pos": (2.0, 2.4)},
    {"name": "Bad", "x": 3.0, "y": 0, "width": 1.0, "height": 2.0, "text_pos": (3.5, 1.0)},
    {"name": "Küche", "x": 0, "y": 0, "width": 3.0, "height": 2.0, "text_pos": (1.5, 1.0)},
    {"name": "Esszimmer", "x": 0, "y": -3.0, "width": 4.0, "height": 3.0, "text_pos": (2.0, -1.5)},
]

# Draw the rectangles for the rooms
for room in rooms:
    x, y = room["x"], room["y"]
    width, height = room["width"], room["height"]
    text_x, text_y = room["text_pos"]
    # Draw a rectangle
    msp.add_lwpolyline([
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height),
        (x, y)
    ], close=True)

    # Add room name at manually specified position
    msp.add_text(
        room["name"],
        dxfattribs={'height': 0.25}  # Text height
    ).set_dxf_attrib("insert", (text_x, text_y))

# Save the DXF file
doc.saveas("floor_plan_2_with_manual_text_fixed.dxf")
