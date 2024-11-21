import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

import ezdxf
from ezdxf.math import Matrix44
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


def get_wcs_to_image_transform(
    ax: plt.Axes, image_size: tuple[int, int]
) -> Matrix44:
    """Returns the transformation matrix from modelspace coordinates to image
    coordinates.
    """

    x1, x2 = ax.get_xlim()
    y1, y2 = ax.get_ylim()
    data_width, data_height = x2 - x1, y2 - y1
    image_width, image_height = image_size
    return (
        Matrix44.translate(-x1, -y1, 0)
        @ Matrix44.scale(
            image_width / data_width, -image_height / data_height, 1.0
        )
        # +1 to counteract the effect of the pixels being flipped in y
        @ Matrix44.translate(0, image_height + 1, 0)
    )

def convert_dxf_to_png(filename_dxf):
    # create the DXF document
    doc = ezdxf.readfile(filename_dxf)
    msp = doc.modelspace()

    # export the pixel image
    fig: plt.Figure = plt.figure()
    ax: plt.Axes = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)
    fig.savefig("converted.png")
    plt.close(fig)

    # reload the pixel image by Pillow (PIL)
    img = Image.open("converted.png")
    draw = ImageDraw.Draw(img)

    # add some annotations to the pixel image by using modelspace coordinates
    m = get_wcs_to_image_transform(ax, img.size)
    a, b, c = (
        (v.x, v.y)  # draw.line() expects tuple[float, float] as coordinates
        # transform modelspace coordinates to image coordinates
        for v in m.transform_vertices([(0.25, 0.75), (0.75, 0.25), (1, 1)])
    )
    draw.line([a, b, c, a], fill=(255, 0, 0))

# show the image by the default image viewer
#img.show()