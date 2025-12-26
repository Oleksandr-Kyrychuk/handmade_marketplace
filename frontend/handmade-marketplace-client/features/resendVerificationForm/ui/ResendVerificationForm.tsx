'use client';

import AuthLayout from "@/entities/authLayout/ui/AuthLayout";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useResendVerificationMutation from "../model/Queries/useResendVerificationMutation";
import { yupResolver } from "@hookform/resolvers/yup";
import { resendVerificationSchema } from "../model/validation/validation";
import { Controller, useForm } from "react-hook-form";
import { CustomError } from "@/entities/auth/model/types/interfaces";
import { Button } from "@/shared/UI";
import InputField from "@/shared/UI/Input/InputField";

function ResendVerificationForm() {
  const t = useTranslations();
  const router = useRouter();
  
  const [globalError, setGlobalError] = useState('');

  const {mutateResendVerif, mutateResendVerifPending} = useResendVerificationMutation();

  const {handleSubmit, formState: {errors, isSubmitting}, setError, control} = useForm({
    resolver: yupResolver(resendVerificationSchema),
    defaultValues: {
      email: ''
    }
  });

  function onSubmit(email: string) {
    mutateResendVerif(email, {
      onSuccess: () => {
        console.log('onSuccess')
      },
      onError: (error: Error) => {
        setGlobalError('');
        const customError = error as CustomError;
        let hasFieldErrors = false;

        if (customError.original) {
          Object.entries(customError.original).forEach(([key, message]) => {
            setError(key as 'email', {
              type: 'server',
              message: message.toString() as string,
            });
          });
          hasFieldErrors = true;
        }

        if(!hasFieldErrors && customError.message) {
          setGlobalError(customError.message);
        }
      }
    })
  }

  return (
    <AuthLayout title={t('resendVerificationPage.title')} subtitle={t('resendVerificationPage.subtitle')}>
      <form autoComplete="false" onSubmit={handleSubmit(onSubmit)} className="lg:mb-12 mb-6">
        <div className="lg:mb-12 mb-6">
          <div className="mb-4">
							<Controller 
								name="email"
								control={control}
								render={({field}) => (
									<InputField 
										{...field}
										id="email"
										inputType="email"
										isHasError={!!errors.email}
										errorText={errors?.email?.message || ''}
										placeholder={t('form.email')}
										inputClassName="rounded-5xl font-secondary"
										labelClassName="block mb-1 font-size-body-4 leading-130"
										label={t('form.email')}
									/>
								)}
							/>
						</div>

            {globalError && (
              <p style={{ color: "red" }} className="mb-4">
                {globalError}
              </p>
            )}

            <Button
              type="submit"
              className="w-full font-bold leading-100 text-size-body-2 h-14"
              size="md"
              variant="default"
              disabled={mutateResendVerifPending}
            >
              {isSubmitting ? 'Loading...' : t('form.send')}
            </Button>
        </div>

      </form>
    </AuthLayout>
  );
}

export default ResendVerificationForm;