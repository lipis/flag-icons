window.LOG = function() {
  return typeof console !== 'undefined' && console !== null
    ? typeof console.log === 'function'
      ? console.log(...arguments)
      : void 0
    : void 0;
};

window.initCommon = () => {
  initLoadingButton();
  initConfirmButton();
  initPasswordShowButton();
  initTime();
  initAnnouncement();
  initRowLink();
};

window.initLoadingButton = () =>
  $('body').on('click', '.btn-loading', function() {
    $(this).button('loading');
  });

window.initConfirmButton = () =>
  $('body').on('click', '.btn-confirm', function() {
    if (!confirm($(this).data('message') || 'Are you sure?')) {
      event.preventDefault();
    }
  });

window.initPasswordShowButton = () =>
  $('body').on('click', '.btn-password-show', function() {
    const $target = $($(this).data('target'));
    $target.focus();
    if ($(this).hasClass('active')) {
      $target.attr('type', 'password');
    } else {
      $target.attr('type', 'text');
    }
  });

window.initTime = () => {
  if ($('time').length > 0) {
    const recalculate = function() {
      $('time[datetime]').each(function() {
        const date = moment.utc($(this).attr('datetime'));
        const diff = moment().diff(date, 'days');
        if (diff > 25) {
          $(this).text(date.local().format('YYYY-MM-DD'));
        } else {
          $(this).text(date.fromNow());
        }
        $(this).attr(
          'title',
          date.local().format('dddd, MMMM Do YYYY, HH:mm:ss Z'),
        );
      });
      setTimeout(recalculate, 1000 * 45);
    };
    recalculate();
  }
};

window.initAnnouncement = () => {
  $('.alert-announcement button.close').click(() =>
    typeof sessionStorage !== 'undefined' && sessionStorage !== null
      ? sessionStorage.setItem(
          'closedAnnouncement',
          $('.alert-announcement').html(),
        )
      : void 0,
  );
  if (
    (typeof sessionStorage !== 'undefined' && sessionStorage !== null
      ? sessionStorage.getItem('closedAnnouncement')
      : void 0) !== $('.alert-announcement').html()
  ) {
    $('.alert-announcement').show();
  }
};

window.initRowLink = () => {
  $('body').on('click', '.row-link', function() {
    window.location.href = $(this).data('href');
  });
  $('body').on('click', '.not-link', event => event.stopPropagation());
};

window.clearNotifications = () => $('#notifications').empty();

window.showNotification = (message, category) => {
  if (category == null) {
    category = 'warning';
  }
  clearNotifications();
  if (!message) {
    return;
  }
  $('#notifications').append(
    `<div class="alert alert-dismissable alert-${category}"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>${message}</div>`,
  );
};
