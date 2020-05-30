# Chess PGN file cleaner / merger
##### Removes text commentary and merge games in file specified by rules

### Usage:
```
usage: pgn_utils.py [-h] [-o pathname] pathname splitter

positional arguments:
  pathname     path to your pgn file
  splitter     rules to split file:
                'w' - group games by white player and merge,
                'b' - group games by black player and merge,
                'a' - merge all games in file,
                custom: string with numbers separated with ':' where number is how much games 
                    in a row will be merged into one chapter, each number produce new chapter 
                    in result file.e.g.: '5:2:4' is 3 chapters with 5, 2 and 4 games merged,
                    rest of the games will be ignored.

optional arguments:
  -h, --help   show this help message and exit
  -o pathname  destination file name. default: [your_file_name]_edited.pgn
```


### Example:
###### some_pgn_file.pgn
```
﻿[Event "London knockout"]
[Site "London"]
[Date "1851.??.??"]
[Round "3.5"]
[White "Anderssen, Adolf"]
[Black "Staunton, Howard"]
[Result "1-0"]

1. e4 e6 2. d4 g6 3. Bd3 Bg7 4. Be3 c5 5. c3 cxd4 6. cxd4 Qb6 $6 {Winning a
pawn, but loosing time.} 7. Ne2 Qxb2 $6 8. Nbc3 Qb6 {White has developed all
his minor pieces.} 9. Rc1 Na6 10. Nb5 Bf8 $2 {Protecting the square d6, but
Black's pieces are completly misplaced.} (10... d6 $142) 11. O-O d6 1-0

[Event "World Cup"]
[Site "Reykjavik"]
[Date "1991.??.??"]
[Round "1"]
[White "Karpov, Anatoly"]
[Black "Speelman, Jonathan S"]
[Result "1-0"]
[WhiteElo "2730"]
[BlackElo "2630"]

1. e4 e6 2. d4 d5 3. Nd2 dxe4 4. Nxe4 Nd7 5. Nf3 Ngf6 6. Nxf6+ Nxf6 7. Bd3 c5
8. dxc5 Bxc5 9. Qe2 O-O $6 (9... Qc7 {is known to be safer.}) 10. Bg5 Qa5+ 1-0
```

###### now we can merge all games of this files with:
```
python3 pgn_utils.py some_pgn_file.pgn a
```

###### RESULT:
###### some_pgn_file_edited.pgn
```
[Event "?"]
[Site "?"]
[Date "????.??.??"]
[Round "?"]
[White "Chapter 1"]
[Black "?"]
[Result "*"]

1. e4 e6 2. d4 g6 ( d5 3. Nd2 dxe4 4. Nxe4 Nd7 5. Nf3 Ngf6 6. Nxf6+ Nxf6 7. Bd3 c5 8. dxc5 Bxc5 9. Qe2 O-O ( Qc7 ) 10. Bg5 Qa5+ ) 3. Bd3 Bg7 4. Be3 c5 5. c3 cxd4 6. cxd4 Qb6 7. Ne2 Qxb2 8. Nbc3 Qb6 9. Rc1 Na6 10. Nb5 Bf8 ( d6 ) 11. O-O d6   *  

```


## TODO:

* option to keep NAG tags (marks for moves such as "!" or "!?")

##### Note:
Keep in mind: Merges affects only on __games__ in single file. It is NOT that program which merge multiple pgn __files__ in one. For such feature you can write your own program, just type in command line:

for windows: \
`
type *.pgn > result.pgn
`

for linux: \
`
cat *.pgn > result.pgn
`
###### congratulations! now you are programmer...
