## Punchcard

Generate GitHub-style punchcard charts with ease.

    python punchcard.py sample.csv output.png "Sample Chart"

![Sample](http://i.imgur.com/I50Rejy.png)

### Dependencies

    brew install py2cairo pango pygtk

### Command Line

    python punchcard.py input.csv output.png [title]

### Programmatically

    punchcard(png_path, data, row_labels, col_labels)

`data` must be a two-dimensional array of data for the punchcard chart (a list of lists where each list is a row). `len(data) == len(row_labels)` and `len(data[0]) == len(col_labels)`

The following keyword arguments are also allowed.

| keyword                | default     | description                                |
|------------------------|------------:|--------------------------------------------|
|padding                 |           12| padding between chart, labels and boundary |
|cell_padding            |            4| padding between circles and cell edges     |
|min_size                |            4| minimum circle size, for smallest value    |
|max_size                |           32| maximum circle size, for largest value     |
|min_color               |          0.8| grayscale value for smallest value         |
|max_color               |          0.0| grayscale value for largest value          |
|font                    |  'Helvetica'| facename used for labels                   |
|font_size               |           14| font size for labels                       |
|font_bold               |        False| bold labels                                |
|title                   |         None| title text, optional                       |
|title_font              |  'Helvetica'| facename used for title                    |
|title_font_size         |           20| font size for title                        |
|title_font_bold         |         True| bold title                                 |
|diagonal_column_labels  |        False| diagonal column labels                     |
