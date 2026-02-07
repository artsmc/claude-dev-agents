interface ButtonProps {
  label: string
  onClick: () => void
}

export default function Button({ label, onClick }: ButtonProps) {
  return (
    <button onClick={onClick}>
      {label}
    </button>
  )
}
