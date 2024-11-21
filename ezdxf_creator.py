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
rooms2 =  [
        {"name": "Wintergarten", "x": 0, "y": 0, "width": 4.75, "height": 4.75, "text_pos": (2.375, 2.375)},
        {"name": "Wohnen", "x": 4.75, "y": 0, "width": 7.6, "height": 4.75, "text_pos": (8.55, 2.375)},
        {"name": "Essen", "x": 12.35, "y": 0, "width": 7.15, "height": 4.75, "text_pos": (15.925, 2.375)},
        {"name": "Küche", "x": 19.5, "y": 0, "width": 7.34, "height": 4.75, "text_pos": (23.17, 2.375)},
        {"name": "WC", "x": 4.75, "y": 4.75, "width": 1.5, "height": 1.5, "text_pos": (5.5, 5.5)},
        {"name": "Abst.", "x": 6.25, "y": 4.75, "width": 1.5, "height": 1.5, "text_pos": (7, 5.5)},
        {"name": "Flur", "x": 7.75, "y": 4.75, "width": 2.5, "height": 1.5, "text_pos": (8.75, 5.5)},
        {"name": "Gäste", "x": 10.25, "y": 4.75, "width": 2.5, "height": 1.5, "text_pos": (11.25, 5.5)},
        {"name": "Arbeiten", "x": 12.75, "y": 4.75, "width": 7.34, "height": 4.75, "text_pos": (16.42, 7.125)},
        {"name": "Müll", "x": 0, "y": 6.25, "width": 4.75, "height": 1.5, "text_pos": (2.375, 7)},
        {"name": "Treppenhaus", "x": 4.75, "y": 6.25, "width": 7.6, "height": 1.5, "text_pos": (8.55, 7)}
    ]
create_floor_plan(rooms2, "other_floor_plan.dxf")