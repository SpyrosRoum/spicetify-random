# spicetify-random
A python script to apply a random spicetify theme from a given list

The only dependency is [spicetify](https://github.com/khanhas/spicetify-cli), you should install it before running this.
By default you should create an options list in ~/.config/spicetify/options.txt with the following format:

theme_name color_scheme=scheme extensions=comma.js,separated.js,list.js

if a theme doesn't have color schemes then you can omit that completely like this:

theme_name extensions=comma.js,separated.js,list.js

same with the extensions:

theme_name color_scheme=scheme 

For example:
```
BIB-Green
DanDrumStone
Kaapi
Dribbblish color_scheme=Gruvbox extensions=dribbblish.js
```
