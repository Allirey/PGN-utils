#!/bin/python3

import io
import os
import re
import argparse
from collections import deque, defaultdict
from pprint import pprint


def _make_file_name(file_name: str):
    """util func for creating file name, which related to original file name"""
    return file_name.split('/')[-1].rstrip('.pgn') + '_edited.pgn'


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


def clean_pgn(pgn_file: str, splitter: str = None, write_to_file: bool = False) -> list:
    """removes text commentary from file, can split files by player name or by specific games number in db pgn file
    additionally return as text pgn file or as list of lists with games

    Args:
        pgn_file (str): path to pgn file
        splitter (str): rules to split file:
            'w' - group by white player and merge,
            'b' - group by black player and merge,
            'a' - merge all games in file,
            custom: string with numbers separated with ':' where number is how much games in a row will be merged
                into one chapter, each number produce new chapter in result file.
                e.g.: '5:2:4' is 3 chapters with 5, 2 and 4 games merged, rest of the games will be ignored.
        write_to_file (bool): if True -> writes result into file(-s)

    Returns:
        list: pgn file as string if splitter not specified, else it return list of lists with games related to
        the same chapter, which specified by splitter

    Notes:
        returns list of lists(!) with games, even if there is only 1 game it looks like this:
        >>> [["...some game content...", ], ]
    """
    splitter_games_number = 0
    if splitter and splitter.lower() not in 'wb':
        try:
            splitter_games_number = splitter if not splitter else sum(list(map(int, splitter.split(':'))))
        except Exception as e:
            raise Exception('incorrect splitter data! should be list of number')

    games = []
    game = ''

    pattern = re.compile(r'\[.*\".*\"\]')
    with open(pgn_file) as src:
        is_header = False
        is_commentary = False
        for line in src:
            if bool(re.search(pattern, line)):
                if not is_header and len(game) > 0 and len(''.join(game.split('\n'))) > 0:
                    games.append(game)
                    game = ''
                is_header = True
                game += line
            elif line == '\n':
                game += line
                is_header = False
            else:
                cleaned_line = ''
                for ch in line:
                    if ch in '{}':
                        is_commentary = {'{': True, '}': False}[ch]
                        continue
                    if not is_commentary:
                        cleaned_line += ch
                game += cleaned_line.lstrip()

        if len(game) > 0 and len(''.join(game.split('\n'))) > 0:
            games.append(game)

    if len(games) < splitter_games_number:
        raise Exception("Games if file less than specified in splitter!")

    result = []

    if splitter and splitter.lower() not in 'wb':
        i = 0
        for j in list(map(int, splitter.split(':'))):
            result.append(games[i:i + j])
            i += j
    elif splitter:
        games_by_player = defaultdict(list)
        pattern = re.compile({'w': r'\[White \"(.*)\"\]', 'b': r'\[Black \"(.*)\"\]'}.get(splitter))

        for game in games:
            games_by_player[re.findall(pattern, game)[0].strip()].append(game)
            # print(re.findall(pattern, game)[0].strip())

        for games in games_by_player.values():
            result.append(games)

    dir_name = 'result'
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    if write_to_file:
        with open(os.path.join(dir_name, _make_file_name(pgn_file)), 'w') as f:
            f.write(''.join(games))

    if write_to_file and splitter:
        c = 1
        for chapter in games:
            with open(os.path.join(dir_name, f'Chapter {c}.pgn'), 'w') as f:
                f.write(''.join(chapter))
            c += 1
    return result


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

    # for variant in res:
    # print(variant)

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

    def pgn_maker(tree, move_count=0, odd=True):
        keys_len = len(tree.keys())
        if keys_len == 0:
            return
        nonlocal pgn
        main_move = list(tree.keys())[0]
        if odd:
            move_count += 1

        pgn += ((str(move_count) + '. ') if odd else '') + main_move + ' '
        odd = not odd
        if keys_len > 1:
            for k, v in list(x for x in tree.items())[1:]:
                pgn += '( '
                pgn_maker({k: v}, move_count - 1, not odd)
                pgn += ') '
        pgn_maker(tree[main_move], move_count, odd)

    pgn_maker(tree['root'])

    return pgn


def process_pgn(file_name, splitter='w', dest_file=None):
    """
    all-in-one. Clean pgn, split it into separate files with given numbers of games in each, merge games in each files,
    and write merged games as chapters to result file

    Args:
        file_name (str): source file
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

    dest_file = dest_file if dest_file else _make_file_name(file_name)

    res = []
    for games in clean_pgn(file_name, splitter):
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

            f.write(header + '\r\n' + game + '  *  \r\n\r\n')
            chapter += 1


if __name__ == '__main__':
    pass
