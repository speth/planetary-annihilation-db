import json
import pprint
import collections
import os
import re
import copy
import collections

try:
    CONFIG = json.load(open('padb.json'))
except IOError:
    print("""
****************************************************************
Error reading configuration. Create a file named 'padb.json'
in the current directory with an entry in the following format:

{
    "pa_root": "C:/Path/To/PlanetaryAnnihilation/PA/media",
    "expansion": "pa_ex1",
    "archive_root": "C:/Path/To/Archived/Files",
    "mods_root": "C:/Path/to/server_mods/directory",
    "versions": [["73823", "units-73823"],
                 ["76766", "units-76766"]]
}

At least one of "pa_root" or "versions" must be supplied. See README.md for
additional information. The "expansion" flag only applies to the active build,
not to archived versions. Archives are generated separately for each expansion.

****************************************************************
""")
    raise


VERSION_DIRS = collections.OrderedDict()
DESCRIPTIONS = collections.OrderedDict()

for description, directory in CONFIG['versions']:
    v0 = re.sub(r'.*?(\d{4,}).*', r'\1', description)

    version = v0
    suffix = 'a'
    while version in DESCRIPTIONS:
        version = v0 + suffix
        suffix = chr(ord(suffix)+1)

    VERSION_DIRS[version] = directory
    DESCRIPTIONS[version] = description

def delocalize(text):
    if text.startswith('!LOC('): # old-sytle localization
        return re.sub(r'!LOC\(.*?\):(.*)', r'\1', text)
    elif text.startswith('!LOC:'): # new-style localization
        return text[5:]
    else:
        return text


