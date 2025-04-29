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

Aspecto | Decisão | Alternativas consideradas | Motivo da escolha
Codificação visual | Linhas conectando posições por corrida; eixo Y invertido (P1 no topo) | Bump chart, heat-map de posições | Linhas mantêm continuidade temporal e são familiares para fãs de F-1 (semelhantes a gráficos de campeonato da TV).
Cores | Paleta d3.schemeTableau10 cíclica | Cores oficiais das equipes | Escolhemos a paleta Tableau10 pela legibilidade universal e contraste adequado em fundo branco; o logotipo colorido ao fim da linha já comunica a identidade da equipe.
Miniaturas | Fotos dos pilotos / escudos recortados (clipPath) | Ícones genéricos ou somente texto | A foto reduz o tempo de reconhecimento visual e dá apelo emocional.
Tooltip & Hover | Tooltip flutuante via Floating-UI, realçando linha ao passar o mouse | Pop-over fixo ou legenda lateral | Tooltip móvel mantém o layout enxuto e evita sobrecarregar rótulos laterais.
Interações | Slider + Play/Pause + clique para destaque | Scroll para animar, “o-domínio” de seletores múltiplos | A combinação cobre bem tanto desktop quanto mobile e não exige barras de rolagem.
Animação | d3.transition() (500 ms), timer de 800 ms entre corridas | Sem animação (jump cuts) | Animação enfatiza mudança de posição; velocidade escolhida equilibra compreensão e dinamismo.
Fullscreen | Componente FullScreen.svelte usando Fullscreen API | Abrir em nova aba ou popup | Mantém o usuário na mesma página e aproveita responsividade do SVG.

## Processo de desenvolvimento & divisão de tarefas

Membro | Principais responsabilidades
Esdras | • Análise exploratória dos dados (exploration/)  • Efeito de hover e tooltips  • Refatoração geral + reorganização de estilos  • Correção de bugs identificados na fase de teste
João Villas | • dataLoader.js (carregamento assíncrono e normalização de JSON)  • standingsUtils.js (filtros de temporada, pilotos e métricas)  • Implementação dos dropdowns e slider de filtros  • Scraper para escuderias das equipes  • Cards de estatísticas complementares
Marcelo Angelo | • Estrutura inicial Svelte (+page.svelte)  • Componente FullScreen.svelte & estilização global  • SeasonChart.svelte (visualização principal)  • Animações das linhas e thumbnails  • Scraper de fotos dos pilotos  • Ajustes de CSS na estilização da visualização e seus componentes