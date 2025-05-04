<script>
  import * as d3 from "d3";
  import { standingsBySeason, getSeasons, getRounds, getEntities } from "$lib/standingsUtils";
  import {
      computePosition,
      autoPlacement,
      offset,
  } from '@floating-ui/dom';
  import CardContainer from "$lib/CardContainer.svelte";
  import { base } from "$app/paths";

  export let f1data = {};

 function clearSelections() {
        clickedEntitys = [];
  }

  let vizContainer;

  let seasons = [];
  $: seasons = getSeasons(f1data);

  let season = null;
  let mode = "driver";
  $: if (season === null) {
    season = seasons[0];
  }

  let standings = [];
  $: standings = standingsBySeason(f1data, season, mode);

  let previousMode = mode;
  let previousSeason = season;

  $: if (mode !== previousMode) {
    clickedEntitys = [];
    previousMode = mode;
  }

$: if (season !== previousSeason) {
    clickedEntitys = [];
    previousSeason = season;
  }

  let maxRound = 1;
  let currentRound = 1;
  let rounds = [];
  let ranks = [];

  let entities = {};
  $: entities = getEntities(f1data, season, mode, currentRound);
  
  let colorScheme;
  $: if (entities) {
    const defaultColorScheme = [
      "#e6194b",  "#3cb44b",  "#ffe119",  "#4363d8",  "#f58231",
      "#911eb4",  "#46f0f0",  "#f032e6",  "#bcf60c",  "#fabebe",
      "#008080",  "#e6beff",  "#9a6324",  "#fffac8",
      "#aaffc3",  "#808000",  "#ffd8b1",  "#808080",
      "#ffffff",  "#ff7f00",  "#1f78b4",  "#b2df8a",
      "#6a3d9a",  "#fb9a99",  "#33a02c",  "#e31a1c",  "#a6cee3",
    ]
    colorScheme = Object.keys(entities).reduce((acc, key, i) => {
      acc[key] = defaultColorScheme[i % defaultColorScheme.length];
      return acc;
    }, {});
  }

  $: season, maxRound = Math.max(...standings.map(d => d.round));
  if (season){
    dispatch("seasonChange", { season });
  }
  
  $: currentRound = maxRound;
  $: season, rounds = getRounds(f1data, season);
  $: ranks = [...new Set(standings.map(d => d.position))].sort((a, b) => a - b);

  const config = {
    width: 800,
    height: 350,
    margin: { top: 50, right: 140, bottom: 40, left: 50 },
    transitionMs: 400,
    opacity: 0.1,
  }

  const innerW = config.width - config.margin.left - config.margin.right;
  const innerH = config.height - config.margin.top - config.margin.bottom;

  let svg, g, x, y, lineGen;

  let series = [];

  // Cria o svg
  $: if (vizContainer) {
    if (svg) {
      svg.remove();
      series = [];
    }
    svg = d3
      .select(vizContainer)
      .append("svg")
      .attr("viewBox", `0 0 ${config.width} ${config.height}`)
      .attr("preserveAspectRatio", "xMidYMid meet");
  
    g = svg
      .append("g")
      .attr("transform", `translate(${config.margin.left},${config.margin.top})`);
  
    x = d3
      .scalePoint()
      .range([0, innerW])
      .padding(0.5);
  
    y = d3
      .scaleLinear()
      .range([innerH, 0]);
  
    lineGen = d3
      .line()
      .curve(d3.curveMonotoneX)
      .x((d) => x(d.round))
      .y((d) => y(d.position)); 
  }

  let cardsData = [
    { title: "Top Driver", value: 0, caption: "Trocas de posição" },
    { title: "Média de Trocas", value: 0, caption: "Trocas em média" },
  ];

  $: if (standings.length) {
    // Calculate swaps for each driver
    const swapsByDriver = d3.rollup(
      standings,
      (values) => {
        let swaps = 0;
        for (let i = 1; i < values.length; i++) {
          if (values[i].position !== values[i - 1].position) {
            swaps++;
          }
        }
        return swaps;
      },
      (d) => d[mode]
    );

    // Find the driver with the most swaps
    const [topDriver, topSwaps] = Array.from(swapsByDriver).reduce(
      (max, current) => (current[1] > max[1] ? current : max),
      ["", 0]
    );

    // Calculate the average swaps
    const totalSwaps = Array.from(swapsByDriver.values()).reduce(
      (sum, swaps) => sum + swaps,
      0
    );
    const avgSwaps = (totalSwaps / swapsByDriver.size).toFixed(2);

    cardsData = [
      { title: topDriver, value: topSwaps, caption: "Trocas de posição" },
      { title: "Média de Trocas", value: avgSwaps, caption: "Trocas em média" },
    ];
  }
 
  // Atualiza o gráfico
  let clickedEntitys = [];
  $: mode, clickedEntitys = []; // Reset clickedEntitys when mode changes
  $: if (vizContainer) {
    let filtered = standings.filter((d) => d.round <= currentRound);
    let groups = d3.group(filtered, (d) => d[mode]);
    series = Array.from(groups, ([key, vals]) => ({
      key,
      values: vals.sort((a, b) => a.round - b.round).map((d) => ({
        key: d[mode],
        round: d.round,
        position: d.position,
      })),
    }));

    // Add a title
    svg.selectAll("text.title").remove();
    svg.append("text")
      .attr("class", "title")
      .attr("x", config.width / 2) // Half of SVG width
      .attr("y", 20)  // Distance from top
      .attr("text-anchor", "middle") // Center the text
      .style("font-size", "1em")
      .style("font-family", "var(--font-f1)")
      .style("fill", "var(--color-text)") // Set text color
      .text(`Histórico de Classificação da Temporada de ${(mode == "driver")?'Pilotos':'Construtores'} ${season}`);

    x.domain(rounds);
    svg.selectAll(".x.label").remove();
    svg.append("text")
      .attr("class", "x label")
      .attr("text-anchor", "middle")
      .attr("x", config.width / 2)
      .attr("y", config.height - 6)
      .style("font-family", "var(--font-f1)")
      .style("fill", "var(--color-text)") // Set text color
      .text("Rodada");
      
    y.domain([d3.max(standings, (d) => d.position) + 1, 1]);
    svg.selectAll(".y.label").remove();
    svg.append("text")
      .attr("class", "y label")
      .attr("text-anchor", "middle")
      .attr("y", 6)
      .attr("x", -config.height / 2)
      .attr("dy", ".75em")
      .attr("transform", "rotate(-90)")
      .style("font-family", "var(--font-f1)")
      .style("fill", "var(--color-text)") // Set text color
      .text("Classificação");

    g.selectAll(".axis").remove();
    g
      .append("g")
      .attr("class", "axis axis-x")
      .attr("transform", `translate(0,${innerH})`)
      .call(d3.axisBottom(x).tickSizeOuter(0))
      .selectAll("text")
      .style("font-size", "0.4rem"); // Adjust font size for x-axis labels
    g
      .append("g")
      .attr("class", "axis axis-y")
      .call(
      d3
        .axisLeft(y)
        .tickValues(ranks)
        .tickFormat(d3.format("d"))
        .tickSizeOuter(0)
      )
      .selectAll("text")
      .style("font-size", "0.4rem"); // Adjust font size for y-axis labels
    
    const lineGroup = g.selectAll(".series").data(series, (d) => d.key);
    lineGroup.exit().remove();
    const lineEnter = lineGroup.enter().append("g").attr("class", "series");
    lineEnter
      .append("path")
      .attr("class", "line")
      .attr("fill", "none")
      .attr("stroke-width", 1.5)
      .merge(lineGroup.select("path.line"))
      .on("mouseenter", (event, d) => nameInteraction(d.key, event))
      .on("mouseleave", (event, d) => nameInteraction(d.key, event))
      .on("click", (event, d) => nameInteraction(d.key, event))
      .transition()
      .duration(config.transitionMs)
      .attr("stroke", (d, i) => colorScheme[d.key])
      .attr("opacity", (d) => 
        clickedEntitys.length === 0 || clickedEntitys.includes(d.key) ? 1 : config.opacity
      )
      .attr("d", (d) => lineGen(d.values));
      
      const labels = g.selectAll(".end-label").data(series, (d) => d.key);
      labels.exit().remove();
      labels
      .enter()
      .append("text")
      .attr("class", "end-label")
      .merge(labels)
      .style("font-size", "0.5rem")
      .style("fill", (d) => colorScheme[d.key])
      .style('cursor', 'pointer')
      .attr("x", innerW + 5)
      .text((d) => `${d.values[d.values.length - 1].position.toString().padStart(2, '0')} - ${d.key}`)
      .on("mouseenter", (event, d) => nameInteraction(d.key, event))
      .on("mouseleave", (event, d) => nameInteraction(d.key, event))
      .on("click", (event, d) => nameInteraction(d.key, event))
      .transition()
      .duration(config.transitionMs)
      .attr("opacity", (d) => {
        return clickedEntitys.length === 0 || clickedEntitys.includes(d.key) ? 1 : config.opacity
      }
      )
      .attr("y", (d) => {
        const last = d.values.find((v) => v.round === currentRound);
        return last ? y(last.position) : y(d.values[d.values.length - 1].position);
      })
      .style("dominant-baseline", "middle");

  }

  /************************************************
  Tooltips
  ************************************************/
  let hoveredIndex = -1;
  $: hoveredEntity = entities[hoveredIndex] ?? hoveredEntity ?? {};

  let cursor = {x: 0, y: 0};
  const cusorOffset = 5;
  function handleMouseMove(event) {
    cursor.x = event.clientX + cusorOffset;
    cursor.y = event.clientY + cusorOffset;
  }
  window.addEventListener("mousemove", handleMouseMove);

  let entityTooltip;
  let tooltipPosition = {x: 0, y: 0};
  async function nameInteraction (index, evt) {
    let hoveredDot = evt.target;
    if (evt.type === "mouseenter") {
        hoveredIndex = index;
        tooltipPosition = await computePosition(hoveredDot, entityTooltip, {
            strategy: "fixed", // because we use position: fixed
            middleware: [
                offset(5), // spacing from tooltip to dot
                autoPlacement() // see https://floating-ui.com/docs/autoplacement
            ],
        });
    } else if (evt.type === "mouseleave") {
        hoveredIndex = -1
    } else if (evt.type === "click") {
        let entity = entities[index]
        if (!clickedEntitys.includes(entity.name)) {
            // Add the entity to the clickedEntitys array
            clickedEntitys = [...clickedEntitys, entity.name];
        }
        else {
            // Remove the entity from the array
            clickedEntitys = clickedEntitys.filter(c => c !== entity.name);
        }
    }
  }

  /************************************************
  Play/Pause
  ************************************************/
  let playing = false;
  let timer;
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
</script>

