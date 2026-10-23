const ROTULOS = {
  aguardando: 'Na fila',
  enviando: 'Enviando…',
  ok: 'Concluído',
  conflito: 'Clientes deixaram de ser rastreados',
  erro: 'Erro ao processar',
}

export default function Results({ resultados }) {
  return (
    <ul className="resultados" aria-live="polite">
      {resultados.map((r) => (
        <li key={r.path} className={`resultado resultado--${r.status}`}>
          <div className="resultado__topo">
            <span className="resultado__titulo">{r.titulo}</span>
            <span className="resultado__status">{ROTULOS[r.status]}</span>
          </div>

          {r.status === 'conflito' && (
            <p className="resultado__msg">
              {r.mensagem.replace(/[.\s]+$/, '')}. A planilha com os clientes removidos foi baixada. Ela lista só os
              excluídos: <strong>não a use como Somaoffice_Passado</strong>.
            </p>
          )}
          {r.status === 'erro' && <p className="resultado__msg">{r.mensagem}</p>}

          {r.url && (
            <a className="link" href={r.url} download={r.nomeArquivo}>
              Baixar {r.nomeArquivo} de novo
            </a>
          )}
        </li>
      ))}
    </ul>
  )
}
