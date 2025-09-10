'use client'

import { IInputErrorProps } from "../types/interfaces";

function InputError({errorText, errors}: IInputErrorProps) {
  return <p className={errors ? 'text-error' : ''}>{errorText}</p>;
}

export default InputError;