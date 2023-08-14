const loadJSON = (path, callback) => {
  var xobj = new XMLHttpRequest();
  xobj.overrideMimeType("application/json");
  xobj.open("GET", path, true);
  xobj.onreadystatechange = function () {
    if (xobj.readyState == 4 && xobj.status == "200") {
      callback(xobj.responseText);
    }
  };
  xobj.send(null);
};

const addFlag = (country, rowDiv) => {
  const colDiv = document.createElement("div");
  colDiv.classList.add("col-xl-2");
  colDiv.classList.add("col-lg-3");
  colDiv.classList.add("col-md-4");
  colDiv.classList.add("col-6");
  colDiv.id = country.code;
  const flagDiv = document.createElement("div");
  flagDiv.classList.add("flag");

  // Code
  const codeSpan = document.createElement("span");
  codeSpan.classList.add("flag-code");
  const code = document.createTextNode(country.code);
  codeSpan.appendChild(code);
  // Divider
  const dividerSpan = document.createElement("span");
  const divider = document.createTextNode(" ");
  dividerSpan.appendChild(divider);
  //Country
  const countryDiv = document.createElement("div");
  countryDiv.classList.add("flag-country");
  countryDiv.classList.add("no-wrap");
  countryDiv.title = country.name;
  const countrySpan = document.createElement("span");
  const countryName = document.createTextNode(country.name);
  countrySpan.appendChild(countryName);
  countryDiv.appendChild(codeSpan);
  countryDiv.appendChild(dividerSpan);
  countryDiv.appendChild(countrySpan);

  const flagImg = document.createElement("img");
  flagImg.classList.add("flag-img");
  flagImg.src = country.flag_4x3;
  flagImg.alt = `Flag of ${country.name}`;

  const flagImgSquare = document.createElement("img");
  flagImgSquare.classList.add("flag-img-square");
  flagImgSquare.classList.add("hide");
  flagImgSquare.src = country.flag_1x1;
  flagImgSquare.alt = `Flag of ${country.name}`;

  colDiv.appendChild(flagDiv);
  flagDiv.appendChild(countryDiv);
  flagDiv.appendChild(flagImg);
  flagDiv.appendChild(flagImgSquare);
  rowDiv.appendChild(colDiv);
};

const show4x3 = () => {
  const click4x3 = document.getElementById("click-4x3");
  const click1x1 = document.getElementById("click-1x1");
  click1x1.classList.remove("hide");
  click4x3.classList.add("hide");
  const flags = document.getElementsByClassName("flag-img");
  for (flag of flags) {
    flag.classList.remove("hide");
  }
  const flagsSquared = document.getElementsByClassName("flag-img-square");
  for (flag of flagsSquared) {
    flag.classList.add("hide");
  }
  gtag("event", "switch", {
    event_category: "flags",
    event_label: "4x3",
  });
};

const show1x1 = () => {
  const click4x3 = document.getElementById("click-4x3");
  const click1x1 = document.getElementById("click-1x1");
  click4x3.classList.remove("hide");
  click1x1.classList.add("hide");
  const flagsSquared = document.getElementsByClassName("flag-img-square");
  for (flag of flagsSquared) {
    flag.classList.remove("hide");
  }
  const flags = document.getElementsByClassName("flag-img");
  for (flag of flags) {
    flag.classList.add("hide");
  }

  gtag("event", "switch", {
    event_category: "flags",
    event_label: "1x1",
  });
};

window.onload = function () {
  const isoFlagsRow = document.getElementById("iso-flags");
  const nonIsoFlagsRow = document.getElementById("non-iso-flags");
  const click4x3 = document.getElementById("click-4x3");
  click4x3.addEventListener("click", (event) => {
    event.stopPropagation();
    event.preventDefault();
    show4x3();
  });

  const click1x1 = document.getElementById("click-1x1");
  click1x1.addEventListener("click", (event) => {
    event.stopPropagation();
    event.preventDefault();
    show1x1();
  });

  loadJSON("country.json", (response) => {
    const countries = JSON.parse(response);
    for (country of countries) {
      if (country.iso) {
        addFlag(country, isoFlagsRow);
      } else {
        addFlag(country, nonIsoFlagsRow);
      }
    }
  });
};
