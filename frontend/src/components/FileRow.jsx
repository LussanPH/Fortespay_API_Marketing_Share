import { TIPOS } from '../config.js'
import Select from './Select.jsx'

function formatarTamanho(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function FileRow({ arquivo, duplicado, disabled, onTipo, onRemover }) {
  return (
    <li className={`file${duplicado ? ' file--erro' : ''}`}>
      <div className="file__info">
        <span className="file__nome" title={arquivo.file.name}>{arquivo.file.name}</span>
        <span className="file__meta">
          {formatarTamanho(arquivo.file.size)}
          {duplicado && ' · já existe outro arquivo com este tipo'}
        </span>
      </div>
      <Select
        value={arquivo.tipo}
        onChange={onTipo}
        invalid={duplicado || !arquivo.tipo}
        disabled={disabled}
        label={`Tipo de ${arquivo.file.name}`}
      >
        <option value="">Selecionar tipo…</option>
        {Object.entries(TIPOS).map(([chave, nome]) => (
          <option key={chave} value={chave}>{nome}</option>
        ))}
      </Select>
      <button
        type="button"
        className="file__remover"
        onClick={onRemover}
        disabled={disabled}
        aria-label={`Remover ${arquivo.file.name}`}
      >
        ×
      </button>
    </li>
  )
}
