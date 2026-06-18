interface Props {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "accent" | "outline" | "danger" | "ghost";
  title?: string;
  type?: "button" | "submit";
  disabled?: boolean;
}

const variants = {
  primary: "action-btn action-btn-primary",
  accent: "action-btn action-btn-accent",
  outline: "action-btn action-btn-outline",
  danger: "action-btn action-btn-danger",
  ghost: "action-btn action-btn-ghost",
};

export default function ActionButton({
  children,
  onClick,
  variant = "primary",
  title,
  type = "button",
  disabled,
}: Props) {
  return (
    <button
      type={type}
      title={title}
      disabled={disabled}
      onClick={onClick}
      className={variants[variant]}
    >
      {children}
    </button>
  );
}
