"use client";

import { IButtonBaseProps } from "./types/interfaces";

function Button({className, children, variant, size, disabled = false, ...props}: IButtonBaseProps) {
  const base = "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md font-medium transition-all disabled:pointer-events-none disabled:opacity-50 shrink-0  outline-none aria-invalid:border-destructive btn"

  const variantClasses =
  variant === 'secondary'
    ? "bg-accent-700 duration-500 hover:box-shadow-custom1 hover:bg-accent-600"
    : variant === 'ghost'
    ? "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50"
    : variant === 'link'
    ? "text-primary-900"
    : "bg-primary-900 duration-500 hover:box-shadow-custom1 hover:bg-primary-800";

const sizeClasses =
  size === 'sm'
    ? 'p-4 rounded-full'
    : size === 'md'
    ? "py-4 px-9 rounded-full"
    : size === 'lg'
    ? "px-10.5 py-4 rounded-full"
    : "py-4 px-9 rounded-full";

  
  return (
    <button className={`${base} ${variantClasses} ${sizeClasses} ${className} ${
        disabled ? "opacity-50 cursor-not-allowed" : ""
      }`}
      disabled={disabled} {...props}>
      {children}
    </button>
  );
}

export default Button;