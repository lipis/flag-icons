loadJSON = (path, callback) => {
  var xobj = new XMLHttpRequest();
  xobj.overrideMimeType('application/json');
  xobj.open('GET', path, true);
  xobj.onreadystatechange = function () {
    if (xobj.readyState == 4 && xobj.status == '200') {
      callback(xobj.responseText);
    }
  };
  xobj.send(null);
};

window.onload = function () {
  const flagsRow = document.getElementById('flags');
  console.log('divvvv', flagsRow);
  loadJSON('country.json', response => {
    const countries = JSON.parse(response);
    console.log(countries[3].name);

    for (country of countries) {
      console.log(country);
      const colDiv = document.createElement('div');
      colDiv.classList.add('col-lg-3');
      colDiv.classList.add('col-md-4');
      colDiv.classList.add('col-sm-6');
      const flagDiv = document.createElement('div');
      flagDiv.classList.add('flag');
      const countryDiv = document.createElement('div');
      countryDiv.classList.add('flag-country');
      countryDiv.classList.add('no-wrap')
      const countryName = document.createTextNode(country.name);
      const flagImg = document.createElement('img');
      flagImg.classList.add('flag-img');
      flagImg.src = country.flag_4x3;
      countryDiv.appendChild(countryName);

      colDiv.appendChild(flagDiv)
      flagDiv.appendChild(countryDiv);
      flagDiv.appendChild(flagImg);
      console.log(flagDiv);
      flagsRow.appendChild(colDiv);
    }
  });
};
