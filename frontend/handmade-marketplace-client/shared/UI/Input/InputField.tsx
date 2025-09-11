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
  errors='',
  type="text",
  register,
  onChange,
  value,
  labelClassName = "",
  inputClassName = "",
  isRequired = false,
  isHiddenLabel = false,
  isDisabled = false
}: IInputFieldProps) {
  const [showPassword, setShowPassword] = useState(false);
  const isPassword = type === 'password';
  const inputTypeNew = type === 'password' && showPassword ? 'text' : type;

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
            isErrors={errors}
            inputClassName={inputClassName}
            isDisabled={isDisabled}
            isRequired={isRequired}
            value={value}
            {...(register ? { register } : { onChange: onChange! })}
          />

          {isPassword && <PasswordToggle isVisible={showPassword} onToggle={togglePassword} />}
        </div>
      </InputLabel>

      <InputError errorText={errorText} errors={errors} />
    </div>
  );
}

export default InputField;
