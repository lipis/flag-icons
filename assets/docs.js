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
}
