"use client";

import { usePathname, useRouter } from "@/i18n/navigation";
import { Local } from "@/i18n/routing";
import { useDropdown } from "@/UI/DropDown/hook/useDropdown";
import { useLocale } from "next-intl";
import { useSearchParams } from "next/navigation";

export function useLanguage(locals: readonly Local[]) {
  const router = useRouter();
  const currentPath = usePathname();
  const searchParams = useSearchParams();
  const activeLocale = useLocale();
  console.log('currentPath', currentPath)

  const initLocal = locals.find(local => local === activeLocale) || locals[0];

  const { isOpen, selectedValue, dropdownRef, handleOpen, handleSelect } = useDropdown(initLocal);

  const handleLocalChange = (item: string) => {
    const locale = item.toLocaleLowerCase() || locals[0];
    console.log('locale', locale)

    handleSelect(locale)

    const queryString = searchParams.toString();

    const newUrl = queryString ? `${currentPath}?${queryString}` : currentPath;

    router.replace(newUrl, {locale})
    router.refresh();
  }

  return {isOpen, selectedValue, dropdownRef, handleOpen, handleLocalChange}
}

