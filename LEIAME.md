# Anúncios Concursos DR — versão online (GitHub Pages)

Isto põe a app **permanentemente online**, num endereço fixo, que se **atualiza sozinha todos os dias** num servidor do GitHub (grátis). Não depende do seu computador nem do Chrome.

## O que está nesta pasta
- `index.html` — a app (a página).
- `gerar_dados.py` — o "robô" que vai buscar os anúncios (oficiais + Diário da República).
- `dados.json.gz` — os dados (o robô refá-los sozinho todos os dias).
- `.github/workflows/atualizar.yml` — o agendamento que faz o robô correr e publicar.

## Montagem (uma só vez, ~10 minutos)

1. **Criar o repositório**
   - No GitHub, canto superior direito → **+** → **New repository**.
   - Nome: `anuncios-dr` (ou o que quiser). Deixe **Public**. Carregue **Create repository**.

2. **Carregar os ficheiros**
   - Na página do repositório novo: **Add file → Upload files**.
   - Arraste para lá **tudo o que está nesta pasta**, incluindo a pasta `.github`.
     (Se o arrastar da pasta `.github` não pegar, veja o "Plano B" no fim.)
   - Em baixo, carregue **Commit changes**.

3. **Ligar a publicação (Pages)**
   - No repositório: **Settings** (definições) → **Pages** (menu à esquerda).
   - Em **Build and deployment → Source**, escolha **GitHub Actions**.

4. **Pôr o robô a correr**
   - Vá ao separador **Actions** (no topo). Se pedir para ativar, carregue em **I understand my workflows, enable them**.
   - Clique no workflow **"Atualizar e publicar Anúncios DR"** → botão **Run workflow** → **Run workflow**.
   - Espere uns minutos (fica verde ✓ quando acabar).

5. **Guardar o endereço**
   - Volte a **Settings → Pages**. Aparece lá o link (algo como `https://oseu-nome.github.io/anuncios-dr/`).
   - Abra-o e guarde nos favoritos. Está sempre atualizado.

A partir daqui, o robô corre **sozinho, 2x por dia**. Não tem de fazer mais nada.

## Plano B (se a pasta `.github` não subir pelo arrastar)
No repositório: **Add file → Create new file**. No nome do ficheiro escreva exatamente:
`.github/workflows/atualizar.yml`
Cole o conteúdo do ficheiro com o mesmo nome desta pasta e carregue **Commit changes**.

## Notas
- Os dados oficiais têm ~1 semana de atraso (limite da fonte); o robô junta os dias mais recentes indo ao site do Diário da República.
- As suas marcações/observações ficam guardadas no navegador (por computador).
