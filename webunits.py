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

from bottle import route, run, template, static_file

import os
import units
import itertools
import collections

db = units.VersionDb('current')
db.load_units()
webunits = {u.safename:u for u in db.units.values()
            if u.health > 0 and u.build_cost > 0}
sorted_units = sorted(webunits.values(), key=lambda u: u.build_cost)

def get_units(restriction):
    """ Get the units that match the specified category restriction """
    R = units.get_restriction(restriction)
    for u in sorted_units:
        if R.satisfies(u):
            yield u

def timestr(val):
    """ Convert a time in seconds into string with the format '[m]m:ss'."""
    val = int(val)
    minutes = val // 60
    seconds = val % 60
    return '{}:{:02}'.format(minutes, seconds)

def get_icon_path(unit_name):
    filename = '/ui/alpha/live_game/img/build_bar/units/{}.png'.format(unit_name)
    if os.path.exists(units.PA_ROOT + filename):
        return filename

unit_cols = ['Name', 'Cost', 'DPS', 'HP']
def unit_data(restriction):
    return [(u, u.build_cost, u.dps, u.health)
            for u in get_units(restriction)]

mobile_cols = ['Name', 'Cost', 'DPS', 'HP', 'Speed']
def mobile_data(restriction):
    return [(u, u.build_cost, u.dps, u.health, u.move_speed)
            for u in get_units(restriction)]

builder_cols = ['Name', 'Cost', 'HP', 'Build Rate', 'Build Energy', 'Energy per Metal']
def builder_data(restriction):
    return [(u, u.build_cost, u.health, u.build_rate, u.tool_consumption.energy,
             '{:.1f}'.format(u.build_inefficiency))
            for u in get_units(restriction)]

econ_cols = ['Name', 'Cost', 'HP', 'M Rate', 'E Rate', 'M Storage', 'E Storage']
def econ_data(restriction):
    return [(u, u.build_cost, u.health, u.metal_rate, u.energy_rate,
             u.storage.metal, u.storage.energy)
            for u in get_units(restriction)]

unit_groups = collections.OrderedDict([
    ('factories', ('Factories', builder_cols, builder_data, 'Factory')),
    ('builders', ('Construction Units', builder_cols, builder_data,'Mobile & Construction')),
    ('vehicles', ('Vehicles', mobile_cols, mobile_data, 'Mobile & Tank - Construction')),
    ('bots', ('Bots', mobile_cols, mobile_data, 'Mobile & Bot - Construction')),
    ('air', ('Aircraft', mobile_cols, mobile_data, 'Mobile & Air - Construction')),
    ('naval', ('Naval', mobile_cols, mobile_data, 'Mobile & Naval - Construction')),
    ('orbital', ('Orbital', unit_cols, unit_data, 'Orbital - Construction')),
    ('defense', ('Defensive Structures', unit_cols, unit_data, 'Structure & Defense')),
    ('economy', ('Economic Structures', econ_cols, econ_data, 'Structure & Economy')),
    ('other', ('Other Structures', unit_cols, unit_data, 'Structure - Defense - Factory - Economy'))])

@route('/table/<name>')
def callback(name):
    caption, columns, data_function, categories = unit_groups[name]
    return template('unit_table_single',
                    caption=caption,
                    columns=columns,
                    data=data_function(categories))

@route('/table/all')
def callback():
    table_data = {}
    tables = []
    for group,(caption, columns, data_function, categories) in unit_groups.items():
        table_data[group] = data_function(categories)
        tables.append(template('unit_table', caption=caption,
                               columns=columns, data=table_data[group]))

    # Check to make sure we didn't forget anything important
    other2 = set(webunits.values())
    for u,*cols in itertools.chain.from_iterable(table_data.values()):
        other2.discard(u)

    if other2:
        leftover_data = [(u, u.build_cost, u.dps, u.health) for u in other2]
        leftover = template('unit_table', caption='Uncategorized Units',
                            columns=unit_cols, data=leftover_data)
        tables.append(leftover)

    return template('unitlist', tables=tables)

@route('/')
def callback():
    tables = {}
    for group,(caption, _, _, categories) in unit_groups.items():
        tables[group] = get_units(categories)

    return template('all_units_list', **tables)


@route('/unit/<name>')
def callback(name):
    have_icon = bool(get_icon_path(name))
    return template('unit', u=db.units[name], have_icon=have_icon)


@route('/build_icons/<name>')
def callback(name):
    return static_file(get_icon_path(name), root=units.PA_ROOT)


@route('/static/<filename>')
def callback(filename):
    return static_file(filename, root='./static/')


if __name__ == '__main__':
    run(host='localhost', port=8080,
        reloader=True, # Reload on changes to .py files
        debug=True, # Reload changes to .tpl files
        )
