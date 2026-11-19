"""
sketch.py: a tiny Processing-style drawing toolkit for Jupyter and Google Colab.

    from sketch import size, background, fill, circle

    size(400, 300)
    background("white")
    fill(255, 0, 0)
    circle(200, 150, 100)

The picture appears below the cell automatically. Start each new picture with
size(). Coordinates work like in Processing: (0, 0) is the top-left corner,
x grows to the right, y grows downwards.

Colours can be given in any of these ways:
    fill(120)                  grey: 0 = black ... 255 = white
    fill(120, 100)             grey with transparency (alpha: 0 = invisible ... 255 = solid)
    fill(255, 0, 0)            red, green, blue (each 0 ... 255)
    fill(255, 0, 0, 100)       red, green, blue + transparency
    fill("tomato")             a colour name, or a hex code like "#ff6347"
    fill("tomato", 100)        ... plus transparency
    fill(hsb(200, 80, 90))     hue (0 ... 360), saturation and brightness (0 ... 100)
    fill(hsb(200, 80, 90), 100)  ... plus transparency

Shapes:
    point(x, y)
    line(x1, y1, x2, y2)
    rect(x, y, width, height)       x, y = top-left corner
    square(x, y, side)
    ellipse(x, y, width, height)    x, y = centre
    circle(x, y, diameter)
    triangle(x1, y1, x2, y2, x3, y3)
    text("hello", x, y)             x, y = start of the baseline

Style (applies to every shape drawn afterwards):
    fill(...) / no_fill()            inside colour of shapes
    stroke(...) / no_stroke()        outline colour of shapes, colour of lines and points
    stroke_weight(3)                 outline / line thickness
    text_size(24)

Other:
    show()                           draw the picture now (only needed for several pictures in one cell)
    save("my_picture.svg")           save the picture as an SVG file
"""

import colorsys
from html import escape
from numbers import Real

__all__ = [
    "size", "background",
    "fill", "no_fill", "stroke", "no_stroke", "stroke_weight", "text_size", "hsb",
    "point", "line", "rect", "square", "ellipse", "circle", "triangle", "text",
    "show", "save",
]


class _Canvas:
    """Everything that has been drawn so far, plus the current style settings."""

    def __init__(self, width=400, height=400):
        self.width = width
        self.height = height
        self.background = ("rgb(204,204,204)", 1.0)  # Processing's default grey
        self.shapes = []                             # SVG elements, in drawing order
        self.fill = ("rgb(255,255,255)", 1.0)        # None means no_fill()
        self.stroke = ("rgb(0,0,0)", 1.0)            # None means no_stroke()
        self.stroke_weight = 1
        self.text_size = 16
        self.needs_showing = False


_canvas = _Canvas()


# ---------------------------------------------------------------- helpers

