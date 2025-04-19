<script>
    import { onMount } from 'svelte';
    import { loadData } from '$lib/dataLoader';
    import { createChart } from '$lib/charts/lineStandings';
    import { listSeasons } from '$lib/standingsUtils';
  
    // estado
    let datasets;
    let seasons = [];
    let season;
    let mode = 'driver';
  
    let round = 1;
    let maxRound = 1;
  
    let chart;
    let playing = false;
    let timer;

    // reatividade automática
    $: if (chart) chart.update({ mode, season, round });

    // se mudar a temporada, reseta round
    $: if (season) {
        round = 1;
        calcMaxRound();
    }
  
    // -----------------------------------------------------
    onMount(async () => {
      datasets = await loadData();
      seasons = listSeasons(datasets.driverStandings);
  
      season = seasons.at(-1);      // última temporada
      calcMaxRound();
      chart = createChart('#chart', datasets, { mode, season, round });
  

    });
  
    function calcMaxRound() {
      if (!datasets) return;
      const src =
        (mode === 'driver' ? datasets.driverStandings : datasets.constructorStandings)
          .filter((d) => d.season === +season)
          .map((d) => d.round);
      maxRound = Math.max(...src);
    }
  
    // PLAY ------------------------------------------------
    function togglePlay() {
      playing = !playing;
      if (playing) {
        timer = setInterval(() => {
          if (round < maxRound) {
            round += 1;
          } else {
            playing = false;
            clearInterval(timer);
          }
        }, 1100);
      } else {
        clearInterval(timer);
      }
    }
  </script>
  
  <svelte:head>
    <title>F1 • Standings por rodada</title>
  </svelte:head>
  
  <main>
    <h1 class="title">Evolução das posições na temporada {season}</h1>
  
    <!-- CONTROLES ----------------------------------------------------------- -->
    <section class="controls">
      <label>Modo:
        <select bind:value={mode} on:change={calcMaxRound}>
          <option value="driver">Pilotos</option>
          <option value="constructor">Escuderias</option>
        </select>
      </label>
  
      <label>Temporada:
        <select bind:value={season}>
          {#each seasons as y}
            <option value={y}>{y}</option>
          {/each}
        </select>
      </label>
  
      <label class="round-slider">
        Rodada: {round}
        <input
          type="range"
          min="1"
          max={maxRound}
          bind:value={round}
          step="1"
        />
        / {maxRound}
      </label>
  
      <button class="play-btn" on:click={togglePlay}>
        {playing ? '⏸ Pausar' : '▶️ Play'}
      </button>
    </section>
  
    <!-- GRÁFICO ------------------------------------------------------------- -->
    <div id="chart" class="visualization"></div>
    <div class="legend">
      <!-- Add legend items dynamically if needed -->
      <div class="legend-item">
        <div class="legend-color" style="background-color: red;"></div>
        <span>Example Legend</span>
      </div>
    </div>
  </main>
  
  <style>
    @import '/style.css'; /* usa o global */
  
    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      justify-content: center;
      margin: 1.2rem 0;
    }
  
    select,
    input[type='range'],
    button {
      font-size: 1rem;
      padding: 0.35rem 0.6rem;
    }
  
    .round-slider {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      min-width: 220px;
    }
  
    .play-btn {
      background: #333;
      color: #fff;
      border: none;
      cursor: pointer;
    }
  
    .play-btn:hover {
      background: #555;
    }
  
    /* ---------- LEGENDA (gerada dentro do chart wrapper) ------------------ */
    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem 1rem;
      justify-content: center;
      margin-top: 0.6rem;
      font-size: 0.85rem;
    }
  
    .legend-item {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      cursor: default;
    }
  
    .legend-color {
      width: 14px;
      height: 14px;
      border-radius: 3px;
      flex-shrink: 0;
    }
  
    /* ---------- TOOLTIP --------------------------------------------------- */
    /* Removed unused .d3-tip selector */
  </style>
  