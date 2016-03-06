"""
Local "web app" for the PA unit database. See http://localhost:8080/list
"""

WEB_PORT = 8080
WEB_BASE = '' # empty or root relative path eg /units

# Step 0: Make sure we have Bottle. If not, download it.
try:
    import bottle
except ImportError:
    def get_bottle():
        import urllib.request
        import os.path
        savename = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'bottle.py')
        urllib.request.urlretrieve('https://raw.github.com/defnull/bottle/0.11.6/bottle.py',
                                   savename)
        print("Saved Bottle as '{}'".format(savename))
    get_bottle()

from bottle import route, run, template, static_file, request, abort

import os
import pprint
import re
import units
import itertools
import collections
import logging
import html

def show_variants():
    return bool(int(request.get_cookie("show_commander_variants", '0')))

def show_inaccessible():
    return bool(int(request.get_cookie("show_inaccessible_units", '0')))

def update_query(field, value):
    # Get a modified request string with the *field* set to *value*
    new_query = [k+'='+v for k,v in request.query.items() if k != field]
    if value:
        new_query.append(field + '=' + value)

    if new_query:
        return request.fullpath + '?' + '&'.join(new_query)
    else:
        return request.fullpath


def update_version(version=None, add_mod=None, remove_mod=None, field='version'):
    # Get a modified request string with changes to the version, mods, or other
    # fields specified in the query string
    q = getattr(request.query, field)
    items = q.split(':') if q else []
    if not items:
        items.append(LATEST_VERSION)
    if add_mod:
        items.append(add_mod)
    if remove_mod:
        items.remove(remove_mod)
    if version:
        items[0] = version
    if len(items) == 1 and items[0] == LATEST_VERSION:
        items = []

    return update_query(field, ':'.join(items))


