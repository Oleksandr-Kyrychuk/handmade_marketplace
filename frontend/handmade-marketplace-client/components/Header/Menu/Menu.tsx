"use client";

import { AnimatePresence, motion } from 'motion/react';
import { useRef } from 'react';
import MenuLinks from './MenuLinks';
import { useHandleClickOutside } from '@/hooks/useHandleClickOutside';
import Button from '@/UI/Button/Button';
import { ArrowDown, CatalogIcon } from '@/assets/Icons';
import { useTranslations } from 'next-intl';
import { IMenuProps } from './types/interfaces';
import MenuCatalog from './MenuCatalog';

function Menu({openMenuCatalog, handleOpenMenuCatalog}: IMenuProps) {
  const t = useTranslations('header');
  const buttonRef = useRef<HTMLButtonElement | null>(null);
  useHandleClickOutside(buttonRef, openMenuCatalog, () => handleOpenMenuCatalog())

  return (
    <nav className="menu border-b-1 border-primary-100 py-7">
      <div className="container mx-auto px-4">
        <div className=" menu__inner relative">
          <div className="flex items-center">
            <div className="xl:mr-9 lg:mr-7 lg:py-0 py-2">
              <Button variant="link" ref={buttonRef} className={
                `bg-transparent hover:bg-transparent flex items-center 
                lg:px-5 min-w-[165px] min-h-[40px] border-1 border-transparent font-normal 
                duration-500 !rounded-[64px] !py-2 !px-3 shadow-none font-secondary text-size-body-3
                ${openMenuCatalog ? 'lg:shadow-custom1 lg:border-primary-100 duration-500' : ''}
              `} 
                onClick={handleOpenMenuCatalog}
              >
                <CatalogIcon className="text-primary-900" width={24} height={24} />
                {t('category')}
                <ArrowDown className="text-primary-700 -rotate-90" width={20} height={20} />
              </Button>
            </div>

            <MenuLinks />
          </div>

          <AnimatePresence>
            {openMenuCatalog && (
                <motion.div
                  key="catalogMenu"
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 5 }}
                  exit={{ opacity: 0, y: -5 }}
                  transition={{ duration: 0.25 }}
                >
                  <MenuCatalog />
                </motion.div>
              )
            }
          </AnimatePresence>
        </div>
      </div>
    </nav>
  );
}

export default Menu;