<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    % if defined('title'):
      <title>PADB - {{title}}</title>
    % else:
      <title>PADB</title>
    % end
    <link rel="stylesheet" href="/static/site.css">
  </head>
  <body>
    % include nav_bar
    <div class="content">
      % include
    </div>
  </body>
</html>
