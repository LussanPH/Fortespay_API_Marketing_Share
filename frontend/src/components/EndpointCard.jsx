import { TIPOS } from '../config.js'
import Checkbox from './Checkbox.jsx'

export default function EndpointCard({ estado, selecionado, onToggle, disabled }) {
  const { ep, total, presentes, faltando, duplicados, completo } = estado

  let detalhe
  if (duplicados.length > 0) {
    detalhe = (
      <span className="endpoint__detalhe endpoint__detalhe--erro">
        Arquivos repetidos: {duplicados.map((t) => TIPOS[t]).join(', ')}
      </span>
    )
  } else if (faltando.length > 0) {
    detalhe = (
      <span className="endpoint__detalhe endpoint__detalhe--erro">
        Falta: {faltando.map((t) => TIPOS[t]).join(', ')} ({presentes}/{total})
      </span>
    )
  } else {
    detalhe = <span className="endpoint__detalhe">{presentes}/{total} arquivos</span>
  }

  return (
    <div className="endpoint">
      <Checkbox checked={selecionado} onChange={onToggle} disabled={disabled || !completo}>
        <span className="endpoint__titulo">
          {ep.titulo} <code>POST {ep.path}</code>
        </span>
        {detalhe}
      </Checkbox>
    </div>
  )
}