<div class="graph-container season-chart">
  <div class="controls">
    <label>Modo:
      <select bind:value={mode}>
        <option value="driver">Pilotos</option>
        <option value="constructor">Escuderias</option>
      </select>
    </label>

    <label>Temporada:
      <select bind:value={season}>
        {#each seasons as y}
          <option value={y}>{y}</option>
        {/each}
      </select>
    </label>

    <input
        type="range"
        id="round-slider"
        min="1"
        max={maxRound}
        bind:value={currentRound}
        on:input={handleSlider}
      />

    <button class="play-pause-button" on:click={togglePlay}>
      {playing ? "Pausar" : "Play"}
    </button>
       <button class="clear-button" on:click={clearSelections}>
            Limpar seleção
          </button>
    <CardContainer cardsData={cardsData} />
  </div>

  <div
    bind:this={vizContainer}
    id="season-chart-container"
  />
  <div class="info tooltip" hidden={hoveredIndex === -1}  bind:this={entityTooltip} style="top: {cursor.y}px; left: {cursor.x}px">
    {#if hoveredEntity.name}
      <img 
      src={`${base}/images/${mode}s/${hoveredEntity.id}.png`}
      alt={hoveredEntity.name}
      class="thumb" 
      onerror={`this.src='${base}/images/unknown.png';`}
      />
    {/if}
    <dt>{(mode == 'driver')?'Piloto':'Construtor'}</dt>
    <dd><a href="{ hoveredEntity.url }" target="_blank">{ hoveredEntity.name }</a></dd>
    
    <dt>Nacionalidade</dt>
    <dd>{ hoveredEntity.nationality }</dd>
    
    {#if mode == 'driver'}
      <dt>Nascimento</dt>
      <dd>{#if hoveredEntity.dateOfBirth}{d3.timeFormat("%d/%m/%Y")(new Date(hoveredEntity.dateOfBirth))}{/if}</dd>

      <dt>Escuderia</dt>
      <dd>{ hoveredEntity.constructor }</dd>
    {/if}

    <dt>Posição</dt>
    <dd>{ hoveredEntity.position }</dd>

    <dt>Pontos</dt>
    <dd>{ hoveredEntity.points }</dd>

    <dt>Vitórias</dt>
    <dd>{ hoveredEntity.wins }</dd>
</div>    
</div>

<style lang="scss">
  .graph-container {
    border-radius: 8px;
    background-color: var(--color-background-light);
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-around;
    padding: 20px;
    gap: 20px;
  }

  .graph-container :global(svg),
  .graph-container :global(canvas) {
    width: auto;
    max-height: 100%;
  }

  .controls {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-around;
    gap: 20px;
    width: 100%;
    height: 10%;
    padding: 0 10px;
  }

  .controls label {
    display: inline-flex;
    align-items: center;
    justify-content: flex-start;
    gap: 4px;
  }

  .controls select,
  .controls .play-pause-button {
    padding: 10px 16px;
    border: none;
    background-color: var(--color-dark-light);
    color: var(--color-text);
    border-radius: 4px;
    transition: background-color 0.2s ease;
    cursor: pointer;
  }
  .controls select {
    width: auto;
    max-width: 120px;
  }
  .controls .play-pause-button {
    width: 80px;
  }
  .controls select:hover,
  .controls .play-pause-button:hover {
    background-color: #555;
  }

  #round-slider {
    -webkit-appearance: none;
    width: 150px;
    background: var(--color-dark-light);
    border-radius: 2px;
    cursor: pointer;
    height: 5px;
  }
  
  #round-slider::-webkit-slider-thumb{
    -webkit-appearance: none;
    width: 12px;
    height: 12px;
    background: var(--color-text);
    border-radius: 50%;
    cursor: pointer;
    margin: 3px 0;
  }

  #round-slider::-moz-range-thumb {
    width: 12px;
    height: 12px;
    background: var(--color-text);
    border-radius: 50%;
    cursor: pointer;
    margin: 3px 0;
  }

  #season-chart-container {
    width: 100%;
    height: 90%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .end-thumb:not([href]) { display: none; }

  .info {
    display: grid;
    grid-template-columns: auto auto;
    background-color: var(--color-background-light);
    box-shadow: 1px 1px 3px 3px gray;
    border-radius: 5px;
    backdrop-filter: blur(10px);
    padding: 10px;
    gap: 5px;
    width: 250px;
    transition: opacity 0.5s, visibility 0.5s;
  }
  .info[hidden]:not(:hover, :focus-within) {
    opacity: 0;
    visibility: hidden;
  }
  .info dt {
    grid-column: 1;
  }
  .info dd {
    grid-column: 2;
    font-weight: 400;
  }
  .tooltip {
    position: fixed;
    top: 1em;
    left: 1em;
  }
  .cards {
    height: 65px;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  img.thumb {
    grid-column: span 2;
    justify-self: center;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    margin: 0 auto;
  }
  .controls .clear-button {
    padding: 10px 16px;
    border: none;
    background-color: var(--color-dark-light);
    color: var(--color-text);
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  .controls .clear-button:hover {
    background-color: #555;
  }
</style>
