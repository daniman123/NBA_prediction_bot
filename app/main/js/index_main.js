// get logs
async function getLogs(savefile) {
  const response = await fetch(savefile);
  const rawData = await response.text();
  // parse raw data
  let arrayOne = rawData.split("\r\n");
  arrayOne.splice(-1);
  let last_update = arrayOne[arrayOne.length - 1];
  last_update = last_update.slice(0, 19);
  // console.log(last_update);
  return last_update;
}

// create tables
async function getData(savefile) {
  // fetch data
  const response = await fetch(savefile);
  const rawData = await response.text();

  // parse raw data
  let arrayOne = rawData.split("\r\n");

  let header = arrayOne[0].split(",");
  let table_data = arrayOne.splice(1);
  table_data.splice(-1);

  // set parsed data to table
  let table = [];

  table_data.forEach((data_row) => {
    data_row = data_row.split(",");
    let obj = {};

    // parse headers
    header.forEach((val, inds) => {
      obj[val] = data_row[inds];
    });
    table.push(obj);
  });

  // console.table(table);
  return table;
}

async function create_table(table_name, savefile) {
  // init vars
  let children = await getData(savefile);
  let table = document.createElement("table");
  let thead = document.createElement("thead");
  let tbody = document.createElement("tbody");

  // func to gen table headers
  function addHeaders(table, keys) {
    let row = thead.insertRow();
    for (let i = 0; i < keys.length; i++) {
      let cell = row.insertCell();
      cell.appendChild(document.createTextNode(keys[i]));
    }
  }

  // gen table
  for (let i = 0; i < children.length; i++) {
    let child = children[i];
    // gen head row
    if (i === 0) {
      addHeaders(table, Object.keys(child));
    }
    // gen data rows
    let row = tbody.insertRow();
    Object.keys(child).forEach(function (k) {
      let cell = row.insertCell();
      if (
        /[0-9]/.test(child[k]) &&
        !/[A-Z]/.test(child[k]) &&
        !/-/.test(child[k])
      ) {
        cell.appendChild(
          document.createTextNode(parseFloat(child[k]).toFixed(4))
        );
      } else {
        cell.appendChild(document.createTextNode(child[k]));
      }
    });
  }

  table.appendChild(thead);
  table.appendChild(tbody);
  document.querySelector(table_name).appendChild(table);
}

create_table(".adj_ffac", "\\data\\Adj_FFAC.csv");
create_table(".daily_ffac", "\\data\\daily_ffac.csv");
create_table(".injuries", "\\data\\injuries.csv");

// Menu handler
function close_open_tabs() {
  // close open tabs
  const sections = document.querySelectorAll("section");
  sections.forEach((sects) => {
    // sects.style.display = "none"
    sects.classList.remove("active");
  });
}

// anime consts
const x_cor = 0;
const x_cor_to = 10;
const y_cor = 0;
const y_cor_to = 5;
const dur = 0;
const dur_to = 0.5;

const abbr_team = await getData("\\data\\TeamAbbr.csv");

