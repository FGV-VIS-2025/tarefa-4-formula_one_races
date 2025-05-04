## ✨ Visão-geral

Depois de uma análise exploratória dos dados da F1 utilizando a API [Jolpica](https://github.com/jolpica/jolpica-f1), decidimos responder a pergunta: **"Como os pilotos trocam de posição durante uma corrida?"**. Essa pergunta foi motivada sobretudo pelo início de temporada onde constuma-se dizer que nada está definido ainda.

Utilizamos como inspiração gráficos comuns utilizados em campeonatos de futebol para entender as mudanças no ranking.

Este projeto apresenta uma **linha do tempo interativa** que mostra, corrida a corrida, como pilotos trocam de posição durante uma temporada da Fórmula 1 (2000-2025). Além de uma breve explicação para contextualizar o leitor, bem como um gráfico secundário com uma resposta mais deireta para a pergunta inicial.

As principais características são:

* **Play / pause** para "assistir" a temporada em fast-forward.  
* **Filtro** por temporada (dropdown) e por modo *Pilotos ◄► Construtores*.  
* **Miniaturas** (foto do piloto ou escudo da equipe) pousadas no ponto mais recente do traçado.  
* **Tooltip** com estatísticas detalhadas (pontos, vitórias, nacionalidade…).  
* **Destaque por clique** para comparar apenas pilotos/equipes escolhidos.  
* **Botão de tela-cheia** que expande o gráfico (útil para apresentações).

Todo o _dataset_ é pré-coletado via *scrapers* (API, RaceFans, Wikipedia, SeekLogo) e empacotado como **CSVs + imagens estáticas**. Assim, a aplicação front-end carrega em milissegundos e não depende de chamadas de rede na hora da visualização, haja vista que para a quantidade de dados utilizadas seriam necessárias muitas chamadas na **API** atrapalhando a usabilidade..

## Justificativa de design

| Aspecto            | Decisão                                                                    | Alternativas consideradas                                                                                  | Motivo da escolha                                                                                                                                                                                               |
|--------------------|----------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Codificação visual | Linhas conectando posiçõespor corrida; eixo Y invertido (P1 no topo)      | Linhas mantêm continuidade temporal e são familiares para fãs de F1 (semelhantes a gráficos de campeonato) | As linhas destacam a trajetória de cada piloto; o eixo invertido coloca o líder sempre no topo, facilitando a leitura.                                                                                          |
| Cores              | Paleta de cores aleatórias que se encaixam bem com o tema escuro utilizado | Cores oficiais das equipes, já que não há cores oficias dos pilotos                                        | A utilização de cores aleatórias permite distinguir os pilotos, optar por cores das equipes adicionaria uma camada a mais de complexidade na coleta dos dados e faria com que dois pilotes tivessem a mesma cor |
| Miniaturas         | Fotos dos pilotos / escudos recortados (`clipPath`)                        | Ícones genéricos ou círculos coloridos                                                                     | Imagens reais agilizam o reconhecimento e criam apelo emocional para entusiastas do automobilismo.                                                                                                              |
| Tooltip & Hover    | Tooltip flutuante via Floating-UI, realçando linha ao passar o mouse       | Pop-over fixo ou legenda lateral                                                                           | Tooltip móvel mantém o layout enxuto, evita distrações e permite visualização imediata de estatísticas detalhadas.                                                                                              |
| Interações         | Slider + Play/Pause + clique para destaque                                 | Scroll para animar; seletores múltiplos                                                                    | Controle direto via slider e botões é mais intuitivo para "assistir" à evolução e destacar elementos específicos.                                                                                               |
| Animação           | `d3.transition()` (500 ms), timer de 800 ms entre corridas                 | Sem animação (jump cuts)                                                                                   | Animação suave enfatiza mudança de posições sem cansar o usuário; tempos balanceados para clareza e ritmo.                                                                                                      |


## Processo de desenvolvimento & divisão de tarefas

| Membro            | Principais responsabilidades                                                                                                                                                                                                              |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Esdras Cavalcanti | • Análise exploratória dos dados (`exploration/`)<br>• Criação da base de dados utilizada no frontend<br>• Efeito de hover e tooltips<br>• Refatoração geral e reorganização de estilos<br>• Correção de bugs identificados               |
| João Villas       | • `dataLoader.js`: carregamento assíncrono e normalização de JSON<br>• `standingsUtils.js`: filtros de temporada, pilotos e métricas<br>• Dropdowns e slider<br>• Scraper equipes<br>• Cards de estatísticas                              |
| Marcelo Angelo    | • Estrutura inicial em Svelte (`+page.svelte`)<br>• Componente `FullScreen.svelte` e estilização global<br>• `SeasonChart.svelte` (visualização principal)<br>• Animações e thumbnails<br>• Scraper fotos dos pilotos<br>• Ajustes de CSS |
| Todos os membros  | • Testes funcionais finais da visualização                                                                                                                                                                                                |

Os membros da equipe gastaram em média 3 horas para cada uma das tasks listadas acima.


## Uso de IA

Utilizamos IAs sobre tudo Copilot para auxiliar na escrita de código. Contudo, todo o código foi revisado, garantindo tanto o entendimento do que estava sendo utilizado quanto garantir a qualidade do mesmo.