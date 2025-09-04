'use client';

import { IInputLabelProps } from "../types/interfaces";

function InputLabel({children, id, label, labelClassName = '', isRequired, isHiddenLabel}: IInputLabelProps) {
  return (
    <label htmlFor={id} className={`${labelClassName} mb-2 relative`}>
      <span className={`${isHiddenLabel ? 'sr-only' : 'text-white text-xs block'}`}>
        {label}
        {isRequired &&<sup className='text-sm text-error'>*</sup>}
      </span>
      {children}
    </label>
  );
}

export default InputLabel;