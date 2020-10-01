var countryList = require('./country-list.json');

module.exports = {
  getCountryList: function () {
    return countryList;
  },
  getCodes: function () {
    return countryList.map(function (country) {
      return country.code;
    });
  },
  getNameByCode: function (code) {
    var uppercaseCode = code.toUpperCase();
    for (var i = 0; i < countryList.length; i++) {
      if (countryList[i].code === uppercaseCode) {
        return countryList[i].name;
      }
    }
  }
};
