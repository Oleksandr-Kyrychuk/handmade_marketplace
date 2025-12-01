"use client";

import { useState } from "react";
import BaseInput from "./BaseInput";
import { InputError, InputLabel, PasswordToggle } from "./subcomponents";
import { IInputFieldProps } from "./types/interfaces";


function InputField({
  id,
  placeholder,
  icon,
  label='',
  errorText='',
  inputType="text",
  register,
  onChange,
  value,
  labelClassName = "",
  inputClassName = "",
  isHasError=false,
  isRequired = false,
  isHiddenLabel = false,
  isDisabled = false
}: IInputFieldProps) {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = inputType === 'password';
  const inputTypeNew = inputType === 'password' && showPassword ? 'text' : inputType;

  const togglePassword = () => setShowPassword((prev) => !prev);

  return (
    <div>
      <InputLabel
        id={id}
        label={label}
        labelClassName={labelClassName}
        isRequired={isRequired}
        isHiddenLabel={isHiddenLabel}
      >
        <div className="relative">
          {icon && <span className="absolute top-1/2 -translate-y-1/2 left-4">{icon}</span>}

          <BaseInput
            id={id}
            inputType={inputTypeNew}
            placeholder={placeholder}
            isHasError={isHasError}
            inputClassName={inputClassName}
            isDisabled={isDisabled}
            isRequired={isRequired}
            value={value}
            {...(register ? { register } : { onChange: onChange! })}
          />

          {isPassword && <PasswordToggle iconClassName={`w-5  ${isHasError ? 'text-red-200' : 'text-primary-600'}`}  isVisible={showPassword} onToggle={togglePassword} />}
        </div>
      </InputLabel>

      {errorText && <InputError errorText={errorText} />}
    </div>
  );
}

export default InputField;
