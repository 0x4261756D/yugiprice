# yugiprice
Stupid little Python tool to scrape card prices based on a list of card ID's.
Now also multithreaded though probably pretty badly (I have no clue how to do this properly in python...).
Uses python3's request and concurrent.futures libraries for multithreadedly scraping prices off of [Cardmarket](https://cardmarket.com/en/YuGiOh), 
falling back to first getting the name and pack from [Yugipedia](https://yugipedia.com) case cardmarket for some strange reason can not find the card based on it's ID
(which happens far more often than you might think...).
This mashing-together of different services produces very many edge cases (read the code if you want to see it...) on top of the ones these sites generate on their own.
## Usage
```bash
python3 getInfos.py path/to/your/file
```
The format for the input file is one card id per line, if multiple versions of a card exist in the same pack add *-<version index>*(see cardmarket's **V.<version index>**).
(Also please tell me if there is a better solution to this as needing to visit cardmarket in order to scrape data kind of undermines the intention of this script...)
Only outputs the card's id, name and prices (in the same order they appear on cardmarket) to stdout once the whole input file is processed.
