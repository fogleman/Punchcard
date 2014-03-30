from math import pi, sin
import csv
import cairo
import pango
import pangocairo
import sizers

DEFAULTS = {
    'padding': 12,
    'cell_padding': 4,
    'min_size': 4,
    'max_size': 32,
    'min_color': 0.8,
    'max_color': 0.0,
    'font': 'Helvetica',
    'font_size': 14,
    'font_bold': False,
    'title': None,
    'title_font': 'Helvetica',
    'title_font_size': 20,
    'title_font_bold': True,
    'diagonal_column_labels': False,
}

class Text(object):
    def __init__(self, dc=None):
        self.dc = dc or cairo.Context(
            cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1))
        self.pc = pangocairo.CairoContext(self.dc)
        self.layout = self.pc.create_layout()
    def set_font(self, name, size, bold):
        weight = ' bold ' if bold else ' '
        fd = pango.FontDescription('%s%s%d' % (name, weight, size))
        self.layout.set_font_description(fd)
    def measure(self, text):
        self.layout.set_text(str(text))
        return self.layout.get_pixel_size()
    def render(self, text):
        self.layout.set_text(str(text))
        self.pc.update_layout(self.layout)
        self.pc.show_layout(self.layout)

class ColLabels(sizers.Box):
    def __init__(self, model):
        super(ColLabels, self).__init__()
        self.model = model
    def get_min_size(self):
        if self.model.col_labels is None:
            return (0, 0)
        text = Text()
        text.set_font(
            self.model.font, self.model.font_size, self.model.font_bold)
        width = self.model.width
        height = 0
        for i, col in enumerate(self.model.col_labels):
            tw, th = text.measure(col)
            if self.model.diagonal_column_labels:
                x = i * self.model.cell_size + th / 2
                w = (tw + th / 2) * sin(pi / 4)
                width = max(width, x + w)
                height = max(height, w)
            else:
                height = max(height, tw)
        return (width, height)
    def render(self, dc):
        if self.model.col_labels is None:
            return
        dc.set_source_rgb(0, 0, 0)
        text = Text(dc)
        text.set_font(
            self.model.font, self.model.font_size, self.model.font_bold)
        for i, col in enumerate(self.model.col_labels):
            tw, th = text.measure(col)
            x = self.x + i * self.model.cell_size + th / 2
            y = self.bottom
            dc.save()
            if self.model.diagonal_column_labels:
                dc.translate(x, y - th * sin(pi / 4) / 2)
                dc.rotate(-pi / 4)
            else:
                dc.translate(x, y)
                dc.rotate(-pi / 2)
            dc.move_to(0, 0)
            text.render(col)
            dc.restore()

class RowLabels(sizers.Box):
    def __init__(self, model):
        super(RowLabels, self).__init__()
        self.model = model
    def get_min_size(self):
        if self.model.row_labels is None:
            return (0, 0)
        text = Text()
        text.set_font(
            self.model.font, self.model.font_size, self.model.font_bold)
        width = max(text.measure(x)[0] for x in self.model.row_labels)
        height = self.model.height
        return (width, height)
    def render(self, dc):
        if self.model.row_labels is None:
            return
        dc.set_source_rgb(0, 0, 0)
        text = Text(dc)
        text.set_font(
            self.model.font, self.model.font_size, self.model.font_bold)
        for i, row in enumerate(self.model.row_labels):
            tw, th = text.measure(row)
            x = self.right - tw
            y = self.y + i * self.model.cell_size + th / 2
            dc.move_to(x, y)
            text.render(row)

