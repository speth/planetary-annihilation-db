import json
import pprint
import collections
import os
import re

try:
    CONFIG = json.load(open('padb.json'))
except IOError:
    print("""
****************************************************************
Error reading configuration. Create a file named 'padb.json'
in the current directory with an entry in the following format,
with the path to the Planetary Annihilation 'media' directory:

{
    "pa_root": "C:/Path/To/PlanetaryAnnihilation/PA/media",
    "versions": ["current": ""]
}

****************************************************************
""")
    raise

def delocalize(text):
    if text.startswith('!LOC'):
        return re.sub(r'!LOC\(.*?\):(.*)', r'\1', text)
    else:
        return text


class VersionDb:
    def __init__(self, version='current'):
        self.version = version

        # Directory containing the 'pa' and 'ui' subdirectories
        if version == 'current':
            self.root = CONFIG['pa_root']
        else:
            self.root = os.path.join(CONFIG['archive_root'], CONFIG['versions'][version])
        # internal use, keyed by resource_name
        self._units = {}
        self._things = {}

        # for inspection, using a friendly name
        self.units = collections.OrderedDict()
        self.weapons = {}

    def build_build_tree(self):
        for unit in sorted(self._units.values(), key=lambda u: (u.build_cost, u.name)):
            if unit.base_template:
                continue

            self.units[unit.safename] = unit

            if unit.buildable_types:
                r = get_restriction(unit.buildable_types)
            else:
                continue

            for other in self._units.values():
                if not other.base_template and r.satisfies(other):
                    unit.builds.add(other)
                    other.built_by.add(unit)

        # find a reference commander
        commanders = []
        for unit in self.units.values():
            base = unit.base
            while base:
                if base.safename == 'base_commander':
                    commanders.append(unit)
                    break
                else:
                    base = base.base
        commanders.sort(key=lambda x: x.name)

        # Mark all the other commanders as 'variants'
        for commander in commanders[1:]:
            commander.variant = True

        # Determine units that can actually be built
        for commander in commanders:
            commander.set_accessible()

    def load_units(self):
        unitlist = json.load(open(self.root + '/pa/units/unit_list.json'))['units']
        for u in unitlist:
            Unit(self, u)
        self.build_build_tree()

    def report(self):
        print('{0:>30s}  {1:>7s}  {2:>7s}  {3:>7s}'.format('Name', 'HP', 'DPS', 'salvo'))
        print('{0:>30s}  {1:>7s}  {2:>7s}  {2:>7s}'.format('-'*20, *['-'*7]*3))
        for unit in sorted(self.units.values(), key=lambda u: u.role):
            if unit.health > 0:
                print('{0.role:>30s}  {0.health:7.1f}  {0.dps:7.1f}  {0.salvo_damage:7.1f}'.format(unit))


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

    def __init__(self, db, resource_name):
        self.db = db

        with open(db.root + resource_name) as datafile:
            raw = json.load(datafile)

        if 'base_spec' in raw:
            base = self.__class__(self.db, raw['base_spec'])
            self.__dict__.update(base.__dict__)
            self.base = base

        self.resource_name = resource_name
        self.raw = raw
        self.db._things[self.resource_name] = self

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
    build_inefficiency = 0
    health = 0
    weapons = ()
    build_arms = ()
    misc_tools = ()
    production = Resources()
    consumption = Resources()
    storage = Resources()
    move_speed = 0
    turn_speed = 0
    acceleration = 0
    brake = 0
    tier = 0
    variant = False
    accessible = False

    vision_radius = 0
    underwater_vision_radius = 0
    orbital_vision_radius = 0
    radar_radius = 0
    sonar_radius = 0
    orbital_radar_radius = 0

    def __init__(self, db, resource_name):
        super().__init__(db, resource_name)
        db._units[resource_name] = self

        self.name = delocalize(self.raw.pop('display_name', self.safename))
        self.role = delocalize(self.raw.pop('unit_name', self.name))
        self.description = delocalize(self.raw.pop('description', ''))

        if 'unit_types' in self.raw:
            self.unit_types = set()
            for unit_type in self.raw.pop('unit_types'):
                assert unit_type.startswith('UNITTYPE_')
                self.unit_types.add(unit_type[9:])

        if 'Basic' in self.unit_types:
            self.tier = 1
        elif 'Advanced' in self.unit_types:
            self.tier = 2

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
                        self.weapons.append(Weapon(self.db, resource))
                    elif 'build_arm' in tool_name:
                        self.build_arms.append(BuildArm(self.db, resource))
                    else:
                        self.misc_tools.append(Thing(self.db, resource))
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

        if self.tool_consumption.metal:
            self.build_inefficiency = (self.tool_consumption.energy /
                                       self.tool_consumption.metal)

        self.weapon_consumption = Resources()
        for weapon in self.weapons:
            self.weapon_consumption.metal -= weapon.metal_rate
            self.weapon_consumption.energy -= weapon.energy_rate

        self.base_template = self.safename.startswith('base_')

        nav = self.raw.get('navigation', {})
        if 'move_speed' in nav:
            self.move_speed = nav.pop('move_speed')
        if 'turn_speed' in nav:
            self.turn_speed = nav.pop('turn_speed')
        if 'acceleration' in nav:
            self.acceleration = nav.pop('acceleration')
        if 'brake' in nav:
            self.brake = nav.pop('brake')

        try:
            recon = self.raw['recon']['observer'].pop('items')
        except KeyError:
            recon = []

        for item in recon:
            if item['channel'] == 'sight':
                if item['layer'] == 'surface_and_air':
                    self.vision_radius = item['radius']
                elif item['layer'] == 'underwater':
                    self.underwater_vision_radius = item['radius']
                elif item['layer'] == 'orbital':
                    self.orbital_vision_radius = item['radius']
                elif item['layer'] == 'celestial':
                    pass # not sure what this is...
                else:
                    print('unparsed recon item:', item)
            elif item['channel'] == 'radar':
                if item['layer'] == 'surface_and_air':
                    self.radar_radius = item['radius']
                elif item['layer'] == 'underwater':
                    self.sonar_radius = item['radius']
                elif item['layer'] == 'orbital':
                    self.orbital_radar_radius = item['radius']
                else:
                    print('unparsed recon item:', item)
            else:
                print('unparsed recon item:', item)


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

    def set_accessible(self):
        self.accessible = True
        for u in self.builds:
            if not u.accessible:
                u.set_accessible()

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

    def __init__(self, db, resource_name):
        super().__init__(db, resource_name)

        if 'rate_of_fire' in self.raw:
            self.rof = self.raw.pop('rate_of_fire')
        self.name = self.safename

        ammo_id = self.raw.pop('ammo_id', None)
        if ammo_id:
            if not isinstance(ammo_id, str):
                # Weird inconsistency with assault_bot_tool_weapon in 71459
                ammo_id = ammo_id[0]['id']
            self.ammo = Ammo(self.db, ammo_id)
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
    metal_cost = 0

    def __init__(self, db, resource_name):
        super().__init__(db, resource_name)

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
        if 'build_metal_cost' in self.raw:
            self.metal_cost = self.raw.pop('build_metal_cost')

    def __repr__(self):
        return '<Ammo: {!r}>'.format(self.name)


