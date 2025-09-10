'use client';

import { Eye, EyeClose } from "@/assets/Icons";
import { IPasswordToggleProps } from "../types/interfaces";


function PasswordToggle({onToggle, isVisible, iconClassName}: IPasswordToggleProps) {
  return (
    <span onClick={onToggle} className="absolute right-4 top-1/2 transform -translate-y-1/2 cursor-pointer">
      {isVisible ? <Eye className={iconClassName} /> : <EyeClose className={iconClassName} />}
    </span>
  );
};

export default PasswordToggle;