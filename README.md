## Punchcard

Generate GitHub-style punchcard charts with ease. Uses pycairo for rendering.

### Command Line

    python punchcard.py input.csv output.png [title]

### Programmatically

    punchcard(png_path, row_labels, col_labels, data)

`data` must be a two-dimensional array of data for the punchcard chart (a list of lists where each list is a row). `len(data) == len(row_labels)` and `len(data[0]) == len(col_labels)`

### Sample

![Sample](http://i.imgur.com/34wPmmB.png)