def _num(function_name, value):
    """Check that value is a number and format it compactly for SVG."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{function_name}() needs numbers, but got {value!r}")
    text = str(round(float(value), 2))
    return text.removesuffix(".0")


def _color(function_name, args):
    """Turn Processing-style colour arguments into (svg_colour, opacity)."""
    if len(args) == 1 and isinstance(args[0], (tuple, list)):
        args = tuple(args[0])  # allow fill((255, 0, 0)) as well as fill(255, 0, 0)

    if len(args) in (1, 2) and isinstance(args[0], str):
        alpha = args[1] if len(args) == 2 else 255
        _num(function_name, alpha)
        return (escape(args[0]), max(0, min(255, alpha)) / 255)

    for value in args:
        _num(function_name, value)
    values = [max(0, min(255, value)) for value in args]

    if len(values) == 1:
        r = g = b = values[0]
        alpha = 255
    elif len(values) == 2:
        r = g = b = values[0]
        alpha = values[1]
    elif len(values) == 3:
        r, g, b = values
        alpha = 255
    elif len(values) == 4:
        r, g, b, alpha = values
    else:
        raise TypeError(
            f"{function_name}() takes 1 to 4 numbers or a colour name, "
            f"but got {len(args)} values"
        )
    return (f"rgb({round(r)},{round(g)},{round(b)})", alpha / 255)


def _paint(kind, color):
    """SVG attributes for a fill or stroke colour, e.g. 'fill="rgb(1,2,3)"'."""
    if color is None:
        return f'{kind}="none"'
    value, opacity = color
    attributes = f'{kind}="{value}"'
    if opacity < 1:
        attributes += f' {kind}-opacity="{round(opacity, 3)}"'
    return attributes


def _style(filled=True):
    parts = [_paint("fill", _canvas.fill if filled else None)]
    if _canvas.stroke is not None:
        parts.append(_paint("stroke", _canvas.stroke))
        parts.append(f'stroke-width="{_num("stroke_weight", _canvas.stroke_weight)}"')
    return " ".join(parts)


def _add(element):
    _canvas.shapes.append(element)
    _canvas.needs_showing = True


# ---------------------------------------------------------------- canvas

def size(width, height):
    """Start a new, empty picture of the given size (in pixels)."""
    global _canvas
    _num("size", width)
    _num("size", height)
    _canvas = _Canvas(width, height)
    _canvas.needs_showing = True


def background(*color):
    """Fill the whole picture with one colour (this covers everything drawn so far)."""
    _canvas.background = _color("background", color)
    _canvas.shapes.clear()
    _canvas.needs_showing = True


# ---------------------------------------------------------------- style

def fill(*color):
    """Set the inside colour for the shapes drawn after this."""
    _canvas.fill = _color("fill", color)


def no_fill():
    """Draw shapes as outlines only."""
    _canvas.fill = None


def stroke(*color):
    """Set the outline colour (and the colour of lines and points)."""
    _canvas.stroke = _color("stroke", color)


def no_stroke():
    """Draw shapes without an outline."""
    _canvas.stroke = None


def stroke_weight(weight):
    """Set the thickness of outlines, lines and points."""
    _num("stroke_weight", weight)
    _canvas.stroke_weight = weight


def text_size(size_in_pixels):
    """Set the font size for text()."""
    _num("text_size", size_in_pixels)
    _canvas.text_size = size_in_pixels


def hsb(hue, saturation=100, brightness=100):
    """A colour from hue (0-360, around the colour wheel), saturation and brightness (0-100).

    Use it like this: fill(hsb(30, 80, 100))
    """
    for value in (hue, saturation, brightness):
        _num("hsb", value)
    saturation = max(0, min(100, saturation))
    brightness = max(0, min(100, brightness))
    r, g, b = colorsys.hsv_to_rgb((hue % 360) / 360, saturation / 100, brightness / 100)
    return f"#{round(r * 255):02x}{round(g * 255):02x}{round(b * 255):02x}"


# ---------------------------------------------------------------- shapes

def point(x, y):
    """A single dot, in the stroke colour, as big as stroke_weight."""
    if _canvas.stroke is None:
        return
    radius = max(_canvas.stroke_weight, 1) / 2
    _add(
        f'<circle cx="{_num("point", x)}" cy="{_num("point", y)}" '
        f'r="{_num("point", radius)}" {_paint("fill", _canvas.stroke)}/>'
    )


def line(x1, y1, x2, y2):
    """A straight line from (x1, y1) to (x2, y2), in the stroke colour."""
    xs = [_num("line", value) for value in (x1, y1, x2, y2)]
    _add(f'<line x1="{xs[0]}" y1="{xs[1]}" x2="{xs[2]}" y2="{xs[3]}" {_style(filled=False)}/>')


def _rect(function_name, x, y, width, height):
    xs = [_num(function_name, value) for value in (x, y, width, height)]
    _add(f'<rect x="{xs[0]}" y="{xs[1]}" width="{xs[2]}" height="{xs[3]}" {_style()}/>')


def rect(x, y, width, height):
    """A rectangle whose top-left corner is at (x, y)."""
    _rect("rect", x, y, width, height)


def square(x, y, side):
    """A square whose top-left corner is at (x, y)."""
    _rect("square", x, y, side, side)


def _ellipse(function_name, x, y, width, height):
    for value in (width, height):
        _num(function_name, value)
    xs = [_num(function_name, value) for value in (x, y, width / 2, height / 2)]
    _add(f'<ellipse cx="{xs[0]}" cy="{xs[1]}" rx="{xs[2]}" ry="{xs[3]}" {_style()}/>')


def ellipse(x, y, width, height):
    """An ellipse centred on (x, y)."""
    _ellipse("ellipse", x, y, width, height)


def circle(x, y, diameter):
    """A circle centred on (x, y)."""
    _ellipse("circle", x, y, diameter, diameter)


def triangle(x1, y1, x2, y2, x3, y3):
    """A triangle through three corner points."""
    xs = [_num("triangle", value) for value in (x1, y1, x2, y2, x3, y3)]
    points = f"{xs[0]},{xs[1]} {xs[2]},{xs[3]} {xs[4]},{xs[5]}"
    _add(f'<polygon points="{points}" {_style()}/>')


def text(content, x, y):
    """Write text (in the fill colour) starting at (x, y)."""
    _add(
        f'<text x="{_num("text", x)}" y="{_num("text", y)}" '
        f'font-size="{_num("text", _canvas.text_size)}" font-family="sans-serif" '
        f'{_paint("fill", _canvas.fill)}>{escape(str(content))}</text>'
    )


# ---------------------------------------------------------------- output

def _svg():
    width = _num("size", _canvas.width)
    height = _num("size", _canvas.height)
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" {_paint("fill", _canvas.background)}/>',
        *_canvas.shapes,
        "</svg>",
    ])


def show():
    """Display the picture below the cell.

    You only need this to show several pictures from one cell: at the end of
    every cell that draws something, the picture is shown automatically.
    """
    _canvas.needs_showing = False
    try:
        from IPython.display import SVG, display
    except ImportError:
        print("show() only works inside a Jupyter notebook. Use save('picture.svg') instead.")
        return
    display(SVG(_svg()))


def save(filename):
    """Save the picture as an SVG file (open it in any web browser)."""
    if not filename.lower().endswith(".svg"):
        raise ValueError(f"save() writes SVG files, so the name should end in .svg, not {filename!r}")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(_svg())


def _show_if_drawn():
    if _canvas.needs_showing:
        show()


# Like matplotlib in notebooks: after a cell has run, show its picture automatically.
try:
    from IPython import get_ipython
    _ipython = get_ipython()
except ImportError:
    _ipython = None

if _ipython is not None:
    _ipython.events.register("post_execute", _show_if_drawn)