class WebUnits(units.VersionDb):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_units()
        self.units = {u.safename:u for u in self.units.values()
                      if u.health > 0 and u.build_cost > 0}
        self.sorted_units = sorted(self.units.values(), key=lambda u: u.build_cost)
        self.icon_paths = {}

        if self.version != LATEST_VERSION or self.active_mods:
            self.queryversion = ':'.join([self.version] + self.active_mods)
        else:
            self.queryversion = None

        self.unit_groups = collections.OrderedDict([
            ('factories', ('Factories', self.builder_cols, self.builder_data, 'Factory - PlanetEngine')),
            ('builders', ('Construction Units', self.builder_cols, self.builder_data,'Mobile & Construction')),
            ('vehicles', ('Vehicles', self.mobile_cols, self.mobile_data, 'Mobile & Tank - Construction')),
            ('bots', ('Bots', self.mobile_cols, self.mobile_data, 'Mobile & Bot - Construction')),
            ('air', ('Aircraft', self.mobile_cols, self.mobile_data, 'Mobile & Air - Construction')),
            ('naval', ('Naval', self.mobile_cols, self.mobile_data, 'Mobile & Naval - Construction')),
            ('orbital', ('Orbital', self.unit_cols, self.unit_data, 'Orbital - Construction - Recon')),
            ('titans', ('Titans', self.mobile_cols, self.mobile_data, 'Titan')),
            ('defense', ('Defensive Structures', self.unit_cols, self.unit_data, 'Structure & Defense')),
            ('economy', ('Economy', self.econ_cols, self.econ_data, 'Economy - Commander')),
            ('recon', ('Reconnaissance', self.recon_cols, self.recon_data, 'Recon')),
            ('other', ('Other', self.unit_cols, self.unit_data, 'Ungrouped'))])

        for u in self.sorted_units:
            u.unit_types.add('Ungrouped')

        for category, data in self.unit_groups.items():
            for unit in self.get_units(data[3], True):
                unit.web_category = category
                if category != 'other':
                    unit.unit_types.discard('Ungrouped')

    def get_units(self, restriction, get_all=False):
        """ Get the units that match the specified category restriction """
        R = units.get_restriction(restriction)
        for u in self.sorted_units:
            if R.satisfies(u):
                if not get_all and (u.variant and not show_variants()):
                    continue
                if not get_all and not (u.accessible or show_inaccessible()):
                    continue
                yield u

    def get_icon_path(self, unit):
        # returns root directory and icon path
        if unit in self.icon_paths:
            return self.icon_paths[unit]

        path_tmpl = ['/{exp}/units/{subdir}/{name}/{name}_icon_buildbar.png',
                     '/pa/units/{subdir}/{name}/{name}_icon_buildbar.png',
                     '/ui/main/game/live_game/img/build_bar/units/{name}.png',
                     '/ui/alpha/live_game/img/build_bar/units/{name}.png']

        subdir = unit.resource_name.split('/')[3]
        for directory in self.data_dirs:
            for tmpl in path_tmpl:
                filename = tmpl.format(name=unit.safename, subdir=subdir,
                                       exp=self.expansion or 'pa')
                if os.path.exists(directory + filename):
                    self.icon_paths[unit] = directory, filename
                    return directory, filename

        return None, None


    unit_cols = ['Name', 'Cost', 'DPS', 'HP']
    def unit_data(self, restriction):
        return [(u, u.build_cost, u.dps, u.health)
                for u in self.get_units(restriction)]

    mobile_cols = ['Name', 'Cost', 'DPS', 'HP', 'Speed']
    def mobile_data(self, restriction):
        return [(u, u.build_cost, u.dps, u.health, u.move_speed)
                for u in self.get_units(restriction)]

    builder_cols = ['Name', 'Cost', 'HP', 'Build Rate', 'Build Energy', 'Energy per Metal']
    def builder_data(self, restriction):
        return [(u, u.build_cost, u.health, u.build_rate, u.tool_consumption.energy,
                 '{:.1f}'.format(u.build_inefficiency))
                for u in self.get_units(restriction)]

    econ_cols = ['Name', 'Cost', 'HP', 'M Rate', 'E Rate', 'M Storage', 'E Storage']
    def econ_data(self, restriction):
        return [(u, u.build_cost, u.health, u.metal_rate, u.energy_rate,
                 u.storage.metal, u.storage.energy)
                for u in self.get_units(restriction)]

    recon_cols = ['Name', 'Cost', 'HP', 'E Rate',
                  'Vision', 'Radar', 'Orbital Vision', 'Orbital Radar', 'Sonar']
    def recon_data(self, restriction):
        return [(u, u.build_cost, u.health, -u.energy_rate,
                 u.vision_radius, u.radar_radius, u.orbital_vision_radius,
                 u.orbital_radar_radius, u.sonar_radius)
                for u in self.get_units(restriction)]


def timestr(val):
    """ Convert a time in seconds into string with the format '[m]m:ss'."""
    if val > 3:
        val = int(val)
        minutes = val // 60
        seconds = val % 60
        return '{}:{:02}'.format(minutes, seconds)
    else:
        return '0:{:04.1f}'.format(val)

LOADED_DBS = {}
AVAILABLE_VERSIONS = collections.OrderedDict(units.DESCRIPTIONS)
if 'pa_root' in units.CONFIG:
    AVAILABLE_VERSIONS['current'] = 'current'
LATEST_VERSION = next(reversed(AVAILABLE_VERSIONS))
DB_COUNTER = 0
MAX_DBS = units.CONFIG.get('cache_size', 50)

def get_db(key=None):
    # default version and mods are from the query string
    if key is None:
        key = request.query.version or LATEST_VERSION

    desc, *mods = key.split(':')
    version = desc

    if version not in AVAILABLE_VERSIONS:
        logging.warning(
            'No such version: {!r}; headers={!r}, query={!r}'.format(
                version, dict(request.headers), dict(request.query)))
        abort(404, "No such version: {!r}".format(version))

    for mod in mods:
        if mod not in units.AVAILABLE_MODS:
            logging.warning(
                'No such mod: {!r}; headers={!r}, query={!r}'.format(
                    mod, dict(request.headers), dict(request.query)))
            abort(404, "No such mod: {!r}. Available mods: {!r}".format(
                mod, list(units.AVAILABLE_MODS)))

    if key not in LOADED_DBS:
        print('loading DB for', key)
        LOADED_DBS[key] = WebUnits(version, mods)

    # Limit the number of loaded databases
    global DB_COUNTER
    db = LOADED_DBS[key]
    db.last_accessed = DB_COUNTER
    DB_COUNTER += 1
    if len(LOADED_DBS) >= MAX_DBS:
        loser = sorted(LOADED_DBS.items(),
                       key=lambda item: item[1].last_accessed)[0]
        print('Unloading DB:', loser[0])
        del LOADED_DBS[loser[0]]

    return db


