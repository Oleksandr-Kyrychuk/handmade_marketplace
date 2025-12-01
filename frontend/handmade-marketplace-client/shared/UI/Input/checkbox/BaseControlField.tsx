import { InputError, InputLabel } from "../subcomponents";
import { IBaseControlFieldProps } from "../types/interfaces";
import BaseControl from "./BaseControl";

function BaseControlField({
  inputId,
  label='',
  errorText='',
  inputType="checkbox",
  register,
  onChange,
  labelClassName = "",
  inputClassName = "",
  isHasError=false,
  isRequired = false,
  isHiddenLabel = false,
  isDisabled = false,
  isChecked=false
}: IBaseControlFieldProps) {

  return (
    <>
      <InputLabel
        id={inputId}
        label={label}
        labelClassName={labelClassName}
        isRequired={isRequired}
        isHiddenLabel={isHiddenLabel}
      >

        <BaseControl 
          inputId={inputId}
          inputType={inputType}
          isHasError={isHasError}
          inputClassName={inputClassName}
          isDisabled={isDisabled}
          isRequired={isRequired}
          isChecked={isChecked}
          register={register}
          onChange={onChange}
        />
      </InputLabel>
      {errorText && <InputError errorText={errorText} />}
    </>
  );
}

export default BaseControlField;