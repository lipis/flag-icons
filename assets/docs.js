window.onload = function () {
  $('.all-flags .flag-icon-background').click(function(event){
    const flag = $(event.currentTarget).attr('title');
    const w = 640;
    const h = 480;
    const left = window.outerWidth / 2 + window.screenX - ( w / 2);
    const top = window.outerHeight / 2 + window.screenY - ( h / 2);

    if (flag) {
      window.open('flags/4x3/' + flag + '.svg', 'flag-4x3', 'width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);
    }
  });
}
