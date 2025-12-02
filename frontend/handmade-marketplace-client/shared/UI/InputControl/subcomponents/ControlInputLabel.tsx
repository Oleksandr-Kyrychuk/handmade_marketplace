'use client';

import { IInputLabelProps } from "../../Input/types/interfaces";

function ControlInputLabel({children, id, label}: IInputLabelProps) {
  return (
    <label htmlFor={id} className="mb-2 relative flex items-start label__input-checkbox cursor-pointer">
      
      {children}

      <span className="text-primary-800 text-sm ml-2 flex items-center">
        {label}
      </span>
      
    </label>
  );
}

export default ControlInputLabel;