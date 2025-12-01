import { SignUpRequestDTO } from "@/entities/auth/model/types/interfaces";
import { IChildren } from "@/shared/types/general-interfaces";
import { ReactElement } from "react";
import { UseFormRegister, UseFormRegisterReturn } from "react-hook-form";

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

export interface IBaseCheckbox {
  inputId: string,
  inputType: 'checkbox' | 'radio',
  isChecked: boolean,
  isDisabled: boolean,
  isRequired: boolean,
  isHasError: boolean,
  inputClassName: string,
}

export interface IRegisterFunctionProp {
  register?: UseFormRegisterReturn | UseFormRegister<SignUpRequestDTO>; 
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export type IBaseCheckboxBase = IBaseCheckbox & IRegisterFunctionProp;

export interface IBaseControlField {
  inputId: string,
  label?: string,
  errorText?: string,
  inputType: 'checkbox' | 'radio',
  labelClassName?: string,
  inputClassName?: string,
  isHasError?: boolean,
  isRequired?: boolean,
  isHiddenLabel?: boolean,
  isDisabled?: boolean,
  isChecked?: boolean,
}

export interface IRegisterHandlerProp {
  register: UseFormRegister<SignUpRequestDTO>;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export type IBaseControlFieldProps = IBaseControlField & (IRegisterHandlerProp );