document.addEventListener("click", (e) => {
  // define tabs in nav
  let adj_nav = "[data-nav-bar-adjusted-ffac]";
  let daily_nav = "[data-nav-bar-daily-ffac]";
  let injuries_nav = "[data-nav-bar-injuries]";
  let game = "section.daily_ffac > table > tbody > tr > td";
  // check tab match
  const adj_tab_match = e.target.matches(adj_nav);
  const daily_tab_match = e.target.matches(daily_nav);
  const inj_tab_match = e.target.matches(injuries_nav);
  const game_match = e.target.matches(game);

  // main tabs
  if (adj_tab_match) {
    try {
      const daily_expanded_ffac_table = document.querySelector(
        "[data-daily-ffac-expanded-table] > table"
      );
      daily_expanded_ffac_table.remove();
    } catch {}
    close_open_tabs();

    document
      .querySelector("[data-adjusted-ffac-table]")
      .classList.toggle("active");

    const adj_ffac_table = document.querySelector("[data-adjusted-ffac-table]");
    gsap.fromTo(
      adj_ffac_table,
      { x: x_cor, y: y_cor },
      { x: x_cor_to, y: y_cor_to, duration: dur_to }
    );

    // tbl title anime
    const adj_ffac_title = document.querySelector(".adj_title");
    gsap.fromTo(adj_ffac_title, { x: -50 }, { x: 0, duration: 0.5 });

    // set update log text
    const update_log_title = document.querySelector(
      "[data-adjusted-ffac-update-log]"
    );
    getLogs("\\logs\\adj_ffac_update.log").then((value) => {
      update_log_title.innerHTML = value;
    });
    gsap.fromTo(update_log_title, { x: -50 }, { x: 0, duration: 0.5 });
  }

  if (daily_tab_match) {
    close_open_tabs();

    document
      .querySelector("[data-daily-ffac-table]")
      .classList.toggle("active");

    const daily_ffac_table = document.querySelector("[data-daily-ffac-table]");
    gsap.fromTo(
      daily_ffac_table,
      { x: x_cor, y: y_cor },
      { x: x_cor_to, y: y_cor_to, duration: dur_to }
    );

    // tbl title anime
    const daily_ffac_title = document.querySelector(".daily_title");
    gsap.fromTo(daily_ffac_title, { x: -50 }, { x: 0, duration: 0.5 });
  }

  if (inj_tab_match) {
    close_open_tabs();
    document.querySelector("[data-injuries-table]").classList.toggle("active");

    const injuries_table = document.querySelector("[data-injuries-table]");
    gsap.fromTo(
      injuries_table,
      { x: x_cor, y: y_cor },
      { x: x_cor_to, y: y_cor_to, duration: dur_to }
    );

    // tbl title anime
    const injuries_title = document.querySelector(".injuries_title");
    gsap.fromTo(injuries_title, { x: -50 }, { x: 0, duration: 0.5 });
  }

  // Expanded tables daily FFAC
  if (game_match) {
    try {
      document.querySelector(".daily_expanded_ffac > table").remove();
    } catch {}

    const tr = e.target.parentNode.children;
    let away_team = tr[1].innerHTML;
    let home_team = tr[2].innerHTML;

    const myTable = document.querySelector(".daily_expanded_ffac");
    let table = document.createElement("table");
    let theader = document.createElement("thead");
    let tbody = document.createElement("tbody");

    const headers = document.querySelector(
      "section.adj_ffac > table > thead > tr"
    );
    let table_headers = headers.cloneNode(true);
    const table_data = document.querySelectorAll(
      "section.adj_ffac > table > tbody > tr"
    );

    theader.appendChild(table_headers);
    table.appendChild(theader);

    const teams = document.querySelectorAll(
      "section.adj_ffac > table > tbody > tr > td:nth-child(1)"
    );
    teams.forEach((team, ind) => {
      if (team.innerHTML === away_team) {
        let clone = table_data[ind].cloneNode(true);
        tbody.appendChild(clone);
        table.appendChild(tbody);
      }
    });
    teams.forEach((team, ind) => {
      if (team.innerHTML === home_team) {
        let clone = table_data[ind].cloneNode(true);
        tbody.appendChild(clone);
        table.appendChild(tbody);
      }
    });

    myTable.appendChild(table);

    document
      .querySelector("[data-daily-ffac-expanded-table]")
      .classList.toggle("active", true);
    gsap.fromTo(
      myTable,
      { x: x_cor_to, y: y_cor, duration: dur },
      { x: x_cor_to, y: 5, duration: 0.45 }
    );

    // tbl title anime
    const expanded_title = document.querySelector(".daily_expanded_title");
    gsap.fromTo(expanded_title, { x: -30 }, { x: 0, duration: 0.5 });
  }

  // set injury for teams table
  if (game_match) {
    try {
      document.querySelector(".injuries_expanded > table").remove();
    } catch {}

    const tr = e.target.parentNode.children;
    let away_team = tr[1].innerHTML;
    let home_team = tr[2].innerHTML;

    const myTable = document.querySelector(".injuries_expanded");
    let table = document.createElement("table");
    let theader = document.createElement("thead");
    let tbody = document.createElement("tbody");

    const headers = document.querySelector(
      "section.injuries > table > thead > tr"
    );
    let table_headers = headers.cloneNode(true);
    const table_data = document.querySelectorAll(
      "section.injuries > table > tbody > tr"
    );

    theader.appendChild(table_headers);
    table.appendChild(theader);

    const teams = document.querySelectorAll(
      "section.injuries > table > tbody > tr > td:nth-child(2)"
    );
    teams.forEach((team, ind) => {
      abbr_team.forEach((val, s) => {
        if (team.innerHTML === val["Abbr"] && away_team === val["Team"]) {
          // console.log("abr",val['Abbr'],"inj",team.innerHTML)
          // console.log("tm",val['Team'],"day",away_team);
          let clone = table_data[ind].cloneNode(true);
          tbody.appendChild(clone);
          table.appendChild(tbody);
        }
      });
    });
    teams.forEach((team, ind) => {
      abbr_team.forEach((val, s) => {
        if (team.innerHTML === val["Abbr"] && home_team === val["Team"]) {
          // console.log("abr",val['Abbr'],"inj",team.innerHTML)
          // console.log("tm",val['Team'],"day",home_team);
          let clone = table_data[ind].cloneNode(true);
          // console.log(clone)
          let born = clone.childNodes;
          born.forEach((element) => {
            element.style.backgroundColor = " rgb(15, 59, 30)";
          });

          tbody.appendChild(clone);
          table.appendChild(tbody);
        }
      });
    });

    myTable.appendChild(table);

    document
      .querySelector("[data-injuries-expanded-table]")
      .classList.toggle("active", true);
    gsap.fromTo(
      myTable,
      { x: x_cor_to, y: y_cor, duration: dur },
      { x: x_cor_to, y: 5, duration: 0.45 }
    );

    // tbl title anime
    const injuries_expanded_title = document.querySelector(
      ".injuries_expanded_title"
    );
    gsap.fromTo(injuries_expanded_title, { x: -30 }, { x: 0, duration: 0.5 });
  }
});

