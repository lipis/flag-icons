window.initAuth = () => {
  $('.remember').change(() => {
    let href;
    const buttons = $('.btn-social')
      .toArray()
      .concat($('.btn-social-icon').toArray());
    const remember = $('.remember input').is(':checked');
    for (const button of buttons) {
      href = $(button).prop('href');
      if (remember) {
        $(button).prop('href', `${href}&remember=true`);
      } else {
        $(button).prop('href', href.replace('&remember=true', ''));
      }
    }
  });
  $('.remember').change();
};
