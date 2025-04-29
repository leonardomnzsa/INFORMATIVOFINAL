# Documentação do Dashboard de Informativos STF (V3 - Final)

## Visão Geral

Este dashboard interativo, desenvolvido com Streamlit, permite a exploração e análise dos Informativos de Jurisprudência do Supremo Tribunal Federal (STF) compilados a partir do arquivo `Dados_InformativosSTF_filtrado.xlsx`. O objetivo é fornecer uma ferramenta para estudo e consulta dos julgados, com funcionalidades adicionais para auxiliar na fixação do conteúdo e organização dos estudos.

## Funcionalidades Principais (V3)

O dashboard está organizado em abas e possui uma barra lateral para filtros avançados.

### 1. Carregamento e Processamento de Dados (Atualizado)

- Os dados são carregados a partir do arquivo Excel `Dados_InformativosSTF_filtrado.xlsx`.
- O processo inclui:
    - Identificação e uso da coluna "Tese Julgado" para exibir a "Tese / Notícia Completa".
    - Limpeza de colunas e renomeação para nomes padronizados.
    - Conversão de tipos de dados (especialmente datas).
    - Extração de **Ano** e **Mês/Ano** da coluna "Data Julgamento" para filtros granulares.
    - Processamento da coluna "Ramo Direito": divisão dos valores múltiplos (separados por ";") e criação de linhas individuais para cada ramo (`explode`), permitindo filtragem precisa.
    - Mapeamento (simulado via dicionário) dos "Ramos do Direito" para "Áreas de Estudo" mais amplas (ex: Direito Público, Direito Privado).
    - Tratamento de valores ausentes.

### 2. Barra Lateral: Filtros Avançados (Atualizado)

- **Filtrar Data Por:** Opção para escolher entre filtrar por "Ano" ou "Mês/Ano".
    - **Ano do Julgamento:** Permite selecionar um ou mais anos.
    - **Mês/Ano do Julgamento:** Permite selecionar um ou mais meses específicos (formato AAAA-MM).
- **Área de Estudo (Simulado IA):** Permite selecionar uma ou mais áreas de estudo amplas.
- **Ramo do Direito (Específico):** Permite selecionar um ou mais ramos do direito individualmente.
- **Classe Processual:** Permite selecionar uma ou mais classes processuais.
- **Número do Informativo:** Permite selecionar um número de informativo específico ou visualizar todos.
- **Repercussão Geral:** Permite filtrar julgados com ou sem repercussão geral reconhecida (ou não informada).
- **Mostrar Apenas Favoritos:** Checkbox para exibir somente os julgados marcados como favoritos.
- **Contador:** Exibe o número total de julgados (linhas/ramos individuais) e o número de julgados únicos que correspondem aos filtros aplicados.

### 3. Aba "🔍 Informativos" (Atualizado)

- **Busca por Palavra-Chave:** Campo de texto permite buscar termos específicos nas colunas `Título`, `Tese Julgado` (Notícia Completa) e `Resumo`.
- **Modo de Visualização:**
    - **Cards:** Exibe os julgados em formato de "Cards de Leitura" expansíveis. Cada card mostra:
        - Título, número do informativo, data.
        - Botão de **Favoritar** (⭐/☆).
        - Classe processual.
        - Todos os Ramos do Direito e Áreas de Estudo associados.
        - **Tese / Notícia Completa** (conteúdo da coluna "Tese Julgado" do Excel).
        - Resumo (quando disponível e diferente da Tese).
        - Legislação (quando disponível).
        - Repercussão Geral.
        - Botões de ação ("Gerar Assertivas", "Ver Caso Prático").
    - **Tabela:** Exibe os julgados em uma tabela interativa.
- **Funcionalidade Favoritos:** Permite marcar/desmarcar julgados como favoritos.
- **Funcionalidade "Caso Prático" (Simulado):** Exibe um exemplo prático simulado.

### 4. Aba "📊 Estatísticas" (Atualizado)

- Exibe gráficos interativos baseados nos dados filtrados.
- Gráficos: Julgados por Ramo do Direito, Julgados por Área de Estudo, Julgados Únicos por Ano, Repercussão Geral.

### 5. Aba "✅ Assertivas" (Simulado)

- Permite selecionar um julgado na aba "Informativos" e simular a geração de assertivas sobre ele.

### 6. Aba "❓ Perguntas" (Simulado)

- Permite fazer perguntas em linguagem natural sobre os julgados filtrados e simula uma resposta baseada nesses dados.

### 7. Aba "🎯 Metas de Estudo" (Atualizado - Interativo)

- Permite ao usuário definir uma meta de leitura.
- **Quantidade de Julgados para Ler:** Campo numérico.
- **Botão "Gerar Meta de Leitura Aleatória":** Seleciona aleatoriamente julgados únicos a partir dos resultados filtrados/buscados.
- **Lista de Metas:** Exibe botões para cada julgado da meta gerada (Inf. + Data).
- **Interatividade:** Ao clicar em um botão da lista de metas, o **card completo do julgado correspondente é exibido diretamente abaixo da lista**, na mesma aba, para leitura imediata.

## Acesso para Teste

O dashboard atualizado está temporariamente acessível para teste no seguinte endereço:
[http://8501-i0t0z2gvvtgdbelwsng9q-13f789e2.manus.computer](http://8501-i0t0z2gvvtgdbelwsng9q-13f789e2.manus.computer)

*Nota: Este é um link temporário e pode expirar.*
