import json

PA_ROOT = 'G:/Games/PlanetaryAnnihilation/PA/media'
MISSING = '#MISSING#'

# internal use, keyed by resource_name
UNITS = {}
WEAPONS = {}
AMMO = {}

# for inspection, using a friendly name
units = {}
weapons = {}


class Thing:
    def __init__(self, resource_name):
        self.resource_name = resource_name
        with open(PA_ROOT + resource_name) as datafile:
            raw = json.load(datafile)
        self.raw = raw


class Unit(Thing):
    def __init__(self, resource_name):
        super().__init__(resource_name)
        UNITS[resource_name] = self

        self.name = self.raw.pop('display_name', MISSING)
        self.role = self.raw.pop('unit_name', MISSING)
        self.description = self.raw.pop('description', MISSING)
        self.unit_types = set(self.raw.pop('unit_types', ()))

        self.build_cost = self.raw.pop('build_metal_cost', 0)
        self.health = self.raw.pop('max_health', 0)

        self.weapons = []
        for tool in self.raw.pop('tools', ()):
            try:
                self.weapons.append(Weapon(tool['spec_id']))
            except IOError:
                pass
        self.dps = sum(w.dps for w in self.weapons)
        self.salvo_damage = sum(w.damage for w in self.weapons)

        if self.role != MISSING:
            units[self.role] = self


class Weapon(Thing):
    def __init__(self, resource_name):
        super().__init__(resource_name)
        WEAPONS[resource_name] = self

        self.rof = self.raw.pop('rate_of_fire', 0.0)

        ammo_id = self.raw.pop('ammo_id', None)
        if ammo_id:
            self.ammo = Ammo(ammo_id)
            self.damage = self.ammo.damage + self.ammo.splash_damage
            self.dps = self.rof * self.damage
        else:
            self.dps = 0.0
            self.damage = 0.0



class Ammo(Thing):
    def __init__(self, resource_name):
        super().__init__(resource_name)
        AMMO[resource_name] = self

        self.damage = self.raw.pop('damage', 0.0)
        self.splash_damage = self.raw.pop('splash_damage', 0.0)


def load_units():
    unitlist = json.load(open(PA_ROOT + '/pa/units/unit_list.json'))['units']
    for u in unitlist:
        Unit(u)

def report():
    print('{0:>30s}  {1:>7s}  {2:>7s}  {3:>7s}'.format('Name', 'HP', 'DPS', 'salvo'))
    print('{0:>30s}  {1:>7s}  {2:>7s}  {2:>7s}'.format('-'*20, *['-'*7]*3))
    for unit in sorted(units.values(), key=lambda u: u.role):
        if unit.health > 0:
            print('{0.role:>30s}  {0.health:7.1f}  {0.dps:7.1f}  {0.salvo_damage:7.1f}'.format(unit))

if __name__ == '__main__':
    load_units()
    report()
