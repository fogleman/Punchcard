from math import pi, sin
import csv
import cairo

PADDING = 12
CELL_PADDING = 4
MIN_SIZE = 4
MAX_SIZE = 32
MIN_COLOR = 0.8
MAX_COLOR = 0.0

FONT = 'Helvetica'
FONT_SIZE = 14
FONT_BOLD = False

TITLE_FONT = 'Helvetica'
TITLE_FONT_SIZE = 20
TITLE_FONT_BOLD = True

DIAGONAL_COLUMN_LABELS = False

def set_font(dc, name=None, size=None, bold=False):
    if name is not None:
        weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
        dc.select_font_face(name, cairo.FONT_SLANT_NORMAL, weight)
    if size is not None:
        dc.set_font_size(size)

def punchcard(path, rows, cols, data, **kwargs):
    # get options
    padding = kwargs.get('padding', PADDING)
    cell_padding = kwargs.get('cell_padding', CELL_PADDING)
    min_size = kwargs.get('min_size', MIN_SIZE)
    max_size = kwargs.get('max_size', MAX_SIZE)
    min_color = kwargs.get('min_color', MIN_COLOR)
    max_color = kwargs.get('max_color', MAX_COLOR)
    title = kwargs.get('title', None)
    font = kwargs.get('font', FONT)
    font_size = kwargs.get('font_size', FONT_SIZE)
    font_bold = kwargs.get('font_bold', FONT_BOLD)
    title_font = kwargs.get('title_font', TITLE_FONT)
    title_font_size = kwargs.get('title_font_size', TITLE_FONT_SIZE)
    title_font_bold = kwargs.get('title_font_bold', TITLE_FONT_BOLD)
    diagonal_column_labels = kwargs.get(
        'diagonal_column_labels', DIAGONAL_COLUMN_LABELS)
    size = max_size + cell_padding * 2
    # measure text
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
    dc = cairo.Context(surface)
    set_font(dc, font, font_size, font_bold)
    row_text_size = max(dc.text_extents(str(x))[2] for x in rows)
    col_text_size = max(dc.text_extents(str(x))[2] for x in cols)
    # generate punchcard
    if diagonal_column_labels:
        width = size * len(cols) + row_text_size + padding * 3 + \
            sin(pi / 4) * col_text_size
        height = size * len(rows) + col_text_size * sin(pi / 4) + padding * 3
    else:
        width = size * len(cols) + row_text_size + padding * 3
        height = size * len(rows) + col_text_size + padding * 3
    if title is not None:
        set_font(dc, title_font, title_font_size, title_font_bold)
        title_size = dc.text_extents(title)[2:4]
        height += title_size[1] + padding
    dx = row_text_size + padding * 2
    if diagonal_column_labels:
        dy = sin(pi / 4) * col_text_size + padding * 2
    else:
        dy = col_text_size + padding * 2
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, int(width), int(height))
    dc = cairo.Context(surface)
    set_font(dc, font, font_size, font_bold)
    dc.set_source_rgb(1, 1, 1)
    dc.paint()
    dc.set_source_rgb(0, 0, 0)
    dc.set_line_width(1)
    # column labels
    for i, col in enumerate(cols):
        col = str(col)
        tw, th = dc.text_extents(col)[2:4]
        x = dx + i * size + size / 2 + th / 2
        if diagonal_column_labels:
            y = padding + sin(pi / 4) * col_text_size
        else:
            y = padding + col_text_size
        dc.save()
        dc.translate(x, y)
        if diagonal_column_labels:
            dc.rotate(-pi / 4)
        else:
            dc.rotate(-pi / 2)
        dc.move_to(0, 0)
        dc.show_text(col)
        dc.restore()
    # row labels
    for j, row in enumerate(rows):
        row = str(row)
        tw, th = dc.text_extents(row)[2:4]
        x = padding + row_text_size - tw
        y = dy + j * size + size / 2 + th / 2
        dc.move_to(x, y)
        dc.show_text(row)
    # grid
    for i, col in enumerate(cols):
        for j, row in enumerate(rows):
            x = dx + i * size
            y = dy + j * size
            dc.rectangle(x, y, size, size)
    dc.stroke()
    # punches
    lo = min(x for row in data for x in row if x)
    hi = max(x for row in data for x in row if x)
    min_area = pi * (min_size / 2.0) ** 2
    max_area = pi * (max_size / 2.0) ** 2
    for i, col in enumerate(cols):
        for j, row in enumerate(rows):
            value = data[j][i]
            if not value:
                continue
            pct = 1.0 * (value - lo) / (hi - lo)
            # pct = pct ** 0.5
            area = pct * (max_area - min_area) + min_area
            radius = (area / pi) ** 0.5
            radius = int(round(radius))
            color = pct * (max_color - min_color) + min_color
            dc.set_source_rgb(color, color, color)
            x = dx + i * size + size / 2
            y = dy + j * size + size / 2
            dc.arc(x, y, radius, 0, 2 * pi)
            dc.fill()
    # title
    if title is not None:
        dc.set_source_rgb(0, 0, 0)
        set_font(dc, title_font, title_font_size, title_font_bold)
        x = dx + size * len(cols) / 2 - title_size[0] / 2
        y = height - padding
        dc.move_to(x, y)
        dc.show_text(title)
    surface.write_to_png(path)

def punchcard_from_csv(csv_path, path, **kwargs):
    with open(csv_path, 'rb') as fp:
        reader = csv.reader(fp)
        csv_rows = list(reader)
    row_labels = [x[0] for x in csv_rows[1:]]
    col_labels = csv_rows[0][1:]
    rows = []
    for csv_row in csv_rows[1:]:
        row = []
        for value in csv_row[1:]:
            try:
                value = float(value)
            except ValueError:
                value = None
            row.append(value)
        rows.append(row)
    punchcard(path, row_labels, col_labels, rows, **kwargs)

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if len(args) == 2:
        punchcard_from_csv(args[0], args[1])
    elif len(args) == 3:
        punchcard_from_csv(args[0], args[1], title=args[2])
    else:
        print 'Usage: python punchcard.py input.csv output.png [title]'
