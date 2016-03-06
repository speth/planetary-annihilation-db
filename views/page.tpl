<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    % if defined('title'):
      <title>PADB - {{title}}</title>
    % else:
      <title>PADB</title>
    % end
    <link rel="stylesheet" href="{{WEB_BASE}}/static/flatly.css">
    <link rel="stylesheet" href="{{WEB_BASE}}/static/site.css">
  </head>
  <body>
    % include nav_bar db=db, WEB_BASE=WEB_BASE, unit=get('unit'), hide_version=get('hide_nav_version')
    <div class="content">
      % include
    </div>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-cookie/1.4.1/jquery.cookie.min.js"></script>
    <script src="{{WEB_BASE}}/static/bootstrap.min.js"></script>
    <script src="{{WEB_BASE}}/static/utils.js"></script>
  </body>
</html>
