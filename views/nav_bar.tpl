% import webunits
% suffix = '?version='+version if version != 'current' else ''
<div class="navbar navbar-default navbar-fixed-top">
  <div class="container-fluid">
  <div class="navbar-collapse collapse navbar-responsive-collapse">
    <ul class="nav navbar-nav">
      <li><a href="/{{suffix}}">Home</a></li>
      <li><a href="/table/factories{{suffix}}">Factories</a></li>
      <li><a href="/table/builders{{suffix}}">Builders</a></li>
      <li><a href="/table/economy{{suffix}}">Economy</a></li>
      <li><a href="/table/vehicles{{suffix}}">Vehicles</a></li>
      <li><a href="/table/bots{{suffix}}">Bots</a></li>
      <li><a href="/table/air{{suffix}}">Air</a></li>
      <li><a href="/table/naval{{suffix}}">Naval</a></li>
      <li><a href="/table/orbital{{suffix}}">Orbital</a></li>
      <li><a href="/table/defense{{suffix}}">Defense</a></li>
      <li><a href="/table/other{{suffix}}">Other</a></li>
    </ul>
    <ul class="nav navbar-nav navbar-right">
      <li><p class="navbar-text">{{version}}</p></li>
    </ul>
  </div>
  </div>
</div>
