# -*- coding: utf-8 -*-
#
from .helpers import create_padding_tuple


def _create_alignment(alignment, num_columns):
    if len(alignment) == 1:
        alignment = num_columns * alignment
    return alignment


def _get_border_chars(border_style):
    if border_style is None:
        border_chars = None
    elif len(border_style) == 1:
        border_chars = 11 * [border_style]
    elif isinstance(border_style, list):
        assert len(border_style) == 11
        border_chars = border_style
    else:
        border_chars = {
            "thin": ["─", "│", "┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼"],
            "thin rounded": ["─", "│", "╭", "╮", "╰", "╯", "├", "┤", "┬", "┴", "┼"],
            "thick": ["━", "┃", "┏", "┓", "┗", "┛", "┣", "┫", "┳", "┻", "╋"],
            "double": ["═", "║", "╔", "╗", "╚", "╝", "╠", "╣", "╦", "╩", "╬"],
            "ascii": ["-", "|", "+", "+", "+", "+", "+", "+", "+", "+", "+"],
        }[border_style]

    return border_chars


def _get_column_widths(strings, num_columns):
    column_widths = num_columns * [0]
    for row in strings:
        for j, item in enumerate(row):
            column_widths[j] = max(column_widths[j], len(item))
    return column_widths


def _align(strings, alignments, column_widths):
    for row in strings:
        for k, (item, align, cw) in enumerate(zip(row, alignments, column_widths)):
            rest = cw - len(item)
            if rest <= 0:
                row[k] = item[:cw]
            else:
                if align == "l":
                    left = 0
                elif align == "r":
                    left = rest
                else:
                    assert align == "c"
                    left = rest // 2
                right = rest - left
                row[k] = " " * left + item + " " * right
    return strings


def _add_padding(strings, column_widths, padding):
    for row in strings:
        for k, (item, cw) in enumerate(zip(row, column_widths)):
            s = []
            for _ in range(padding[0]):
                s += [" " * cw]
            s += [" " * padding[3] + item + " " * padding[1]]
            for _ in range(padding[2]):
                s += [" " * cw]
            row[k] = "\n".join(s)
    return strings


def table(data, header=None, alignment="l", border_style="thin", padding=(0, 1)):
    # TODO header

    # Make sure the data is consistent
    num_columns = len(data[0])
    for row in data:
        assert len(row) == num_columns

    padding = create_padding_tuple(padding)
    alignments = _create_alignment(alignment, num_columns)
    border_chars = _get_border_chars(border_style)

    strings = [["{}".format(item) for item in row] for row in data]

    column_widths = _get_column_widths(strings, num_columns)
    column_widths_with_padding = [c + padding[1] + padding[3] for c in column_widths]

    # add spaces according to alignment
    strings = _align(strings, alignments, column_widths)

    # add spaces according to padding
    strings = _add_padding(strings, column_widths, padding)

    # plot the table
    out = []

    out += [
        border_chars[2]
        + border_chars[8].join([s * border_chars[0] for s in column_widths_with_padding])
        + border_chars[3]
    ]

    # collect the subfigure rows
    srows = []
    for row in strings:
        cstrings = [item.split("\n") for item in row]
        max_num_lines = max(len(item) for item in cstrings)
        pp = []
        for k in range(max_num_lines):
            p = []
            for j, cstring in enumerate(cstrings):
                try:
                    s = cstring[k]
                except IndexError:
                    s = ""
                # truncate or extend with spaces to match the column width
                if len(s) >= column_widths_with_padding[j]:
                    s = s[: column_widths_with_padding[j]]
                else:
                    s += " " * (column_widths_with_padding[j] - len(s))
                p.append(s)
            if border_chars:
                join_char = border_chars[1]
            else:
                join_char = ""
            pp.append(join_char + join_char.join(p) + join_char)
        srows.append("\n".join([p.rstrip() for p in pp]))

    if border_chars:
        intermediate_border_row = (
            "\n"
            + border_chars[6]
            + border_chars[10].join([s * border_chars[0] for s in column_widths_with_padding])
            + border_chars[7]
            + "\n"
        )
    else:
        intermediate_border_row = "\n"

    # TODO First join, then split. There must be a better way
    out += intermediate_border_row.join(srows).split("\n")

    if border_chars:
        # final row
        out += [
            border_chars[4]
            + border_chars[9].join([s * border_chars[0] for s in column_widths_with_padding])
            + border_chars[5]
        ]

    return [s.rstrip() for s in out]
