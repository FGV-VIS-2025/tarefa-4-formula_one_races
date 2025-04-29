<script>
  let slotWrapper;
  export let text = "Expandir Visualização";

  function toggleFullScreen() {
    if (!document.fullscreenElement) {
      slotWrapper?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }
</script>

<div class="fullscreen-container">
  <div class="slot" bind:this={slotWrapper}>
    <slot/>
  </div>
  <button class="fullscreen-button" on:click={toggleFullScreen}>
    {text}
  </button>
</div>

<style lang="scss">
  .fullscreen-container {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px;
    justify-content: center;
    align-items: center;
  }

  .slot {
    width: 100%;
    height: 100%;
  }

  button {
    padding: 10px 0;
    border: none;
    background-color: #333;
    color: #fff;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    width: 100%;
    max-width: 480px;

    &:hover {
      background-color: #555;
    }
  }

  .slot:fullscreen,
  .slot:-webkit-full-screen,
  .slot:-moz-full-screen,
  .slot:-ms-fullscreen {
    position: fixed !important;
    top: 50%;
    left: 50%;
    width: 95vw !important;
    height: 95vh !important;
    transform: translate(-50%, -50%);
    margin: 0 !important;
    padding: 0 !important;
    background-color: #fff !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    z-index: 9999 !important;
    border: none !important;
    border-radius: 0 !important;
  }

  .slot:fullscreen svg,
  .slot:-webkit-full-screen svg,
  .slot:-moz-full-screen svg,
  .slot:-ms-fullscreen svg {
    width: 100% !important;
    height: 100% !important;
  }

</style>