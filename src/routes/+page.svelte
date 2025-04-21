<script>
  import { onMount, onDestroy } from "svelte";
  import { loadData } from "$lib/dataLoader";
  import { createChart } from "$lib/charts/lineStandings";
  import { standingsBySeason } from "$lib/standingsUtils";

  let vizContainer;
  let chartInstance;
  let maxRound = 1;
  let currentRound = 1;
  let playing = false;
  let timer;

  const season = 2023;
  const mode = "driver";

  function toggleFullScreen() {
    const elem = document.querySelector(".visualization");
    if (!document.fullscreenElement) {
      elem.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }

  onMount(async () => {
    const { driverStandings, constructorStandings } = await loadData();
    const raw = standingsBySeason(driverStandings, season, mode);
    const rounds = Array.from(new Set(raw.map(d => d.round))).sort((a,b)=>a-b);
    maxRound = rounds[rounds.length - 1];
    currentRound = maxRound;

    chartInstance = createChart(
      vizContainer,
      { driverStandings, constructorStandings },
      { season, mode, round: currentRound }
    );
  });

  function updateChart(round) {
    chartInstance?.update({ round });
  }

  // toda vez que currentRound muda, atualiza o gráfico
  $: if (chartInstance) {
    updateChart(currentRound);
  }

  function togglePlay() {
    if (!playing) {
      // se estiver no fim, reinicia
      if (currentRound >= maxRound) {
        currentRound = 1;
      }
      playing = true;
      timer = setInterval(() => {
        if (currentRound < maxRound) {
          currentRound += 1;
        } else {
          clearInterval(timer);
          playing = false;
        }
      }, 800);
    } else {
      playing = false;
      clearInterval(timer);
    }
  }

  function handleSlider(e) {
    currentRound = +e.target.value;
  }

  onDestroy(() => {
    chartInstance?.destroy();
    clearInterval(timer);
  });
</script>

<svelte:head>
  <title>Visualização de Dados</title>
</svelte:head>

<main>
  <h1 class="title">O quanto varia a posição de um piloto de F1 durante uma temporada?</h1>
  <p class="description">
    Texto para explicarmos os dados de F1 
  </p>

  <div class="visualization-container">
    <div class="visualization" bind:this={vizContainer}></div>

    <div class="controls">
      <button class="play-pause-button" on:click={togglePlay}>
        {playing ? "Pausar" : "Play"}
      </button>
      <input
        type="range"
        class="round-slider"
        min="1"
        max={maxRound}
        bind:value={currentRound}
        on:input={handleSlider}
      />
      <span class="round-label">Round: {currentRound}</span>
    </div>

    <button class="fullscreen-button" on:click={toggleFullScreen}>
      Expandir Visualização
    </button>
  </div>
</main>
