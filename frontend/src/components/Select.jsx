export default function Select({ value, onChange, children, invalid = false, disabled = false, label }) {
  return (
    <select
      className={`select${invalid ? ' select--invalid' : ''}`}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      aria-label={label}
    >
      {children}
    </select>
  )
}
