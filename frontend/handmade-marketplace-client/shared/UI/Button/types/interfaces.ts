import { ButtonHTMLAttributes, ReactNode } from "react";

export type IButtonVariant = 'secondary' | 'ghost' | 'link' | 'default'

export type IButtonSize = 'sm' | 'md' | 'lg';
export interface IButtonBaseProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  className?: string;
  variant?: IButtonVariant;
  size?: IButtonSize;
  disabled?: boolean;
  href?: string;
}