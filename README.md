# Fortespay API

API em FastAPI que automatiza a manutenção das planilhas da Fortespay a partir dos dados exportados do **Somaoffice**. Em vez de juntar e conferir planilhas manualmente, você envia os arquivos e recebe de volta a planilha pronta.

## Endpoints

| Método | Rota                 | Para que serve                                                          |
| ------ | -------------------- | ----------------------------------------------------------------------- |
| POST   | `/somaoffice_update` | Atualiza a base de clientes (`Somaoffice_Passado`)                      |
| POST   | `/somaoffice_tempo`  | Atualiza a planilha de evolução no tempo (`Somaoffice_Tempo`)           |

Todos recebem arquivos `.xlsx` via `multipart/form-data` e devolvem um `.xlsx`.

---

### `POST /somaoffice_update`

Atualiza a planilha com todos os clientes da Fortespay. Junta cinco planilhas e gera a nova versão da `Somaoffice_Passado`.

**Arquivos de entrada**

| Campo                                | Conteúdo                                                        |
| ------------------------------------ | --------------------------------------------------------------- |
| `detalhamento_empresas_somaoffice`   | Exportação atual do Somaoffice (Detalhamento de Empresas)       |
| `nectar_crm`                         | Base do CRM Nectar                                              |
| `fortes_ag`                          | Base da Fortes AG                                               |
| `somaoffice_passado`                 | A última versão da planilha `Somaoffice_Passado`                |
| `unidades_municipios`                | Planilha com a aba `Unidades` (colunas `CIDADE`, `UF`, `UNIDADE`) |

**O que ele faz**

1. Limpa o detalhamento exportado do Somaoffice.
2. Cruza Somaoffice, CRM e Fortes AG pelo CNPJ para montar a base atual.
3. Compara a base atual com a `somaoffice_passado`.
   - Se algum cliente da base passada **não aparece mais** na base atual, interrompe e devolve a lista deles (veja abaixo).
   - Caso contrário, atualiza os campos dos clientes existentes (funil, grupo empresarial, nome da empresa, município, representante, UF, cliente Fortes) com os valores novos que não estejam vazios, e acrescenta os clientes novos.
4. Quando o representante está vazio, preenche com a unidade correspondente ao município/UF.

**Respostas**

| Status | Quando                                  | Corpo                                                                 |
| ------ | --------------------------------------- | --------------------------------------------------------------------- |
| 200    | Atualização concluída                   | `dadosatulizacao.xlsx`, aba `Somaoffice_passado`                      |
| 409    | Clientes deixaram de ser rastreados     | `dados_excluidos.xlsx`, aba `Dados_Excluidos`, com os clientes removidos. A mensagem também vai no header `X-Erro` |
| 500    | Qualquer outro erro de processamento    | JSON com `detail`                                                     |

> **Atenção:** o 409 devolve um arquivo, não um JSON. Quem chama a API precisa salvar o corpo da resposta mesmo com status de erro (por exemplo, não usar `raise_for_status()` antes de gravar o arquivo). Esse arquivo lista apenas os clientes excluídos: **não** o use como nova `Somaoffice_Passado`.

**Exemplo**

```bash
curl -D - -o resultado.xlsx -X POST http://localhost:8000/somaoffice_update \
  -F detalhamento_empresas_somaoffice=@Detalhamento_Empresas.xlsx \
  -F nectar_crm=@nectar_crm.xlsx \
  -F fortes_ag=@fortes_ag.xlsx \
  -F somaoffice_passado=@Somaoffice_Passado.xlsx \
  -F unidades_municipios=@Unidades_Municipios.xlsx
```

---

### `POST /somaoffice_tempo`

Atualiza diariamente a planilha de evolução no tempo com os dados mais recentes do Somaoffice.

**Arquivos de entrada**

| Campo                    | Conteúdo                                                                                      |
| ------------------------ | --------------------------------------------------------------------------------------------- |
| `somaoffice_tempo`       | Planilha de tempo atual, com as abas `Export` e `Somaoffice_Tempo_Total`                      |
| `detalhamento_empresas`  | Exportação atual do Somaoffice (Detalhamento de Empresas)                                     |
| `somaoffice_totais`      | Exportação com os totais mensais (coluna `Date - Mês`, com o nome do mês)                     |

