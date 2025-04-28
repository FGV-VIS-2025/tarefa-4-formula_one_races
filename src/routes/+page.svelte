<script>
  import { onMount, onDestroy } from "svelte";
  import SeasonChart from "$lib/SeasonChart.svelte";
  import FullScreen from "$lib/FullScreen.svelte";
  import { loadData } from '$lib/dataLoader.js';
  import { writable } from "svelte/store";

    /* ▼ ADICIONE estas stores logo após os imports */
    const topDriver = writable(null);
  const topSwaps  = writable(0);
  const avgSwaps  = writable(0);


  let f1data;
  onMount(async () => {
  f1data = await loadData();   // pronto. mais nada aqui
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

    <!-- ▼ ADICIONE esta seção de cards -->
    <section class="cards">
      <div class="card metric-card">
        <h2>{$topDriver}</h2>
        <p class="metric">{$topSwaps}</p>
        <p class="caption">trocas de posição</p>
      </div>
  
      <div class="card metric-card">
        <h2>Média por piloto</h2>
        <p class="metric">{$avgSwaps}</p>
        <p class="caption">trocas em média</p>
      </div>
    </section>
  
  <div class="season-chart">
    <FullScreen text="Expandir Visualização">
      {#if !f1data}
        <p>Carregando dados...</p>
      {:else}
      <SeasonChart
      {f1data}
      on:metrics={e => {
        topDriver.set(e.detail.topDriver);
        topSwaps.set(e.detail.topSwaps);
        avgSwaps.set(e.detail.avgSwaps);
      }} />
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

  /* ▼ ADICIONE estes estilos */

.cards {
  width: 90%;
  max-width: 1280px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem;
  margin: 1.5rem auto;
}

.card {
  flex: 1 1 200px;
  padding: 1rem 1.50rem;
  border-radius: 14px;
  box-shadow: 0 8px 18px rgba(0, 0, 0, .35);
  color: #f5f5f5;
  transition: transform .2s ease, box-shadow .2s ease;
  background: #2b2b2b;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, .45);
}

.metric-card {
  background: linear-gradient(135deg, #e10600 0%, #9b0000 100%);
}

.text-card {
  background: #121212;
}

.metric {
  font-size: 2.4rem;
  font-weight: 700;
  margin: .25rem 0 .5rem;
  line-height: 1;
}

.caption {
  font-size: .9rem;
  opacity: .9;
}

</style>