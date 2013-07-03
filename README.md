Planetary Annihilation Unit Database
************************************

This is a set of tools for accessing information about the units in Planetary
Annihilation. It works by parsing the JSON unit descriptions from the
installed game. Information can be accessed directly from a Python console or
through a (currently very rudimentary) local web app.

Requirements
============

- Python >= 3.2

Installation
============

- Clone this repository or download it as an archive.
- Create a file named `padb.json` in the same directory as `units.py`
  containing entry in the following format with the path to the Planetary
  Annihilation `media` directory:

        {
            "pa_root": "C:/Path/To/PlanetaryAnnihilation/PA/media"
        }

Usage
=====

Web Interface
-------------

From a command prompt in the directory containing `units.py`, run:

    python webunits.py

Then, point your web browser to http://localhost:8080/list .

The first time you run `webunits.py`, it will automatically download a copy of
[Bottle](http://bottlepy.org/). If this fails for some reason, you can
download `bottle.py` from https://github.com/defnull/bottle and place it in
the same directory as `webunits.py`.

Shell Usage
-----------

From a Python prompt ([IPython](http://ipython.org/install.html) *highly*
recommended) in the directory containing `units.py`:

    >>> from units import *
    >>> load_units()

To get the list of units:

    >>> sorted(units.keys())

To get information about a particular unit:

    >>> units['Vehicle Factory']()
