import { IBaseCheckboxBase } from "../types/interfaces";


function BaseControl({
  inputId,
  inputType,
  onChange,
  register,
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

    />
  );
}

export default BaseControl;
