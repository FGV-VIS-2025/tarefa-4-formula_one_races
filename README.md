## ✨ Visão-geral

Este projeto apresenta uma **linha do tempo interativa** que mostra, corrida a corrida, como pilotos trocam de posição durante uma temporada da Fórmula 1 (2000-2025).  
As principais características são:

* **Play / pause** para “assistir” a temporada em fast-forward.  
* **Filtro** por temporada (dropdown) e por modo *Pilotos ◄► Construtores*.  
* **Miniaturas** (foto do piloto ou escudo da equipe) pousadas no ponto mais recente do traçado.  
* **Tooltip** com estatísticas detalhadas (pontos, vitórias, nacionalidade…).  
* **Destaque por clique** para comparar apenas pilotos/equipes escolhidos.  
* **Botão de tela-cheia** que expande o gráfico (útil para apresentações).

Todo o _dataset_ é pré-coletado via *scrapers* (APIs Ergast, RaceFans, Wikipedia, SeekLogo) e empacotado como **JSON + imagens estáticas**. Assim, a aplicação front-end carrega em milissegundos e não depende de chamadas de rede na hora da visualização.

## Justificativa de design

| Aspecto                | Decisão                                                                                  | Alternativas consideradas                                                                                   | Motivo da escolha                                                                                                  |
|------------------------|------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| Codificação visual     | Linhas conectando posições por corrida; eixo Y invertido (P1 no topo)                    | Linhas mantêm continuidade temporal e são familiares para fãs de F-1 (semelhantes a gráficos de campeonato) | As linhas destacam a trajetória de cada piloto; o eixo invertido coloca o líder sempre no topo, facilitando a leitura. |
| Cores                  | Paleta `d3.schemeTableau10` cíclica                                                      | Cores oficiais das equipes                                                                                  | O Tableau10 oferece contraste equilibrado em fundo branco; o logotipo colorido ao fim da linha reforça a identidade. |
| Miniaturas             | Fotos dos pilotos / escudos recortados (`clipPath`)                                      | Ícones genéricos ou círculos coloridos                                                                      | Imagens reais agilizam o reconhecimento e criam apelo emocional para entusiastas do automobilismo.                |
| Tooltip & Hover        | Tooltip flutuante via Floating-UI, realçando linha ao passar o mouse                     | Pop-over fixo ou legenda lateral                                                                             | Tooltip móvel mantém o layout enxuto, evita distrações e permite visualização imediata de estatísticas detalhadas. |
| Interações             | Slider + Play/Pause + clique para destaque                                               | Scroll para animar; seletores múltiplos                                                                      | Controle direto via slider e botões é mais intuitivo para “assistir” à evolução e destacar elementos específicos. |
| Animação               | `d3.transition()` (500 ms), timer de 800 ms entre corridas                              | Sem animação (jump cuts)                                                                                    | Animação suave enfatiza mudança de posições sem cansar o usuário; tempos balanceados para clareza e ritmo.        |
| Fullscreen             | Componente `FullScreen.svelte` usando Fullscreen API                                     | Abrir em nova aba ou popup                                                                                  | Mantém o usuário na mesma página, aproveita responsividade do SVG e facilita apresentações sem descontinuidades.  |

## Processo de desenvolvimento & divisão de tarefas

| Membro            | Principais responsabilidades                                                                                                                                                    |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Esdras            | • Análise exploratória dos dados (`exploration/`)<br>• Efeito de hover e tooltips<br>• Refatoração geral e reorganização de estilos<br>• Correção de bugs identificados            |
| João Villas       | • `dataLoader.js`: carregamento assíncrono e normalização de JSON<br>• `standingsUtils.js`: filtros de temporada, pilotos e métricas<br>• Dropdowns e slider<br>• Scraper equipes<br>• Cards de estatísticas |
| Marcelo Angelo    | • Estrutura inicial em Svelte (`+page.svelte`)<br>• Componente `FullScreen.svelte` e estilização global<br>• `SeasonChart.svelte` (visualização principal)<br>• Animações e thumbnails<br>• Scraper fotos dos pilotos<br>• Ajustes de CSS |
| Todos os membros  | • Testes funcionais finais da visualização |

Os membros da equipe gastaram em média 3 horas para cada uma das tasks listadas acima.