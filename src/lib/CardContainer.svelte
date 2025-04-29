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
    </div>
  {/each}
</section>

<style>
  .cards {
    max-width: 720px;
    height: fit-content;
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    align-items: space-around;
    gap: 2rem;
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
  }

  .card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, .45);
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
</style>