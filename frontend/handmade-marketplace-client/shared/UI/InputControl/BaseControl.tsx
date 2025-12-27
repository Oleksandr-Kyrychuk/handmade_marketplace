import { IBaseCheckboxBase } from "./types/interfaces";


function BaseControl({
  inputId,
  inputType,
  onChange,
  register,
  inputClassName = '',
  isDisabled = false,
  isRequired = false,
  isChecked = false
}: IBaseCheckboxBase) {
  const isRHF = typeof register === 'function';

  const requiredAttr = (!isRHF && isRequired) ? { required: true } : {};

  const controlProps = isRHF
    ? register(inputId)
    : {
        onChange,
        checked: isChecked,
        name: inputId
      };

  return (
    <input
      id={inputId}
      type={inputType}
      disabled={isDisabled}
      {...requiredAttr}
      {...controlProps}
      className={`${inputClassName} absolute opacity-0 hidden w-0 h-0`}

    />
  );
}

export default BaseControl;
