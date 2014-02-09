"""
Local "web app" for the PA unit database. See http://localhost:8080/list
"""

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

from bottle import route, run, template, static_file, request

import os
import units
import itertools
import collections

class WebUnits:
    def __init__(self, db):
        self.db = db
        self.units = {u.safename:u for u in db.units.values()
                      if u.health > 0 and u.build_cost > 0}
        self.sorted_units = sorted(self.units.values(), key=lambda u: u.build_cost)

        self.unit_groups = collections.OrderedDict([
            ('factories', ('Factories', self.builder_cols, self.builder_data, 'Factory')),
            ('builders', ('Construction Units', self.builder_cols, self.builder_data,'Mobile & Construction')),
            ('vehicles', ('Vehicles', self.mobile_cols, self.mobile_data, 'Mobile & Tank - Construction')),
            ('bots', ('Bots', self.mobile_cols, self.mobile_data, 'Mobile & Bot - Construction')),
            ('air', ('Aircraft', self.mobile_cols, self.mobile_data, 'Mobile & Air - Construction')),
            ('naval', ('Naval', self.mobile_cols, self.mobile_data, 'Mobile & Naval - Construction')),
            ('orbital', ('Orbital', self.unit_cols, self.unit_data, 'Orbital - Construction')),
            ('defense', ('Defensive Structures', self.unit_cols, self.unit_data, 'Structure & Defense')),
            ('economy', ('Economic Structures', self.econ_cols, self.econ_data, 'Structure & Economy')),
            ('other', ('Other Structures', self.unit_cols, self.unit_data, 'Structure - Defense - Factory - Economy'))])

    def get_units(self, restriction):
        """ Get the units that match the specified category restriction """
        R = units.get_restriction(restriction)
        for u in self.sorted_units:
            if R.satisfies(u):
                yield u

    def get_icon_path(self, unit_name):
        filename = '/ui/alpha/live_game/img/build_bar/units/{}.png'.format(unit_name)
        if os.path.exists(self.db.root + filename):
            return filename

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


def timestr(val):
    """ Convert a time in seconds into string with the format '[m]m:ss'."""
    val = int(val)
    minutes = val // 60
    seconds = val % 60
    return '{}:{:02}'.format(minutes, seconds)


dbs = {}
for version,db in units.load_all().items():
    dbs[version] = WebUnits(db)


@route('/table/<name>')
def callback(name):
    version = request.query.version or 'current'
    db = dbs[version]
    print(version)
    caption, columns, data_function, categories = db.unit_groups[name]
    return template('unit_table_single',
                    caption=caption,
                    columns=columns,
                    data=data_function(categories),
                    version=version)

@route('/table/all')
def callback():
    version = request.query.version or 'current'
    db = dbs[version]
    table_data = {}
    tables = []
    for group,(caption, columns, data_function, categories) in db.unit_groups.items():
        table_data[group] = data_function(categories)
        tables.append(template('unit_table', caption=caption,
                               columns=columns, data=table_data[group],
                               version=version))

    # Check to make sure we didn't forget anything important
    other2 = set(db.units.values())
    for u,*cols in itertools.chain.from_iterable(table_data.values()):
        other2.discard(u)

    if other2:
        leftover_data = [(u, u.build_cost, u.dps, u.health) for u in other2]
        leftover = template('unit_table', caption='Uncategorized Units',
                            columns=unit_cols, data=leftover_data, version=version)
        tables.append(leftover)

    return template('unitlist', version=version, tables=tables)

@route('/')
def callback():
    version = request.query.version or 'current'
    db = dbs[version]
    tables = {}
    for group,(caption, _, _, categories) in db.unit_groups.items():
        tables[group] = db.get_units(categories)

    return template('all_units_list', version=version, **tables)


@route('/unit/<name>')
def callback(name):
    version = request.query.version or 'current'
    db = dbs[version]
    have_icon = bool(db.get_icon_path(name))
    return template('unit', u=db.units[name], have_icon=have_icon, version=version)


@route('/build_icons/<name>')
def callback(name):
    version = request.query.version or 'current'
    db = dbs[version]
    return static_file(db.get_icon_path(name), root=db.db.root)


@route('/static/<filename>')
def callback(filename):
    return static_file(filename, root='./static/')


if __name__ == '__main__':
    run(host='localhost', port=8080,
        reloader=True, # Reload on changes to .py files
        debug=True, # Reload changes to .tpl files
        )
