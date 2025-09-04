"use client";

import { IBaseInputProps } from "./types/interfaces";

function BaseInput({
  id,
  inputType,
  placeholder,
  isErrors,
  register,
  value,
  onChange,
  inputClassName = "",
  isDisabled = false,
  isRequired = false
}: IBaseInputProps) {
  
  return (
    <input
      id={id}
      type={inputType}
      required={isRequired}
      placeholder={placeholder}
      autoComplete={`new-${id}`}
      disabled={isDisabled}
      value={register ? undefined : value}
      {...(register ?? { onChange })}
      aria-invalid={!!isErrors}
      className={`${inputClassName} border rounded-5xl p-4 bg-snow shadow-custom1 w-full 
        hover:border-primary-100 focus:border-accent-600 disabled:bg-primary-100 
        duration-500 min-h-[55px] ${
          isErrors ? "border-red-200" : "border-transparent"
        } `}
    />
  );
}

export default BaseInput;
