"use client";

import { useTranslations } from "next-intl";
import { Link } from "@/shared/i18n";
import { BaseSlider, Button } from "@/shared/UI";
import PromoLogo from '@/assets/PromoSlider/PromoLogo.svg'

import style from './style/PromoSlider.module.scss'
import { promoSliderData } from "./data/data";
import Container from "../Container/Container";


function PromoSlider() {
  const t = useTranslations();

  return (
    <div className="pattern-bg lg:py-6 py-12">
      <Container>
        <BaseSlider 
          pagination={true} 
          spaceBetween={10}
          className="promo-banner"
        >
          {promoSliderData.map(slide => (
            <div className="slide" key={slide.titleKey}>
              <div className="flex items-center justify-between lg:gap-6 gap-9 lg:flex-row flex-col">
                <div className="lg:order-1 order-2">
                  <div className="slide__content lg:p-12 md:p-6 p-4 bg-snow rounded-4xl shadow-custom2 max-w-[566px]">
                    <div className="slide__content-body">
                      <div className="slide__content-title leading-130 uppercase xl:text-size-h1 lg:text-size-h5 md:text-size-h3 text-size-h1 text-accent-800 lg:mb-10 md:mb-8 mb-4">
                       {t(slide.titleKey)}
                      </div>
                      <div className="slide__content-text">
                        {slide.descriptionKeys.map((descKey, i) => (
                          <p key={i} className="font-secondary xl:text-size-body-1 lg:text-size-body-3 md:text-size-body-2 text-size-body-3 leading-130 mb-3">
                            {t(descKey)} 
                          </p>
                        ))}
                      </div>
                    </div>
                    <div className="slide__content-btns flex md:gap-4 gap-2 lg:mt-14 mt-8">
                      {slide.buttons && (
                        slide.buttons.map(button => (
                          <Button key={button.labelKey} className="md:text-size-body-2 text-size-body-3 md:py-[18px] md:px-10 p-4" variant={button.variant}>
                            <Link href={button.href}>{t(button.labelKey)}</Link>
                          </Button>
                        ))
                      )}
                      
                    </div>
                  </div>
                </div>

                <div className="relative lg:pl-6 lg:w-[58%] lg:order-2 order-1">
                  {slide.stats && (
                    slide.stats.map(stat => (
                      <div key={stat.labelKey} className={`${style['infoBlock']} ${style[stat.style]} bg-primary-900 xl:rounded-4xl lg:rounded-2xl xl:py-6 xl:px-8 lg:py-3 lg:px-4 p-2 flex items-center justify-center xl:w-[200px] xl:h-[200px] lg:w-[98px] lg:h-[98px] md:w-[150px] md:h-[150px] w-[96px] h-[96px] md:rounded-4xl rounded-2xl flex-col`}>
                          <div className="info-block__title xl:text-size-h2 lg:text-size-h5 text-size-h2 text-snow text-center leading-100 md:mb-3 mb-1">{stat.value}</div>
                          <div className="info-block__text xl:text-size-h6 lg:text-size-h7 md:text-size-h6 leading-130 text-snow text-center">{t(stat.labelKey)}</div>
                      </div>
                    ))
                  )}
                  <PromoLogo className="xl:w-auto lg:w-full xl:h-auto lg:h-full w-full h-full" />
                </div>
              </div>
            </div>
          ))}
        </BaseSlider>
      </Container>
    </div>
  );
}

export default PromoSlider;