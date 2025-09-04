import { getHeaderActionLinks } from '@/data/LayoutData';
import { Link } from '@/i18n/navigation';
import { iconActive } from '@/maps/SocialIcons';
import { useTranslations } from 'next-intl';
import UserIcon from '@/assets/HeaderActions/UserIcon.svg'
import { Path } from '@/enums/Path';
import Button from '@/UI/Button/Button';
import UserMenu from '../UserMenu/UserMenu';

function HeaderActions({handleOpenUserMenu}) {
  const t = useTranslations('header.actions');

  const getAction = getHeaderActionLinks();
  return (
    <div className="flex lg:flex-row flex-col  lg:items-center lg:gap-4">
      {getAction.map(({path, labelKey, icon, count}) => {
        const Icon = iconActive[icon]
        return (
          <Link key={path} href={path} className='flex items-center'>
            <div className='relative'>
              <Icon className="text-snow hover:text-accent-600 duration-500" width={24} height={24} />
            {count && <span className='bg-red-100 absolute -top-1 left-2.5 w-4 h-4 flex items-center justify-center text-snow rounded-full text-[10px]'>1</span>}
            </div>
            <span className="lg:hidden text-size-body-3 ml-2 text-snow font-bold">{t(labelKey)}</span>
          </Link>
        )
      })}
      <Link href={Path.LogIn}>
        <UserIcon className="text-snow hover:text-accent-600 duration-500" width={24} height={24} />
      </Link>

      {/* Show after log in */}
      {/* <Button type="button" className="!p-0 hover:bg-transparent w-auto h-auto" onClick={() => handleOpenUserMenu()}>
        <span className="flex items-center justify-center lg:w-[56px] lg:h-[56px] h-[40px] w-[40px] bg-primary-100 hover:bg-primary-100 p-0 rounded-full">
          <UserIcon className="text-primary-900 hover:text-accent-600" width={24} height={24} />
        </span>
        <span className="lg:hidden text-size-body-3 ml-2 text-snow block font-bold">Профіль</span>
      </Button> */}

      {/* <UserMenu /> */}
    </div>
  );
}

export default HeaderActions;