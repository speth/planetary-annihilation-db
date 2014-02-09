% import webunits
% suffix = '?version='+version if version != 'current' else ''
<div class="navbar">
  <div style="float:left">
    <a href="/{{suffix}}">Home</a> &bull;
    <a href="/table/factories{{suffix}}">Factories</a> &bull;
    <a href="/table/builders{{suffix}}">Builders</a> &bull;
    <a href="/table/economy{{suffix}}">Economy</a> &bull;
    <a href="/table/vehicles{{suffix}}">Vehicles</a> &bull;
    <a href="/table/bots{{suffix}}">Bots</a> &bull;
    <a href="/table/air{{suffix}}">Air</a> &bull;
    <a href="/table/naval{{suffix}}">Naval</a> &bull;
    <a href="/table/orbital{{suffix}}">Orbital</a> &bull;
    <a href="/table/defense{{suffix}}">Defense</a> &bull;
    <a href="/table/other{{suffix}}">Other</a>
  </div>
  <div style="float:right; color: #AAAAAA">
    {{webunits.db.version}}
  </div>
  <div style="clear:both"></div>
</div>
