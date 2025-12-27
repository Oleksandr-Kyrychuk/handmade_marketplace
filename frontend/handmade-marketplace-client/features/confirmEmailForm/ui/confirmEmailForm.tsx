'use client';

import { EmailConfirmDTO } from "@/entities/auth/model/types/interfaces";
import AuthLayout from "@/entities/authLayout/ui/AuthLayout";
import { yupResolver } from "@hookform/resolvers/yup";
import { useTranslations } from "next-intl";
import { Controller, useForm } from "react-hook-form";
import { emailConfirmSchema } from "../validation/validation";
import OtpInput from "@/shared/UI/OtpInput/OtpInput";
import { HintIcon } from "@/assets/Icons";
import { Button } from "@/shared/UI";
import { useState } from "react";

const MAX_LENGTH = 6;

function ConfirmEmailForm() {
  const t = useTranslations();
  const [globalError, setGlobalError] = useState('');

  const {control, handleSubmit, formState: { errors }, setError, watch} = useForm<EmailConfirmDTO>({
    defaultValues: {
      verification_code: '',
    },
    resolver: yupResolver(emailConfirmSchema),
  });

  const code = watch("verification_code");
  const isCodeCompleted = code.length === MAX_LENGTH;

  async function onSubmitCode(data:EmailConfirmDTO) {
    console.log('data', data) 
  }

  return (
    <AuthLayout title={t('confirmEmailPage.title')} subtitle={t('confirmEmailPage.subtitle')} classSubtitle="text-center mt-8" classFormBlock="max-w-[780px]">
      <form onSubmit={handleSubmit(onSubmitCode)}>
        <div className="md:p-[40px] p-[20px]">
          <div className="mb-12">
            <div className="flex justify-center">
              <Controller 
                control={control}
                name="verification_code"
                render={({ field }) => (
                  <OtpInput
                    {...field}
                    maxLength={MAX_LENGTH}
                    inputType="number"
                  />
                )}
              />
            </div>

            {errors?.verification_code && (
              <div className="flex items-center text-red-600 font-medium mb-2">
                <HintIcon className="text-red-200 flex items-center mr-1 w-5" />
                <span className="text-red-600 text-size-body-4 leading-130 font-secondary">{errors.verification_code.message}</span>
              </div>
            )}
          </div>

          {globalError && (
            <p style={{ color: "red" }} className="mb-4">
              {globalError}
            </p>
          )}
          

          <div className="flex gap-6">
            <Button type="submit" variant="default" disabled={!isCodeCompleted} className="w-1/2 text-size-body-2 font-bold leading-100">
              {t('form.confirm')}
            </Button>
            <Button type="button" variant="secondary" className="w-1/2 font-bold leading-100 text-size-body-2">
              {t('form.resend-code')}
            </Button>
          </div>
        </div>
      </form>
    </AuthLayout>
  );
}

export default ConfirmEmailForm;