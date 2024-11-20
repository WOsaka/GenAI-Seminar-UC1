import matplotlib.pyplot as plt
import matplotlib.patches as patches

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
    if min_X == 0:
        min_X = -2
    if min_Y == 0:
        min_Y = -2    
    ax.set_xlim(min_X * 1.5, max_X * 1.5)
    ax.set_ylim(min_Y * 1.5, max_Y * 1.5)
    # Add grid lines for better visualization
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    # Add labels for the axes
    ax.set_xlabel("X (meters)")
    ax.set_ylabel("Y (meters)")
    # Set a title for the plot
    ax.set_title("Room Layout")
    
    # Show the plot
    plt.show()

# Define the rooms
rooms = [
    {"name": "Wohnzimmer", "x": 0, "y": 4.0, "width": 4.0, "height": 6.5, "text_pos": (2.0, 7.25)},
    {"name": "Windfang", "x": 0, "y": 2.8, "width": 4.0, "height": 1.2, "text_pos": (2.0, 3.4)},
    {"name": "Flur", "x": 0, "y": 2.0, "width": 4.0, "height": 0.8, "text_pos": (2.0, 2.4)},
    {"name": "Bad", "x": 3.0, "y": 0, "width": 1.0, "height": 2.0, "text_pos": (3.5, 1.0)},
    {"name": "Küche", "x": 0, "y": 0, "width": 3.0, "height": 2.0, "text_pos": (1.5, 1.0)},
    {"name": "Esszimmer", "x": 0, "y": -3.0, "width": 4.0, "height": 3.0, "text_pos": (2.0, -1.5)},
]

# Plot the rooms
#plot_rooms(rooms)