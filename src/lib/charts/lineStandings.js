/*  ==========================================================================
    charts/lineStandings.js   –  v2  (incremental + legend + tooltip)
    ========================================================================== */

    import * as d3 from 'd3';
    import { standingsBySeason } from '../standingsUtils';
    
    // --- CONSTANTES GERAIS ------------------------------------------------------
    const COLORS = d3.schemeTableau10;
    const T_MARGIN = { top: 20, right: 20, bottom: 40, left: 40 };
    
    // --- TOOLTIP (singleton) ----------------------------------------------------
    const tip = (() => {
      let div;
      return {
        show(html, evt) {
          if (!div) {
            div = d3
              .select('body')
              .append('div')
              .attr('class', 'd3-tip')
              .style('position', 'fixed')
              .style('pointer-events', 'none')
              .style('padding', '6px 8px')
              .style('background', '#000')
              .style('color', '#fff')
              .style('font-size', '0.75rem')
              .style('border-radius', '4px')
              .style('opacity', 0);
          }
          div.html(html).style('opacity', 1);
          const { clientX: x, clientY: y } = evt;
          div.style('left', `${x + 12}px`).style('top', `${y + 12}px`);
        },
        hide() {
          if (div) div.style('opacity', 0);
        }
      };
    })();
    
    /* ===========================================================================
       FACTORY
       ========================================================================== */
    export function createChart(containerSelector, datasets, optsInit = {}) {
      /* -- ESTADO ---------------------------------------------------------------- */
      let cfg = {
        width: 850,
        height: 480,
        transitionMs: 800,
        ...optsInit
      };
    
      let mode = cfg.mode ?? 'driver'; // 'driver' | 'constructor'
      let season = +cfg.season;
      let round = cfg.round ?? 1;
    
      const labelField = () => (mode === 'driver' ? 'driver' : 'constructor');
    
      /* -- PREPARE DOM ----------------------------------------------------------- */
      const root = d3.select(containerSelector);
      root.selectAll('*').remove();
    
      // wrapper flex → gráfico + legenda
      const wrap = root.append('div').style('display', 'flex').style('flex-direction', 'column');
    
      const svg = wrap
        .append('svg')
        .attr('viewBox', [0, 0, cfg.width, cfg.height].join(' '))
        .attr('width', '100%')
        .attr('height', cfg.height);
    
      const legendDiv = wrap.append('div').attr('class', 'legend');
    
      // escalas fixas
      const { top, right, bottom, left } = T_MARGIN;
      const innerW = cfg.width - left - right;
      const innerH = cfg.height - top - bottom;
    
      const x = d3.scaleLinear().range([left, left + innerW]);
      const y = d3.scaleLinear().range([top + innerH, top]); // invertido
      const color = d3.scaleOrdinal(COLORS);
    
      const gx = svg.append('g').attr('class', 'axis-x');
      const gy = svg.append('g').attr('class', 'axis-y');
    
      const gLines = svg.append('g').attr('class', 'lines');
    
      const lineG = d3
        .line()
        .x((d) => x(d.round))
        .y((d) => y(d.position))
        .curve(d3.curveMonotoneX);
    
      /* -------------------------------------------------------------------------
       *  RENDER (full = axes + legend;  partial = só estende linha)
       * ----------------------------------------------------------------------- */
      function render({ fullUpdate }) {
        /* 1. Filtra e corta pelos parâmetros atuais */
        const raw = mode === 'driver' ? datasets.driverStandings : datasets.constructorStandings;
        const fullSeasonData = standingsBySeason(raw, season, labelField());
        const visible = fullSeasonData.filter((d) => d.round <= round);
    
        // grupos
        const grouped = d3.group(visible, (d) => d.key);
    
        /* 2. DOMÍNIOS */
        const maxRound = d3.max(fullSeasonData, (d) => d.round);
        x.domain([1, maxRound]);
        y.domain([d3.max(fullSeasonData, (d) => d.position), 1]);
        color.domain([...grouped.keys()]);
    
        /* 3. JOIN LINHAS */
        const paths = gLines.selectAll('path').data(grouped, (d) => d[0]);
    
        // EXIT
        paths.exit().remove();
    
        // UPDATE
        paths
          .transition()
          .duration(cfg.transitionMs)
          .attr('d', (d) => lineG(d[1]));
    
        // ENTER
        paths
          .enter()
          .append('path')
          .attr('fill', 'none')
          .attr('stroke-width', 2)
          .attr('stroke', (d) => color(d[0]))
          .attr('opacity', 0.8)
          .attr('d', (d) => lineG(d[1]))
          .on('mouseenter', (_, key) => highlight(key, true))
          .on('mouseleave', (_, key) => highlight(key, false));
    
        /* 4. AXES (apenas em fullUpdate p/ performance) */
        if (fullUpdate) {
          gx
            .attr('transform', `translate(0,${top + innerH})`)
            .transition()
            .duration(cfg.transitionMs)
            .call(d3.axisBottom(x).ticks(maxRound).tickSizeOuter(0));
    
          gy.attr('transform', `translate(${left},0)`).call(d3.axisLeft(y).ticks(10).tickSizeOuter(0));
        }
    
        /* 5. LEGENDA ---------------------------------------------------------------- */
        if (fullUpdate) updateLegend();
      }
    
      /* ------- LEGENDA DINÂMICA ------------------------------------------------- */
      function updateLegend() {
        const items = legendDiv.selectAll('div.legend-item').data(color.domain(), (d) => d);
    
        items.exit().remove();
    
        const enter = items.enter().append('div').attr('class', 'legend-item');
        enter
          .append('span')
          .attr('class', 'legend-color')
          .style('background', (d) => color(d));
    
        enter.append('span').attr('class', 'legend-label').text((d) => d);
    
        items
          .select('.legend-color')
          .style('background', (d) => color(d))
          .on('mouseenter', (_, key) => highlight(key, true))
          .on('mouseleave', (_, key) => highlight(key, false));
      }
    
      /* ------- HIGHLIGHT (mouse) ------------------------------------------------ */
      function highlight(key, on) {
        gLines
          .selectAll('path')
          .attr('opacity', (d) => (on ? (d[0] === key ? 1 : 0.1) : 0.8));
    
        legendDiv
          .selectAll('.legend-item')
          .style('opacity', (d) => (on ? (d === key ? 1 : 0.3) : 1));
      }
    
      /* ------- API PÚBLICA ------------------------------------------------------ */
      render({ fullUpdate: true }); // first
    
      return {
        update({ mode: m, season: s, round: r } = {}) {
          const fullUpdate = m && m !== mode || s && +s !== season;
    
          if (m) mode = m;
          if (s) season = +s;
          if (r !== undefined) round = +r;
    
          render({ fullUpdate });
        },
        destroy() {
          root.selectAll('*').remove();
        }
      };
    }
    