import os
import json
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import ezdxf
import roboflow
import json
import shutil
from PIL import Image, ImageDraw
from shapely.geometry import Point, Polygon
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()


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
            print(f"Failed to delete {file_path}. Reason: {e}")


def call_vision(image_path, json_output_path):
    # Set the values of your computer vision endpoint and computer vision key
    # as environment variables:
    try:
        endpoint = os.environ.get("VISION_ENDPOINT")
        key = os.environ.get("VISION_KEY")
    except KeyError:
        print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create an Image Analysis client
    client = ImageAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Load image to analyze into a 'bytes' object
    with open(image_path, "rb") as f:
        image_data = f.read()

    visual_features = [
        VisualFeatures.READ,
    ]

    # Get a caption for the image. This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image_data,
        visual_features=visual_features,
        gender_neutral_caption=True,  # Optional (default is False)
    )

    with open(f"{json_output_path}.json", "w") as file:
        json.dump(result.read.as_dict(), file, indent=4)


def draw_polygons_around_words(
    image_path, json_file_path, output_path, confidence_threshold
):
    # Load the image
    image = cv.imread(image_path)
    assert image is not None, "File could not be read, check with os.path.exists()"

    # Load JSON data from a file
    with open(json_file_path, "r") as json_file:
        text_data = json.load(json_file)

    # Iterate through each block, line, and word to draw polygons
    for block in text_data["blocks"]:
        for line in block["lines"]:
            for word in line["words"]:
                if word["confidence"] >= confidence_threshold:
                    bounding_polygon = word["boundingPolygon"]
                    points = [(pt["x"], pt["y"]) for pt in bounding_polygon]
                    points = np.array(points, np.int32).reshape((-1, 1, 2))
                    cv.polylines(
                        image, [points], isClosed=True, color=(0, 0, 255), thickness=2
                    )

    # Save the image with polygons
    cv.imwrite(r"pipeline\1_text_highlighted.png", image)
    cv.imwrite(output_path, image)


def expand_polygon_horizontally(points, expand_left=5, expand_right=5):
    """Expand the polygon horizontally to the left and right sides."""
    expanded_points = []
    for i, pt in enumerate(points):
        if i == 0 or i == 3:  # Adjust the left-side points
            expanded_points.append({"x": pt["x"] - expand_left, "y": pt["y"]})
        else:  # Adjust the right-side points
            expanded_points.append({"x": pt["x"] + expand_right, "y": pt["y"]})
    return expanded_points


def remove_text_from_image(
    image_path, json_file_path, output_path, confidence_threshold
):
    # Load the image
    image = cv.imread(image_path)
    assert image is not None, "File could not be read, check with os.path.exists()"

    # Load JSON data from a file
    with open(json_file_path, "r") as json_file:
        text_data = json.load(json_file)

    # Create a mask for inpainting
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    # Iterate through each block, line, and word to create mask
    for block in text_data["blocks"]:
        for line in block["lines"]:
            for word in line["words"]:
                if word["confidence"] >= confidence_threshold:
                    bounding_polygon = word["boundingPolygon"]
                    expanded_points = expand_polygon_horizontally(
                        bounding_polygon, expand_left=0, expand_right=12
                    )
                    points = np.array(
                        [(pt["x"], pt["y"]) for pt in expanded_points], np.int32
                    ).reshape((-1, 1, 2))
                    cv.fillPoly(mask, [points], 255)

    # Inpaint the masked areas
    inpainted_image = cv.inpaint(image, mask, inpaintRadius=7, flags=cv.INPAINT_TELEA)

    # Save the inpainted image
    cv.imwrite(r"pipeline\2_text_removed.png", inpainted_image)
    cv.imwrite(output_path, inpainted_image)


