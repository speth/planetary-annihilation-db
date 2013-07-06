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

import units
import itertools
units.load_units()
webunits = {u.safename:u for u in units.units.values()
            if u.health > 0 and u.build_cost > 0}

def timestr(val):
    """ Convert a time in seconds into string with the format '[m]m:ss'."""
    val = int(val)
    minutes = val // 60
    seconds = val % 60
    return '{}:{:02}'.format(minutes, seconds)

@route('/')
def unit_list():
    U = sorted(webunits.values(), key=lambda u: u.build_cost)
    def get_units(restriction):
        R = units.get_restriction(restriction)
        for u in U:
            if R.satisfies(u):
                yield u

    builder_cols = ['Name', 'Cost', 'Build Rate', 'HP']
    builder_data = lambda u: (u, u.build_cost, u.build_rate, u.health)
    factory_data = [builder_data(u) for u in get_units('Factory')]
    factories = template('unit_table', caption='Factories',
                         columns=builder_cols, data=factory_data)

    fabber_data = [builder_data(u) for u in get_units('Mobile & Construction')]
    fabbers = template('unit_table', caption='Construction Units',
                       columns=builder_cols, data=fabber_data)

    unit_cols = ['Name', 'Cost', 'DPS', 'HP']
    def unit_data(restriction):
        return [(u, u.build_cost, u.dps, u.health)
                for u in get_units(restriction)]

    vehicle_data = unit_data('Mobile & Tank - Construction')
    vehicles = template('unit_table', caption='Vehicles',
                        columns=unit_cols, data=vehicle_data)

    bot_data = unit_data('Mobile & Bot - Construction')
    bots = template('unit_table', caption='Bots',
                    columns=unit_cols, data=bot_data)

    plane_data = unit_data('Mobile & Air - Construction')
    planes = template('unit_table', caption='Aircraft',
                      columns=unit_cols, data=plane_data)

    boat_data = unit_data('Mobile & Naval - Construction')
    boats = template('unit_table', caption='Naval',
                     columns=unit_cols, data=boat_data)

    orbital_data = unit_data('Orbital - Construction')
    orbital = template('unit_table', caption='Orbital Units',
                       columns=unit_cols, data=orbital_data)

    defense_data = unit_data('Structure & Defense')
    defenses = template('unit_table', caption='Defensive Structures',
                        columns=unit_cols, data=defense_data)

    econ_cols = ['Name', 'Cost', 'HP', 'M Rate', 'E Rate',
                 'M Storage', 'E Storage']
    econ_data = [(u, u.build_cost, u.health, u.metal_rate, u.energy_rate,
                  u.storage.metal, u.storage.energy)
                 for u in get_units('Structure & Economy')]
    econ = template('unit_table', caption='Economic Structures',
                    columns=econ_cols, data=econ_data)

    other_struct_data = [(u, u.build_cost, u.dps, u.health)
                         for u in get_units('Structure - Defense - Factory - Economy')]
    other_structs = template('unit_table', caption='Other Structures',
                             columns=unit_cols, data=other_struct_data)


    # Check to make sure we didn't forget anything important
    other2 = set(webunits.values())
    for u,*cols in itertools.chain(factory_data, fabber_data, vehicle_data,
                                   bot_data, plane_data, boat_data,
                                   orbital_data, defense_data, econ_data,
                                   other_struct_data):
        other2.discard(u)

    if other2:
        leftover_data = [(u, u.build_cost, u.dps, u.health) for u in other2]
        leftover = template('unit_table', caption='Uncategorized Units',
                            columns=unit_cols, data=leftover_data)
    else:
        leftover = ''

    return template('unitlist', tables=[factories, fabbers, bots, vehicles,
                                        planes, boats, orbital, defenses,
                                        econ, other_structs, leftover])


@route('/unit/<name>')
def callback(name):
    return template('unit', u=units.units[name])


@route('/static/<filename>')
def callback(filename):
    return static_file(filename, root='./static/')


if __name__ == '__main__':
    run(host='localhost', port=8080,
        reloader=True, # Reload on changes to .py files
        debug=True, # Reload changes to .tpl files
        )