@route(WEB_BASE+'/table/<name>')
def callback(name):
    db = get_db()
    caption, columns, data_function, categories = db.unit_groups[name]
    return template('unit_table',
                    caption=caption,
                    columns=columns,
                    data=data_function(categories),
                    db=db, WEB_BASE=WEB_BASE)


@route(WEB_BASE)
@route(WEB_BASE+'/')
def callback():
    db = get_db()
    tables = {}
    for group,(caption, _, _, categories) in db.unit_groups.items():
        tables[group] = db.get_units(categories)

    return template('all_units_list', db=db, WEB_BASE=WEB_BASE, **tables)


@route(WEB_BASE+'/unit/<name>')
def callback(name):
    db = get_db()
    if name not in db.units:
        abort(404, "No such unit {!r} in version {!r}".format(
            name, db.version))
    unit = db.units[name]
    have_icon = bool(db.get_icon_path(unit))
    return template('unit', u=unit, have_icon=have_icon, db=db, WEB_BASE=WEB_BASE)


@route(WEB_BASE+'/json/<resource>')
def callback(resource):
    version = request.query.version or LATEST_VERSION
    db = get_db()
    text = html.escape(pprint.pformat(db.get_json(db.full_names[resource])), False)
    for item,key in re.findall(r"('/pa/.+?/(\w+)\.json')", text):
        if key in db.full_names:
            ver = '?version={}'.format(version) if version != LATEST_VERSION else ''
            text = text.replace(item, "<a href='" + WEB_BASE+ "/json/{}{}'>{}</a>".format(key, ver, item))

    return template('json', db=db, WEB_BASE=WEB_BASE, resource=resource, text=text)


@route(WEB_BASE+'/compare')
def callback():
    v1 = request.query.v1 or LATEST_VERSION
    v2 = request.query.v2 or LATEST_VERSION
    db1 = get_db(v1)
    db2 = get_db(v2)
    u1 = db1.units[request.query.u1 or 'land_scout']
    u2 = db2.units[request.query.u2 or 'land_scout']
    cat1 = request.query.cat1 or u1.web_category
    cat2 = request.query.cat2 or u2.web_category

    if cat1 != u1.web_category:
        u1 = next(db1.get_units(db1.unit_groups[cat1][3]))
    if cat2 != u2.web_category:
        u2 = next(db2.get_units(db2.unit_groups[cat2][3]))

    have_icon1 = bool(db1.get_icon_path(u1))
    have_icon2 = bool(db2.get_icon_path(u2))
    return template('compare', request=request,
                    db1=db1, db2=db2,
                    u1=u1, u2=u2,
                    v1=v1, v2=v2,
                    cat1=cat1, cat2=cat2,
                    have_icon1=have_icon1, have_icon2=have_icon2,
                    WEB_BASE=WEB_BASE)


@route(WEB_BASE+'/about')
def callback():
    db = get_db()
    return template('about', db=db, WEB_BASE=WEB_BASE)


@route(WEB_BASE+'/build_icons/<name>')
def callback(name):
    db = get_db()
    root, icon = db.get_icon_path(db.units[name])
    if icon:
        return static_file(icon, root=root)
    else:
        return static_file('blank.png', root='./static/')


@route(WEB_BASE+'/static/<filename>')
def callback(filename):
    return static_file(filename, root='./static/')

@route(WEB_BASE+'/fonts/<filename>')
def callback(filename):
    return static_file(filename, root='./static/')

@route(WEB_BASE+'/robots.txt')
def callback():
    return static_file('robots.txt', root='./static/')

if __name__ == '__main__':
    run(host='localhost', port=WEB_PORT,
        reloader=True, # Reload on changes to .py files
        debug=True, # Reload changes to .tpl files
        )
