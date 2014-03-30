from itertools import product

# Orientation
HORIZONTAL = 1
VERTICAL = 2

# Alignment
NONE = 0
LEFT = 1
RIGHT = 2
TOP = 3
BOTTOM = 4
CENTER = 5

def unpack_border(border):
    try:
        l, t, r, b = border
        return (l, t, r, b)
    except Exception:
        pass
    try:
        x, y = border
        return (x, y, x, y)
    except Exception:
        pass
    n = border
    return (n, n, n, n)

class Target(object):
    def get_min_size(self):
        raise NotImplementedError
    def get_dimensions(self):
        raise NotImplementedError
    def set_dimensions(self, x, y, width, height):
        raise NotImplementedError
    x = l = left = property(lambda self: self.get_dimensions()[0])
    y = t = top = property(lambda self: self.get_dimensions()[1])
    w = width = property(lambda self: self.get_dimensions()[2])
    h = height = property(lambda self: self.get_dimensions()[3])
    r = right = property(lambda self: self.x + self.w)
    b = bottom = property(lambda self: self.y + self.h)
    cx = property(lambda self: self.x + self.w / 2)
    cy = property(lambda self: self.y + self.h / 2)

class Box(Target):
    def __init__(self, width=0, height=0):
        self.min_size = (width, height)
        self.dimensions = (0, 0, width, height)
    def get_min_size(self):
        return self.min_size
    def get_dimensions(self):
        return self.dimensions
    def set_dimensions(self, x, y, width, height):
        self.dimensions = (x, y, width, height)

class SizerItem(object):
    def __init__(self, target, proportion, expand, border, align):
        self.target = target
        self.proportion = proportion
        self.expand = expand
        self.border = unpack_border(border)
        self.align = align
    def get_min_size(self):
        l, t, r, b = self.border
        width, height = self.target.get_min_size()
        width = width + l + r
        height = height + t + b
        return (width, height)
    def get_dimensions(self):
        return self.target.get_dimensions()
    def set_dimensions(self, x, y, width, height):
        l, t, r, b = self.border
        lr, tb = l + r, t + b
        self.target.set_dimensions(x + l, y + t, width - lr, height - tb)

class Sizer(Target):
    def __init__(self):
        self.items = []
        self.dimensions = (0, 0, 0, 0)
    def add(self, target, proportion=0, expand=False, border=0, align=NONE):
        item = SizerItem(target, proportion, expand, border, align)
        self.items.append(item)
    def add_spacer(self, size=0):
        spacer = Box(size, size)
        self.add(spacer)
    def add_stretch_spacer(self, proportion=1):
        spacer = Box()
        self.add(spacer, proportion)
    def get_dimensions(self):
        return self.dimensions
    def set_dimensions(self, x, y, width, height):
        min_width, min_height = self.get_min_size()
        width = max(min_width, width)
        height = max(min_height, height)
        self.dimensions = (x, y, width, height)
        self.layout()
    def fit(self):
        width, height = self.get_min_size()
        self.set_dimensions(0, 0, width, height)
    def get_min_size(self):
        raise NotImplementedError
    def layout(self):
        raise NotImplementedError

class BoxSizer(Sizer):
    def __init__(self, orientation):
        super(BoxSizer, self).__init__()
        self.orientation = orientation
    def get_min_size(self):
        width = 0
        height = 0
        for item in self.items:
            w, h = item.get_min_size()
            if self.orientation == HORIZONTAL:
                width += w
                height = max(height, h)
            else:
                width = max(width, w)
                height += h
        return (width, height)
    def layout(self):
        x, y = self.x, self.y
        width, height = self.width, self.height
        min_width, min_height = self.get_min_size()
        extra_width = max(0, width - min_width)
        extra_height = max(0, height - min_height)
        total_proportions = float(sum(item.proportion for item in self.items))
        if self.orientation == HORIZONTAL:
            for item in self.items:
                w, h = item.get_min_size()
                if item.expand:
                    h = height
                if item.proportion:
                    p = item.proportion / total_proportions
                    w += int(extra_width * p)
                if item.align == CENTER:
                    offset = height / 2 - h / 2
                    item.set_dimensions(x, y + offset, w, h)
                elif item.align == BOTTOM:
                    item.set_dimensions(x, y + height - h, w, h)
                else: # TOP
                    item.set_dimensions(x, y, w, h)
                x += w
        else:
            for item in self.items:
                w, h = item.get_min_size()
                if item.expand:
                    w = width
                if item.proportion:
                    p = item.proportion / total_proportions
                    h += int(extra_height * p)
                if item.align == CENTER:
                    offset = width / 2 - w / 2
                    item.set_dimensions(x + offset, y, w, h)
                elif item.align == RIGHT:
                    item.set_dimensions(x + width - w, y, w, h)
                else: # LEFT
                    item.set_dimensions(x, y, w, h)
                y += h

