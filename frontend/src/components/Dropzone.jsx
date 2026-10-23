import { useRef, useState } from 'react'

export default function Dropzone({ onFiles, disabled = false }) {
  const inputRef = useRef(null)
  const [arrastando, setArrastando] = useState(false)

  function abrirSeletor() {
    if (!disabled) inputRef.current?.click()
  }

  function aoSoltar(e) {
    e.preventDefault()
    setArrastando(false)
    if (disabled) return
    onFiles(Array.from(e.dataTransfer.files))
  }

  return (
    <div
      className={`dropzone${arrastando ? ' dropzone--ativa' : ''}${disabled ? ' dropzone--desabilitada' : ''}`}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-disabled={disabled}
      onClick={abrirSeletor}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          abrirSeletor()
        }
      }}
      onDragOver={(e) => {
        e.preventDefault()
        if (!disabled) setArrastando(true)
      }}
      onDragLeave={() => setArrastando(false)}
      onDrop={aoSoltar}
    >
      <svg className="dropzone__icone" viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">
        <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M4 15v3a2 2 0 002 2h12a2 2 0 002-2v-3" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span className="dropzone__titulo">Arraste os arquivos .xlsx aqui</span>
      <span className="dropzone__sub">ou clique para selecionar vários de uma vez</span>
      <input
        ref={inputRef}
        type="file"
        multiple
        hidden
        accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        onChange={(e) => {
          onFiles(Array.from(e.target.files))
          e.target.value = ''
        }}
      />
    </div>
  )
}
