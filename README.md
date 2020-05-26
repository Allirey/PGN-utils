# Chess PGN file cleaner / merger (Beta)
##### Removes text commentary and merge games in file specified by rules

### Usage:
```
usage: pgn_utils.py [-h] [-o pathname] pathname splitter

positional arguments:
  pathname     path to your pgn file
  splitter     rules to split file:
                'w' - group games by white player and merge,
                'b' - group games by black player and merge,
                'a'(not implemented ATM) - merge all games in file,
                custom: string with numbers separated with ':' where number is how much games 
                    in a row will be mergedinto one chapter, each number produce new chapter 
                    in result file.e.g.: '5:2:4' is 3 chapters with 5, 2 and 4 games merged,
                    rest of the games will be ignored.

optional arguments:
  -h, --help   show this help message and exit
  -o pathname  destination file name. default: [your_file_name]_edited.pgn
```


### Example:
in progress

##TODO:

* option to keep NAG tags (marks for moves such as "!" or "!?")
* option to merge games from multiple files (not sure about this, read __Note__ below)

##### Note:
Keep in mind: it is NOT that program which merge multiple pgn __files__ in one, merges affects only on  __games__. For such feature you can write your own program, just type in command line:

for windows: \
`
type *.pgn > result.pgn
`

for linux: \
`
cat *.pgn > result.pgn
`
###### congratulations! now you are programmer...
