window.onload = function () {
  document.getElementById('btn-bootstrap').onclick = function() {
    if (document.getElementById('bootstrap').rel == 'stylesheet') {
      document.getElementById('bootstrap').rel = 'styleshit';
      document.getElementById('btn-bootstrap').innerHTML = document.getElementById('btn-bootstrap').innerHTML.replace('Disable', 'Enable');
    } else {
      document.getElementById('bootstrap').rel = 'stylesheet';
      document.getElementById('btn-bootstrap').innerHTML = document.getElementById('btn-bootstrap').innerHTML.replace('Enable', 'Disable');
    }
  }

  $('.all-flags .flag-icon-background').click(function(event){
    var flag = $(event.currentTarget).attr('title');
    var w = 640;
    var h = 480;
    var left = (screen.width / 2) - (w / 2);
    var top = (screen.height / 2) - (h / 2);

    if (flag) {
      window.open('flags/4x3/' + flag + '.svg', 'flag-4x3', 'width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);
    }
  });
}
