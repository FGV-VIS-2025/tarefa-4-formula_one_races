/*  ==========================================================================
standingsUtils.js
--------------------------------------------------------------------------
Funções de conveniência que filtram/transformam os standings
para um formato amigável ao gráfico.
========================================================================== */

function getDriverStandings(f1data, season) {
  let standings = null;
  standings = f1data.driverStandings.filter((d) => d.season === season);
  return standings;
}

function getConstructorStandings(f1data, season) {
  let standings = null;
  standings = f1data.constructorStandings.filter((d) => d.season === season);
  return standings;
}

export function getSeasons(f1data, firstSeason = 2000) {
  return [...new Set(f1data.driverStandings.map((d) => d.season))]
    .sort((a, b) => b - a)
    .filter((d) => d >= firstSeason);
}

export function getRounds(f1data, season) {
  return [...new Set(f1data.races.filter((d) => d.season === season).map((d) => d.round))]
    .sort((a, b) => a - b);
}

export function getEntities(f1data, season, mode, round) {
  let standings = standingsBySeason(f1data, season, mode);
  let entities = {};
  [...new Set(standings.map((d) => d[mode]))].forEach((d) => {
    let entity = standings.filter((e) => e[mode] === d && e.round == round)[0];
    if (!entity) return;
    entities[d] = {
      name: entity[mode],
      points: entity.points,
      position: entity.position,
      round: entity.round,
      season: entity.season,
      wins: entity.wins,
    };
  
    let driver = f1data.drivers.filter((e) => e.driverId === entity.driverId)[0];
    let constructor = f1data.constructors.filter((e) => e.constructorId === entity.constructorId)[0];
    if (mode === 'driver') {
      entities[d].id = driver.driverId;
      entities[d].url = driver.url;
      entities[d].dateOfBirth = driver.dateOfBirth;
      entities[d].nationality = driver.nationality
      entities[d].constructor = constructor.name;
    } else if (mode === 'constructor') {
      entities[d].id = constructor.constructorId;
      entities[d].url = constructor.url;
      entities[d].nationality = constructor.nationality;
    }
  });
  return entities
}

export function standingsBySeason(f1data, season, labelField) {
  // Recebe (driver OR constructor) standings cru,
  // devolve array ordenado por round, já com
  // { round, position, key, points } pronto para plotagem.

  let standings = [];
  if (labelField === 'driver') {
    standings = getDriverStandings(f1data, season);
  } else if (labelField === 'constructor') {
    standings = getConstructorStandings(f1data, season);
  }

  return standings;
}
