import React, { RefObject } from "react";

export interface Option<ID extends string> {
  id: ID;
  label: string;
}

export interface IDropDownProps<ID extends string>  {
  selectedValue: ID | null;
  placeholder?: string;
  onToggle: () => void;
  isOpen: boolean;
  listClass?: string;
  options: Option<ID>[];
  dropdownRef: RefObject<HTMLDivElement | null>;
  handleSelect?: (id: ID, e?: React.MouseEvent<HTMLAnchorElement>) => void;
  renderOption: (option: Option<ID>, handleClick: () => void) => React.ReactNode
}