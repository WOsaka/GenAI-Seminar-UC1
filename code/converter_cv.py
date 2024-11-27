import os
import json
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
load_dotenv()


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
  client = ImageAnalysisClient(
      endpoint=endpoint,
      credential=AzureKeyCredential(key)
  )

  # Load image to analyze into a 'bytes' object
  with open(image_path, "rb") as f:
    image_data = f.read()

  visual_features =[
      VisualFeatures.READ,
    ]

  # Get a caption for the image. This will be a synchronously (blocking) call.
  result = client.analyze(
    image_data=image_data,
    visual_features=visual_features,
    gender_neutral_caption=True,  # Optional (default is False)
  )

  with open(f'{json_output_path}.json', 'w') as file:
    json.dump(result.read.as_dict(), file, indent=4)

def draw_polygons_around_words(image_path, json_file_path, output_path, confidence_threshold):
    # Load the image
    image = cv.imread(image_path)
    assert image is not None, "File could not be read, check with os.path.exists()"

    # Load JSON data from a file
    with open(json_file_path, 'r') as json_file:
        text_data = json.load(json_file)

    # Iterate through each block, line, and word to draw polygons
    for block in text_data['blocks']:
        for line in block['lines']:
            for word in line['words']:
                if word['confidence'] >= confidence_threshold:
                    bounding_polygon = word['boundingPolygon']
                    points = [(pt['x'], pt['y']) for pt in bounding_polygon]
                    points = np.array(points, np.int32).reshape((-1, 1, 2))
                    cv.polylines(image, [points], isClosed=True, color=(0, 0, 255), thickness=2)

    # Save the image with polygons
    cv.imwrite(r'pipeline\1_text_highlighted.png', image)
    cv.imwrite(output_path, image)

def expand_polygon_horizontally(points, expand_left=5, expand_right=5):
    """Expand the polygon horizontally to the left and right sides."""
    expanded_points = []
    for i, pt in enumerate(points):
        if i == 0 or i == 3:  # Adjust the left-side points
            expanded_points.append({'x': pt['x'] - expand_left, 'y': pt['y']})
        else:  # Adjust the right-side points
            expanded_points.append({'x': pt['x'] + expand_right, 'y': pt['y']})
    return expanded_points

def remove_text_from_image(image_path, json_file_path, output_path, confidence_threshold):
    # Load the image
    image = cv.imread(image_path)
    assert image is not None, "File could not be read, check with os.path.exists()"

    # Load JSON data from a file
    with open(json_file_path, 'r') as json_file:
        text_data = json.load(json_file)

    # Create a mask for inpainting
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    # Iterate through each block, line, and word to create mask
    for block in text_data['blocks']:
        for line in block['lines']:
            for word in line['words']:
                if word['confidence'] >= confidence_threshold:
                    bounding_polygon = word['boundingPolygon']
                    expanded_points = expand_polygon_horizontally(bounding_polygon, expand_left=0, expand_right=12)
                    points = np.array([(pt['x'], pt['y']) for pt in expanded_points], np.int32).reshape((-1, 1, 2))
                    cv.fillPoly(mask, [points], 255)

    # Inpaint the masked areas
    inpainted_image = cv.inpaint(image, mask, inpaintRadius=7, flags=cv.INPAINT_TELEA)

    # Save the inpainted image
    cv.imwrite(r'pipeline\2_text_removed.png', inpainted_image)
    cv.imwrite(output_path, inpainted_image)

def find_contours(image_path):
  # Load the image
  img = cv.imread(image_path)
  assert img is not None, "File could not be read, check with os.path.exists()"

  # Get the image dimensions
  image_height, _ = img.shape[:2]

  # Convert to binary 
  _, binary = cv.threshold(img,127,255,cv.THRESH_BINARY_INV)
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
    doc = ezdxf.new('R2010')
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
  fig.savefig(r'pipeline\6_image_dxf.png')
  plt.close(fig)

def main(image_path):
    confidence_threshold = 0.65
    call_vision(image_path, r'uploads\result_vision') 
    draw_polygons_around_words(image_path, r'uploads\result_vision.json', r'pipeline\1_text_highlighted.png', confidence_threshold) 
    remove_text_from_image(image_path, r'uploads\result_vision.json', r'uploads\output.png', confidence_threshold) 
    contours, image_height = find_contours(r'uploads\output.png')
    contours_to_dxf(contours, r'uploads\output.dxf', image_height)
    dxf_to_png(r'uploads\output.dxf', r'uploads\output.png')

# Example usage
if __name__ == "__main__":
    main(r'Grundriss Beispiele\Beispiel_Niklas.jpg')