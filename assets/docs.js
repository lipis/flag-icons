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
      colDiv.classList.add('col-xl-2');
      colDiv.classList.add('col-lg-3');
      colDiv.classList.add('col-md-4');
      colDiv.classList.add('col-6');
      const flagDiv = document.createElement('div');
      flagDiv.classList.add('flag');
      const countryDiv = document.createElement('div');
      countryDiv.classList.add('flag-country');
      countryDiv.classList.add('no-wrap');
      const countryName = document.createTextNode(country.name);
      countryDiv.appendChild(countryName);
      const flagImg = document.createElement('img');
      flagImg.classList.add('flag-img');
      flagImg.src = country.flag_4x3;
      // Code
      const codeDiv = document.createElement('div');
      codeDiv.classList.add('flag-code');
      const code = document.createTextNode(
        country.flag_4x3.substr(10).replace('.svg', ''),
      );
      codeDiv.appendChild(code);

      colDiv.appendChild(flagDiv);
      flagDiv.appendChild(countryDiv);
      flagDiv.appendChild(flagImg);
      flagDiv.appendChild(codeDiv);
      flagsRow.appendChild(colDiv);
    }
  });
};
