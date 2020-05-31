#!/bin/python3

import sys
import io
import os
import re
import argparse
from collections import deque, defaultdict


def _make_file_name(file_name: str):
    """util func for creating file name, which related to original file name"""
    return file_name.split('/')[-1][:-4] + '_edited.pgn'


def _get_moves_from_game(pgn: str) -> list:
    """
    Retrieve moves from pgn, clean moves number and NAG tags (move commentary from pgn specification), split it to
     list and clean

    Args:
        pgn: chess game in pgn format

    Returns:
        list: retrieved moves from pgn game as list
    """
    moves = ''
    for line in io.StringIO(pgn):
        if not bool(re.search(re.compile(r'\[.*\".*\"\]'), line)) or line == '\n':
            moves += line
    moves = re.sub(r'\)', ' )', moves)
    moves = re.sub(r'\$\d+ |\d+\.\.\.|\d+\.|\$\d+', '', moves).split()[:-1]

    return moves


def clean_pgn(source_file: str) -> list:
    """removes text commentary from games in pgn file

    Args:
        source_file (str): path to pgn file

    Returns:
        list: list of chess games from source file
    """

    games = []
    with open(source_file) as f:
        for game in re.findall(r'(?s)\[.*?(?:\*|1-0|1/2-1/2|0-1)[^\"]', f.read()):
            cleaned_game = ''
            is_comment = False
            for ch in game:
                if ch in '{}':
                    is_comment = {'{': True, '}': False}[ch]
                elif not is_comment:
                    cleaned_game += ch
            games.append(cleaned_game)
    print(f'\033[94mFound {len(games)} games')

    return games


def split_game_to_lines(game: str) -> list:
    """
    split pgn game moves to separate move lines

    Args:
        game (str): pgn game with variations in it

    Returns:
        list: all game variations as list

    Examples:
        >>> split_game_to_lines('1. Nf3 ( 1. e4 c5 ) c5 ( b6 2. d4 ) ')
        >>> [['Nf3', 'c5'], ['Nf3', 'b6', 'd4'], ['e4', 'c5']]
    """

    moves = _get_moves_from_game(game)

    stack = deque()
    res = []
    move_stack = []
    for move in moves:
        if move in "()":
            if move == "(":
                stack.append(move_stack.copy())
                move_stack = move_stack[:-1]
            elif move == ")":
                res.append(move_stack)
                move_stack = stack.pop()
            continue
        else:
            move_stack.append(move)
    res.append(move_stack)

    return res[::-1]


def merge_lines(move_lines: list) -> str:
    """
    merge list of lines to pgn-like moves notation with variants

    Args:
        move_lines (list): list of lists with move lines

    Returns:
        str: pgn formatted moves

    Examples:
        >>> merge_lines([['Nf3', 'c5'], ['Nf3', 'b6', 'd4'], ['e4', 'c5']])
        >>> '1. Nf3 ( 1. e4 c5 ) c5 ( b6 2. d4 )'
    """

    tree = dict(root=dict())
    for moves in move_lines:
        curr_node = tree['root']
        for move in moves:
            if move not in curr_node.keys():
                curr_node[move] = dict()
            curr_node = curr_node[move]
    pgn = ''

    def pgn_maker(_tree, move_count=0, odd=True):
        keys_len = len(_tree.keys())
        if keys_len == 0:
            return
        nonlocal pgn
        main_move = list(_tree.keys())[0]
        if odd:
            move_count += 1

        pgn += ((str(move_count) + '. ') if odd else '') + main_move + ' '
        odd = not odd
        if keys_len > 1:
            for k, v in list(x for x in _tree.items())[1:]:
                pgn += '( ' + (f'{move_count}... ' if odd else '')
                pgn_maker({k: v}, move_count - (not odd), not odd)
                pgn += ') '
        pgn_maker(_tree[main_move], move_count, odd)

    pgn_maker(tree['root'])

    return pgn


