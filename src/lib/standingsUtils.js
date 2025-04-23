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
