<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    % if defined('title'):
      <title>PADB - {{title}}</title>
    % else:
      <title>PADB</title>
    % end
    <link rel="stylesheet" href="/static/flatly.css">
    <link rel="stylesheet" href="/static/site.css">
  </head>
  <body>
    % include nav_bar version=version, unit=get('unit')
    <div class="content">
      % include
    </div>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <script src="/static/bootstrap.min.js"></script>
  </body>
</html>
