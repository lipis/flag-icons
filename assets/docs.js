window.onload = function () {
  document.getElementById('btn-bootstrap').onclick = function() {
    console.log('shit');
    if (document.getElementById('bootstrap').rel == 'stylesheet') {
      document.getElementById('bootstrap').rel = 'none';
      document.getElementById('btn-bootstrap').innerHTML = 'Enable Bootstrap';
    } else {
      document.getElementById('bootstrap').rel = 'stylesheet';
      document.getElementById('btn-bootstrap').innerHTML = 'Disalbe Bootstrap';
    }
  }
}
