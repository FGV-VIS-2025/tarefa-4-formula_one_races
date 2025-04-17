# Dataset

Decidimos utilizar dados das corridas de formula 1 que serão consumidos da API [jolpica](https://github.com/jolpica/jolpica-f1).

## Análise exploratória

Durante a análise exploratória tivemos o primeiro contato com a API e decidimos utilizar seus dados, mas com uma abordagem um pouco diferente do ponto de vista de arquitetura, para garantir a constância das informações. Para isso, salvaremos os dados de forma local, no repositório, utilizando o GitHub Actions para atualizar esses dados a partir da API toda segunda-feira após as corridas.

## Como a classificação muda ao longo das corridas?

A ideia inicial é observar como a classificação dos pilos/scuderias muda ao longo de uma temporada.
