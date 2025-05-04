<script>
  import { onMount } from "svelte";
  import { fade, slide } from "svelte/transition";
  import SeasonChart from "$lib/SeasonChart.svelte";
  import VariationHeatmap from "$lib/charts/VariationHeatmap.svelte";
  import { loadData } from "$lib/dataLoader.js";
  import { base } from "$app/paths";

  let f1data = null;

  // fetch data once component mounts
  onMount(async () => {
    f1data = await loadData(base);
  });

  // smooth-scroll to next viewport‑height
  const scrollNext = () => {
    console.log("scrollNext()");
    window.scrollBy({ top: window.innerHeight, behavior: "smooth" });
  };
</script>

<svelte:head>
  <title>F1 | Volatilidade de Posições</title>
  <meta name="theme-color" content="#e10600" />
</svelte:head>

<!-- ╔══════════════════════  FULLPAGE  ══════════════════════╗ -->
<div class="fullpage">
  <!-- ░░ SLIDE 1 ░░ -->
  <section class="slide intro" in:fade={{ duration: 600 }}>
    <div class="intro-copy" in:slide={{ x: -40, duration: 600 }}>
      <h1>Quanto muda o ranking na Fórmula 1?</h1>
      <p>
        É comum ouvir que, no começo da temporada, "tudo ainda vai virar de
        cabeça para baixo". Mas qual é o tamanho real dessa dança das cadeiras —
        e quando a tabela finalmente sossega?
      </p>
      <p>
        Usando o repositório <a
          href="https://github.com/jolpica/jolpica-f1"
          target="_blank">Jolpica</a
        >
        combinado ao histórico
        <a href="https://ergast.com/mrd/" target="_blank">Ergast</a>, calculamos as trocas de posição corrida a corrida desde 2000.
      </p>
      <p>
        Olhando o minigráfico à direita, a resposta é direta: sim, a tabela muda bastante no começo da temporada.
        Matematicamente falando, a volatilidade no começo acaba sendo alta porque todos os pilotos estão com pontuações próximas.
        Ao longo da temporada os gaps de pontos começam a ficar grandes e é difícil se recuperar.
      </p>
      <p>
        Resumindo: a tabela muda bastante, mas fazer um bom começo ajuda a ter um bom final.
      </p>
      <p>
        Explore os mini gráfico à direita e depois role para baixo e veja o gráfico completo de cada temporada.
        Mergulhe na nossa base de dados e verifique você mesmo esse fenômeno.
      </p>
      <p>
        Feito por:
        <a href="https://github.com/wobetec">Esdras Cavalcanti</a>,
        <a href="https://github.com/Vilasz">João Felipe</a> e
        <a href="https://github.com/MasFz">Marcelo Angelo</a>.
      </p>
      <p>
        Confira nosso repositório no <a href="https://github.com/FGV-VIS-2025/tarefa-4-formula_one_races">GitHub</a>.
      </p>
    </div>

    <div class="mini-charts" in:slide={{ x: 40, duration: 600 }}>
      {#if f1data}
        <VariationHeatmap {f1data} />
      {:else}
        <div class="loading">Carregando…</div>
      {/if}
    </div>

    <button class="scroll-btn" aria-label="Descer" on:click={scrollNext}>
      <svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" /></svg>
    </button>
  </section>

  <!-- ░░ SLIDE 2 ░░ -->
  <section class="slide season" in:slide={{ y: 200, duration: 600 }}>
    {#if f1data}
      <SeasonChart {f1data} />
    {:else}
      <div class="loading">Carregando…</div>
    {/if}
  </section>
</div>

<style>
  /* Hide scrollbar yet keep scroll */
  .fullpage::-webkit-scrollbar {
    width: 0;
    height: 0;
  }
  .fullpage {
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  /* ——— Full‑viewport scroller ——— */
  .fullpage {
    height: 100vh;
    overflow-y: auto;
    scroll-snap-type: y mandatory;
  }
  .slide {
    width: 100%;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5rem;
    position: relative;
    padding: 1rem;
    box-sizing: border-box;
    scroll-snap-align: start;
    background: #0f0f0f
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23171717' opacity='0.45'%3E%3Crect width='6' height='6'/%3E%3C/svg%3E")
    repeat;
    box-shadow: inset 6px 0 0 #e10600;
  }

  /* ① INTRO SLIDE — dark carbon motif with red racing stripe on the left */
  /* ② SEASON SLIDE — radial spotlight */
  .season {
    background: radial-gradient(circle at center 25%, #202020 0%, #000 75%);
  }

  /* ——— Intro column ——— */
  .intro-copy {
    width: 30%;
  }
  .intro-copy h1 {
    font-family: var(--font-f1);
    font-weight: 700;
    font-size: 2.5rem;
    line-height: 1.1;
    margin: 0 0 1rem;
    color: #fff;
    text-shadow: 0 0 12px rgba(225, 6, 0, 0.6);
  }
  .intro-copy p {
    font-size: 1.05rem;
    line-height: 1.6;
    margin: 0 0 1rem;
    text-align: justify;
    color: #d7d7d7;
  }
  .intro-copy a {
    color: #e10600;
    text-decoration: underline;
  }
  .intro-copy a:hover {
    color: #ff5033;
  }

  /* ——— Mini‑charts grid ——— */
  .mini-charts {
    width: 45%;
    aspect-ratio: 16 / 9;
  }
  .mini-charts :global(svg),
  .mini-charts :global(canvas) {
    width: 100%;
    height: 100%;
    background-color: var(--color-background-light);
    border-radius: 8px;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.6);
  }

  /* ——— Arrow button ——— */
  .scroll-btn {
    position: absolute;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    width: 56px;
    height: 56px;
    border-radius: 50%;
    border: none;
    background: #e10600;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    animation: bounce 2s infinite;
    transition: background 0.2s ease;
  }
  .scroll-btn:hover {
    background: #ff5033;
  }
  .scroll-btn svg {
    width: 28px;
    height: 28px;
    stroke: #fff;
    stroke-width: 2;
    fill: none;
  }
  @keyframes bounce {
    0%,
    100% {
      transform: translate(-50%, 0);
    }
    50% {
      transform: translate(-50%, -12px);
    }
  }

  /* ——— Loading placeholder ——— */
  .loading {
    font-size: 1.25rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: #888;
    text-transform: uppercase;
  }

  /* Responsive tweaks */
  @media (max-width: 900px) {
    .intro-copy {
      max-width: 100%;
      flex: 1 1 100%;
      margin: 0 0 2rem;
    }
    .mini-charts {
      max-width: 100%;
      flex: 1 1 100%;
    }
  }
</style>
