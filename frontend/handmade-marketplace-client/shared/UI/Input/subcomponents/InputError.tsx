'use client'


import { HintIcon } from "@/assets/Icons";
import { IInputErrorProps } from "../types/interfaces";

function InputError({errorText}: IInputErrorProps) {
  return (
    <div className="flex items-center mt-1">
      <HintIcon className="text-red-200 flex items-center w-4 mr-1 -mt-1"/>
      <span className="text-red-600 text-size-body-4 leading-130">{errorText}</span>
    </div>
  );
}

export default InputError;