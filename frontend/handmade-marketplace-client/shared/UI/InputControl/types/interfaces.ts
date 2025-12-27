import { SignUpRequestDTO } from "@/entities/auth/model/types/interfaces";
import { UseFormRegister, UseFormRegisterReturn } from "react-hook-form";

export interface IBaseCheckbox {
  inputId: any,
  inputType: 'checkbox' | 'radio',
  isChecked?: boolean,
  isDisabled?: boolean,
  isRequired?: boolean,
  isHasError?: boolean,
  inputClassName?: string,
}

export interface IRegisterFunctionProp {
  register?: UseFormRegisterReturn | UseFormRegister<SignUpRequestDTO>; 
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void | undefined;
}

export type IBaseCheckboxBase = IBaseCheckbox & IRegisterFunctionProp;

export interface IBaseControlField {
  inputId: any,
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
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void | undefined;
}

export type IBaseControlFieldProps = IBaseControlField & (IRegisterHandlerProp );