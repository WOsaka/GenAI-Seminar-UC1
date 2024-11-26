import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

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

if __name__ == "__main__":
  dxf_to_png('floor_plan.dxf', 'output.png')
