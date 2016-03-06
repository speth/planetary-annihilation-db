<h1>Planetary Annihilation Unit Database</h1>
<div class="columns">
  <div>
    % include units_list heading='Factories', units=factories, link='factories', db=db, WEB_BASE=WEB_BASE
    % include units_list heading='Construction Units', units=builders, link='builders', db=db, WEB_BASE=WEB_BASE
    % include units_list heading='Economy', units=economy, link='economy', db=db, WEB_BASE=WEB_BASE
    % include units_list heading='Reconnaissance', units=recon, link='recon', db=db, WEB_BASE=WEB_BASE
  </div>
  <div>
    % include units_list heading='Vehicles', units=vehicles, link='vehicles', db=db, WEB_BASE=WEB_BASE
    % include units_list heading='Bots', units=bots, link='bots', db=db, WEB_BASE=WEB_BASE
    % include units_list heading='Aircraft', units=air, link='air', db=db, WEB_BASE=WEB_BASE
    % include units_list heading='Naval', units=naval, link='naval', db=db, WEB_BASE=WEB_BASE
  </div>
  <div>
    % include units_list heading='Titans', units=titans, link='titans', db=db, WEB_BASE=WEB_BASE
    % include units_list heading='Defensive Structures', units=defense, link='defense', db=db, WEB_BASE=WEB_BASE
    % include units_list heading='Orbital', units=orbital, link='orbital', db=db, WEB_BASE=WEB_BASE
    % include units_list heading='Other', units=other, link='other', db=db, WEB_BASE=WEB_BASE
  </div>
</div>
<div class="clear"></div>
% rebase page db=db, WEB_BASE=WEB_BASE
