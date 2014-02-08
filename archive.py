import units
import tarfile
import os

def save_db_info(archive_name):
    archive_root = 'padb-data'
    if not units.THINGS:
        units.load_units()

    with tarfile.open(archive_name, 'w:bz2') as archive:
        archive.add(units.PA_ROOT + '/pa/units/unit_list.json',
                    arcname=archive_root + '/pa/units/unit_list.json')

        for filename in units.THINGS:
            archive.add(units.PA_ROOT + filename,
                        arcname=archive_root + filename)

        for unit in units.UNITS.values():

            iconpath = '/ui/alpha/live_game/img/build_bar/units/{}.png'.format(unit.safename)
            if os.path.exists(units.PA_ROOT + iconpath):
                archive.add(units.PA_ROOT + iconpath,
                            arcname=archive_root + iconpath)

if __name__ == '__main__':
    import sys
    save_db_info(sys.argv[1])
