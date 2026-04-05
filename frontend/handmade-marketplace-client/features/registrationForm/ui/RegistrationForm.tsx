'use client';

import AuthLayout from "@/entities/authLayout/ui/AuthLayout";
import { yupResolver } from "@hookform/resolvers/yup";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { signupSchema } from "../validation/validation";
import { CustomError, SignUpRequestDTO } from "@/entities/auth/model/types/interfaces";
import PlatformsButtons from "@/entities/platformsButtons/PlatformsButtons";
import { Button } from "@/shared/UI";
import InputField from "@/shared/UI/Input/InputField";
import { ErrorCheckIcon, SuccessCheckIcon } from "@/assets/Icons";
import Link from "next/link";
import { Path } from "@/shared/enums/Path";
import BaseControlField from "@/shared/UI/InputControl/BaseControlField";
import useRegistrationMutation from "../model/Quries/useRegistrationMutation";
import { useRouter } from "@/shared/i18n";



function RegistrationForm() {
  const t = useTranslations();
	const router = useRouter()

	const [globalError, setGlobalError] = useState('');
	const { registrationMutation } = useRegistrationMutation();


  const {handleSubmit, register, formState: {errors, isSubmitting}, setError, watch, control} = useForm<SignUpRequestDTO>({
    resolver: yupResolver(signupSchema),
		mode: 'onChange',
    defaultValues: {
      username: '',
      surname: '',
			email: '',
      password: '',
      password_confirm: '',
      agree_terms: false,
    }
  });

  const isTermsAccepted = watch('agree_terms');
  const passwordValue = watch('password');
	const isLengthValid = passwordValue ? passwordValue.length >= 8 : '';
	const hasUpperCase = /[A-Z]/.test(passwordValue);
	const hasNumber = /\d/.test(passwordValue);
	const hasSpecialChar = /[!@#&()–/[{}\]:;',?/*~$^+=<>]/.test(passwordValue);

  function onSubmit(data: SignUpRequestDTO) {
    console.log('data', data)
		console.log('router',router);

		registrationMutation(data, {
			onSuccess: () => {
				router.push(Path.Send_confirm_email)
			},
			onError: (error: Error) => {
				setGlobalError('');
				const customError = error as CustomError;
				let hasFieldErrors = false;

				console.log('error', error)

				if (customError.fieldErrors) {
					Object.entries(customError.fieldErrors).forEach(([key, message]) => {
						setError(key as keyof SignUpRequestDTO, {
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
    <AuthLayout title={t('registrationPage.title')} subtitle={t("registrationPage.subtitle")}>
      <form autoComplete="off" onSubmit={handleSubmit(onSubmit)} className="lg:mb-12 mb-6">
					<div className="lg:mb-12 mb-6">
						<div className="flex lg:gap-6 lg:flex-row flex-col">
							<div className="mb-4 flex-1/2">
							<Controller 
								name="username"
								control={control}
								render={({field}) => (
									<InputField 
										{...field}
										id="username"
										inputType="text"
										isHasError={!!errors.username}
										errorText={errors?.username?.message || ''}
										placeholder={t('form.name')}
										inputClassName="rounded-5xl font-secondary"
										labelClassName="block mb-1 font-size-body-4 leading-130"
										label={t('form.name')}
										
									/>
								)}
							/>
                
							</div>
							<div className="mb-4 flex-1/2">
								<Controller 
									name="surname"
									control={control}
									render={({field}) => (
										<InputField 
											{...field}
											id="surname"
											inputType="text"
											isHasError={!!errors.surname}
											errorText={errors?.surname?.message || ''}
											placeholder={t('form.last-name')}
											inputClassName="rounded-5xl font-secondary"
											labelClassName="block mb-1 font-size-body-4 leading-130"
											label={t('form.last-name')}
											
										/>
									)}
								/>
							</div>
						</div>

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

						<div className="flex lg:gap-6 lg:flex-row flex-col">
							<div className="flex-1/2">
								<div className="mb-4">
									<Controller 
										name="password"
										control={control}
										render={({field}) => (
											<InputField
												{...field}
												id="password"
												inputType="password"
												inputClassName="rounded-5xl font-secondary pr-12"
												labelClassName="block mb-1 font-size-body-4 leading-130"
												placeholder={t('form.enter-password')}
												isHasError={!!errors.password}
												errorText={errors?.password?.message || ''}
												label={t('form.password')}
											/>
										)}
									/>
									
								</div>
							</div>
							<div className="flex-1/2">
								<div className="mb-4">
									<Controller 
										name="password_confirm"
										control={control}
										render={({field}) => (
											<InputField
												{...field}
												id="password_confirm"
												inputType="password"
												inputClassName="rounded-5xl font-secondary pr-12"
												labelClassName="block mb-1 font-size-body-4 leading-130"
												placeholder={t('form.repeat-the-password')}
												isHasError={!!errors.password_confirm}
												errorText={errors?.password_confirm?.message || ''}
												label={t('form.repeat-the-password')}
											/>
										)}
									/>
								</div>
							</div>
						</div>

						{passwordValue && (<div>
							<div className="text-size-body-4 font-secondary text-primary-500 mb-2">Ваш пароль має:</div>
								<ul className='list-none'>
									<li className="flex items-center mb-2">
										{hasUpperCase ? <SuccessCheckIcon className="text-green-200 w-5" /> : <ErrorCheckIcon className="text-red-200 w-5" /> }
										<span className="text-primary-500 text-size-body-4 font-secondary ml-1">Включати великі та малі літери</span>
									</li>
									<li className="flex items-center mb-2">
										{hasNumber ? <SuccessCheckIcon className="text-green-200 w-5" /> : <ErrorCheckIcon className="text-red-200 w-5" /> }
										<span className="text-primary-500 text-size-body-4 font-secondary ml-1">Включати цифри</span>
									</li>
									<li className="flex items-center mb-2">
										{isLengthValid ? <SuccessCheckIcon className="text-green-200 w-5" /> : <ErrorCheckIcon className="text-red-200 w-5" /> }
										<span className="text-primary-500 text-size-body-4 font-secondary ml-1">Бути не менш ніж 8 символів</span>
									</li>
									<li className="flex items-center mb-2">
										{hasSpecialChar ? <SuccessCheckIcon className="text-green-200 w-5" /> : <ErrorCheckIcon className="text-red-200 w-5" /> }
										<span className="text-primary-500 text-size-body-4 font-secondary ml-1">Принаймні один спеціальний символ.</span>
									</li>
								</ul>
							</div>
						)}


						<div className="mt-4">
              <BaseControlField 
                inputId="agree_terms" 
                inputType="checkbox" 
                inputClassName="w-5 h-5"
                register={register}
                isHasError={!!errors.agree_terms}
                errorText={errors?.agree_terms?.message || ''} 
                label={t('form.i-agree')}
              />
						</div>
					</div>

					{globalError && (
						<p style={{ color: "red" }} className="mb-4">
							{globalError}
						</p>
					)}

					<Button
						disabled={!isTermsAccepted || isSubmitting}
						type="submit"

						className="w-full h-[55px] font-secondary text-size-body-2 font-bold leading-100"
            variant="default"
					>
						{isSubmitting ? 'Loading...' : t('form.sign-up')}
						
					</Button>
				</form>

				<div className="separateBlock relative text-center mb-6">
					<span className="bg-transparent relative z-10 px-2 text-primary-400 separateBlock__text leading-130 inline-block">
						{t('form.sing-up-with')}
					</span>
				</div>

				<PlatformsButtons />

				<div className="formBottom mb-6">
					<div className="flex justify-center items-center lg:flex-row flex-col ">
						<div className="text-size-body-3 leading-130 lg:mb-0 mb-2 font-secondary">
							{t('form.resend-verification')}
						</div>
						<Link href={Path.Resend_verification}
							className="text-primary-600 text-size-link-1 ml-2 leading-100"
						>
							{t('form.resend-verification-link')}
						</Link>
					</div>
				</div>

				<div className="formBottom">
					<div className="flex justify-center items-center lg:flex-row flex-col ">
						<div className="text-size-body-3 leading-130 lg:mb-0 mb-2 font-secondary">
							{t('form.not-registered-yet')}
						</div>
						<Link href={Path.LogIn}
							className="text-primary-600 text-size-link-1 ml-2 leading-100"
						>
							{t('form.exit')}
						</Link>
					</div>
				</div>
    </AuthLayout>
  );
}

export default RegistrationForm;