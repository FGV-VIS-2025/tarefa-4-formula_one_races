<script>
    import * as d3 from 'd3';
    import { onMount } from 'svelte';
  
    /**
     * ┌──────────────────────────────────────────────────────────┐
     * │   F1 RVI – Rank-Volatility Index Dashboard              │
     * └──────────────────────────────────────────────────────────┘
     *  A polished, information-dense visual that quantifies how
     *  turbulent the points table is from race to race.
     *
     *  RVI(r) = 1/(n·(n−1)) · Σ |posᵢ(r) − posᵢ(r−1)|
     *           → 0 (stable) … 1 (total shake-up)
     *
     *  Extra goodies:
     *   • dropdown season filter
     *   • hover card with deep stats & top movers
     *   • animated redraw on season switch
     */
  
    export let f1data = {};
    export let mode = 'driver';         // 'driver' | 'constructor'
    export let season = null;           // if null => latest
    export let showSeasonSelector = false;
  
    /* ───────────────────────────────────────────── Seasons  */
    let seasons = [];
    $: if (f1data[mode + 'Standings']) {
      seasons = [...new Set(f1data[mode + 'Standings'].map(d => d.season))].sort((a,b)=>b-a);
      if (!season) season = seasons[0];
    }
  
    /* ───────────────────────────────────────────── Data prep */
    let series = [];
    let rounds = [];
    $: season, mode, f1data, buildSeries();
  
    function buildSeries() {
      if (!f1data[mode + 'Standings'] || !season) return;
  
      const standings = f1data[mode + 'Standings'].filter(d => d.season === season);
      const byRound   = d3.group(standings, d => d.round);
      const maxRound  = d3.max(standings, d => d.round) || 0;
      rounds          = d3.range(1, maxRound + 1);
  
      series = d3.range(2, maxRound + 1).map(r => {
        const prev = byRound.get(r-1) || [];
        const curr = byRound.get(r)   || [];
        const id   = mode==='driver' ? d => d.driverId : d => d.constructorId;
  
        // Map id → position last round
        const prevPos = new Map(prev.map(d => [id(d), d.position]));
        const deltas  = curr.map(d => ({
          id : id(d),
          delta : (prevPos.get(id(d)) ?? d.position) - d.position   // + = climb
        }));
        const n = deltas.length || 1;
        const sumAbs = d3.sum(deltas, d => Math.abs(d.delta));
        const rvi = sumAbs / (n*(n-1));       // 0–1 scale
  
        // auxiliary metrics
        const swaps = deltas.filter(d => d.delta !== 0).length;
        const topClimber = d3.least(deltas, d => d.delta) || {id:'', delta:0};
        const topDropper = d3.greatest(deltas, d => d.delta) || {id:'', delta:0};
  
        const nameMap = mode==='driver' ? new Map(f1data.drivers.map(d=>[d.driverId, `${d.givenName} ${d.familyName}`]))
                                        : new Map(f1data.constructors.map(d=>[d.constructorId, d.name]));
  
        return {
          round: r,
          rvi,
          swaps,
          swapPct: swaps / n,
          topClimber: { name: nameMap.get(topClimber.id), delta: topClimber.delta },
          topDropper: { name: nameMap.get(topDropper.id), delta: topDropper.delta }
        };
      });
  
      draw();
    }
  
    /* ───────────────────────────────────────────── SVG dims */
    const cfg = { w: 780, h: 340, m:{t:36,r:40,b:40,l:56}, dur:650 };
    let svgEl, tooltipEl;
  
    function draw(){
      if(!svgEl || !series.length) return;
      const innerW = cfg.w - cfg.m.l - cfg.m.r;
      const innerH = cfg.h - cfg.m.t - cfg.m.b;
  
      const svg = d3.select(svgEl)
        .attr('viewBox',`0 0 ${cfg.w} ${cfg.h}`)
        .attr('preserveAspectRatio','xMidYMid meet');
      svg.selectAll('*').remove();
  
      const g = svg.append('g').attr('transform',`translate(${cfg.m.l},${cfg.m.t})`);
  
      const x = d3.scaleLinear().domain(d3.extent(series,d=>d.round)).range([0,innerW]);
      const y = d3.scaleLinear().domain([0,d3.max(series,d=>d.rvi)]).nice().range([innerH,0]);
  
      /* Glow defs */
      svg.append('defs').append('filter').attr('id','glow')
         .html('<feGaussianBlur stdDeviation="3" result="colored"/><feMerge><feMergeNode in="colored"/><feMergeNode in="SourceGraphic"/></feMerge>');
  
      /* Gradient for area */
      const defs = svg.append('defs');
      const grd  = defs.append('linearGradient').attr('id','areaGrad').attr('x1','0%').attr('y1','0%').attr('x2','0%').attr('y2','100%');
      grd.append('stop').attr('offset','0%').attr('stop-color','#e10600').attr('stop-opacity',0.5);
      grd.append('stop').attr('offset','100%').attr('stop-color','#e10600').attr('stop-opacity',0);
  
      /* Axes */
      const axisX = g.append('g').attr('class','axis x').attr('transform',`translate(0,${innerH})`)
        .call(d3.axisBottom(x).ticks(series.length).tickFormat(d3.format('d')));
      const axisY = g.append('g').attr('class','axis y')
        .call(d3.axisLeft(y).ticks(6).tickFormat(d3.format('.0%')));
  
      /* Axis styles */
      svg.selectAll('.axis text').attr('fill','#fff').style('font-size','11px');
      svg.selectAll('.axis path, .axis line').attr('stroke','#666').attr('stroke-opacity',0.25);
  
      /* Area */
      const area = d3.area()
        .x(d=>x(d.round)).y0(innerH).y1(d=>y(d.rvi)).curve(d3.curveMonotoneX);
      g.append('path').datum(series).attr('fill','url(#areaGrad)').attr('d',area).attr('opacity',0.8);
  
      /* Line */
      const line = d3.line().x(d=>x(d.round)).y(d=>y(d.rvi)).curve(d3.curveMonotoneX);
      g.append('path').datum(series)
        .attr('fill','none').attr('stroke','#e10600').attr('stroke-width',2.5)
        .attr('filter','url(#glow)')
        .attr('d',line)
        .attr('stroke-dasharray',function(){return this.getTotalLength()})
        .attr('stroke-dashoffset',function(){return this.getTotalLength()})
        .transition().duration(cfg.dur).ease(d3.easeQuadOut)
        .attr('stroke-dashoffset',0);
  
      /* Dots */
      g.selectAll('circle').data(series).enter().append('circle')
        .attr('cx',d=>x(d.round)).attr('cy',d=>y(d.rvi)).attr('r',4)
        .attr('fill','#fff').attr('stroke','#e10600').attr('stroke-width',1.5)
        .on('mouseenter', (e,d)=>showTip(e,d)).on('mouseleave',hideTip);
  
      /* Title */
      svg.append('text').attr('x',cfg.w/2).attr('y',24).attr('text-anchor','middle')
        .style('font-size','16px').style('font-weight',600).style('fill','#fff')
        .text(`RVI – Volatilidade de ${(mode==='driver')? 'Pilotos':'Construtores'} · ${season}`);
    }
  
    /* ───────────────────────────────────────────── Tooltip */
    function showTip(evt,d){
      tooltipEl.hidden=false;
      tooltipEl.style.left=(evt.clientX+12)+'px';
      tooltipEl.style.top =(evt.clientY+12)+'px';
      tooltipEl.innerHTML = `
        <strong>Corrida ${d.round}</strong><br>
        RVI: <b>${d3.format('.3f')(d.rvi)}</b><br>
        Trocas: <b>${d.swaps}</b> (${d3.format('.0%')(d.swapPct)})<br>
        ⬆️ ${d.topClimber.name ?? '—'} (${Math.abs(d.topClimber.delta)}↑)<br>
        ⬇️ ${d.topDropper.name ?? '—'} (${d.topDropper.delta}↓)`;
    }
    function hideTip(){ tooltipEl.hidden=true; }
  
    onMount(()=> draw());
  </script>
  
  <!-- ───────────────────────────── UI Wrapper -->
  <div class="chartwrap">
    {#if showSeasonSelector && seasons.length}
      <label class="selector">Temporada:
        <select bind:value={season}>
          {#each seasons as y}<option value={y}>{y}</option>{/each}
        </select>
      </label>
    {/if}
  
    <svg bind:this={svgEl}></svg>
    <div class="tooltip" hidden bind:this={tooltipEl}></div>
  </div>
  
  <style>
    .chartwrap{position:relative;width:100%;height:100%;display:flex;flex-direction:column;align-items:center;gap:8px}
    svg{width:100%;height:100%;max-height:320px}
  
    .selector{color:#fff;font-size:0.9rem;font-family:system-ui;padding:4px 6px;border-radius:4px;align-self:flex-end}
    select{background:#111;color:#fff;border:1px solid #444;border-radius:4px;padding:4px 6px;cursor:pointer}
    select:focus{outline:none;border-color:#e10600}
  
    .tooltip{position:fixed;background:rgba(0,0,0,.88);color:#fff;padding:8px 10px;border-radius:4px;font-size:0.75rem;pointer-events:none;z-index:10000;box-shadow:0 3px 8px rgba(0,0,0,.5);white-space:nowrap}
  </style>