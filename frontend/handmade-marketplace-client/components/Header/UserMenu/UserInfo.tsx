import { User } from '@/assets/Icons';
import React from 'react';

function UserInfo() {
  return (
    <div className="mb-6 flex items-center">
      <div className="rounded-full w-[56px] h-[56px] mr-4">
        <span className="flex items-center justify-center lg:w-[56px] lg:h-[56px] h-[40px] w-[40px] bg-primary-100 p-0 rounded-full">
          <User className="text-primary-900" width={24} height={24} />
        </span>
      </div>
      <div className="">
        <div className="user-menu__name text-size-h7 font-bold leading-130 mb-2">name</div>
        <div className="user-menu__contact text-size-h7 text-primary-600 leading-130">email</div>
      </div>
    </div>
  );
}

export default UserInfo;