import React, { RefObject } from "react";

export interface Option {
  id: string;
  label: string;
}

export interface IDropDownProps {
  selectedValue: string | null;
  placeholder?: string;
  onToggle: () => void;
  isOpen: boolean;
  listClass?: string;
  options: Option[];
  dropdownRef: RefObject<HTMLDivElement | null>;
  handleSelect?: (id: string) => void;
  renderOption: (option: Option, handleClick: () => void) => React.ReactNode
}