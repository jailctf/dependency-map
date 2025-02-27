# cpython modules dependency map

work in progress

## what

ways to get from each python module to other python modules and by what means

## why

if we are in module A and we want to get module B on python version 3.X.X, we can get all of the paths and determine which one is ideal to use for a pyjail escape based on what is needed

## todo

- go into nested folders of cpython/Lib (handle os.path properly)
- better-er graph
- fix zoom button if you get lost
- toggle for keeping non-root level deps in graph
- fix non-root level deps (try-catch) detection
- cache node positions so you dont have to do the animation again
- click on button for whatever.py ref to select the node
- api? idk what this would entail
- easy script to run to get module dependencies for non-builtin module
- deep mode

