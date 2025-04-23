<script>
  import { onMount, onDestroy } from "svelte";
  import * as d3 from "d3";
  import { standingsBySeason, getSeasons, getRounds } from "$lib/standingsUtils";
  import { createChart } from "$lib/charts/lineStandings";

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

  $: season, maxRound = Math.max(...standings.map(d => d.round));
  $: currentRound = maxRound;
  $: season, rounds = getRounds(f1data, season);
  $: ranks = [...new Set(standings.map(d => d.position))].sort((a, b) => a - b);

  const config = {
    width: 800,
    height: 360,
    margin: { top: 50, right: 140, bottom: 40, left: 50 },
    transitionMs: 500,
  }

  const innerW = config.width - config.margin.left - config.margin.right;
  const innerH = config.height - config.margin.top - config.margin.bottom;

  let svg, g, x, y, lineGen;

  $: if (vizContainer) {
    if (svg) {
      svg.remove();
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

  $: if (vizContainer) {
    let filtered = standings.filter((d) => d.round <= currentRound);
    let groups = d3.group(filtered, (d) => d[mode]);
    let series = Array.from(groups, ([key, vals]) => ({
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
      .text("Round");
      
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
      .attr("d", (d) => lineGen(d.values));

    const circleEnter = lineGroup
      .enter()
      .append("g")
      .attr("class", "circle")
    
    circleEnter
      .selectAll("circle")
      .data((d) => d.values.filter((v) => v.round == 1).map((v) => ({ key: d.key, data: v })))
      .join("circle")
      .attr("r", 2)
      .attr("fill", (d) => {
        const seriesIndex = series.findIndex((s) => s.key === d.key);
        return d3.schemeTableau10[seriesIndex % 10];
      })
      .attr("cy", (d) => y(d.data.position))
      .transition()
      .duration(config.transitionMs)
      .attr("cx", (d) => x(d.data.round));

    const labels = g.selectAll(".end-label").data(series, (d) => d.key);
    labels.exit().remove();
    labels
      .enter()
      .append("text")
      .attr("class", "end-label")
      .merge(labels)
      .style("font-size", "0.75rem")
      .attr("x", innerW + 5)
      .text((d) => `${d.values[d.values.length - 1].position.toString().padStart(2, '0')} - ${d.key}`)
      .transition()
      .duration(config.transitionMs)
      .attr("y", (d) => {
        const last = d.values.find((v) => v.round === rounds[d.values.length - 1]);
        return last ? y(last.position) : y(d.values[d.values.length - 1].position);
      })
      .style("dominant-baseline", "middle");
  }

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
</div>

<style lang="scss">
  .play-pause-button {
    padding: 2px 0;
    cursor: pointer;
    border: none;
    background-color: #333;
    color: #fff;
    border-radius: 4px;
    width: 60px;
    transition: background-color 0.2s ease;
  }

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
    justify-content: space-around;
    width: 100%;
    height: 50px;
  }

  #season-chart-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  #round-slider {
    width: 240px;
    margin: 0 10px;
  }
</style>
