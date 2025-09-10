import { ButtonHTMLAttributes, ReactNode } from "react";

export interface IButtonBaseProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  className?: string;
  variant?: 'secondary' | 'ghost' | 'link';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}