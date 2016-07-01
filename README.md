# miscell
## A language for writing spreadsheets

On Wednesday 22nd of June 2016, I attended a [talk](https://github.com/triangle-man/intro-to-cellular-talk) given by James Geddes ([@triangle-man](https://github.com/triangle-man)) about his Cellular project which aims to bridge the divide between coding and spreadsheets.  In it he described a fairly large and complex system he intends to build which will allow users to write some code in a to be designed programming language, put it through a compiler and have it spit out a spreadsheet.

As part of the talk he described an intermediate language which looks something like this...

```none
A1:=45
A2:=57.3
B1:=A1*A2
```

... and is the text file representation of the data you enter into a spreadsheet.

I am an impatient man, and I really want to be able to not edit spreadsheets as soon as possible, and this intermediate language looks friendly enough for me, so I decided to start writing something to parse a language like that and generate a .CSV file which could be loaded into your spreadsheet of choice.

Over a couple of lunch breaks, I've written this prototype which I fully intend to re-write and expand on with more features as time goes on.  Currently it's exceedingly basic, a proof of concept more than anything else and you probably shouldn't use it at all, but I'm putting it in github so I can easily work on it wherever I am.

It's MIT licensed, so knock yourselves out.

## Language 

At the moment miscell can cope with only one type of statement, and that's one where you assign some expression to a cell on the left side of the statement.

e.g.

```none
A1 <- 56
```

when compiled will produce a spreadsheet where A1 is 56.

You can include expressions in "spreadsheet language" and they'll be interpreted (or at least they are in LibreOffice and Excel).

```none
A1 <- 2
A2 <- 3
B1 <- = A1 * A2
```

Will generate a spreadsheet where A1 is 2, A2 is 3 and B1 is the expression "= A1 * A2".

Comments *must* start with a "\#" as the first character on the line.

## Operation

You currently invoke miscell withe the *miscellc.py* command like so:

```bash
$ ./miscellc.py -i examples/commute.mcl -o commute.csv
```

By default, miscell uses a pipe "|" as a seperator, but you can specify any string you like with the *-s* option.

You can then open the CSV file with your chosen spreadsheet, remembering to set the seperator appropriately.

![Import in LibreOffice](images/import.png)

And there you have it.

![commute.csv in LibreOffice](images/commute.png)

## To come(!)

* Support right -> assignment
* Support importing and re-writing "data" CSV sheets
* Robustness (there is currently none as this is a proof of concept)
* Error message (currently you get a cryptic python error when things go wrong)
* Spreadsheet -> miscell code program