def put_text_on_image(image_path, json_file_path, output_path, confidence_threshold):
    # Load the image
    image = cv.imread(image_path)
    assert image is not None, "File could not be read, check with os.path.exists()"

    # Load JSON data from a file
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        text_data = json.load(json_file)

    # Iterate through each block, line, and word to put text on image
    for block in text_data["blocks"]:
        for line in block["lines"]:
            for word in line["words"]:
                if word["confidence"] >= confidence_threshold:
                    # Calculate the bounding box for the line
                    bounding_polygon = line["boundingPolygon"]

                    # Calculate the top-left corner of the bounding box to place the text
                    top_left_x = min(pt["x"] for pt in bounding_polygon)
                    top_left_y = max(pt["y"] for pt in bounding_polygon)

                    # Put the text on the image
                    cv.putText(
                        image,
                        line["text"],
                        (top_left_x, top_left_y),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 0),
                        2,
                        cv.LINE_AA,
                        False,
                    )

    # Save the image with text
    cv.imwrite(output_path, image)


def find_contours(image_path):
    # Load the image
    img = cv.imread(image_path)
    assert img is not None, "File could not be read, check with os.path.exists()"

    # Get the image dimensions
    image_height, _ = img.shape[:2]

    # Convert to binary
    _, binary = cv.threshold(img, 127, 255, cv.THRESH_BINARY_INV)
    cv.imwrite(r"pipeline\3_image_binary.png", binary)

    # Apply Canny edge detection
    edges = cv.Canny(binary, 215, 370)
    cv.imwrite(r"pipeline\4_image_canny.png", edges)

    # Find contours
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    cv.drawContours(img, contours, -1, (0, 255, 0), 2)
    cv.imwrite(r"pipeline\5_image_contours.png", img)

    return (contours, image_height)


def contours_to_dxf(contours, dxf_path, image_height):
    # Create a new DXF document
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Iterate through each contour and create a polyline in the DXF document
    for contour in contours:
        points = [(point[0][0], image_height - point[0][1]) for point in contour]
        if points:
            msp.add_lwpolyline(points, close=True)

    # Save the DXF document
    doc.saveas(dxf_path)


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
    fig.savefig(r"pipeline\6_image_dxf.png")
    plt.close(fig)


def convert_to_jpg(input_path, output_path):
    # Öffne das Bild
    img = Image.open(input_path)

    # Konvertiere das Bild in RGB (JPG unterstützt keine Transparenz)
    rgb_img = img.convert("RGB")

    # Speichere das Bild als JPG
    rgb_img.save(output_path, "JPEG")


def call_roboflow(image):
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    rf = roboflow.Roboflow(api_key)

    project = rf.workspace().project("segmenting-a-floor-plan")
    model = project.version("1").model

    # predict on a local image
    # prediction =
    return model.predict(image)


def save_json(data, path_to):
    # Writing JSON data to the file
    with open(path_to, "w") as json_file:
        json.dump(data, json_file)


def delete_replace_door_window(image_path, confidence):
    # Roboflow
    convert_to_jpg(image_path, r"data\segment_floorplan.jpg")
    prediction = call_roboflow(r"data\segment_floorplan.jpg")
    data = prediction.json()
    save_json(data, r"data\segment_floorplan.json")

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
    output_paths = [r"data/output.png", r"uploads/output.png"]
    for output_path in output_paths:
        image.save(output_path)


def main(image_path):
    confidence_vision = 0
    confidence_roboflow = 0.4
    delete_replace_door_window(image_path, confidence_roboflow)
    call_vision(r"uploads\output.png", r"uploads\result_vision")
    draw_polygons_around_words(
        image_path,
        r"uploads\result_vision.json",
        r"pipeline\1_text_highlighted.png",
        confidence_vision,
    )
    remove_text_from_image(
        r"uploads\output.png",
        r"uploads\result_vision.json",
        r"uploads\output.png",
        confidence_vision,
    )
    # put_text_on_image(r"pipeline\2_text_removed.png", r"uploads\result_vision.json", r"pipeline/2.1_text_added.png", confidence_threshold)

    contours, image_height = find_contours(r"uploads\output.png")
    contours_to_dxf(contours, r"uploads\output.dxf", image_height)
    dxf_to_png(r"uploads\output.dxf", r"uploads\output.png")


# Example usage
if __name__ == "__main__":
    main(r"Neue Grundrisse\image.png")
    # clear_folder(r"C:\Users\Oskar\Documents\Seminar\GenAI-Seminar-UC1\uploads")
    # clear_folder(r"C:\Users\Oskar\Documents\Seminar\GenAI-Seminar-UC1\data")
