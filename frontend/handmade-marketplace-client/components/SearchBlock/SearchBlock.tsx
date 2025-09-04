"use client";

import { SearchIcon } from "@/assets/Icons";
import InputField from "@/UI/Input/InputField";
import { useTranslations } from "next-intl";
import { useState } from "react";

function SearchBlock() {
  const t = useTranslations('search');

  const [searchVal, setSearchVal] = useState('');
  
  return (
    <div className='search-block'>
      <InputField
        id="search"
        icon={<SearchIcon color="text-primary-400" width={24} height={24} />}
        inputClassName="p-4 pl-12 h-[56px] bg-snow focus-visible:ring-0 placeholder:text-primary-400 text-primary-900"
        placeholder={t('placeholder')}
        onChange={(e) => setSearchVal(e.target.value)}
        value={searchVal}
      />
    </div>
  );
}

export default SearchBlock;