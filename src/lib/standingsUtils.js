/*  ==========================================================================
    standingsUtils.js
    --------------------------------------------------------------------------
    Funções de conveniência que filtram/transformam os standings
    para um formato amigável ao gráfico.
    ========================================================================== */

    export function standingsBySeason(rawStandings, season, labelField) {
        // Recebe (driver OR constructor) standings cru,
        // devolve array ordenado por round, já com
        // { round, position, key, points } pronto para plotagem.
        return rawStandings
          .filter((d) => d.season === season)
          .map((d) => ({
            round: +d.round,
            position: +d.position,
            key: d[labelField],         // 'driver'  ou  'constructor'
            points: +d.points
          }))
          .sort((a, b) => a.round - b.round);
      }
      
      export function listSeasons(rawStandings) {
        // Extrai todos os anos disponíveis, ordenados
        return [...new Set(rawStandings.map((d) => d.season))].sort((a, b) => a - b);
      }
      