import json
import pprint

try:
    config = json.load(open('padb.json'))
except IOError:
    print("""
****************************************************************
Error reading configuration. Create a file named 'padb.json'
in the current directory with an entry in the following format,
with the path to the Planetary Annihilation 'media' directory:

{
    "pa_root": "C:/Path/To/PlanetaryAnnihilation/PA/media"
}

****************************************************************
""")
    raise

PA_ROOT = config['pa_root']
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

    def report(self, show_all=False):
        out = []
        for k,v in self.__dict__.items():
            if not show_all and k in ('raw',):
                continue
            indent = len(k) + 2
            s = pprint.pformat(v)
            lines = s.split('\n')
            out.append('{}: {}'.format(k, lines[0]))
            out.extend(' '*indent + line for line in lines[1:])
        return '\n'.join(out)

    def __call__(self, show_all=False):
        """ Print info about this unit """
        print(self.report(show_all))


class Unit(Thing):
    def __init__(self, resource_name):
        super().__init__(resource_name)
        UNITS[resource_name] = self

        self.name = self.raw.pop('display_name', MISSING)
        self.role = self.raw.pop('unit_name', MISSING)
        self.description = self.raw.pop('description', MISSING)
        self.webname = self.name.replace(' ', '')

        self.unit_types = set()
        for unit_type in self.raw.pop('unit_types', ()):
            assert unit_type.startswith('UNITTYPE_')
            self.unit_types.add(unit_type[9:])
        self.buildable_types = self.raw.pop('buildable_types', '')

        self.builds = set()
        self.built_by = set()

        self.build_cost = self.raw.pop('build_metal_cost', 0)
        self.health = self.raw.pop('max_health', 0)

        self.weapons = []
        self.build_arms = []
        self.misc_tools = []

        for tool in self.raw.pop('tools', ()):
            resource = tool['spec_id']
            tool_name = resource.rsplit('/')[-1].split('.')[0]
            try:
                if 'weapon' in tool_name:
                    self.weapons.append(Weapon(resource))
                elif 'build_arm' in tool_name:
                    self.build_arms.append(BuildArm(resource))
                else:
                    self.misc_tools.append(Thing(resource))
            except IOError:
                    pass

        self.dps = sum(w.dps for w in self.weapons)
        self.salvo_damage = sum(w.damage for w in self.weapons)

        # Economy
        consumption = self.raw.pop('consumption', {})
        production = self.raw.pop('production', {})
        self.metal_rate = production.get('metal', 0)
        self.metal_rate -= consumption.get('metal', 0)
        self.energy_rate = production.get('energy', 0)
        self.energy_rate -= consumption.get('energy', 0)
        self.build_rate = 0
        for tool in self.build_arms:
            self.metal_rate -= tool.metal_consumption
            self.energy_rate -= tool.energy_consumption
            self.build_rate += tool.metal_consumption

        for weapon in self.weapons:
            self.metal_rate += weapon.metal_rate
            self.energy_rate += weapon.energy_rate

        if self.role != MISSING:
            units[self.role] = self

    def __repr__(self):
        return '<Unit: {!r}>'.format(self.role)


class Weapon(Thing):
    def __init__(self, resource_name):
        super().__init__(resource_name)
        WEAPONS[resource_name] = self

        self.rof = self.raw.pop('rate_of_fire', 0.0)
        self.name = self.resource_name.rsplit('/', 1)[1].split('.')[0]

        ammo_id = self.raw.pop('ammo_id', None)
        if ammo_id:
            self.ammo = Ammo(ammo_id)
            self.damage = self.ammo.damage + self.ammo.splash_damage
            self.dps = self.rof * self.damage
        else:
            self.dps = 0.0
            self.damage = 0.0

        self.metal_rate = 0
        self.energy_rate = 0
        self.metal_per_shot = 0
        self.energy_per_shot = 0
        ammo_source = self.raw.pop('ammo_source', None)
        if ammo_source:
            self.ammo_demand = self.raw.pop('ammo_demand', 0)
            ammo_per_shot = self.raw.pop('ammo_per_shot', 0)
            rate = min(self.ammo_demand, ammo_per_shot * self.rof)
            if ammo_source == 'energy':
                self.energy_rate = - rate
                self.energy_per_shot = ammo_per_shot
            else:
                self.metal_rate = - rate
                self.metal_per_shot = ammo_per_shot

    def __repr__(self):
        return '<Weapon: {!r}>'.format(self.name)


class Ammo(Thing):
    def __init__(self, resource_name):
        super().__init__(resource_name)
        AMMO[resource_name] = self

        self.name = self.resource_name.rsplit('/', 1)[1].split('.')[0]
        self.damage = self.raw.pop('damage', 0.0)
        self.splash_damage = self.raw.pop('splash_damage', 0.0)

    def __repr__(self):
        return '<Ammo: {!r}>'.format(self.name)


class BuildArm(Thing):
    def __init__(self, resource_name):
        super().__init__(resource_name)

        self.name = self.resource_name.rsplit('/', 1)[1].split('.')[0]
        demand = self.raw.pop('construction_demand', {})
        self.metal_consumption = demand.get('metal', 0)
        self.energy_consumption = demand.get('energy', 0)

    def __repr__(self):
        return '<Build Arm: {!r}>'.format(self.name)


###### Buildable Categories ######

class SimpleRestriction:
    def __init__(self, category):
        self.category = category.strip()

    def satisfies(self, unit):
        return self.category in unit.unit_types

class CompoundRestriction:
    def __init__(self, left, right):
        self.left = left
        self.right = right

class CompoundAnd(CompoundRestriction):
    def satisfies(self, unit):
        return self.left.satisfies(unit) and self.right.satisfies(unit)

class CompoundOr(CompoundRestriction):
    def satisfies(self, unit):
        return self.left.satisfies(unit) or self.right.satisfies(unit)

class CompoundMinus(CompoundRestriction):
    def satisfies(self, unit):
        return self.left.satisfies(unit) and not self.right.satisfies(unit)

def get_restriction(text):
    if '|' in text:
        return CompoundOr(*map(get_restriction, text.split('|', 1)))
    elif '&' in text:
        return CompoundAnd(*map(get_restriction, text.split('&', 1)))
    elif '-' in text:
        return CompoundMinus(*map(get_restriction, text.rsplit('-', 1)))
    else:
        return SimpleRestriction(text)

def build_build_tree():
    for unit in UNITS.values():
        if unit.buildable_types:
            r = get_restriction(unit.buildable_types)
        else:
            continue

        for other in UNITS.values():
            if r.satisfies(other):
                unit.builds.add(other)
                other.built_by.add(unit)

def load_units():
    unitlist = json.load(open(PA_ROOT + '/pa/units/unit_list.json'))['units']
    for u in unitlist:
        Unit(u)
    build_build_tree()

def report():
    print('{0:>30s}  {1:>7s}  {2:>7s}  {3:>7s}'.format('Name', 'HP', 'DPS', 'salvo'))
    print('{0:>30s}  {1:>7s}  {2:>7s}  {2:>7s}'.format('-'*20, *['-'*7]*3))
    for unit in sorted(units.values(), key=lambda u: u.role):
        if unit.health > 0:
            print('{0.role:>30s}  {0.health:7.1f}  {0.dps:7.1f}  {0.salvo_damage:7.1f}'.format(unit))

if __name__ == '__main__':
    load_units()
    report()