class VersionDb:
    def __init__(self, version='current', active_mods=(), expansion=None):
        self.version = version
        self.description = DESCRIPTIONS.get(version, version)
        self.active_mods = active_mods

        # None or the name of the directory which shadows 'pa', e.g. 'pa_ex1'
        if version =='current':
            self.expansion = CONFIG.get("expansion", None)
        else:
            self.expansion = None

        # Directory containing the 'pa' and 'ui' subdirectories
        if version == 'current':
            self.root = CONFIG['pa_root']
        else:
            self.root = os.path.join(CONFIG['archive_root'], VERSION_DIRS[version])

        # data_dirs includes directories containing files overridden by server mods
        self.mod_dirs = []
        for mod in active_mods:
            self.mod_dirs.append(AVAILABLE_MODS[mod]['dir'])
        self.data_dirs = self.mod_dirs + [self.root]

        # internal use, keyed by resource_name
        self._units = {}
        self._things = {}

        # for inspection, using a friendly name
        self.units = collections.OrderedDict()
        self.weapons = {}

        # unique short names for each resource
        self.safe_names = {} # full resource path -> safe name
        self.full_names = {} # safe name -> full resource path

        # Parsed JSON objects. Keys are the json file, minus the extension
        self.json = {}

    def get_safe_name(self, resource_name):
        if resource_name in self.safe_names:
            return self.safe_names[resource_name]

        # Find a unique short name
        dirname, filename = resource_name.rsplit('/', 2)[-2:]
        filename = filename.split('.')[0]
        if filename not in self.full_names:
            safe_name = filename
        elif dirname not in self.full_names:
            safe_name = dirname
        else:
            # Fallback mechanism for units which do not follow Uber's convention
            # where the unit blueprint has a unique name which matches the
            # directory name.
            i = 2
            while True:
                safe_name = '{}_{}'.format(dirname, i)
                if safe_name not in self.full_names:
                    break
                i += 1

        self.safe_names[resource_name] = safe_name
        self.full_names[safe_name] = resource_name
        return safe_name

    def get_json(self, resource_name):
        if resource_name in self.json:
            return self.json[resource_name]

        if self.expansion and resource_name.startswith('/pa/'):
            names = ('/{}/{}'.format(self.expansion, resource_name[4:]),
                     resource_name)
        else:
            names = (resource_name,)

        for directory in self.data_dirs:
            for resource_name in names:
                path = directory + resource_name
                if os.path.exists(path):
                    with open(path) as datafile:
                        j = json.load(datafile)
                        for name in names:
                            self.json[name] = j
                        return j

        print('failed to load {!r} (version {})'.format(resource_name, self.version))
        self.json[resource_name] = {}
        return self.json[resource_name]

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

        # find all commanders
        commanders = [u for u in self.units.values()
                      if 'Commander' in u.unit_types]
        commanders.sort(key=lambda x: x.name)

        # Mark all but the first as 'variants'
        for commander in commanders[1:]:
            commander.variant = True

        # Determine units that can actually be built
        for commander in commanders:
            commander.set_accessible()

    def load_units(self):
        unitlist = self.get_json('/pa/units/unit_list.json')['units']
        for u in unitlist:
            Unit(self, u)
        self.build_build_tree()
        self.apply_corrections()

    def apply_corrections(self):
        """ Fix things that are not correctly indicated by the unit JSON files"""

        # These units are not actually buildable
        disabled = ['tutorial_titan_commander', 'sea_mine']
        for name in disabled:
            if name in self.units:
                self.units[name].accessible = False

        if 'titan_structure' in self.units:
            self.units['titan_structure'].tier = 3
            self.units['titan_structure'].unit_types.add('Titan')

        if 'teleporter' in self.units:
            self.units['teleporter'].tier = 1

        if 'mining_platform' in self.units:
            self.units['mining_platform'].tier = 2

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
        raw = copy.deepcopy(self.db.get_json(resource_name))

        if 'base_spec' in raw:
            base = self.__class__(self.db, raw['base_spec'])
            self.__dict__.update(base.__dict__)
            self.base = base

        self.resource_name = resource_name
        self.raw = raw
        self.db._things[self.resource_name] = self
        self.safename = self.db.get_safe_name(self.resource_name)

    @property
    def json(self):
        return self.db.get_json(self.resource_name)

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
    build_range = 0
    assist_buildable_only = None
    spawn_layers = ()
    amphibious = False
    hover = False
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

    unit_storage = 0
    stored_unit_type = 'unit'

    vision_radius = 0
    underwater_vision_radius = 0
    orbital_vision_radius = 0
    mine_vision_radius = 0
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

        if 'spawn_layers' in self.raw:
            layers = self.raw.pop('spawn_layers')
            if layers == 'WL_LandHorizontal':
                self.spawn_layers = ('land',)
            elif layers == 'WL_WaterSurface':
                self.spawn_layers = ('water surface',)
            elif layers == 'WL_DeepWater':
                self.spawn_layers = ('deep water',)
            elif layers == 'WL_Air':
                self.spawn_layers = ('air',)
            elif (layers == 'WL_AnyHorizontalGroundOrWaterSurface' or
                  layers == 'WL_AnySurface'):
                self.spawn_layers = ('land', 'water surface')
            elif layers == 'WL_Orbital':
                self.spawn_layers = ('orbital',)
            else:
                print('Unknown spawn layer:', layers)

        if 'Basic' in self.unit_types:
            self.tier = 1
        elif 'Titan' in self.unit_types:
            self.tier = 3
        elif 'Advanced' in self.unit_types:
            self.tier = 2

        if 'buildable_types' in self.raw:
            self.buildable_types = self.raw.pop('buildable_types')

        if 'can_only_assist_with_buildable_items' in self.raw:
            self.assist_buildable_only = self.raw.pop('can_only_assist_with_buildable_items')

        self.builds = set()
        self.built_by = set()

        if 'build_metal_cost' in self.raw:
            self.build_cost = self.raw.pop('build_metal_cost')
        if 'max_health' in self.raw:
            self.health = self.raw.pop('max_health')

        if 'tools' in self.raw or 'death_weapon' in self.raw:
            self.weapons = []
            self.build_arms = []
            self.misc_tools = []

            tools = {}
            for tool in self.raw.pop('tools', ()):
                resource = tool['spec_id']
                if resource in tools:
                    tools[resource]['count'] += 1
                else:
                    tools[resource] = tool
                    tools[resource]['count'] = 1

            # The information available to identify tool types has changed over
            # the builds, so there are multiple selection criteria for some tool
            # types.
            for resource,tool in tools.items():
                name = tool['spec_id'].rsplit('/')[-1].split('.')[0]
                try:
                    if ('weapon' in name or 'primary_weapon' in name or
                        'aim_weapon' in name or 'secondary_weapon' in name):
                        w = Weapon(self.db, resource)
                        self.weapons.append(w)
                        w.count = tool['count']
                        if 'death_weapon' in tool:
                            w.death_explosion = True
                        if 'projectiles_per_fire' in tool:
                            w.projectiles_per_fire = tool['projectiles_per_fire']
                    elif 'build_arm' in name or tool.get('build_arm'):
                        self.build_arms.append(BuildArm(self.db, resource))
                        self.build_arms[-1].count = tool['count']
                    else:
                        test = Tool(self.db, resource)
                        if test.tool_type == 'TOOL_Weapon':
                            w = Weapon(self.db, resource)
                            self.weapons.append(w)
                            w.count = tool['count']
                            if 'death_weapon' in tool:
                                w.death_explosion = True
                            if 'projectiles_per_fire' in tool:
                                w.projectiles_per_fire = tool['projectiles_per_fire']
                        else:
                            print('unclassified tool for {}: {}'.format(
                                  self.name, tool))
                            self.misc_tools.append(test)
                            self.misc_tools[-1].count = tool['count']
                except IOError:
                    pass

            death_weapon = self.raw.pop('death_weapon', {})
            if 'ground_ammo_spec' in death_weapon:
                w = Weapon(self.db, death_weapon['ground_ammo_spec'])
                w.count = 1
                w.death_explosion = True
                # Keep a reference to this in case it becomes interesting
                if 'air_ammo_spec' in death_weapon:
                    w.air_ammo = Ammo(self.db, death_weapon['air_ammo_spec'])
                self.weapons.append(w)

        self.dps = sum(w.dps*w.count for w in self.weapons
                       if not w.death_explosion and not w.self_destruct)
        self.salvo_damage = sum(w.damage*w.count for w in self.weapons)
        if self.build_arms:
            self.build_range = max(arm.range for arm in self.build_arms)

        # Economy
        for field in ('consumption', 'production', 'storage'):
            data = self.raw.pop(field, {})
            base = getattr(self, field)
            setattr(self, field, Resources(base.metal, base.energy))
            if 'metal' in data:
                getattr(self, field).metal = data['metal']
            if 'energy' in data:
                getattr(self, field).energy = data['energy']

        if 'teleporter' in self.raw:
            self.consumption.energy = self.raw['teleporter']['energy_demand']

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
            self.weapon_consumption.metal -= weapon.metal_rate * weapon.count
            self.weapon_consumption.energy -= weapon.energy_rate * weapon.count

        self.base_template = self.safename.startswith('base_')

        factory = self.raw.get('factory')
        if factory and factory.get('store_units'):
            spawn_points = factory.get('spawn_points', ())
            self.unit_storage = len(spawn_points)
            if self.unit_storage and 'missile' in spawn_points[0]:
                self.stored_unit_type = 'missile'

        nav = self.raw.get('navigation', {})
        if 'move_speed' in nav:
            self.move_speed = nav.pop('move_speed')
        if 'turn_speed' in nav:
            self.turn_speed = nav.pop('turn_speed')
        if 'acceleration' in nav:
            self.acceleration = nav.pop('acceleration')
        if 'brake' in nav:
            self.brake = nav.pop('brake')
        nav_type = nav.pop('type', '')
        if nav_type == 'amphibious':
            self.amphibious = True
        elif nav_type == 'hover':
            self.hover = True

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
                elif item['layer'] == 'mine':
                    self.mine_vision_radius = item['radius']
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
        return '<Unit: {} {!r}>'.format(self.safename, self.role)


