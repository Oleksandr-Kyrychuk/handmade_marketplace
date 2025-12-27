'use client';

import { IInputLabelProps } from "../types/interfaces";

function InputLabel({children, id, label, labelClassName = '', isRequired, isHiddenLabel}: IInputLabelProps) {
  return (
    <label htmlFor={id} className={`${labelClassName} relative`}>
      <span className={`${isHiddenLabel ? 'sr-only' : ` text-primary-800 text-sm block`} mb-2`}>
        {label}
        {isRequired &&<sup className='text-sm text-error'>*</sup>}
      </span>
      {children}
    </label>
  );
}

export default InputLabel;