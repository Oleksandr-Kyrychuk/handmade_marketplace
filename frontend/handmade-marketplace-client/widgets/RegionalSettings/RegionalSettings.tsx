'use client';

import { Link } from "@/shared/i18n/config/navigation";
import { Local, routing } from "@/shared/i18n/config/routing";
import DropDown from "@/shared/UI/DropDown/DropDown";
import { useLanguage } from "./hook/useLanguage";

function RegionalSettings() {
  const locals = routing.locales;
  const {isOpen, selectedValue, dropdownRef, handleOpen, handleLocalChange} = useLanguage(locals);
  
  const options = locals.map(option => ({
    id: option,
    label: option.toLocaleUpperCase(),
  }));

  const handleClickLink = (e: React.MouseEvent<HTMLAnchorElement>, id: Local) => {
    handleLocalChange(id, e);

    handleOpen?.();
  };

  return (
    <div className='regional-settings'>
      <div className='flex items-center'>
        <DropDown<Local> 
          isOpen={isOpen}
          selectedValue={selectedValue as Local | null}
          onToggle={handleOpen}
          handleSelect={handleLocalChange}
          options={options}
          dropdownRef={dropdownRef}
          renderOption={(option, handleClick) => (
            <Link key={option.id} href={option.id} onClick={(e) => handleClickLink(e, option.id)} className="px-3 py-2 w-full text-primary-900">{option.label}</Link>
          )}
        />
      </div>
    </div>
  );
}

export default RegionalSettings;