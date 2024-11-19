import ezdxf

def create_floor_plan(rooms, filename):
    """
    Create a floor plan DXF document with given room definitions and save it to a file.

    Parameters:
    - rooms: List of dictionaries, each containing room details with keys:
        - "name": Room name (str)
        - "x": X-coordinate of the bottom-left corner (float)
        - "y": Y-coordinate of the bottom-left corner (float)
        - "width": Width of the room (float)
        - "height": Height of the room (float)
        - "text_pos": Tuple (x, y) for text insertion point (float, float)
    - filename: The name of the DXF file to save (str)
    """
    # Create a new DXF document
    doc = ezdxf.new()

    # Add a modelspace to the DXF document
    msp = doc.modelspace()

    # Draw the rectangles and add text for each room
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
    doc.saveas(filename)

# Example usage
rooms = [
    {"name": "Wohnzimmer", "x": 0, "y": 4.0, "width": 4.0, "height": 6.5, "text_pos": (2.0, 7.25)},
    {"name": "Windfang", "x": 0, "y": 2.8, "width": 4.0, "height": 1.2, "text_pos": (2.0, 3.4)},
    {"name": "Flur", "x": 0, "y": 2.0, "width": 4.0, "height": 0.8, "text_pos": (2.0, 2.4)},
    {"name": "Bad", "x": 3.0, "y": 0, "width": 1.0, "height": 2.0, "text_pos": (3.5, 1.0)},
    {"name": "Küche", "x": 0, "y": 0, "width": 3.0, "height": 2.0, "text_pos": (1.5, 1.0)},
    {"name": "Esszimmer", "x": 0, "y": -3.0, "width": 4.0, "height": 3.0, "text_pos": (2.0, -1.5)},
]

create_floor_plan(rooms, "floor_plan_2_with_manual_text_fixed.dxf")