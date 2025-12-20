'use client';

import { Controller, useForm } from "react-hook-form";
import { resetEmailSchema } from "../model/validation/validation";
import { yupResolver } from "@hookform/resolvers/yup";
import AuthLayout from "@/entities/authLayout/ui/AuthLayout";
import { useTranslations } from "next-intl";
import InputField from "@/shared/UI/Input/InputField";
import { useState } from "react";
import { Button } from "@/shared/UI";
import useResetVerificationMutation from "../model/Queries/useResetVerificationMutation";
import { Path } from "@/shared/enums/Path";
import { CustomError } from "@/entities/auth/model/types/interfaces";
import { useRouter } from "next/navigation";

function ResetPasswordForm() {
  const t = useTranslations();
  const router = useRouter()

  const [globalError, setGlobalError] = useState('');

  const {mutateResetVerif, mutateResetVerifPending} = useResetVerificationMutation();

  const {handleSubmit, register, formState: {errors}, setError, control} = useForm({
    resolver: yupResolver(resetEmailSchema),
  });

  function onSubmit(data: string) {
    console.log('data', data)

    mutateResetVerif(data, {
      onSuccess: () => {
        router.push(Path.Confirm_email)
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
    <AuthLayout title={t('resetPasswordPage.title')} subtitle={t('resetPasswordPage.subtitle')}>
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
										{...register('email')}
										placeholder="Email"
										inputClassName="rounded-5xl font-secondary"
										label={t('form.email')}
									/>
								)}
							/>
						</div>

            <Button
              type="submit"
              className="w-full font-bold leading-100 text-size-body-2 h-14"
              size="md"
              variant="default"
              disabled={mutateResetVerifPending}
            >
              {t('form.send')}
            </Button>
        </div>

        {globalError && (
						<p style={{ color: "red" }} className="mb-4">
							{globalError}
						</p>
					)}

      </form>
    </AuthLayout>
  );
}

export default ResetPasswordForm;