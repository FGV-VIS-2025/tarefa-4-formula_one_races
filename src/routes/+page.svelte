<script>
  import { onMount, onDestroy } from "svelte";
  import SeasonChart from "$lib/SeasonChart.svelte";
  import FullScreen from "$lib/FullScreen.svelte";
  import { loadData } from '$lib/dataLoader.js';
  import { writable } from "svelte/store";

  let f1data;
  onMount(async () => {
    f1data = await loadData();
  });
</script>

<svelte:head>
  <title>Visualização de Dados</title>
</svelte:head>

<main>
  <h1>Quanto varia a classificação na F1 ao longo de uma temporada?</h1>
  <p class="description">
    Texto para explicarmos os dados de F1 
  </p>
  <div class="season-chart">
    <FullScreen text="Expandir Visualização">
      {#if !f1data}
        <p>Carregando dados...</p>
      {:else}
        <SeasonChart f1data={f1data}/>
      {/if}
    </FullScreen>
  </div>
</main>

<style lang="scss">
  h1 {
    text-align: center;
    margin-top: 20px;
  }

  p.description {
    text-align: center;
    font-size: 1.2em;
    margin: 10px 20px;
  }

  .season-chart {
    width: 80%;
    max-width: calc(0.8 * 1280px);
    aspect-ratio: 16/9;

    margin: 0 auto;
  }
</style>