<% _.forEach(flagsList, function(countryCode) {
  %>@include flag-icon(<%= countryCode %>);
<% }) %>