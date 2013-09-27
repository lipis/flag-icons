window.onload = function () {
  document.getElementById('btn-bootstrap').onclick = function() {
    if (document.getElementById('bootstrap').rel == 'stylesheet') {
      document.getElementById('bootstrap').rel = 'styleshit';
      document.getElementById('btn-bootstrap').innerHTML = 'Enable Bootstrap';
    } else {
      document.getElementById('bootstrap').rel = 'stylesheet';
      document.getElementById('btn-bootstrap').innerHTML = 'Disable Bootstrap';
    }
  }
}
