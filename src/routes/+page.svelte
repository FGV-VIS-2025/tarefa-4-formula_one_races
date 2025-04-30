<script>
  import { onMount } from "svelte";
  import { fade, slide } from "svelte/transition";
  import SeasonChart from "$lib/SeasonChart.svelte";
  import VariationHeatmap from "$lib/charts/VariationHeatmap.svelte";
  import PositionVolatilityChart from "$lib/charts/PositionVolatilityChart.svelte";
  import { loadData } from "$lib/dataLoader.js";
  import { base } from "$app/paths";

  let f1data = null;

  // fetch data once component mounts
  onMount(async () => {
    f1data = await loadData(base);
  });

  // smooth-scroll to next viewport‑height
  const scrollNext = () => {
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
      <h1>Quanto mudam as posições na Fórmula 1?</h1>
      <p>
        É comum ouvir que, no começo da temporada, “tudo ainda vai virar de cabeça para baixo”. Mas qual é o tamanho
        real dessa dança das cadeiras — e quando a tabela finalmente sossega?
      </p>
      <p>
        Usando o repositório <a href="https://github.com/jolpica/jolpica-f1" target="_blank">Jolpica</a> combinado ao
        histórico <a href="https://ergast.com/mrd/" target="_blank">Ergast</a>, calculamos quanta gente troca de
        posição corrida a corrida desde 2000.
      </p>
      <p>
        Explore os mini‑gráficos à direita e depois clique na seta — ou role — para mergulhar no gráfico completo da
        temporada.
      </p>
    </div>

    <div class="mini-charts" in:slide={{ x: 40, duration: 600 }}>
      {#if f1data}
        <VariationHeatmap {f1data} lines={5} />
        <PositionVolatilityChart {f1data} lines={5} />
      {:else}
        <div class="loading">Carregando…</div>
      {/if}
    </div>

    <button class="scroll-btn" aria-label="Descer" on:click={scrollNext}>
      <svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
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
<!-- ╚════════════════════════════════════════════════════════╝ -->

<style>
  /* ——— Site‑wide baseline ——— */
  html,body{margin:0;height:100%;font-family:"Roboto Condensed",Arial,Helvetica,sans-serif;background:#0d0d0d;color:#f0f0f0;overflow:hidden}

  /* Hide scrollbar yet keep scroll */
  .fullpage::-webkit-scrollbar{width:0;height:0}
  .fullpage{scrollbar-width:none;-ms-overflow-style:none}

  /* ——— Full‑viewport scroller ——— */
  .fullpage{height:100vh;overflow-y:auto;scroll-snap-type:y mandatory}
  .slide{width:100%;height:100vh;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;position:relative;padding:2rem;box-sizing:border-box;scroll-snap-align:start}

  /* ① INTRO SLIDE — dark carbon motif with red racing stripe on the left */
  .intro{background:#0f0f0f url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23171717' opacity='0.45'%3E%3Crect width='6' height='6'/%3E%3C/svg%3E") repeat; box-shadow:inset 6px 0 0 #e10600}

  /* ② SEASON SLIDE — radial spotlight */
  .season{background:radial-gradient(circle at center 25%, #202020 0%, #000 75%)}

  /* ——— Intro column ——— */
  .intro-copy{flex:1 1 45%;max-width:45%;margin-right:2rem}
  .intro-copy h1{font-family:"Orbitron",sans-serif;font-weight:700;font-size:2.5rem;line-height:1.1;margin:0 0 1rem;color:#fff;text-shadow:0 0 12px rgba(225,6,0,.6)}
  .intro-copy p{font-size:1.05rem;line-height:1.6;margin:0 0 1rem;text-align:justify;color:#d7d7d7}
  .intro-copy a{color:#e10600;text-decoration:underline}
  .intro-copy a:hover{color:#ff5033}

  /* ——— Mini‑charts grid ——— */
  .mini-charts{flex:1 1 45%;max-width:45%;display:grid;grid-template-rows:1fr 1fr;gap:2rem}
  .mini-charts :global(svg), .mini-charts :global(canvas){width:100%;height:40vh;background:#111;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,.6)}

  /* ——— Arrow button ——— */
  .scroll-btn{position:absolute;bottom:2rem;left:50%;transform:translateX(-50%);width:56px;height:56px;border-radius:50%;border:none;background:#e10600;display:flex;align-items:center;justify-content:center;cursor:pointer;animation:bounce 2s infinite;transition:background .2s ease}
  .scroll-btn:hover{background:#ff5033}
  .scroll-btn svg{width:28px;height:28px;stroke:#fff;stroke-width:2;fill:none}
  @keyframes bounce{0%,100%{transform:translate(-50%,0)}50%{transform:translate(-50%,-12px)}}

  /* ——— Loading placeholder ——— */
  .loading{font-size:1.25rem;font-weight:600;letter-spacing:.05em;color:#888;text-transform:uppercase}

  /* ——— Season chart viewport ——— */
  .season :global(svg), .season :global(canvas){width:90%;height:90vh;border-radius:8px;box-shadow:0 10px 28px rgba(0,0,0,.75)}

  /* Responsive tweaks */
  @media(max-width:900px){
    .intro-copy{max-width:100%;flex:1 1 100%;margin:0 0 2rem}
    .mini-charts{max-width:100%;flex:1 1 100%}
  }
</style>
