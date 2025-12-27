"use client";

import { usePathname, useRouter } from "@/shared/i18n/config/navigation";
import { Local } from "@/shared/i18n/config/routing";
import { useDropdown } from "@/shared/UI/DropDown/hook/useDropdown";
import { useLocale } from "next-intl";
import { useSearchParams } from "next/navigation";

export function useLanguage(locals: readonly Local[]) {
  const router = useRouter();
  const currentPath = usePathname();
  const searchParams = useSearchParams();
  const activeLocale = useLocale();

  const initLocal = locals.find(local => local === activeLocale) || locals[0];

  const { isOpen, selectedValue, dropdownRef, handleOpen, handleSelect } = useDropdown(initLocal);

  const handleLocalChange = (id: Local, e?: React.MouseEvent<HTMLAnchorElement>) => {
    e?.preventDefault();
    e?.stopPropagation();

    const locale = id.toLocaleLowerCase() || locals[0];
    handleSelect(locale)

    const queryString = searchParams.toString();

    const newUrl = queryString ? `${currentPath}?${queryString}` : currentPath;

    router.replace(newUrl, {locale})
  }

  return {isOpen, selectedValue, dropdownRef, handleOpen, handleLocalChange}
}

