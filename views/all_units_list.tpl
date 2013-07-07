<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>PADB</title>
    <link rel="stylesheet" href="/static/site.css">
  </head>
  <body>
    <h1>Planetary Annihilation Unit Database</h1>
    <div class="columns">
      <div>
        % include units_list heading='Factories', units=factories, link='factories'
        % include units_list heading='Construction Units', units=builders, link='builders'
        % include units_list heading='Economic Structures', units=economy, link='economy'
      </div>
      <div>
        % include units_list heading='Vehicles', units=vehicles, link='vehicles'
        % include units_list heading='Bots', units=bots, link='bots'
        % include units_list heading='Aircraft', units=air, link='air'
        % include units_list heading='Naval', units=naval, link='naval'
      </div>
      <div>
        % include units_list heading='Defensive Structures', units=defense, link='defense'
        % include units_list heading='Orbital', units=orbital, link='orbital'
        % include units_list heading='Other Structures', units=other, link='other'
      </div>
    </div>
    <div class="clear"></div>
  </body>
</html>
