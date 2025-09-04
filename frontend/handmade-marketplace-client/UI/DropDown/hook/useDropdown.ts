'use client';

import { useHandleClickOutside } from "@/hooks/useHandleClickOutside";
import { useRef, useState } from "react";

export function useDropdown(initValue: string) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState<string>(initValue);

  const dropdownRef = useRef<HTMLDivElement | null>(null);

  const handleOpen = () => {
    setIsOpen(!isOpen)
  }

  const handleSelect = (id: string) => {
    setSelectedValue(id);
    setIsOpen(false);
  }

  useHandleClickOutside(dropdownRef, isOpen, () => setIsOpen(false))

  return { isOpen, selectedValue, dropdownRef, handleOpen, handleSelect }
}
