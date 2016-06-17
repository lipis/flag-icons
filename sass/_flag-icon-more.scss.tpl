<% _.forEach(moreFlags, function(countryCode) {
  %>@include flag-icon(<%= countryCode %>);
<% }) %>