class Tool(Thing):
    tool_type = None

    def __init__(self, db, resource_name):
        super().__init__(db, resource_name)

        if 'tool_type' in self.raw:
            self.tool_type = self.raw.pop('tool_type')


class Weapon(Tool):
    rof = 0.0
    ammo = None
    dps = 0.0
    damage = 0.0
    projectiles_per_fire = 1
    muzzle_velocity = 0.0
    splash_damage = 0.0
    splash_radius = 0
    full_damage_radius = 0
    max_range = 0
    count = 1
    self_destruct = False
    death_explosion = False

    metal_rate = 0
    energy_rate = 0
    metal_per_shot = 0
    energy_per_shot = 0

    ammo_source = None
    ammo_demand = 0 # rate at which stored ammo recharges
    ammo_per_shot = 0
    ammo_capacity = 0
    ammo_drain_time = 0
    ammo_recharge_time = 0
    ammo_shots_to_drain = 0

    yaw_range = 0
    yaw_rate = 0
    pitch_rate = 0
    pitch_range = 0

    target_layers = ()

    def __init__(self, db, resource_name):
        super().__init__(db, resource_name)

        if 'rate_of_fire' in self.raw:
            self.rof = self.raw.pop('rate_of_fire')
        self.name = self.safename

        ammo_id = self.raw.pop('ammo_id', None)

        # Combine Ammo / weapon info for death explosions
        if ammo_id is None and 'ammo_type' in self.raw:
            ammo_id = resource_name

        if ammo_id:
            if not isinstance(ammo_id, str):
                # Weird inconsistency with assault_bot_tool_weapon in 71459
                ammo_id = ammo_id[0]['id']
            self.ammo = Ammo(self.db, ammo_id)
            self.damage = self.ammo.damage
            self.muzzle_velocity = self.ammo.muzzle_velocity
            self.splash_damage = self.ammo.splash_damage
            self.splash_radius = self.ammo.splash_radius
            self.full_damage_radius = self.ammo.full_damage_radius

        if 'max_range' in self.raw:
            self.max_range = self.raw.pop('max_range')

        if 'ammo_source' in self.raw:
            self.ammo_source = self.raw.pop('ammo_source')
            # Don't inherit these values
            self.energy_rate = 0
            self.energy_per_shot = 0
            self.metal_rate = 0
            self.metal_per_shot = 0

        if self.ammo_source:
            if 'ammo_demand' in self.raw:
                self.ammo_demand = self.raw.pop('ammo_demand')
                self.ammo_capacity = self.raw.pop('ammo_capacity')
            if 'ammo_per_shot' in self.raw:
                self.ammo_per_shot = self.raw.pop('ammo_per_shot')
            if self.ammo_source == 'time':
                self.ammo_demand = 1

            if self.ammo_demand:
                self.ammo_recharge_time = self.ammo_capacity / self.ammo_demand
            else:
                self.ammo_recharge_time = 0

            if self.ammo_capacity == self.ammo_per_shot and self.ammo_recharge_time:
                # Actual rate of fire may be strictly limited by ammo consumption
                self.rof = min(self.rof, 1 / self.ammo_recharge_time)

            rate = round(self.ammo_per_shot * self.rof, 2)
            if self.ammo_demand and rate > self.ammo_demand:
                t = round(self.ammo_capacity / (rate - self.ammo_demand), 2)
                self.ammo_shots_to_drain = int(self.rof * t)
                self.ammo_drain_time = round(self.ammo_shots_to_drain / self.rof, 2)
            elif self.ammo_drain_time:
                self.ammo_drain_time = 0

            consumption_rate = min(self.ammo_demand,
                                   round(self.ammo_per_shot * self.rof, 2))

            if self.ammo_source == 'energy':
                self.energy_rate = - consumption_rate
                self.energy_per_shot = self.ammo_per_shot
            elif self.ammo_source == 'metal':
                self.metal_rate = - consumption_rate
                self.metal_per_shot = self.ammo_per_shot
            elif self.ammo_source in ('infinite', 'time', 'factory'):
                pass
            else:
                print('Unhandled ammo source {!r} for {}'.format(self.ammo_source, resource_name))


        if 'target_layers' in self.raw:
            self.target_layers = [layer[3:] if layer.startswith('WL_') else layer
                                  for layer in self.raw.pop('target_layers', ())]

        if (self.raw.pop('self_destruct', False) or
            self.raw.pop('only_fire_once', False)):
            self.self_destruct = True

        if 'yaw_range' in self.raw:
            self.yaw_range = self.raw.pop('yaw_range')
        if 'yaw_rate' in self.raw:
            self.yaw_rate = self.raw.pop('yaw_rate')
        if 'pitch_range' in self.raw:
            self.pitch_range = self.raw.pop('pitch_range')
        if 'pitch_rate' in self.raw:
            self.pitch_rate = self.raw.pop('pitch_rate')

    def __repr__(self):
        return '<Weapon: {} {!r}>'.format(self.safename, self.name)

    @property
    def dps(self):
        return round(self.rof * self.damage * self.projectiles_per_fire, 2)