class BuildArm(Thing):
    metal_consumption = 0
    energy_consumption = 0

    def __init__(self, db, resource_name):
        super().__init__(db, resource_name)

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
        self.category = category

    def satisfies(self, unit):
        return self.category in unit.unit_types

    def __str__(self):
        return str(self.category)


class CompoundRestriction:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class CompoundAnd(CompoundRestriction):
    def satisfies(self, unit):
        return self.left.satisfies(unit) and self.right.satisfies(unit)

    def __str__(self):
        return '({} & {})'.format(self.left, self.right)


class CompoundOr(CompoundRestriction):
    def satisfies(self, unit):
        return self.left.satisfies(unit) or self.right.satisfies(unit)

    def __str__(self):
        return '({} | {})'.format(self.left, self.right)


class CompoundMinus(CompoundRestriction):
    def satisfies(self, unit):
        return self.left.satisfies(unit) and not self.right.satisfies(unit)

    def __str__(self):
        return '({} - {})'.format(self.left, self.right)


def _restriction(R):
    if '|' in R:
        i = R.index('|')
        return CompoundOr(_restriction(R[:i]), _restriction(R[i+1:]))
    elif '&' in R:
        i = R.index('&')
        return CompoundAnd(_restriction(R[:i]), _restriction(R[i+1:]))
    elif '-' in R:
        i = len(R) - list(reversed(R)).index('-') - 1
        return CompoundMinus(_restriction(R[:i]), _restriction(R[i+1:]))
    else:
        assert len(R) == 1, R
        if isinstance(R[0], str):
            return SimpleRestriction(R[0])
        else:
            return _restriction(R[0])

def get_restriction(text):
    special = set('|&-() ')
    # first pass: tokenize
    tokens = []
    word = []
    for c in text + ' ':
        if c in special:
            w = ''.join(word).strip()
            word = []
            if w:
                tokens.append(w)
            if c != ' ':
                tokens.append(c)
        else:
            word.append(c)

    # second pass: parse parentheses
    stack = []
    current = []
    for c in tokens:
        if c == '(':
            stack.append(current)
            current = []
        elif c == ')':
            stack[-1].append(current)
            current = stack.pop()
        else:
            current.append(c)
    return _restriction(current)

def load_all():
    dbs = {v: VersionDb(v) for v in CONFIG.get('versions', ())}

    for db in dbs.values():
        db.load_units()

    if 'pa_root' in CONFIG:
        dbs['current'] = VersionDb()
        dbs['current'].load_units()
    else:
        dbs['current'] = sorted(dbs.items())[-1][1]

    return dbs

if __name__ == '__main__':
    dbs = load_all()
