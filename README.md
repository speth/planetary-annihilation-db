Planetary Annihilation Unit Database
====================================

This is a set of tools for accessing information about the units in Planetary
Annihilation. It works by parsing the JSON unit descriptions from the
installed game. Information can be accessed directly from a Python console or
through a local web app.

## Requirements ##

- Python >= 3.2
- A copy of [Planetary Annihilation](http://www.uberent.com/pa/) or copies
  of the relevant unit JSON files for one or more versions

## Installation ##

- Clone this repository or download it as an archive.

## Configuration

- Create a file named `padb.json` in the same directory as `units.py`
  containing a JSON object in the following format:

```json
{
    "pa_root": "C:/Path/To/PlanetaryAnnihilation/PA/media",
    "archive_root": "C:/Path/To/Archived/Files",
    "mods_root": "C:/Path/to/server_mods/directory",
    "versions": [["73823", "units-73823"],
                 ["76766", "units-76766"]]
}
```

- At least one of `pa_root` or `versions` must be supplied. The other variables
  are optional.

- On Windows, your installed server mods are located in your user profile
  directory, e.g. `c:/Users/YourName/AppData/Local/Uber Entertainment/Planetary
  Annihilation/server_mods`.

- The `archive_root` directory may contain directories with JSON files from
  several versions of PA, as specified under the `versions` property. Each
  element of this list consists of a list with two elements. The first is the
  string used to identify the version, and the second is the name of the
  subdirectory under `archive_root` where the files are stored (see below for
  how to create the version archives from a current copy of the game).

## Usage ##

### Web Interface ###

From a command prompt in the directory containing `units.py`, run:

```
python webunits.py
```

Then, point your web browser to `http://localhost:8080/` .

The first time you run `webunits.py`, it will automatically download a copy of
[Bottle](http://bottlepy.org/). If this fails for some reason, you can
download `bottle.py` from https://github.com/defnull/bottle and place it in
the same directory as `webunits.py`.

### Shell Usage

From a Python prompt ([IPython](http://ipython.org/install.html) *highly*
recommended) in the directory containing `units.py`:

```python
>>> import units
>>> db = units.VersionDb()
>>> db.load_units()
```

To get the list of units:

```python
>>> sorted(db.units)
```

To get information about a particular unit:

```python
>>> u = db.units['vehicle_factory']
>>> u() # prints a summary
>>> u.build_rate # -> 15
>>> u.builds # -> set of units build by this unit
```

### Generating Archive Data ###

To generate an archive file for the current version of PA (as specified by the
`pa_root` directory in `padb.json`), run:

```
python archive.py
```

This will generate a file named `units-XXXXX.tar.bz2` where `XXXXX` is the
current build identifier. The `units-XXXXX` directory in this archive can then
be placed in the `archive_root` directory pointed to by `padb.json`.

To generate an archive from a copy of the PA files installed to a different
location, run:

```
python archive.py C:/path/to/PA/media
```
