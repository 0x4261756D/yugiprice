# yugiprice
Python tool to scrape card prices based on a list of card ID's.
Pretty badly multithreaded (I have no clue how to do this in python)
Uses python3's request and concurrent.futures libraries to extract price data from [Cardmarket](https://cardmarket.com/en/YuGiOh) based on a card's ID, 
falling back to first getting the name and pack from [Yugipedia](https://yugipedia.com) because cardmarket does not find some cards based on their ID for some strange reason (it is far more common than you think...).
Because just mashing together two completely different services that do not have an API for that usecase (as far as I am aware) cannot go wrong the code is quite horrible to read and I am sure anyone who dares to use this will find many new pretty edgecases (please feel free to open an Issue or even fix it yourself in a PR).
## Usage
```bash
# help
python3 getInfos.py [-h]
# normal usage
python3 getInfos.py path/to/your/file [-o path/to/your/output/file]
```
The input file should contain one card id per line, if multiple versions of a card exist in the same pack add *-\<version index\>*(see cardmarket's **V.\<version index\>**).
(Also please tell me if there is a better solution to this as needing to visit cardmarket in order to scrape data kind of undermines the intention of this script...)
Only outputs the card's id, name and prices (in the same order they appear on cardmarket) to stdout once the whole input file is processed.
