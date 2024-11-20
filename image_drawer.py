import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_rooms(rooms):
    # Create a new figure and axis for the plot
    fig, ax = plt.subplots(figsize=(10, 10))

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
    ax.set_xlim(-1, 5)
    ax.set_ylim(-4, 8)
    # Add grid lines for better visualization
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    # Add labels for the axes
    ax.set_xlabel("X (meters)")
    ax.set_ylabel("Y (meters)")
    # Set a title for the plot
    ax.set_title("Room Layout")
    
    # Show the plot
    plt.show()
