**Moved to [Codeberg](https://codeberg.org/0x4261756D/yugiprice)**

# yugiprice
Python tool to scrape card prices based on a list of card ID's.
Pretty badly multithreaded. (I have no clue how to do this in python)
Also has Tor support as a bad workaround if you or other people sharing your internet connection want to keep browsing Cardmarket while the tool is running.
Extracts price data from [Cardmarket](https://cardmarket.com/en/YuGiOh) based on a card's ID, 
falling back to first getting the name and pack from [Yugipedia](https://yugipedia.com) because cardmarket does not find some cards based on their ID for some strange reason (it is far more common than you think...).
Because mashing together two completely different services that do not have an API for that usecase (as far as I am aware) cannot go wrong the code is quite horrible to read.
I am sure anyone who dares to use this will find many new pretty edgecases (please feel free to open an Issue or even fix it yourself in a PR).

And yes, I know that there is an actual API but I would still need to do the card ID to card 

## Dependencies
* Python3 obviously
* The concurrent.futures library (should be in the standard library of python3)
* The requests library
```bash
pip install requests
```

Optional:
* The requests sub-package socks for tor-support
```bash
pip install requests[socks]
```


## Usage
```bash
# help
python3 getInfos.py [-h]
# normal usage
python3 getInfos.py path/to/your/file [-o path/to/your/output/file]
```
The input file should contain one card id per line, if multiple versions of a card exist in the same pack add *-\<version index\>*(see cardmarket's **V.\<version index\>**).
(Also please tell me if there is a better solution to this as needing to visit cardmarket in order to scrape data kind of undermines the intention of this script...)
Only outputs the card's id, name and prices (in the same order they appear on cardmarket) to stdout and the output file (if provided) once the whole input file is processed.
