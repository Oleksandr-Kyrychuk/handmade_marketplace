import { IChildren } from "@/shared/types/general-interfaces";
import { ReactElement } from "react";
import { UseFormRegisterReturn } from "react-hook-form";

export interface InputProps {
  id: string; 
  inputType: string; 
  placeholder?: string;  
  inputClassName?: string; 
  isDisabled?: boolean; 
  isRequired?: boolean;
  value?: string | string[] | undefined;
  isHasError? :boolean
}

export interface IInputField {
  id: string;
  placeholder: string;
  icon?: ReactElement,
  label?: string;
  errorText?: string;
  isHasError?: boolean;
  inputType?: string;
  labelClassName?: string;
  inputClassName?: string;
  isRequired?: boolean;
  isHiddenLabel?: boolean;
  isDisabled?: boolean;
  value?: string | string[] | undefined;
}

export interface IControlledProps {
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  register?: never;
}
export interface IFormProps {
  register: UseFormRegisterReturn;
  onChange?: never;
}

export type IBaseInputProps = InputProps & (IControlledProps | IFormProps);


export type IInputFieldProps = IInputField & (IControlledProps | IFormProps);

export interface IInputLabelProps extends IChildren {
  id: string;
  label: string;
  labelClassName?: string;
  isRequired: boolean;
  isHiddenLabel: boolean
}

export interface IInputErrorProps {
  errorText?: string;
}

export interface IPasswordToggleProps {
  onToggle: () => void;
  isVisible: boolean;
  iconClassName?: string
}