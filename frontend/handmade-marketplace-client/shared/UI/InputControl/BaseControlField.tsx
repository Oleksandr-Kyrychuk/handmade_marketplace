import { InputError } from "../Input/subcomponents";
import BaseControl from "./BaseControl";
import ControlInputLabel from "./subcomponents/ControlInputLabel";
import { IBaseControlFieldProps } from "./types/interfaces";

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
      <ControlInputLabel
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
      </ControlInputLabel>
      {errorText && <InputError errorText={errorText} />}
    </>
  );
}

export default BaseControlField;