class HorizontalSizer(BoxSizer):
    def __init__(self):
        super(HorizontalSizer, self).__init__(HORIZONTAL)

class VerticalSizer(BoxSizer):
    def __init__(self):
        super(VerticalSizer, self).__init__(VERTICAL)

class GridSizer(Sizer):
    def __init__(self, rows, cols, row_spacing=0, col_spacing=0):
        super(GridSizer, self).__init__()
        self.rows = rows
        self.cols = cols
        self.row_spacing = row_spacing
        self.col_spacing = col_spacing
        self.row_proportions = {}
        self.col_proportions = {}
    def set_row_proportion(self, row, proportion):
        self.row_proportions[row] = proportion
    def set_col_proportion(self, col, proportion):
        self.col_proportions[col] = proportion
    def get_rows_cols(self):
        rows, cols = self.rows, self.cols
        count = len(self.items)
        if rows <= 0:
            rows = count / cols + int(bool(count % cols))
        if cols <= 0:
            cols = count / rows + int(bool(count % rows))
        return (rows, cols)
    def get_row_col_sizes(self):
        rows, cols = self.get_rows_cols()
        row_heights = [0] * rows
        col_widths = [0] * cols
        positions = product(range(rows), range(cols))
        for item, (row, col) in zip(self.items, positions):
            w, h = item.get_min_size()
            row_heights[row] = max(h, row_heights[row])
            col_widths[col] = max(w, col_widths[col])
        return row_heights, col_widths
    def get_min_size(self):
        row_heights, col_widths = self.get_row_col_sizes()
        width = sum(col_widths) + self.col_spacing * (len(col_widths) - 1)
        height = sum(row_heights) + self.row_spacing * (len(row_heights) - 1)
        return (width, height)
    def layout(self):
        row_spacing, col_spacing = self.row_spacing, self.col_spacing
        min_width, min_height = self.get_min_size()
        extra_width = max(0, self.width - min_width)
        extra_height = max(0, self.height - min_height)
        rows, cols = self.get_rows_cols()
        row_proportions = [
            self.row_proportions.get(row, 0) for row in range(rows)]
        col_proportions = [
            self.col_proportions.get(col, 0) for col in range(cols)]
        total_row_proportions = float(sum(row_proportions))
        total_col_proportions = float(sum(col_proportions))
        row_heights, col_widths = self.get_row_col_sizes()
        for row, proportion in enumerate(row_proportions):
            if proportion:
                p = proportion / total_row_proportions
                row_heights[row] += int(extra_height * p)
        for col, proportion in enumerate(col_proportions):
            if proportion:
                p = proportion / total_col_proportions
                col_widths[col] += int(extra_width * p)
        row_y = [sum(row_heights[:i]) + row_spacing * i for i in range(rows)]
        col_x = [sum(col_widths[:i]) + col_spacing * i for i in range(cols)]
        positions = product(range(rows), range(cols))
        for item, (row, col) in zip(self.items, positions):
            x, y = self.x + col_x[col], self.y + row_y[row]
            w, h = col_widths[col], row_heights[row]
            item.set_dimensions(x, y, w, h)

def main():
    a = Box(10, 10)
    b = Box(25, 25)
    c = Box(50, 10)
    # sizer = VerticalSizer()
    sizer = GridSizer(2, 2)
    sizer.add(a)
    sizer.add(b)
    sizer.add(c)
    sizer.fit()
    print a.dimensions
    print b.dimensions
    print c.dimensions

if __name__ == '__main__':
    main()
