const countryList = require('./country-list.json');

module.exports = {
  getCountryList() {
    return countryList;
  },
  getCodes() {
    return countryList.map(country => country.code);
  },
  getNameByCode(code) {
    const uppercaseCode = code.toUpperCase();
    return countryList.find(country => country.code === uppercaseCode).name;
  }
};
