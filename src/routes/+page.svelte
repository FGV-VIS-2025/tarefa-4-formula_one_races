<script>
  import { onMount, onDestroy } from "svelte";
  import SeasonChart from "$lib/SeasonChart.svelte";
  import FullScreen from "$lib/FullScreen.svelte";
  import { loadData } from '$lib/dataLoader.js';

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
  <div class="description">
    <p>
      No ínicio de uma temporada de Formual 1 é comum dizer que o resultado ainda irá mudar muito. Sempre dizem que durante as primeiras corridas os pilotos ainda estão se adaptando aos carros, às equipes e por aí vai. Será isso verdade?
    </p>
    <p>
      Nossa equipe acompanha F1 e com um começo de temporada um tanto conturbada em 2025, decidimmos avaliar a veracidade ou não desses ditos.
    </p>
    <p>
      Utilizamos o conjunto de dados proveido pelo <a href="https://github.com/jolpica/jolpica-f1" target="_blank">Jolpica</a>, combinado com o histórico do seu antecessor <a href="https://ergast.com/mrd/" target="_blank">Ergast</a>. Optamos por visualizar a evolução dos pilotos/escuderias ao longo de uma temporada, conseguindo visualizar as mudanças de posição e até quantificando essas métricas.
    </p>
    <p>
      Tentamos criar uma visualização iterativa para permitir ao usuário explorar as temporadas da F1 desde 2000, além de poder ver animações e mais detalhes sob demanda.
    </p>
  </div>

  <div class="season-chart">
    <FullScreen text="Expandir Visualização">
      {#if !f1data}
        <p>Carregando dados...</p>
      {:else}
        <SeasonChart {f1data} />
      {/if}
    </FullScreen>
  </div>

  <div class="description footer">
    <p>
      Ao explorar um pouco as temporadas é possível observar que de fato a classificação inicial não quer dizer muita coisa. Em todas as temporadas a variação entre as posições durante as 5 primeiras rodadas é muito alta.
    </p>
    <p>
      Contudo, com o decorrer do ano, as posições se tornam mais estáveis, como é de se esperar pelo aumento de pontos dos pilotos, tornando a pontuação de uma única rodada não tão significativa no resultado global.
    </p>
    <p>
      Apesar dessa estabilidade, finais de temporadas ainda são decisivos e é preciso continuar <a href="https://www.netflix.com/br/title/80204890" target="_blank">correndo para viver</a>.
    </p>
  </div>

  <footer>
    <a href="https://github.com/wobetec" target="_blank">Wobetec</a>
    <a href="https://github.com/MasFz" target="_blank">MasFz</a>
    <a href="https://github.com/Vilasz" target="_blank">Vilasz</a>
  </footer>
</main>

<style lang="scss">
  h1 {
    text-align: center;
    margin-top: 20px;
  }

  .description {
    width: 80%;
    max-width: calc(0.8 * 1280px);
    text-align: justify;
    font-size: 1.2em;
    margin: 20px auto;
  }

  p {
    text-indent: 20px;
    margin-bottom: 5px;
  }

  .season-chart {
    width: 80%;
    max-width: calc(0.8 * 1280px);
    aspect-ratio: 16/10;
    
    margin: 0 auto;
  }
  
  footer {
    margin: 0 auto;
    padding-bottom: 20px;
    max-width: calc(0.8 * 1280px);
    display: flex;
    justify-content: space-around;
  }
</style>