**O que ele faz**

1. Mantém só as empresas com primeiro cash-in (`Prim cashin` preenchido) e as marca com o mês e o ano de hoje.
2. Remove da aba `Export` as linhas do mês/ano atual e acrescenta as novas. Rodar várias vezes no mesmo mês substitui o mês, sem duplicar.
3. Separa o resultado em visões por empresa e por grupo.
4. Nos totais, converte o nome do mês em data e substitui os registros do ano atual, preservando os anos anteriores.

**Resposta**

| Status | Quando                  | Corpo                                  |
| ------ | ----------------------- | -------------------------------------- |
| 200    | Atualização concluída   | `somaoffice_tempo.xlsx` com 4 abas     |
| 500    | Erro de processamento   | JSON com `detail`                      |

Abas do arquivo retornado: `Export`, `Somaoffice_Tempo_Empresas`, `Somaoffice_Tempo_Grupos` e `Somaoffice_Tempo_Total`.

**Exemplo**

```bash
curl -o somaoffice_tempo.xlsx -X POST http://localhost:8000/somaoffice_tempo \
  -F somaoffice_tempo=@Somaoffice_Tempo.xlsx \
  -F detalhamento_empresas=@Detalhamento_Empresas.xlsx \
  -F somaoffice_totais=@Somaoffice_Totais.xlsx
```

---

## Como rodar

Requer Python 3.13+ e [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run uvicorn main_fastapi:app --reload
```

A API sobe em `http://localhost:8000`. A documentação interativa (Swagger), onde dá para enviar os arquivos pelo navegador, fica em `http://localhost:8000/docs`.

## Frontend

Em [frontend/](frontend/) há um site em React (Vite) para usar a API sem `curl`. Você solta todos os `.xlsx` de uma vez, o site identifica cada arquivo pelo nome (dá para corrigir o tipo num seletor) e envia para os endpoints que estiverem completos. O `Detalhamento_Empresas` é reaproveitado nos dois. Os resultados são baixados automaticamente; no caso do 409, o site avisa que os clientes foram excluídos e baixa o `dados_excluidos.xlsx`.

**Rodar localmente** (em dois terminais):

```bash
# 1. API
uv run uvicorn main_fastapi:app --reload

# 2. Frontend (http://localhost:5173)
cd frontend
npm install
npm run dev
```

Em desenvolvimento o Vite repassa as chamadas para a API em `localhost:8000`, então não precisa configurar nada.

**Deploy (Vercel para o site, Render para a API):**

| Onde   | Configuração                                                                                                   |
| ------ | -------------------------------------------------------------------------------------------------------------- |
| Vercel | Importar este repositório com **Root Directory** = `frontend`. Variável `VITE_API_URL` = endereço da API no Render (ex.: `https://sua-api.onrender.com`, sem barra no final). Mudou a URL da API? Faça um novo deploy. |
| Render | Variável `CORS_ORIGINS` com o endereço do site, separando vários por vírgula e **sem espaços** (ex.: `https://seu-site.vercel.app,http://localhost:5173`). Opcional: em *Build Filters → Ignored Paths*, `frontend/**`, para mudanças só no site não reiniciarem a API. |

Sem `CORS_ORIGINS`, a API só aceita chamadas de `http://localhost:5173`.

## Estrutura do projeto

| Arquivo           | Conteúdo                                                                     |
| ----------------- | ---------------------------------------------------------------------------- |
| `main_fastapi.py` | Definição dos endpoints, CORS, leitura dos uploads e geração dos `.xlsx` de resposta |
| `functions.py`    | Regras de negócio: limpeza, cruzamento das bases, atualização e exceção `DadosExluidos` |
| `frontend/`       | Site em React (Vite) para enviar as planilhas                                |
| `pyproject.toml`  | Dependências e versão do Python                                              |
| `uv.lock`         | Versões travadas das dependências                                            |
| `LICENSE`         | Licença do projeto                                                           |

## Observações

- Os CNPJs são lidos como texto para não perder zeros à esquerda.
- As planilhas (`.xlsx` e `.csv`) não ficam no repositório: você envia os seus arquivos a cada chamada.
