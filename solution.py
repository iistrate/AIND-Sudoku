assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    """Cross product of elements in A and elements in B."""
    return [s+t for s in a for t in b]

def alternate(a,b):
    return [a[i]+b[i] for i in range(len(a))]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diagonal_units = [alternate(rows, cols)] + [alternate(''.join(sorted(rows, reverse=True)), cols)]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    n_t = [sorted([t_k, k]) for k in values if len(values[k]) == 2 for t_k in peers[k] if len(values[t_k]) == 2 and values[t_k] == values[k]]

    for twin_pair in n_t:
        index = twin_pair[0]
        twin_values = values[index]
        unit = [unit for unit in units[index] if twin_pair[1] in unit][0]
        for k in unit:
            box_values = values[k]
            if k not in twin_pair and len(box_values) > 2:
                table = str.maketrans(dict.fromkeys(twin_values))
                box_values = box_values.translate(table)
                assign_value(values, k, box_values)
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    possibilities = '123456789'
    values = []
    for c in grid:
        if c == '.':
            values.append(possibilities)
        else:
            values.append(c)

    return {boxes[i]: values[i] for i in range(len(grid))}

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    for key in values.keys():
        if len(values[key]) == 1:
            eliminate = values[key]
            for peer_key in peers[key]:
                assign_value(values, peer_key, values[peer_key].replace(eliminate, ''))
    return values

def only_choice(values):
    for unit in unitlist:
        singles = [values[n] for n in unit if len(values[n]) == 1]
        multiples = ''.join([values[n] for n in unit if len(values[n]) > 1])
        uniques = {u for u in multiples if multiples.count(u) == 1 and u not in singles}
        for box_key in unit:
            box_values = values[box_key]
            intersection = uniques.intersection(set(box_values))
            if len(box_values) > 1 and intersection:
                assign_value(values, box_key, ''.join(intersection))

    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = naked_twins(eliminate(only_choice(values)))
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    values = reduce_puzzle(values)

    if not values:
        return False
    if all(len(box) == 1 for box in values.values()):
        return values


    # Choose one of the unfilled squares with the fewest possibilities
    fewest = dict(
        size=9,
        key=None
    )
    for k in values:
        if 1 < len(values[k]) < fewest.get('size'):
            fewest = dict(
                size=len(values[k]),
                key = k
            )

    key = fewest['key']
    posibilities = sorted(set(values[key]))
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for p in posibilities:
        buffer = values.copy()
        buffer[key] = p
        result = search(buffer)
        if result:
            return result

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values = reduce_puzzle(values)
    values = search(values)
    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

