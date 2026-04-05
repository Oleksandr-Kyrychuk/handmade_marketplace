"use client";

import { Link } from "@/shared/i18n";
import { IButtonBaseProps } from "./types/interfaces";

function Button({className, children, variant, size, href = '', disabled = false, ...props}: IButtonBaseProps) {
  const base = "inline-flex items-center justify-center gap-2 whitespace-nowrap font-secondary transition-all disabled:pointer-events-none disabled:opacity-50 shrink-0  outline-none aria-invalid:border-destructive btn";
 
  const variantClasses =
    variant === 'secondary'
      ? "bg-accent-700 duration-500 hover:box-shadow-custom1 hover:bg-accent-600 font-bold text-size-body-2 text-snow"
      : variant === 'ghost'
      ? "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50"
      : variant === 'link'
      ? "text-primary-900"
      : variant === 'default'
      ? "bg-primary-900 duration-500 hover:box-shadow-custom1 hover:bg-primary-800 text-snow font-bold"
      : "";

  const sizeClasses =
    size === 'sm'
      ? 'p-4 rounded-full'
      : size === 'md'
      ? "py-4 px-9 rounded-full"
      : size === 'lg'
      ? "px-13 py-6 rounded-full"
      : "py-4 px-9 rounded-full";

  const classes = `${base} ${variantClasses} ${sizeClasses} ${className} ${disabled ? "opacity-50 cursor-not-allowed" : ""}`

  if(href) {
    return (
      <Link href={href} className={classes}>{children}</Link>
    )
  }
  
  return (
    <button className={classes} disabled={disabled} {...props}>
      {children}
    </button>
  );
}

export default Button;