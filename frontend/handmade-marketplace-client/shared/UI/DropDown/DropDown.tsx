'use client';

import { ArrowDown, CheckIcon } from "@/assets/Icons";
import { IDropDownProps, Option } from "./types/interfaces";

function DropDown<ID extends string>({selectedValue, placeholder, onToggle, isOpen, listClass='', options, handleSelect, renderOption, dropdownRef}: IDropDownProps<ID>) {

  return (
    <div className="relative" ref={dropdownRef}>
      <button type="button" onClick={onToggle} className="flex items-center gap-2 cursor-pointer py-2 px-4 min-w-[84px] min-h-[40px] hover:text-accent-600 duration-500 text-snow">
        {selectedValue ? selectedValue.toLocaleUpperCase() : placeholder}

        <ArrowDown color="text-snow" className="-mt-1" width={20} height={20} />
      </button>
      {isOpen && (
        <div className="absolute z-10 mt-1 w-full">
          <ul className={`${isOpen ? 'animate-slideDown' : 'animate-slideUp'} ${listClass} max-h-60 bg-white overflow-auto rounded-xl shadow-md p-2`}>
            {options.map((option: Option<ID>) => {
              const isActive = option.id === selectedValue?.toLocaleLowerCase();
              const handleClick = () => {
                handleSelect?.(option.id);
                onToggle()
              }
              return (
                <li key={option.id} className="flex relative items-center justify-between cursor-pointer rounded-md hover:bg-gray-100"
                >
                  {renderOption(option, handleClick)}
                  {isActive && (<CheckIcon className="absolute right-0 top-1/2 -translate-y-1/2 -mt-0.5 text-primary-900" width={20} height={20} />)}
                </li>
              )
            })}
          </ul>
        </div>
      )}
    </div>
  );
}

export default DropDown;