def process_pgn(source_file: str, splitter: str = 'w', dest_file: str = None):
    """
    all-in-one. Clean pgn, and merge specified games into chapters and write to result file

    Args:
        source_file (str): source file
        splitter (str): rules to split file:
            'w' - group by white player and merge,
            'b' - group by black player and merge,
            'a' - merge all games in file,
            custom: string with numbers separated with ':' where number is how much games in a row will be merged
                into one chapter, each number produce new chapter in result file.
                e.g.: '5:2:4' is 3 chapters with 5, 2 and 4 games merged, rest of the games will be ignored.
        dest_file (str): destination file name

    Returns:
        None: create pgn file in result folder, without text commentary, and merged games depending on splitter rule
    """

    dest_file = dest_file if dest_file else _make_file_name(source_file)

    res = []

    cleaned_games = clean_pgn(source_file)
    cleaned_grouped_games = []

    if splitter and splitter.lower() not in 'wb':
        splitter = [len(cleaned_games)] if splitter.lower() == 'a' else list(map(int, splitter.split(':')))
        i = 0
        for j in splitter:
            cleaned_grouped_games.append(cleaned_games[i:i + j])
            i += j
    elif splitter:
        games_by_player = defaultdict(list)
        pattern = re.compile({'w': r'\[White \"(.*)\"\]', 'b': r'\[Black \"(.*)\"\]'}.get(splitter))

        for game in cleaned_games:
            games_by_player[re.findall(pattern, game)[0].strip()].append(game)

        for games in games_by_player.values():
            cleaned_grouped_games.append(games)

    # dir_name = 'result'
    # if not os.path.isdir(dir_name) and write_to_file:
    #     os.mkdir(dir_name)
    #
    # if write_to_file:
    #     with open(os.path.join(dir_name, _make_file_name(source_file)), 'w') as f:
    #         f.write(''.join(games))
    #
    # if write_to_file and splitter:
    #     c = 1
    #     for chapter in games:
    #         with open(os.path.join(dir_name, f'Chapter {c}.pgn'), 'w') as f:
    #             f.write(''.join(chapter))
    #         c += 1

    for games in cleaned_grouped_games:
        tmp = []
        for game in games:
            tmp += split_game_to_lines(game)
        res.append(merge_lines(tmp))

    with open(dest_file, 'w') as f:
        chapter = 1
        for game in res:
            header = '[Event "?"]\r\n'
            header += '[Site "?"]\r\n'
            header += '[Date "????.??.??"]\r\n'
            header += '[Round "?"]\r\n'
            header += '[White "Chapter {}"]\r\n'.format(chapter)
            header += '[Black "?"]\r\n'
            header += '[Result "*"]\r\n'

            f.write(header + '\r\n' + game + ' *\r\n\r\n')
            chapter += 1
    print(f'Successfully merged into {len(res)} chapters\nresult file: {dest_file}\033[0m')


if __name__ == '__main__':
    # print("PGN-utils.")
    print('\033[95m')
    parser = argparse.ArgumentParser(add_help=True, description="Clean or merge your chess games")

    parser.add_argument('filename', action='store', metavar="pathname",
                        help='path to your pgn file')
    parser.add_argument(
        'splitter', action='store', nargs='?', default='w',
        help="rules to split file:"
             "'w' - group games by white player and merge,"
             "'b' - group games by black player and merge,"
             "'a' - merge all games in file,"
             "custom: string with numbers separated with ':' where number is how much games in a row will be merged"
             "into one chapter, each number produce new chapter in result file."
             "e.g.: '5:2:4' is 3 chapters with 5, 2 and 4 games merged, rest of the games will be ignored.")
    parser.add_argument('-o', action='store', metavar="pathname",
                        help='destination file name. default: [your_file_name]_edited.pgn')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    options = parser.parse_args()
    process_pgn(options.filename, options.splitter, options.o)
