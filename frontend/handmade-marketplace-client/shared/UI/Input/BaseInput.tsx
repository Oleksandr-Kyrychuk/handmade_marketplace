"use client";

import { IBaseInputProps } from "./types/interfaces";

function BaseInput({
  id,
  inputType,
  placeholder,
  register,
  value,
  onChange,
  inputClassName = "",
  isHasError = false,
  isDisabled = false,
  isRequired = false
}: IBaseInputProps) {
  const isRHF = !!register;
  const htmlRequired = isRHF ? false : isRequired;
  const requiredAttr = htmlRequired ? { required: true } : {};
  
  return (
    <input
      id={id}
      type={inputType}
      placeholder={placeholder}
      autoComplete={`new-${id}`}
      disabled={isDisabled}
      value={register ? undefined : value}
      {...requiredAttr}
      {...(register ?? { onChange })}
      aria-invalid={!!isHasError}
      className={`${inputClassName} border rounded-5xl p-4 bg-snow shadow-custom1 w-full 
        hover:border-primary-100 focus:border-accent-600 disabled:bg-primary-100 
        duration-500 min-h-[55px] ${
          isHasError ? "border-red-200" : "border-transparent"
        } `}
    />
  );
}

export default BaseInput;
