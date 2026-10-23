export default function Checkbox({ checked, onChange, disabled = false, children }) {
  return (
    <label className={`check${disabled ? ' check--disabled' : ''}`}>
      <input
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className="check__box" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="18" height="18">
          <path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
      <span className="check__content">{children}</span>
    </label>
  )
}
