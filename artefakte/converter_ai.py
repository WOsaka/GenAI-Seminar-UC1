import chat_gpt
import ezdxf
import os
import shutil
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def clear_folder(folder_path):
  # List all files and directories in the folder
  for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    try:
      if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)  # Remove the file or link
      elif os.path.isdir(file_path):
        shutil.rmtree(file_path)  # Remove the directory and its contents
    except Exception as e:
        print(f'Failed to delete {file_path}. Reason: {e}')

def dxf_to_png(dxf_path, png_path):
  # Load the DXF document
  doc = ezdxf.readfile(dxf_path)
  
  # Set up Matplotlib figure and axis
  fig = plt.figure()
  ax = fig.add_axes([0, 0, 1, 1])
  
  # Create the render context and backend
  ctx = RenderContext(doc)
  out = MatplotlibBackend(ax)
  
  # Draw the DXF layout
  Frontend(ctx, out).draw_layout(doc.modelspace(), finalize=True)
  
  # Save the figure as a PNG file
  fig.savefig(png_path)
  plt.close(fig)

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

def plot_rooms(rooms):
    # Create a new figure and axis for the plot
    fig, ax = plt.subplots(figsize=(10, 10))

    min_X = 0
    max_X = 0
    min_Y = 0
    max_Y = 0

    # Iterate over the list of rooms to draw each one
    for room in rooms:
        # Create a rectangle for the room
        rect = patches.Rectangle(
            (room["x"], room["y"]),
            room["width"],
            room["height"],
            linewidth=1,
            edgecolor='black',
            facecolor='lightblue'
        )

        if room["x"] < min_X:
            min_X = room["x"]         
        if room["x"] + room["width"] > max_X: 
            max_X = room["x"] + room["width"]     
        if room["y"] < min_Y:
            min_Y = room["y"]    
        if room["y"] + room["height"] > max_Y: 
            max_Y = room["y"] + room["height"]
          

        # Add the rectangle to the plot
        ax.add_patch(rect)
        # Add the room name at the specified text position
        ax.text(
            room["text_pos"][0],
            room["text_pos"][1],
            room["name"],
            ha='center',
            va='center',
            fontsize=10,
            color='black'
        )

    # Set the aspect ratio to equal for proper scaling
    ax.set_aspect('equal')
    # Set the limits of the plot based on the layout
    # Set the limits of the plot based on the layout
     
    ax.set_xlim(min_X - 3, max_X + 3)
    ax.set_ylim(min_Y - 3, max_Y + 3)
    # Add grid lines for better visualization
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    # Add labels for the axes
    ax.set_xlabel("X (meters)")
    ax.set_ylabel("Y (meters)")
    # Set a title for the plot
    ax.set_title("Room Layout")
    
    # Show the plot
    plt.show()

def main(image_path=r"Grundriss Beispiele\Beispiel_David.png"):
  response = chat_gpt.chat_with_gpt(image_path)
  print(response)
  extracted_rooms = chat_gpt.extract_rooms(response)
  create_floor_plan(extracted_rooms, r"uploads\output.dxf")
  dxf_to_png(r"uploads\output.dxf", r"uploads\output.png")


if __name__ == "__main__":
  # Example usage create_floor_plan
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
  #create_floor_plan(rooms, r"uploads\output.dxf")
  #dxf_to_png(r"uploads\output.dxf", r"uploads\output.png")

  #clear_folder(r"C:\Users\Oskar\Documents\Seminar\GenAI-Seminar-UC1\uploads")

  main()

  # Example usage dxf_to_png
  #dxf_to_png(r'uploads\dxf_converter.dxf', r'uploads\dxf_converter.png')
  
  # Example usage image_drawer 
  rooms = [
      {"name": "Wohnzimmer", "x": 0, "y": 4.0, "width": 4.0, "height": 6.5, "text_pos": (2.0, 7.25)},
      {"name": "Windfang", "x": 0, "y": 2.8, "width": 4.0, "height": 1.2, "text_pos": (2.0, 3.4)},
      {"name": "Flur", "x": 0, "y": 2.0, "width": 4.0, "height": 0.8, "text_pos": (2.0, 2.4)},
      {"name": "Bad", "x": 3.0, "y": 0, "width": 1.0, "height": 2.0, "text_pos": (3.5, 1.0)},
      {"name": "Küche", "x": 0, "y": 0, "width": 3.0, "height": 2.0, "text_pos": (1.5, 1.0)},
      {"name": "Esszimmer", "x": 0, "y": -3.0, "width": 4.0, "height": 3.0, "text_pos": (2.0, -1.5)},
  ]
  #plot_rooms(rooms)