class Chart(sizers.Box):
    def __init__(self, model):
        super(Chart, self).__init__()
        self.model = model
    def get_min_size(self):
        return (self.model.width, self.model.height)
    def render(self, dc):
        self.render_grid(dc)
        self.render_punches(dc)
    def render_grid(self, dc):
        size = self.model.cell_size
        dc.set_source_rgb(0.5, 0.5, 0.5)
        dc.set_line_width(1)
        for i in range(self.model.cols):
            for j in range(self.model.rows):
                x = self.x + i * size - 0.5
                y = self.y + j * size - 0.5
                dc.rectangle(x, y, size, size)
        dc.stroke()
        dc.set_source_rgb(0, 0, 0)
        dc.set_line_width(3)
        width, height = self.get_min_size()
        dc.rectangle(self.x - 0.5, self.y - 0.5, width, height)
        dc.stroke()
    def render_punches(self, dc):
        data = self.model.data
        size = self.model.cell_size
        lo = min(x for row in data for x in row if x)
        hi = max(x for row in data for x in row if x)
        min_area = pi * (self.model.min_size / 2.0) ** 2
        max_area = pi * (self.model.max_size / 2.0) ** 2
        min_color = self.model.min_color
        max_color = self.model.max_color
        for i in range(self.model.cols):
            for j in range(self.model.rows):
                value = data[j][i]
                if not value:
                    continue
                pct = 1.0 * (value - lo) / (hi - lo)
                # pct = pct ** 0.5
                area = pct * (max_area - min_area) + min_area
                radius = (area / pi) ** 0.5
                color = pct * (max_color - min_color) + min_color
                dc.set_source_rgb(color, color, color)
                x = self.x + i * size + size / 2 - 0.5
                y = self.y + j * size + size / 2 - 0.5
                dc.arc(x, y, radius, 0, 2 * pi)
                dc.fill()

class Title(sizers.Box):
    def __init__(self, model):
        super(Title, self).__init__()
        self.model = model
    def get_min_size(self):
        if self.model.title is None:
            return (0, 0)
        text = Text()
        text.set_font(
            self.model.title_font, self.model.title_font_size,
            self.model.title_font_bold)
        return text.measure(self.model.title)
    def render(self, dc):
        if self.model.title is None:
            return
        dc.set_source_rgb(0, 0, 0)
        text = Text(dc)
        text.set_font(
            self.model.title_font, self.model.title_font_size,
            self.model.title_font_bold)
        tw, th = text.measure(self.model.title)
        x = max(self.x, self.x + self.model.width / 2 - tw / 2)
        y = self.cy - th / 2
        dc.move_to(x, y)
        text.render(self.model.title)

class Model(object):
    def __init__(self, data, row_labels=None, col_labels=None, **kwargs):
        self.data = data
        self.row_labels = row_labels
        self.col_labels = col_labels
        for key, value in DEFAULTS.items():
            value = kwargs.get(key, value)
            setattr(self, key, value)
        self.cell_size = self.max_size + self.cell_padding * 2
        self.rows = len(self.data)
        self.cols = len(self.data[0])
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
    def render(self):
        col_labels = ColLabels(self)
        row_labels = RowLabels(self)
        chart = Chart(self)
        title = Title(self)
        grid = sizers.GridSizer(3, 2, self.padding, self.padding)
        grid.add_spacer()
        grid.add(col_labels)
        grid.add(row_labels)
        grid.add(chart)
        grid.add_spacer()
        grid.add(title)
        sizer = sizers.VerticalSizer()
        sizer.add(grid, border=self.padding)
        sizer.fit()
        surface = cairo.ImageSurface(
            cairo.FORMAT_RGB24, int(sizer.width), int(sizer.height))
        dc = cairo.Context(surface)
        dc.set_source_rgb(1, 1, 1)
        dc.paint()
        col_labels.render(dc)
        row_labels.render(dc)
        chart.render(dc)
        title.render(dc)
        return surface

def punchcard(path, data, row_labels, col_labels, **kwargs):
    model = Model(data, row_labels, col_labels, **kwargs)
    surface = model.render()
    surface.write_to_png(path)

def punchcard_from_csv(csv_path, path, **kwargs):
    with open(csv_path, 'rb') as fp:
        reader = csv.reader(fp)
        csv_rows = list(reader)
    row_labels = [x[0] for x in csv_rows[1:]]
    col_labels = csv_rows[0][1:]
    data = []
    for csv_row in csv_rows[1:]:
        row = []
        for value in csv_row[1:]:
            try:
                value = float(value)
            except ValueError:
                value = None
            row.append(value)
        data.append(row)
    punchcard(path, data, row_labels, col_labels, **kwargs)

if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if len(args) == 2:
        punchcard_from_csv(args[0], args[1])
    elif len(args) == 3:
        punchcard_from_csv(args[0], args[1], title=args[2])
    else:
        print 'Usage: python punchcard.py input.csv output.png [title]'
