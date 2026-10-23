// Tipos de planilha que o usuário pode soltar na tela.
export const TIPOS = {
  detalhamento: 'Detalhamento de Empresas',
  nectar_crm: 'Nectar CRM',
  fortes_ag: 'Fortes AG',
  somaoffice_passado: 'Somaoffice Passado',
  unidades_municipios: 'Unidades e Municípios',
  somaoffice_tempo: 'Somaoffice Tempo',
  somaoffice_totais: 'Somaoffice Totais',
}

// Endpoints da API. Em "campos": nome do campo do formulário -> tipo de planilha.
// O tipo "detalhamento" é reaproveitado nos dois endpoints.
export const ENDPOINTS = [
  {
    path: '/somaoffice_update',
    titulo: 'Base de clientes',
    campos: {
      detalhamento_empresas_somaoffice: 'detalhamento',
      nectar_crm: 'nectar_crm',
      fortes_ag: 'fortes_ag',
      somaoffice_passado: 'somaoffice_passado',
      unidades_municipios: 'unidades_municipios',
    },
  },
  {
    path: '/somaoffice_tempo',
    titulo: 'Planilha de tempo',
    campos: {
      somaoffice_tempo: 'somaoffice_tempo',
      detalhamento_empresas: 'detalhamento',
      somaoffice_totais: 'somaoffice_totais',
    },
  },
]

// Palavras do nome do arquivo usadas na detecção automática (testadas nesta ordem).
const REGRAS = [
  ['detalhamento', [/detalhamento/]],
  ['somaoffice_passado', [/passado/]],
  ['somaoffice_totais', [/totais?/]],
  ['somaoffice_tempo', [/tempo/]],
  ['unidades_municipios', [/unidade/, /municipio/]],
  ['nectar_crm', [/nectar/, /crm/]],
  ['fortes_ag', [/fortes/, /(^|[^a-z])ag([^a-z]|$)/]],
]

// Devolve o tipo detectado pelo nome ou '' se não reconhecer.
export function detectarTipo(nomeArquivo) {
  const nome = nomeArquivo
    .replace(/\.xlsx$/i, '')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()

  for (const [tipo, regras] of REGRAS) {
    if (regras.some((regra) => regra.test(nome))) return tipo
  }
  return ''
}
