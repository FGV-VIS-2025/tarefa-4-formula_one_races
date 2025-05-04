<script>

export let cardsData = []

</script>

<section class="cards">
  {#each cardsData as card}
    <div class="card">
      <h2>{card.title}</h2>
      <p class="metric">
        <span class="metric">{card.value}</span>
        <span class="caption">{card.caption}</span>
      </p>

      {#if card.description}
        <!-- tooltip que aparece no hover -->
        <div class="tooltip">{card.description}</div>
      {/if}
    </div>
  {/each}
</section>

<style>
  .cards {
    max-width: 720px;
    height: fit-content;
    width: 100%;
    display: flex;
    justify-content: space-around;
    align-items: space-around;
    gap: 2rem;
    position: relative;
  }

  h2 {
    font-size: 1rem;
    margin: 0;
    padding: 0;
    color: #f5f5f5;
  }

  .card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-width: 400px;
    padding: 10px;
    border-radius: 14px;
    box-shadow: 0 8px 18px rgba(0, 0, 0, .35);
    color: #f5f5f5;
    transition: transform .2s ease, box-shadow .2s ease;
    background: #2b2b2b;
    position: relative;
  }

  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, .45);
  }

  .card:hover .tooltip {
    visibility: visible;
    opacity: 1;
  }

  .metric-card {
    background: linear-gradient(135deg, #e10600 0%, #9b0000 100%);
  }

  .text-card {
    background: #121212;
  }

  .metric {
    font-size: 0.8rem;
    font-weight: 700;
    margin: .25rem 0 .5rem;
    line-height: 1;
  }

  .caption {
    font-size: .6rem;
    opacity: .9;
  }

  .tooltip {
    position: absolute;
    bottom: 100%;            /* posiciona acima do card */
    left: 50%;
    transform: translateX(-50%) translateY(-0.5rem);
    background: rgba(0,0,0,0.8);
    color: white;
    padding: 0.5rem;
    border-radius: 4px;
    white-space: nowrap;
    font-size: 0.75rem;
    visibility: hidden;
    opacity: 0;
    transition: opacity 0.2s;
    pointer-events: none;
    z-index: 10;
  }
  .value {
    font-size: 1.5rem;
    font-weight: bold;
  }
</style>