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

# internal use, keyed by resource_name
UNITS = {}
WEAPONS = {}
AMMO = {}
THINGS = {}

# for inspection, using a friendly name
units = {}
weapons = {}

class Resources:
    def __init__(self, metal=0, energy=0):
        self.metal = metal
        self.energy = energy

    def __repr__(self):
        s = 'Resource('
        if self.metal:
            s += 'metal={}'.format(self.metal)
            if self.energy:
                s += ', '
        if self.energy:
            s += 'energy={}'.format(self.energy)
        s += ')'
        return s


class Thing:
    base = None

    def __init__(self, resource_name):
        with open(PA_ROOT + resource_name) as datafile:
            raw = json.load(datafile)

        if 'base_spec' in raw:
            base = self.__class__(raw['base_spec'])
            self.__dict__.update(base.__dict__)
            self.base = base

        self.resource_name = resource_name
        self.raw = raw

    @property
    def safename(self):
        """ A (hopefully) unique name that can be used in URLs """
        return self.resource_name.rsplit('/', 1)[1].split('.')[0]

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
    unit_types = ()
    buildable_types = ''
    build_cost = 0
    health = 0
    weapons = ()
    build_arms = ()
    misc_tools = ()
    production = Resources()
    consumption = Resources()
    storage = Resources()

    def __init__(self, resource_name):
        super().__init__(resource_name)
        UNITS[resource_name] = self

        self.name = self.raw.pop('display_name', self.safename)
        self.role = self.raw.pop('unit_name', self.name)
        self.description = self.raw.pop('description', '')

        if 'unit_types' in self.raw:
            self.unit_types = set()
            for unit_type in self.raw.pop('unit_types'):
                assert unit_type.startswith('UNITTYPE_')
                self.unit_types.add(unit_type[9:])

        if 'buildable_types' in self.raw:
            self.buildable_types = self.raw.pop('buildable_types')

        self.builds = set()
        self.built_by = set()

        if 'build_metal_cost' in self.raw:
            self.build_cost = self.raw.pop('build_metal_cost')
        if 'max_health' in self.raw:
            self.health = self.raw.pop('max_health')

        if 'tools' in self.raw:
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
        for field in ('consumption', 'production', 'storage'):
            data = self.raw.pop(field, {})
            base = getattr(self, field)
            setattr(self, field, Resources(base.metal, base.energy))
            if 'metal' in data:
                getattr(self, field).metal = data['metal']
            if 'energy' in data:
                getattr(self, field).energy = data['energy']

        self.build_rate = 0

        if ('Economy' not in self.unit_types and
            (self.production.metal or self.production.energy or
             self.storage.metal or self.storage.energy)):
            if not self.unit_types:
                self.unit_types = set(('Economy',))
            else:
                self.unit_types.add('Economy')

        self.tool_consumption = Resources()
        for tool in self.build_arms:
            self.tool_consumption.metal += tool.metal_consumption
            self.tool_consumption.energy += tool.energy_consumption
            self.build_rate += tool.metal_consumption

        self.weapon_consumption = Resources()
        for weapon in self.weapons:
            self.weapon_consumption.metal -= weapon.metal_rate
            self.weapon_consumption.energy -= weapon.energy_rate

        if not self.safename.startswith('base_'):
            units[self.safename] = self

    @property
    def metal_rate(self):
        return (self.production.metal - self.consumption.metal
                - self.tool_consumption.metal - self.weapon_consumption.metal)

    @property
    def energy_rate(self):
        return (self.production.energy - self.consumption.energy
                - self.tool_consumption.energy - self.weapon_consumption.energy)

    @property
    def affects_economy(self):
        return bool(self.metal_rate or self.energy_rate or self.build_rate)

    def __repr__(self):
        return '<Unit: {!r}>'.format(self.role)


class Weapon(Thing):
    rof = 0.0
    ammo = None
    dps = 0.0
    damage = 0.0
    muzzle_velocity = 0.0
    splash_damage = 0.0
    splash_radius = 0
    max_range = 0

    metal_rate = 0
    energy_rate = 0
    metal_per_shot = 0
    energy_per_shot = 0
    ammo_demand = 0

    def __init__(self, resource_name):
        super().__init__(resource_name)
        WEAPONS[resource_name] = self

        if 'rate_of_fire' in self.raw:
            self.rof = self.raw.pop('rate_of_fire')
        self.name = self.safename

        ammo_id = self.raw.pop('ammo_id', None)
        if ammo_id:
            self.ammo = Ammo(ammo_id)
            self.damage = self.ammo.damage + self.ammo.splash_damage
            self.dps = self.rof * self.damage
            self.muzzle_velocity = self.ammo.muzzle_velocity
            self.splash_damage = self.ammo.splash_damage
            self.splash_radius = self.ammo.splash_radius

        if 'max_range' in self.raw:
            self.max_range = self.raw.pop('max_range')

        ammo_source = self.raw.pop('ammo_source', None)
        if ammo_source:
            if 'ammo_demand' in self.raw:
                self.ammo_demand = self.raw.pop('ammo_demand')
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
    damage = 0.0
    splash_damage = 0.0
    splash_radius = 0
    muzzle_velocity = 0
    max_velocity = 0
    lifetime = 0

    def __init__(self, resource_name):
        super().__init__(resource_name)
        AMMO[resource_name] = self

        self.name = self.resource_name.rsplit('/', 1)[1].split('.')[0]
        if 'damage' in self.raw:
            self.damage = self.raw.pop('damage')
        if 'splash_damage' in self.raw:
            self.splash_damage = self.raw.pop('splash_damage')
        if 'splash_radius' in self.raw:
            self.splash_radius = self.raw.pop('splash_radius')
        if 'initial_velocity' in self.raw:
            self.muzzle_velocity = self.raw.pop('initial_velocity')
        if 'max_velocity' in self.raw:
            self.max_velocity = self.raw.pop('max_velocity')
        if 'lifetime' in self.raw:
            self.lifetime = self.raw.pop('lifetime')

    def __repr__(self):
        return '<Ammo: {!r}>'.format(self.name)


class BuildArm(Thing):
    metal_consumption = 0
    energy_consumption = 0

    def __init__(self, resource_name):
        super().__init__(resource_name)

        self.name = self.resource_name.rsplit('/', 1)[1].split('.')[0]
        demand = self.raw.pop('construction_demand', {})
        if 'metal' in demand:
            self.metal_consumption = demand.get('metal')
        if 'energy' in demand:
            self.energy_consumption = demand.get('energy')

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
