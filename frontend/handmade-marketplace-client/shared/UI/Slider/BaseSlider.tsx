import React, { useEffect, useRef, useState } from 'react';
import { Swiper as SwiperType } from 'swiper';
import { BaseSliderProps } from './type/interface';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Pagination } from 'swiper/modules';

import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';

import './generalSliderStyle.scss'
import SliderCustomArrows from './SliderArrow/SliderCustomArrows';


function BaseSlider({children, className, navigation, pagination = false, modules = [], spaceBetween = "10", breakpoints = {}, slidesPerView = 1, ...props}: BaseSliderProps) {
  const [isBeginning, setIsBeginning] = useState(true);
  const [isEnd, setIsEnd] = useState(false);
  
  const swiperRef = useRef<SwiperType | null>(null);

  useEffect(() => {
    if (swiperRef.current) {
      swiperRef.current.update();
      setIsBeginning(swiperRef.current.isBeginning);
      setIsEnd(swiperRef.current.isEnd);
    }
  }, [children]);
  return (
    <div className={`relative ${className === 'sliderWithBlocks' ? 'overflow-hidden p-1' : ''})`}>
      <Swiper
        modules={[Navigation, Pagination, ...modules]}
        pagination={pagination ? { clickable: true } : false}
        breakpoints={breakpoints}
        className={`${className === 'sliderWithBlocks' ? '!overflow-visible' : '' })`}
        slidesPerView={slidesPerView}
        spaceBetween={spaceBetween}
        onSwiper={(swiper) => {
          swiperRef.current = swiper;
          setIsBeginning(swiper.isBeginning);
          setIsEnd(swiper.isEnd);
        }}
        onSlideChange={(swiper) => {
          setIsBeginning(swiper.isBeginning);
          setIsEnd(swiper.isEnd);
        }}
        {...props}
      >
        {React.Children.map(children, (child, index) => (
          <SwiperSlide key={index}>{child}</SwiperSlide>
        ))}
      </Swiper>



      {navigation && (<SliderCustomArrows swiperRef={swiperRef} isBeginning={isBeginning} isEnd={isEnd} />)}
    </div>
  );
}

export default BaseSlider;