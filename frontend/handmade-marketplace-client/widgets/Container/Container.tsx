import React from 'react';
import { IContainerProps } from './type/interfaces';

function Container({children}: IContainerProps) {
  return (
    <div className='container mx-auto px-4'>
      {children}
    </div>
  );
}

export default Container;