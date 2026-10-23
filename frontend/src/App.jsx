import { useEffect, useMemo, useRef, useState } from 'react'
import { ENDPOINTS, detectarTipo } from './config.js'
import { DOCS_URL, enviar, pingApi } from './api.js'
import Dropzone from './components/Dropzone.jsx'
import FileRow from './components/FileRow.jsx'
import EndpointCard from './components/EndpointCard.jsx'
import Results from './components/Results.jsx'

let proximoId = 1

function baixar(url, nome) {
  const a = document.createElement('a')
  a.href = url
  a.download = nome
  document.body.appendChild(a)
  a.click()
  a.remove()
}

export default function App() {
  const [arquivos, setArquivos] = useState([])
  const [desmarcados, setDesmarcados] = useState([]) // endpoints que o usuário desmarcou
  const [resultados, setResultados] = useState([])
  const [enviando, setEnviando] = useState(false)
  const [progresso, setProgresso] = useState({ atual: 0, total: 0 })
  const [aviso, setAviso] = useState('')
  const [apiOnline, setApiOnline] = useState(null)
  const urlsRef = useRef([])

  useEffect(() => {
    pingApi().then(setApiOnline)
    return () => urlsRef.current.forEach(URL.revokeObjectURL)
  }, [])

  const contagem = useMemo(() => {
    const c = {}
    arquivos.forEach((a) => {
      if (a.tipo) c[a.tipo] = (c[a.tipo] || 0) + 1
    })
    return c
  }, [arquivos])

  const estados = useMemo(
    () =>
      ENDPOINTS.map((ep) => {
        const tipos = Object.values(ep.campos)
        const faltando = tipos.filter((t) => !contagem[t])
        const duplicados = tipos.filter((t) => contagem[t] > 1)
        return {
          ep,
          total: tipos.length,
          presentes: tipos.length - faltando.length,
          faltando,
          duplicados,
          completo: faltando.length === 0 && duplicados.length === 0,
        }
      }),
    [contagem],
  )

  const selecionados = estados.filter((e) => e.completo && !desmarcados.includes(e.ep.path))

  function adicionarArquivos(lista) {
    const xlsx = lista.filter((f) => /\.xlsx$/i.test(f.name))
    const rejeitados = lista.length - xlsx.length

    setArquivos((atuais) => {
      const novos = xlsx
        .filter((f) => !atuais.some((a) => a.file.name === f.name && a.file.size === f.size && a.file.lastModified === f.lastModified))
        .map((file) => ({ id: proximoId++, file, tipo: detectarTipo(file.name) }))
      return [...atuais, ...novos]
    })
    setAviso(rejeitados > 0 ? `${rejeitados} arquivo(s) ignorado(s): só são aceitos arquivos .xlsx.` : '')
  }

  function alterarTipo(id, tipo) {
    setArquivos((atuais) => atuais.map((a) => (a.id === id ? { ...a, tipo } : a)))
  }

  function removerArquivo(id) {
    setArquivos((atuais) => atuais.filter((a) => a.id !== id))
  }

  function alternarEndpoint(path, marcado) {
    setDesmarcados((atuais) => (marcado ? atuais.filter((p) => p !== path) : [...atuais, path]))
  }

  function limparResultados() {
    urlsRef.current.forEach(URL.revokeObjectURL)
    urlsRef.current = []
    setResultados([])
  }

  function limparTudo() {
    limparResultados()
    setArquivos([])
    setDesmarcados([])
    setAviso('')
  }

  async function enviarTudo() {
    const alvo = selecionados
    limparResultados()
    setEnviando(true)
    setResultados(alvo.map(({ ep }) => ({ path: ep.path, titulo: ep.titulo, status: 'aguardando' })))

    const atualizar = (i, dados) =>
      setResultados((atuais) => atuais.map((r, idx) => (idx === i ? { ...r, ...dados } : r)))

    // Um endpoint depois do outro: a API processa com pouca memória.
    for (let i = 0; i < alvo.length; i++) {
      const { ep } = alvo[i]
      setProgresso({ atual: i + 1, total: alvo.length })
      atualizar(i, { status: 'enviando' })

      const form = new FormData()
      for (const [campo, tipo] of Object.entries(ep.campos)) {
        const arquivo = arquivos.find((a) => a.tipo === tipo)
        form.append(campo, arquivo.file, arquivo.file.name)
      }

      const r = await enviar(ep.path, form)

      let url
      if (r.blob) {
        url = URL.createObjectURL(r.blob)
        urlsRef.current.push(url)
        baixar(url, r.nomeArquivo)
      }
      atualizar(i, { status: r.status, mensagem: r.mensagem, url, nomeArquivo: r.nomeArquivo })
    }

    setEnviando(false)
  }

  return (
    <main className="page">
      <section className="card">
        <h1 className="card__titulo">Atualizar planilhas</h1>
        <p className="card__sub">Solte todos os arquivos de uma vez e envie para a API da Fortespay.</p>

        <div className={`status status--${apiOnline === null ? 'espera' : apiOnline ? 'on' : 'off'}`}>
          <span className="status__ponto" />
          {apiOnline === null ? 'Conectando à API…' : apiOnline ? 'API online' : 'API indisponível'}
        </div>

        <div className="campo">
          <span className="label">Arquivos <span className="obrigatorio">*</span></span>
          <Dropzone onFiles={adicionarArquivos} disabled={enviando} />
          {aviso && <p className="aviso">{aviso}</p>}
          {arquivos.length > 0 && (
            <ul className="lista-arquivos">
              {arquivos.map((a) => (
                <FileRow
                  key={a.id}
                  arquivo={a}
                  duplicado={Boolean(a.tipo) && contagem[a.tipo] > 1}
                  disabled={enviando}
                  onTipo={(tipo) => alterarTipo(a.id, tipo)}
                  onRemover={() => removerArquivo(a.id)}
                />
              ))}
            </ul>
          )}
        </div>

        <div className="campo">
          <span className="label">Endpoints</span>
          {estados.map((estado) => (
            <EndpointCard
              key={estado.ep.path}
              estado={estado}
              selecionado={selecionados.includes(estado)}
              disabled={enviando}
              onToggle={(marcado) => alternarEndpoint(estado.ep.path, marcado)}
            />
          ))}
        </div>

        <button
          type="button"
          className="botao"
          disabled={enviando || selecionados.length === 0}
          onClick={enviarTudo}
        >
          {enviando ? (
            <>
              <span className="spinner" aria-hidden="true" />
              Enviando {progresso.atual}/{progresso.total}…
            </>
          ) : (
            'Enviar'
          )}
        </button>

        {resultados.length > 0 && (
          <div className="campo campo--resultado">
            <span className="label">Resultado</span>
            <Results resultados={resultados} />
          </div>
        )}

        <div className="rodape">
          <button type="button" className="link" onClick={limparTudo} disabled={enviando}>
            Limpar tudo
          </button>
          <a className="link" href={DOCS_URL} target="_blank" rel="noreferrer">
            Documentação da API
          </a>
        </div>
      </section>
    </main>
  )
}
