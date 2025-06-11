def pretty_terminal_table(rows : list[list], column_names : list,  padding : int = 3, border : str = None, row_prefix = ""):
    column_widths = []
    columns = list(map(list, zip(*rows)))

    for i, column in enumerate(columns):
        width = len(column_names[i])
        for value in column:
            width = max(width, len(str(value)))
        column_widths.append(width)

    table = [column_names]
    for row in rows:
        table.append(row)

    for row in table:
        current_column = 0
        for item in row:
            value = str(item)
            if current_column == 0:
                value = row_prefix + value

            total_padding = column_widths[current_column] - len(str(item))
            if border is None or current_column == len(columns) - 1: #Dont draw border after final column
                total_padding += padding
                print(value + " " * total_padding, end = "")
            else:
                total_padding += padding//2
                print(value + " " * total_padding + border + " " * (padding//2) , end = "")

            current_column += 1
        print()