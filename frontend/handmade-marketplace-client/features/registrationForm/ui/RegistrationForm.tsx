'use client';

import AuthLayout from "@/entities/authLayout/ui/AuthLayout";
import { yupResolver } from "@hookform/resolvers/yup";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { signupSchema } from "../validation/validation";
import { SignUpRequestDTO } from "@/entities/auth/model/types/interfaces";
import PlatformsButtons from "@/entities/platformsButtons/PlatformsButtons";
import { Button } from "@/shared/UI";
import InputField from "@/shared/UI/Input/InputField";
import { ErrorCheckIcon, SuccessCheckIcon } from "@/assets/Icons";
import Link from "next/link";
import { Path } from "@/shared/enums/Path";
import BaseControlField from "@/shared/UI/InputControl/BaseControlField";

function RegistrationForm() {
  const t = useTranslations();

  const [showPassword, setShowPassword] = useState(false);
	const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

	const [globalError, setGlobalError] = useState('');


  const {handleSubmit, register, formState: {errors}, setError, watch} = useForm<SignUpRequestDTO>({
    resolver: yupResolver(signupSchema),
    defaultValues: {
      username: '',
      surname: '',
      password: '',
      password_confirm: '',
      agreeTerms: false,
    }
  });

  const isTermsAccepted = watch('agreeTerms');
  const passwordValue = watch('password');
	const isLengthValid = passwordValue ? passwordValue.length >= 8 : '';
	const hasUpperCase = /[A-Z]/.test(passwordValue);
	const hasNumber = /\d/.test(passwordValue);
	const hasSpecialChar = /[!@#&()–/[{}\]:;',?/*~$^+=<>]/.test(passwordValue);

  function onSubmit(data: SignUpRequestDTO) {
    console.log('data', data)
  }

  return (
    <AuthLayout title="registrationPage.title" subtitle="registrationPage.subtitle">
      <form autoComplete="off" onSubmit={handleSubmit(onSubmit)} className="lg:mb-12 mb-6">
					<div className="lg:mb-12 mb-6">
						<div className="flex lg:gap-6 lg:flex-row flex-col">
							<div className="mb-4 flex-1/2">
                <InputField 
                  id="username"
                  inputType="text"
                  isHasError={!!errors.username}
                  errorText={errors?.username?.message || ''}
                  {...register('username')}
                  placeholder={t('form.name')}
                  inputClassName="rounded-5xl font-secondary"
                  labelClassName="block mb-1 font-size-body-4 leading-130"
                  label={t('form.name')}
                />
							</div>
							<div className="mb-4 flex-1/2">
                <InputField 
                  id="surname"
                  inputType="text"
                  isHasError={!!errors.surname}
                  errorText={errors?.surname?.message || ''}
                  {...register('surname')}
                  placeholder={t('form.last-name')}
                  inputClassName="rounded-5xl font-secondary"
                  labelClassName="block mb-1 font-size-body-4 leading-130"
                  label={t('form.last-name')}
                />
							</div>
						</div>

						<div className="mb-4">
							<InputField 
								id="email"
								inputType="email"
								isHasError={!!errors.email}
                errorText={errors?.email?.message || ''}
								{...register('email')}
								placeholder={t('form.email')}
                inputClassName="rounded-5xl font-secondary"
                labelClassName="block mb-1 font-size-body-4 leading-130"
								label={t('form.email')}
							/>
						</div>

						<div className="flex lg:gap-6 lg:flex-row flex-col">
							<div className="flex-1/2">
								<div className="mb-4">
									<InputField
                    id="password"
                    inputType="password"
                    {...register('password')}
                    inputClassName="rounded-5xl font-secondary pr-12"
                    labelClassName="block mb-1 font-size-body-4 leading-130"
                    placeholder={t('form.enter-password')}
                    isHasError={!!errors.password}
                    errorText={errors?.password?.message || ''}
                    label={t('form.password')}
                  />
								</div>
							</div>
							<div className="flex-1/2">
								<div className="mb-4">
                    <InputField
                      id="password_confirm"
                      inputType="password"
                      {...register('password_confirm')}
                      inputClassName="rounded-5xl font-secondary pr-12"
                      labelClassName="block mb-1 font-size-body-4 leading-130"
                      placeholder={t('form.repeat-the-password')}
                      isHasError={!!errors.password_confirm}
                      errorText={errors?.password_confirm?.message || ''}
                      label={t('form.repeat-the-password')}
                    />
								</div>
							</div>
						</div>

						{passwordValue && (<div>
							<div className="text-size-body-4 font-secondary text-primary-500 mb-2">Ваш пароль має:</div>
								<ul className='list-none'>
									<li className="flex items-center mb-2">
										{hasUpperCase ? <SuccessCheckIcon className="text-green-200" /> : <ErrorCheckIcon className="text-red-200" /> }
										<span className="text-primary-500 text-size-body-4 font-secondary ml-1">Включати великі та малі літери</span>
									</li>
									<li className="flex items-center mb-2">
										{hasNumber ? <SuccessCheckIcon className="text-green-200" /> : <ErrorCheckIcon className="text-red-200" /> }
										<span className="text-primary-500 text-size-body-4 font-secondary ml-1">Включати цифри</span>
									</li>
									<li className="flex items-center mb-2">
										{isLengthValid ? <SuccessCheckIcon className="text-green-200" /> : <ErrorCheckIcon className="text-red-200" /> }
										<span className="text-primary-500 text-size-body-4 font-secondary ml-1">Бути не менш ніж 8 символів</span>
									</li>
									<li className="flex items-center mb-2">
										{hasSpecialChar ? <SuccessCheckIcon className="text-green-200" /> : <ErrorCheckIcon className="text-red-200" /> }
										<span className="text-primary-500 text-size-body-4 font-secondary ml-1">Принаймні один спеціальний символ.</span>
									</li>
								</ul>
							</div>
						)}


						<div className="mt-4">
              <BaseControlField 
                inputId="agreeTerms" 
                inputType="checkbox" 
                inputClassName="w-5 h-5"
                register={register}
                isHasError={!!errors.agreeTerms}
                errorText={errors?.agreeTerms?.message || ''} 
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
						disabled={!isTermsAccepted}
						type="submit"
		
						className="w-full h-[55px] font-secondary text-size-body-2 font-bold leading-100"
            variant="default"
					>
						{t('form.sign-up')}
					</Button>
				</form>

				<div className="separateBlock relative text-center mb-6">
					<span className="bg-transparent relative z-10 px-2 text-primary-400 separateBlock__text leading-130 inline-block">
						{t('form.sing-up-with')}
					</span>
				</div>

				<PlatformsButtons />

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