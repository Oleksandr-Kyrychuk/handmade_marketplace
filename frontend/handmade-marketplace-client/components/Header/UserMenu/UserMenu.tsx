import React from 'react';
import UserInfo from './UserInfo';
import { userMenuIcons } from '@/maps/UserMenuIcons'
import { getUserMenuLinks } from '@/data/LayoutData';
import { Link } from '@/i18n/navigation';
import { useTranslations } from 'next-intl';
import Button from '@/UI/Button/Button';

function UserMenu() {
  // const {getUserProfile} = useGetUserQuery();
  // const {logOut} = useLogOutAuthMutation();

  // function handleLogOutUser() {
  //   console.log('log out click')
  //   logOut();
  //   handleCloseUserMenu();
  // }

  const t = useTranslations('user-menu.navigation');

  const userMenuLinks = getUserMenuLinks();

  const firstLinks = userMenuLinks.slice(0, -3);

  const settingsHelp = userMenuLinks.slice(-3, -1);

  const logOut = userMenuLinks.at(-1);

  return (
    <div className="user-menu h-full bg-snow rounded-tl-sm py-6 px-4 rounded-bl-sm shadow-custom1  overflow-y-auto">
      <div className="user-menu__inner">

        <UserInfo />

        <div className="user-menu__items">
          {firstLinks.map(({labelKey, path, icon}) => {
            const LinkIcon = userMenuIcons[icon];
            return (
              <div className="user-menu__item mb-2" key={labelKey}>
                <Link href={path} className="flex items-center text-size-body-3 font-bold p-4 font-secondary hover:text-accent-600 duration-500">
                  <span className="mr-2">
                    <LinkIcon className="font-secondary" width={24} height={24} />
                  </span>
                  {t(labelKey)}
                </Link>
              </div>
            )            
          })}
        </div>

        <div className="user-menu__items mt-2 border-t border-t-primary-100">
          {settingsHelp.map(({labelKey, path, icon}) => {
            const LinkIcon = userMenuIcons[icon];
            return (
              <div className="user-menu__item mb-2" key={labelKey}>
                <Link href={path} className="flex items-center text-size-body-3 font-bold p-4 font-secondary hover:text-accent-600 duration-500">
                  <span className="mr-2">
                    <LinkIcon className="font-secondary" width={24} height={24} />
                  </span>
                  {t(labelKey)}
                </Link>
              </div>
            )
          })}
        </div>

        <div className="user-menu__items mt-2 border-t border-t-primary-100">
          <button type='button' className="flex items-center text-size-body-3 font-bold p-4 font-secondary hover:text-accent-600 duration-500 w-full">
             <span className="mr-2">
                {logOut?.icon && (() => {
                  const LinkIcon = userMenuIcons[logOut.icon];
                  return <LinkIcon className="font-secondary" width={24} height={24} />;
                })()}
              </span>
              {logOut?.labelKey && t(logOut.labelKey)}
          </button>
        </div>

      </div>
    </div>
  );
}

export default UserMenu;