<script>
    import { onMount } from "svelte";
  
    function toggleFullScreen() {
      const elem = document.querySelector(".visualization");
      if (!document.fullscreenElement) {
        elem.requestFullscreen().catch(err => {
          console.error(`Erro ao tentar entrar em Fullscreen: ${err.message} (${err.name})`);
        });
      } else {
        document.exitFullscreen().catch(err => {
          console.error(`Erro ao tentar sair do Fullscreen: ${err.message} (${err.name})`);
        });
      }
    }
  
    onMount(() => {
      console.log("Página carregada e visualização pronta para iniciar...");
    });
  </script>
  
  <svelte:head>
    <title>Visualização de Dados</title>
  </svelte:head>
  
  <header>
  </header>
  
  <main>
    <h1 class="title">O quanto varia a posição de um piloto de F1 durante uma temporada?</h1>
    <p class="description">
      Texto para explicarmos os dados de F1 
    </p>
  
    <div class="visualization-container">
      <div class="visualization">
        Campo para Visualização
      </div>
      <button class="fullscreen-button" on:click={toggleFullScreen}>
        Expandir Visualização
      </button>
    </div>
  </main>
  
  <footer>
  </footer>
  