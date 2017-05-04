"""
Solution utils
"""

def cross(a, b):
    """
    Cross product of elements in A and elements in B.
    :param a: string
    :param b: string
    :return: [string]
    """
    return [s+t for s in a for t in b]

def alternate(a,b):
    """
    Alternates characters from a with b e.g.: a=abc. b=123 => a1b2c3
    :param a: string
    :param b: string
    :return: [string]
    """
    return [a[i]+b[i] for i in range(len(a))]

def assign_value(values, box, value):
    """
    Assigns a value to a given box. If it updates the board record it.
    :param values: dict
    :param box: string
    :param value: string
    :return: dict
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """
    Eliminate values using the naked twins strategy. 
    :param values: dict
    :return: dict
    """
    # Find all instances of naked twins, remove duplicates
    n_t = set(tuple(p) for p in [sorted([t_k, k]) for k in values if len(values[k]) == 2 for t_k in peers[k] if len(values[t_k]) == 2 and values[t_k] == values[k]])
    for twin_pair in n_t:
        index = twin_pair[0]
        twin_values = values[index]
        # finds all units that have both twin keys and flattens them into a single list
        unit = [u for unit in units[index] for u in unit if twin_pair[1] in unit]
        for k in unit:
            box_values = values[k]
            if len(box_values) >= 2 and box_values != twin_values:
                table = str.maketrans(dict.fromkeys(twin_values))
                # eliminates using naked twins
                box_values = box_values.translate(table)
                assign_value(values, k, box_values)
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    :param grid: string
    :return: dict
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
    :param values: dict
    :return: 
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)

def eliminate(values):
    """
    Eliminates duplicated values from box's peers
    :param values: dict
    :return: dict
    """
    for key in values.keys():
        if len(values[key]) == 1:
            eliminate = values[key]
            for peer_key in peers[key]:
                assign_value(values, peer_key, values[peer_key].replace(eliminate, ''))
    return values

def only_choice(values):
    """
    If there is only one box in a unit which would allow a certain digit, then that box must be assigned that digit.
    :param values: dict
    :return: dict
    """
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
    """
    Applies only choice, elminate and naked_twins until sudoku is can no longer be reduced.
    :param values: dict 
    :return: dict
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = only_choice(naked_twins(eliminate(values)))
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Uses depth first search to solve sudoku
    :param values: dict
    :return: dict
    """
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
    Find the solution to a Sudoku grid. Returns the dictionary representation of the final sudoku grid. False if no solution exists.
    :param grid: string 
    :return: dict || false
    """
    # create values dict
    values = grid_values(grid)
    # reduce values dict as much as possible unsing constraint propagation
    values = reduce_puzzle(values)
    # if all else fails use depth first approach
    values = search(values)
    return values

if __name__ == '__main__':

    # for use with pygame
    assignments = []

    # row elements
    rows = 'ABCDEFGHI'
    # col elements
    cols = '123456789'
    # boxes keys
    boxes = cross(rows, cols)
    # row unit key list
    row_units = [cross(r, cols) for r in rows]
    # column unit key list
    column_units = [cross(rows, c) for c in cols]
    # square unit key list
    square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
    # diagonal unit key list
    diagonal_units = [alternate(rows, cols)] + [alternate(''.join(sorted(rows, reverse=True)), cols)]
    # all our units as lists of list
    unitlist = row_units + column_units + square_units + diagonal_units
    # all the units for each box as a dict; accessible through box's key
    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    # all the peers for each box
    peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)

    # unsolved sudoku grid
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    # prints solved sudoku
    display(solve(diag_sudoku_grid))

    # visualization
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue.')

