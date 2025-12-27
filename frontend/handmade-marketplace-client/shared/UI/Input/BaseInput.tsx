"use client";

import { IBaseInputProps } from "./types/interfaces";

function BaseInput({
  id,
  inputType,
  placeholder,
  register,
  value,
  onChange,
  maxLength,
  inputRef,
  onKeyDown,
  onPaste,
  inputClassName = "",
  isHasError = false,
  isDisabled = false,
  isRequired = false
}: IBaseInputProps) {
  
  return (
    <input
      ref={inputRef}
      id={id}
      type={inputType}
      placeholder={placeholder}
      autoComplete={`new-${id}`}
      required={isRequired}
      disabled={isDisabled}
      maxLength={maxLength}
      onKeyDown={onKeyDown}
      onPaste={onPaste}
      {...(register ? register : onChange ? { value: value ?? '', onChange } : { value })}
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