class Ammo(Thing):
    damage = 0.0
    full_damage_radius = 0
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
        if 'full_damage_splash_radius' in self.raw:
            self.full_damage_radius = self.raw.pop('full_damage_splash_radius')
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
        return '<Ammo: {} {!r}>'.format(self.safename, self.name)


class BuildArm(Tool):
    metal_consumption = 0
    energy_consumption = 0
    range = 0

    def __init__(self, db, resource_name):
        super().__init__(db, resource_name)

        self.name = self.resource_name.rsplit('/', 1)[1].split('.')[0]
        demand = self.raw.pop('construction_demand', {})
        if 'metal' in demand:
            self.metal_consumption = demand.get('metal')
        if 'energy' in demand:
            self.energy_consumption = demand.get('energy')
        if 'max_range' in self.raw:
            self.range = self.raw.pop('max_range')

    def __repr__(self):
        return '<Build Arm: {} {!r}>'.format(self.safename, self.name)


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

AVAILABLE_MODS = {}
def load_mods():
    if 'mods_root' not in CONFIG:
        return
    for f in os.listdir(CONFIG['mods_root']):
        infoname = os.path.join(CONFIG['mods_root'], f, 'modinfo.json')
        if os.path.exists(infoname):
            modinfo = json.load(open(infoname))
            modinfo['dir'] = os.path.join(CONFIG['mods_root'], f)
            AVAILABLE_MODS[modinfo['identifier']] = modinfo

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

load_mods()

if __name__ == '__main__':
    dbs = load_all()
