window.initUserList = () => {
  initUserSelections();
  initUserDeleteBtn();
  initUserMergeBtn();
};

const initUserSelections = () => {
  $('input[name=user_db]').each(function() {
    userSelectRow($(this));
  });
  $('#select-all').change(function() {
    $('input[name=user_db]').prop('checked', $(this).is(':checked'));
    $('input[name=user_db]').each(function() {
      userSelectRow($(this));
    });
  });
  $('input[name=user_db]').change(function() {
    userSelectRow($(this));
  });
};

const userSelectRow = $element => {
  updateUserSelections();
  $('input[name=user_db]').each(() => {
    const id = $element.val();
    $(`#${id}`).toggleClass('warning', $element.is(':checked'));
  });
};

const updateUserSelections = () => {
  const selected = $('input[name=user_db]:checked').length;
  $('#user-actions').toggleClass('hidden', selected === 0);
  $('#user-merge').toggleClass('hidden', selected < 2);
  if (selected === 0) {
    $('#select-all').prop('indeterminate', false);
    $('#select-all').prop('checked', false);
  } else if ($('input[name=user_db]:not(:checked)').length === 0) {
    $('#select-all').prop('indeterminate', false);
    $('#select-all').prop('checked', true);
  } else {
    $('#select-all').prop('indeterminate', true);
  }
};

const initUserDeleteBtn = () =>
  $('#user-delete').click(function(event) {
    clearNotifications();
    event.preventDefault();
    const confirmMessage = $(this)
      .data('confirm')
      .replace('{users}', $('input[name=user_db]:checked').length);
    if (confirm(confirmMessage)) {
      const user_keys = [];
      $('input[name=user_db]:checked').each(function() {
        $(this).attr('disabled', true);
        user_keys.push($(this).val());
      });
      const deleteUrl = $(this).data('api-url');
      const successMessage = $(this).data('success');
      const errorMessage = $(this).data('error');
      apiCall(
        'DELETE',
        deleteUrl,
        {
          user_keys: user_keys.join(','),
        },
        (err, result) => {
          if (err) {
            $('input[name=user_db]:disabled').removeAttr('disabled');
            showNotification(
              errorMessage.replace('{users}', user_keys.length),
              'danger',
            );
            return;
          }
          $(`#${result.join(', #')}`).fadeOut(function() {
            $(this).remove();
            updateUserSelections();
            showNotification(
              successMessage.replace('{users}', user_keys.length),
              'success',
            );
          });
        },
      );
    }
  });

window.initUserMerge = () => {
  const user_keys = $('#user_keys').val();
  const api_url = $('.api-url').data('api-url');
  apiCall(
    'GET',
    api_url,
    {
      user_keys,
    },
    (error, result) => {
      if (error) {
        LOG('Something went terribly wrong');
        return;
      }
      window.user_dbs = result;
      $('input[name=user_db]').removeAttr('disabled');
    },
  );
  $('input[name=user_db]').change(event => {
    const user_key = $(event.currentTarget).val();
    selectDefaultUser(user_key);
  });
};

const selectDefaultUser = user_key => {
  $('.user-row')
    .removeClass('success')
    .addClass('danger');
  $(`#${user_key}`)
    .removeClass('danger')
    .addClass('success');
  for (const user_db of user_dbs) {
    if (user_key === user_db.key) {
      $('input[name=user_key]').val(user_db.key);
      $('input[name=username]').val(user_db.username);
      $('input[name=name]').val(user_db.name);
      $('input[name=email]').val(user_db.email);
      break;
    }
  }
};

const initUserMergeBtn = () =>
  $('#user-merge').click(function(event) {
    event.preventDefault();
    const user_keys = [];
    $('input[name=user_db]:checked').each(function() {
      user_keys.push($(this).val());
    });
    const user_merge_url = $(this).data('user-merge-url');
    window.location.href = `${user_merge_url}?user_keys=${user_keys.join(',')}`;
  });
