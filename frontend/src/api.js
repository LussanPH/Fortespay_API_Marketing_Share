// Em produção, VITE_API_URL é o endereço da API no Render.
// Em desenvolvimento fica vazio e o proxy do Vite repassa para localhost:8000.
const BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')

export const DOCS_URL = `${BASE}/docs`

function nomeDoArquivo(resposta, padrao) {
  const cabecalho = resposta.headers.get('content-disposition') || ''
  const achado = cabecalho.match(/filename="?([^";]+)"?/i)
  return achado ? achado[1] : padrao
}

function textoDoErro(detail) {
  if (!detail) return 'Erro desconhecido.'
  return typeof detail === 'string' ? detail : JSON.stringify(detail)
}

// Acorda a API (o plano gratuito do Render hiberna) e diz se ela respondeu.
export async function pingApi() {
  try {
    const resposta = await fetch(`${BASE}/openapi.json`)
    return resposta.ok
  } catch {
    return false
  }
}

// Envia as planilhas para um endpoint.
// Retorna { status: 'ok' | 'conflito' | 'erro', mensagem, blob?, nomeArquivo? }
export async function enviar(path, formData) {
  let resposta
  try {
    resposta = await fetch(`${BASE}${path}`, { method: 'POST', body: formData })
  } catch {
    return {
      status: 'erro',
      mensagem:
        'Não foi possível conectar à API. No plano gratuito do Render ela pode levar ~1 min para acordar; tente de novo.',
    }
  }

  if (resposta.ok) {
    return {
      status: 'ok',
      blob: await resposta.blob(),
      nomeArquivo: nomeDoArquivo(resposta, 'resultado.xlsx'),
    }
  }

  // 409: a API devolve a planilha dos clientes excluídos no corpo da resposta.
  if (resposta.status === 409) {
    return {
      status: 'conflito',
      mensagem: resposta.headers.get('x-erro') || 'Clientes deixaram de ser rastreados.',
      blob: await resposta.blob(),
      nomeArquivo: nomeDoArquivo(resposta, 'dados_excluidos.xlsx'),
    }
  }

  let detail
  try {
    detail = (await resposta.json()).detail
  } catch {
    detail = `Erro ${resposta.status} ao processar os dados.`
  }
  return { status: 'erro', mensagem: textoDoErro(detail) }
}
