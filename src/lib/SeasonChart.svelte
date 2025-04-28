<script>
  import * as d3 from "d3";
  import { standingsBySeason, getSeasons, getRounds, getEntities } from "$lib/standingsUtils";
  import {
      computePosition,
      autoPlacement,
      offset,
  } from '@floating-ui/dom';
  import { createEventDispatcher } from "svelte";
  const CLIP_ID = "driver-thumb-clip";
  let topDriverLocal  = null;
  let topSwapsLocal   = 0;
  let avgSwapsLocal   = 0;

  const norm = (str) =>
  str
    .normalize("NFD")               // separa acento
    .replace(/[\u0300-\u036f]/g, "")// remove marcas
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "");     // tira espaços, hífens, etc.

const driverPics = import.meta.glob(
    "/src/lib/assets/img/drivers/*.{png,jpg,jpeg}",
    { eager: true, as: "url" }
  );

  const teamPics = import.meta.glob(
    "/src/lib/assets/img/teams/*.{png,jpg,jpeg}",
    { eager: true, as: "url" }
  );

/* ▼ 1B. Constrói dicionários  { "Nome Sobrenome": url } */
 const imgByDriver = {};
 for (const [path, url] of Object.entries(driverPics)) {
   // tenta extrair o nome após o underscore
   const match = path.match(/\/drivers\/\d+_([^\.]+)\./);
   if (match) {
     const raw = match[1];
     imgByDriver[norm(raw)] = url;
   }
 }

 const imgByTeam = {};
 for (const [path, url] of Object.entries(teamPics)) {
   const match = path.match(/\/teams\/\d+_([^\.]+)\./);
   if (match) {
     const raw = match[1];
     imgByTeam[norm(raw)] = url;
   }
 }
  const dispatch = createEventDispatcher();

  export let f1data = {};

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

  let maxRound = 1;
  let currentRound = 1;
  let rounds = [];
  let ranks = [];

  let entities = {};
  $: entities = getEntities(f1data, season, mode, currentRound);

  $: season, maxRound = Math.max(...standings.map(d => d.round));
  if (season){
    dispatch("seasonChange", { season });
  }

  function thumbPath(name) {
    const key = norm(name);
    return mode === "driver" ? imgByDriver[key] : imgByTeam[key];
  }
  
  $: currentRound = maxRound;
  $: season, rounds = getRounds(f1data, season);
  $: ranks = [...new Set(standings.map(d => d.position))].sort((a, b) => a - b);

  const config = {
    width: 800,
    height: 360,
    margin: { top: 50, right: 140, bottom: 40, left: 50 },
    transitionMs: 500,
    opacity: 0.3,
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

    g.append("defs")
      .append("clipPath")
        .attr("id", CLIP_ID)
      .append("circle")
        .attr("cx", 12)   /* metade do tamanho que daremos à thumb */
        .attr("cy", 12)
        .attr("r", 12);
  
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

  $: if (standings.length) {
  const swapsPerDriver = {};

  /* se não existir positionChange, deriva por diferença entre corridas */
  standings.forEach(d => {
    const key = d.driver;
    if (!swapsPerDriver[key]) swapsPerDriver[key] = 0;

    if (d.hasOwnProperty("positionChange")) {
      swapsPerDriver[key] += Math.abs(d.positionChange ?? 0);
    } else {
      // diferença da posição nesta corrida para a corrida anterior
      const prev = standings.find(p => p.driver === key && p.round === d.round - 1);
      if (prev) swapsPerDriver[key] += Math.abs(prev.position - d.position);
    }
  });

  const entries = Object.entries(swapsPerDriver).sort((a, b) => b[1] - a[1]);

  topDriverLocal = entries[0]?.[0] ?? null;
  topSwapsLocal  = entries[0]?.[1] ?? 0;

  const total = entries.reduce((s, [, v]) => s + v, 0);
  avgSwapsLocal = entries.length ? Number((total / entries.length).toFixed(1)) : 0;

  dispatch("metrics", {
    topDriver: topDriverLocal,
    topSwaps : topSwapsLocal,
    avgSwaps : avgSwapsLocal,
    season   : season          // opcional — mantém a info da temporada
  });
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
      .style("font-family", "sans-serif")
      .text(`Histórico de Classificação da Temporada de ${(mode == "driver")?'Pilotos':'Construtores'} ${season}`);

    x.domain(rounds);
    svg.selectAll(".x.label").remove();
    svg.append("text")
      .attr("class", "x label")
      .attr("text-anchor", "middle")
      .attr("x", config.width / 2)
      .attr("y", config.height - 6)
      .text("Corrida");
      
    y.domain([d3.max(standings, (d) => d.position) + 1, 1]);
    svg.selectAll(".y.label").remove();
    svg.append("text")
      .attr("class", "y label")
      .attr("text-anchor", "middle")
      .attr("y", 6)
      .attr("x", -config.height / 2)
      .attr("dy", ".75em")
      .attr("transform", "rotate(-90)")
      .text("Classificação");

    g.selectAll(".axis").remove();
    g
      .append("g")
      .attr("class", "axis axis-x")
      .attr("transform", `translate(0,${innerH})`)
      .call(d3.axisBottom(x).tickSizeOuter(0));
    g
      .append("g")
      .attr("class", "axis axis-y")
      .call(
        d3
          .axisLeft(y)
          .tickValues(ranks)
          .tickFormat(d3.format("d"))
          .tickSizeOuter(0)
      );
    
    const lineGroup = g.selectAll(".series").data(series, (d) => d.key);
    lineGroup.exit().remove();
    const lineEnter = lineGroup.enter().append("g").attr("class", "series");

    lineEnter
      .append("path")
      .attr("class", "line")
      .attr("fill", "none")
      .attr("stroke-width", 1.5)
      .merge(lineGroup.select("path.line"))
      .transition()
      .duration(config.transitionMs)
      .attr("stroke", (d, i) => d3.schemeTableau10[i % 10])
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
      .style("font-size", "0.75rem")
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

    const thumbs = g.selectAll(".end-thumb").data(series, d => d.key);
    thumbs.exit().remove();

    thumbs.enter()
      .append("image")
      .attr("class", "end-thumb")
      .attr("width", 24)
      .attr("height", 24)
      .attr("clip-path", `url(#${CLIP_ID})`)
    .merge(thumbs)
         .attr("href",       d => thumbPath(d.key) || null)
         .attr("xlink:href", d => thumbPath(d.key) || null)         // muda se a temporada muda
      .attr("opacity", d =>
        clickedEntitys.length === 0 || clickedEntitys.includes(d.key)
          ? 1 : config.opacity )
      .attr("onerror", "this.remove()")
      .attr("x", d => {
        const last = d.values.find(v => v.round === currentRound) 
                  || d.values[d.values.length - 1];
        return x(last.round) - 12;                      // centraliza
      })
      .attr("y", d => {
        const last = d.values.find(v => v.round === currentRound) 
                  || d.values[d.values.length - 1];
        return y(last.position) - 12;
      });
  }

  $: if (g && series.length) {
  const thumbs = g.selectAll(".end-thumb");

  thumbs
    .attr("x", d => {
      const last =
        d.values.find(v => v.round === currentRound) ||
        d.values[d.values.length - 1];
      return x(last.round) - 12;
    })
    .attr("y", d => {
      const last =
        d.values.find(v => v.round === currentRound) ||
        d.values[d.values.length - 1];
      return y(last.position) - 12;
    })
    .raise();

  /* se quiser que o label acompanhe também: */
  const labels = g.selectAll(".end-label");
  labels.attr("y", d => {
    const last =
      d.values.find(v => v.round === currentRound) ||
      d.values[d.values.length - 1];
    return y(last.position);
  });
}

  /************************************************
  Tooltips
  ************************************************/
  let hoveredIndex = -1;
  $: hoveredEntity = entities[hoveredIndex] ?? hoveredEntity ?? {};

  let cursor = {x: 0, y: 0};

  let entityTooltip;
  let tooltipPosition = {x: 0, y: 0};
  async function nameInteraction (index, evt) {
    let hoveredDot = evt.target;
    if (evt.type === "mouseenter") {
        hoveredIndex = index;
        cursor = {x: evt.x, y: evt.y};
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
  </div>
  <div
    bind:this={vizContainer}
    id="season-chart-container"
  />
  <div class="info tooltip" hidden={hoveredIndex === -1}  bind:this={entityTooltip} style="top: {cursor.y}px; left: {cursor.x}px">
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

    <!-- Add: Time, author, lines edited -->
</div>    
</div>

<style lang="scss">
  .graph-container {
    border: 2px solid #ddd;
    border-radius: 8px;
    background-color: #fff;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .controls {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    gap: 20px;
    width: 100%;
    height: 50px;
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
    background-color: #333;
    color: #fff;
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

  .controls input[type="range"] {
    -webkit-appearance: none;
    width: 150px;
    height: 4px;
    background: #333;
    border-radius: 2px;
    cursor: pointer;
  }
  .controls input[type="range"]::-webkit-slider-thumb,
  .controls input[type="range"]::-moz-range-thumb {
    width: 12px;
    height: 12px;
    background: #fff;
    border-radius: 50%;
    cursor: pointer;
    margin-top: -4px;
  }

  #season-chart-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .end-thumb:not([href]) { display: none; }

  .info {
    display: grid;
    grid-template-columns: auto auto;
    background-color: oklch(100% 0% 0 / 80%);
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
</style>
