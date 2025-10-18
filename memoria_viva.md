# Documento de Arquitetura e Escopo do Projeto: Memória Viva
**Versão:** 1.0
**Codinome:** "A Primeira Semente"

---

## 1. Missão do Projeto

Criar um santuário digital global, anônimo e gratuito, que transforma memórias humanas em experiências sensoriais (áudio e visual) compartilháveis, promovendo a empatia e a conexão humana em escala.

---

## 2. Escopo da Versão 1.0

Para garantir um lançamento realista e impactante, o escopo inicial é focado no núcleo da experiência.

### Funcionalidades Incluídas (MVP - Minimum Viable Product):

- **Plataforma Web Responsiva:** Acesso via navegador em desktops e dispositivos móveis.
- **Doação de Memória via Texto:** Interface limpa para submissão de narrativas emocionais.
- **Motor Eunoia v1.0 (Áudio-Visual):**
  - Geração de **Paisagem Sonora** única (~60s) baseada no texto.
  - Geração de **Aura Visual** (luz pulsante) com cor e ritmo derivados do texto.
- **Mapa-Múndi Interativo:** Visualização de todas as Auras doadas.
- **Experiência Imersiva:** Player em tela cheia para vivenciar cada Aura clicada no mapa.
- **Anonimato Total:** Nenhuma coleta de dados pessoais, login ou rastreamento.

### Funcionalidades Excluídas (Para Futuras Versões):

- **NÃO HAVERÁ:** Aplicativo nativo (iOS/Android).
- **NÃO HAVERÁ:** Cápsulas Físicas ou hardware customizado.
- **NÃO HAVERÁ:** Feedback tátil ou de odor.
- **NÃO HAVERÁ:** Doação por áudio/voz.
- **NÃO HAVERÁ:** Perfis de usuário, comentários ou funcionalidades sociais.
- **NÃO HAVERÁ:** Filtros de busca ou categorias no mapa.

---

## 3. Arquitetura Técnica

A pilha tecnológica foi escolhida com base em critérios de ser gratuita, de código aberto, escalável e de alto desempenho.

### a) Front-End (A Experiência Visível)

- **Linguagem Base:** HTML5, CSS3, JavaScript (Vanilla JS)
- **Visualização do Mapa:** `Leaflet.js` com tiles do `OpenStreetMap`
- **Renderização da Aura Visual:** `HTML5 Canvas API`

### b) Back-End (O Cérebro de Eunoia)

- **Linguagem:** `Python 3`
- **Framework de API:** `FastAPI`
- **Motor de Análise Poética (Eunoia Core):**
  - **Análise Estrutural:** `spaCy`
  - **Análise Temática:** `Transformers (Hugging Face)`
- **Motor de Geração de Áudio:** `Pydub` + Biblioteca de sons base (Licença Livre)

### c) Base de Dados (A Memória Coletiva)

- **Tecnologia:** `MongoDB Atlas` (Plano Gratuito)

### d) Hospedagem (Onde o Projeto Viverá)

- **Hospedagem do Front-End:** `Vercel` ou `Netlify` (Plano Gratuito)
- **Hospedagem do Back-End/API:** `Railway` ou `Render` (Plano Gratuito)

---

## 4. Estrutura do Fluxo de Dados

**Fluxo de Doação:**
1.  O usuário escreve e submete a memória no Front-End.
2.  O Front-End envia o texto e a geolocalização (anônima) para a API do Back-End.
3.  O Back-End (Eunoia) processa o texto, gera o arquivo de áudio e os parâmetros da Aura (cor, ritmo).
4.  Os dados da nova Aura são salvos na base de dados MongoDB.
5.  O Back-End retorna os parâmetros da Aura para o Front-End, que renderiza a experiência para o doador.

**Fluxo de Exploração:**
1.  O usuário acessa o mapa no Front-End.
2.  O Front-End solicita ao Back-End a lista de todas as Auras.
3.  O Back-End consulta o MongoDB e retorna uma lista com as coordenadas e identificadores de cada Aura.
4.  O Front-End renderiza cada Aura como um ponto de luz no mapa.
5.  Ao clicar em um ponto, o Front-End solicita os detalhes daquela Aura específica para o Back-End e inicia a experiência imersiva.