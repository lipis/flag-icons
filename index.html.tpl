<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://lipis.github.io/flag-icon-css/" />

    <title>SVG Country Flags | flag-icon-css</title>

    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" rel="stylesheet" id="bootstrap">
    <link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css" rel="stylesheet">
    <link href="./assets/docs.css" rel="stylesheet">
    <link href="./css/flag-icon.css" rel="stylesheet">
  </head>

  <body>
    <div class="jumbotron">
      <div class="container">
        <h1>flag-icon-css</h1>
        <p>
          A collection of all country flags in SVG — plus the CSS for easier integration.
        </p>
        <a href="https://github.com/lipis/flag-icon-css" class="btn btn-outline btn-lg"><span class="fa fa-github"></span> View on GitHub</a>
        <a href="https://github.com/lipis/flag-icon-css/archive/master.zip" class="btn btn-outline btn-lg"><span class="fa fa-download"></span> Download</a>
        <ul class="jumbotron-links">
          <li><a href="https://lipis.github.io/bootstrap-social"><span class="fa fa-facebook"></span> bootstrap-social</a></li>
        </ul>
      </div>
      <div class="bottom">
        <iframe src="https://ghbtns.com/github-btn.html?user=lipis&amp;repo=flag-icon-css&amp;type=watch&amp;count=true" class="social-share"></iframe>
      </div>
    </div>
    <script>
      if (window.location.hostname.indexOf('github') > 0) {
        window.location.replace("http://flag-icon-css.lip.is/");
      }
    </script>
    <div class="container">
      <section id="examples">
        <div class="page-header">
          <h1>Examples (inline with text)</h1>
        </div>
        <div class="no-wrap"><%
        _.forEach(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'], function(tag) { %>
          <<%= tag %>>
            <%= tag %>
            <span class="flag-icon flag-icon-gr"></span>
            <span class="flag-icon flag-icon-squared flag-icon-gr"></span>
            <span class="label label-default"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-primary"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-success"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-info"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-warning"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-danger"><span class="flag-icon flag-icon-gr"></span> GR</span>
          </<%= tag %>><%
        }) %>
          <p class="lead">
            p.lead
            <span class="flag-icon flag-icon-gr"></span>
            <span class="flag-icon flag-icon-squared flag-icon-gr"></span>
            <span class="label label-default"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-primary"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-success"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-info"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-warning"><span class="flag-icon flag-icon-gr"></span> GR</span>
            <span class="label label-danger"><span class="flag-icon flag-icon-gr"></span> GR</span>
          </p>
        </section>
      </section>
      <section id="more" class="d">
        <div class="page-header">
          <h1>Examples (on any element)</h1>
        </div>
        <div class="row">
          <div class="col-lg-3 col-md-4 col-sm-4 col-xs-6">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-gr"></div>
            </div>
          </div>
          <div class="col-lg-3 col-md-4 col-sm-4 col-xs-6">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-es"></div>
            </div>
          </div>
          <div class="col-lg-3 col-md-4 col-sm-4 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-gb"></div>
            </div>
          </div>
          <div class="col-lg-3 col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-dk"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-de"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-ru"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-is"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-fr"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-ge"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-ar"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-br"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-jp"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3 hidden-xs">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-in"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-sa"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-si"></div>
            </div>
          </div>
          <div class="col-sm-2 col-xs-3 visible-lg">
            <div class="flag-wrapper">
              <div class="img-thumbnail flag flag-icon-background flag-icon-ca"></div>
            </div>
          </div>
        </div>
      </section>
      <section class="all-flags">
        <div class="page-header">
          <h1>ISO 3166-1 Flags</h1>
        </div>
        <div class="row"><%
				_.forEach(flagsList, function(countryCode) { %>
          <div class="col-md-1 col-sm-2 col-xs-3"><div class="flag-wrapper"><div class="img-thumbnail flag flag-icon-background flag-icon-<%= countryCode %>" title="<%= countryCode %>" id="<%= countryCode %>"></div></div></div><%
				}) %>
        </div>
      </section>
      <section class="all-flags">
        <div class="page-header">
          <h1>More Flags</h1>
        </div>
        <div class="row"><%
				_.forEach(moreFlags, function(countryCode) { %>
          <div class="col-md-1 col-sm-2 col-xs-3"><div class="flag-wrapper"><div class="img-thumbnail flag flag-icon-background flag-icon-<%= countryCode %>" title="<%= countryCode %>" id="<%= countryCode %>"></div></div></div><%
				}) %>
        </div>
      </section>
    </div>

    <footer>
      <ul class="links">
        <li><a href="https://lip.is">Lipis</a></li>
        <li><a href="https://github.com/lipis"><span class="fa fa-github"></span> GitHub</a></li>
        <li><a href="https://twitter.com/lipis"><span class="fa fa-twitter"></span> Twitter</a></li>
        <li><a href="https://google.com/+PanayiotisLipiridis"><span class="fa fa-google-plus"></span> Google+</a></li>
      </ul>
    </footer>
    <a href="https://github.com/lipis/flag-icon-css" title="Fork me on GitHub" class="github-corner"><svg width="80" height="80" viewbox="0 0 250 250"><title>Fork me on GitHub</title><path d="M0 0h250v250"></path><path d="M127.4 110c-14.6-9.2-9.4-19.5-9.4-19.5 3-7 1.5-11 1.5-11-1-6.2 3-2 3-2 4 4.7 2 11 2 11-2.2 10.4 5 14.8 9 16.2" fill="currentColor" style="transform-origin:130px 110px" class="octo-arm"></path><path d="M113.2 114.3s3.6 1.6 4.7.6l15-13.7c3-2.4 6-3 8.2-2.7-8-11.2-14-25 3-41 4.7-4.4 10.6-6.4 16.2-6.4.6-1.6 3.6-7.3 11.8-10.7 0 0 4.5 2.7 6.8 16.5 4.3 2.7 8.3 6 12 9.8 3.3 3.5 6.7 8 8.6 12.3 14 3 16.8 8 16.8 8-3.4 8-9.4 11-11.4 11 0 5.8-2.3 11-7.5 15.5-16.4 16-30 9-40 .2 0 3-1 7-5.2 11l-13.3 11c-1 1 .5 5.3.8 5z" fill="currentColor" class="octo-body"></path></svg><style> .github-corner svg{position:absolute;right:0;top:0;mix-blend-mode:darken;color:#ffffff;fill:#000000;}.github-corner:hover .octo-arm{animation:octocat-wave .56s;}@keyframes octocat-wave{0%, 100%{transform:rotate(0);}20%, 60%{transform:rotate(-20deg);}40%, 80%{transform:rotate(10deg);}}</style></a>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
    <script src="./assets/docs.js"></script>
  </body>
</html>
