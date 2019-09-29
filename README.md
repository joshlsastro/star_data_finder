# Star Data Finder

This Web application returns data about stars from the Hipparcos Catalog.

## Prerequisites

You need Firefox, Python 3, and astropy.
If you do not have astropy, run setup.py to get it.

## How to Run

Run server.py in Python 3. Example on Linux: `python3 server.py`. Next, open http://localhost:8888 in Firefox. /favicon.ico and /robots.txt behave exactly as one would expect. /update downloads the Hipparcos Catalog. /info gets or calculates information about a given star.

## Works Cited

M. Perryman, K. O'Flaherty, F. Ochsenbein, "The Hipparcos and Tycho Catalogues", ftp://cdsarc.u-strasbg.fr/pub/cats/I/239

## License

[![Creative Commons License](https://i.creativecommons.org/l/by/4.0/88x31.png)](http://creativecommons.org/licenses/by/4.0/)  
This work by joshlsastro is licensed under a [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).
